#!/usr/bin/env python3
"""Bootstrap and build the StarIntel schema from StarLang source.

The legacy JSON Schema remains an immutable compatibility layer. StarLang owns
the release/type registry and all additive profiles; generated JSON overlays it
without weakening any inherited constraint.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "spec" / "starintel-doc-v0.9.1.2.star"
LOCK = ROOT / "spec" / "release.lock.json"
BASE = ROOT / "canonical" / "0.9.0" / "starintel-doc-v0.9.0.schema.json"
EXPANSION = ROOT / "canonical" / "0.9.0" / "starintel-doc-v0.9.0.expansion.json"
PORTABLE = ROOT / "generated" / "0.9.1.2" / "starintel-doc-v0.9.1.2.manifest.json"
SCHEMA = ROOT / "generated" / "0.9.1.2" / "starintel-doc-v0.9.1.2.schema.json"
PROFILE = ROOT / "generated" / "0.9.1.2" / "actor-config-v0.9.2.schema.json"

PRIMITIVES = {
    "string", "integer", "decimal", "float", "boolean", "symbol", "map",
    "reference", "iso-date", "iso-datetime",
}


def camel(name: str) -> str:
    name = name.lstrip("_")
    parts = name.split("_")
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def json_type_to_star(schema: dict) -> str:
    if "x-star-type" in schema:
        return schema["x-star-type"]
    if "const" in schema:
        value = schema["const"]
        if isinstance(value, str):
            return "string"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
    if "anyOf" in schema:
        candidates = [value for value in schema["anyOf"] if value.get("type") != "null"]
        return json_type_to_star(candidates[0]) if len(candidates) == 1 else "map"
    kind = schema.get("type")
    if kind == "array":
        return f"(list {json_type_to_star(schema.get('items', {}))})"
    if kind == "number":
        return "decimal"
    if kind == "object" or not kind:
        return "map"
    return kind


def dtype_branches(base: dict) -> dict[str, dict]:
    branches: dict[str, dict] = {}
    for branch in base["allOf"]:
        dtype = branch.get("if", {}).get("properties", {}).get("dtype", {}).get("const")
        if dtype:
            branches[dtype] = branch["then"]["properties"]["data"]
    return branches


def emit_document(name: str, fields: dict, required: set[str], persistence: str) -> list[str]:
    lines = [f"  (document {name}", f"    (:persistence {persistence})"]
    for field_name, field_schema in fields.items():
        marker = ":required" if field_name in required else ":optional"
        lines.append(f"    ({camel(field_name)} {json_type_to_star(field_schema)} {marker})")
    lines[-1] += ")"
    return lines


def import_star() -> str:
    base = json.loads(BASE.read_text())
    expansion = json.loads(EXPANSION.read_text())
    lines = [
        "; Generated once from the server-pinned canonical v0.9.0 schema.",
        "; This file is now authoritative for additive StarIntel spec changes.",
        "; Deeper legacy JSON constraints are retained by the immutable locked import.",
        '(spec-library "org.starintel/document@0"',
        '  (:version "0.9.1.2")',
        "",
        "  (scalar actor-config-profile-version",
        '    (:base string :pattern "^0\\\\.9\\\\.2$"))',
        "",
        "  (enum actor-group",
        "    (basic plus professional enterprise))",
        "",
    ]
    top_fields = {key: value for key, value in base["properties"].items() if key != "data"}
    lines.extend(emit_document("starintel-document", top_fields, set(base["required"]) - {"data"}, "persistent"))
    lines.append("")
    for dtype, data in dtype_branches(base).items():
        props = data.get("properties", {})
        lines.extend(emit_document(f"{dtype}-data", props, set(data.get("required", [])), "transient"))
        lines.extend([
            f"  (document {dtype}",
            "    (:extends starintel-document :persistence persistent)",
            f"    (data {dtype}-data :required))",
            "",
        ])
    actor_fields = {
        "profile_version": {"x-star-type": "actor-config-profile-version"},
        "tenant_id": {"type": "string"},
        "actor_id": {"type": "string"},
        "enabled": {"type": "boolean"},
        "actor_group": {"x-star-type": "actor-group"},
        "profile_targets": {"type": "array", "items": {"type": "string"}},
        "hashtag_targets": {"type": "array", "items": {"type": "string"}},
        "credential_ref": {"type": "string"},
        "one_run": {"type": "boolean"},
        "max_runs": {"type": "integer"},
        "schedule": {"type": "object"},
        "parameters": {"type": "object"},
        "created_by": {"type": "string"},
    }
    lines.extend(emit_document(
        "actor-config-data", actor_fields,
        {"profile_version", "tenant_id", "actor_id", "enabled", "actor_group"}, "transient",
    ))
    lines.extend([
        "  (document actor-config",
        "    (:extends starintel-document :persistence persistent)",
        "    (data actor-config-data :required)))",
    ])
    return "\n".join(lines) + "\n"


def tokenize(source: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    while index < len(source):
        char = source[index]
        if char.isspace():
            index += 1
        elif char == ";":
            index = source.find("\n", index)
            if index < 0:
                break
        elif char in "()":
            tokens.append(char)
            index += 1
        elif char == '"':
            end = index + 1
            escaped = False
            while end < len(source):
                if source[end] == '"' and not escaped:
                    break
                escaped = source[end] == "\\" and not escaped
                if source[end] != "\\":
                    escaped = False
                end += 1
            if end == len(source):
                raise ValueError("unterminated StarLang string")
            tokens.append(json.loads(source[index : end + 1]))
            index = end + 1
        else:
            end = index
            while end < len(source) and not source[end].isspace() and source[end] not in "();":
                end += 1
            tokens.append(source[index:end])
            index = end
    return tokens


def parse(tokens: list[str]):
    index = 0
    def value():
        nonlocal index
        if tokens[index] != "(":
            item = tokens[index]
            index += 1
            return item
        index += 1
        result = []
        while tokens[index] != ")":
            result.append(value())
        index += 1
        return result
    result = value()
    if index != len(tokens):
        raise ValueError("multiple StarLang root forms")
    return result


def options(values: list) -> dict:
    return dict(zip(values[0::2], values[1::2]))


def portable_type(value, library: str, local_types: set[str]):
    if isinstance(value, list):
        if len(value) == 2 and value[0] == "list":
            return {"list": portable_type(value[1], library, local_types)}
        raise ValueError(f"unsupported type expression: {value!r}")
    return f"{library}/{value}" if value in local_types else value


def portable_manifest(source: str) -> dict:
    form = parse(tokenize(source))
    if form[0] != "spec-library":
        raise ValueError("expected spec-library")
    library = form[1]
    header = options(form[2])
    declarations = form[3:]
    local_types = {declaration[1] for declaration in declarations if declaration[0] in {"scalar", "enum", "document"}}
    result_types = []
    imports = []
    for declaration in declarations:
        kind, name = declaration[:2]
        qualified = f"{library}/{name}"
        if kind == "scalar":
            opts = options(declaration[2])
            item = {"base": opts.pop(":base"), "kind": "scalar", "name": qualified}
            for key, value in opts.items():
                out_key = camel(key[1:])
                item[out_key] = int(value) if isinstance(value, str) and value.isdigit() else value
            result_types.append(item)
        elif kind == "enum":
            result_types.append({"kind": "enum", "name": qualified, "values": declaration[2]})
        elif kind == "document":
            opts = options(declaration[2])
            item = {"fields": [], "kind": "document", "name": qualified,
                    "persistence": opts[":persistence"]}
            if ":extends" in opts:
                item["extends"] = portable_type(opts[":extends"], library, local_types)
            for field in declaration[3:]:
                # A field is `(name type :required|:optional ...)`; markers
                # begin immediately after the two positional values.  Starting
                # at index 3 silently dropped the marker and made every field
                # optional in the bootstrap manifest, diverging from StarLang.
                field_opts = field[2:]
                item["fields"].append({
                    "name": field[0],
                    "required": ":required" in field_opts,
                    "type": portable_type(field[1], library, local_types),
                })
            result_types.append(item)
        elif kind == "import":
            opts = options(declaration[2:])
            imports.append({"digest": opts[":digest"], "kind": "import", "name": name, "version": opts[":version"]})
        else:
            raise ValueError(f"unsupported declaration: {kind}")
    return {
        "actors": [], "imports": imports,
        "library": {"digest": header.get(":digest"), "name": library, "version": header[":version"]},
        "messages": [], "predicates": [], "types": result_types, "wireVersion": 1,
    }


def actor_profile_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://spec.starintel.actor/profile/actor-config-v0.9.2.json",
        "title": "StarIntel actor-config profile v0.9.2",
        "type": "object",
        "additionalProperties": False,
        "required": ["profile_version", "tenant_id", "actor_id", "enabled", "actor_group"],
        "properties": {
            "profile_version": {"const": "0.9.2"},
            "tenant_id": {"type": "string", "minLength": 1},
            "actor_id": {"type": "string", "minLength": 1},
            "enabled": {"type": "boolean"},
            "actor_group": {"enum": ["basic", "plus", "professional", "enterprise"]},
            "profile_targets": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
            "hashtag_targets": {"type": "array", "items": {"type": "string", "pattern": "^#?[^\\s#]+$"}, "uniqueItems": True},
            "credential_ref": {"type": "string", "minLength": 1},
            "one_run": {"type": "boolean", "default": False},
            "max_runs": {"type": "integer", "minimum": 1},
            "schedule": {"type": "object", "additionalProperties": True},
            "parameters": {"type": "object", "additionalProperties": True},
            "created_by": {"type": "string"},
        },
        "allOf": [{"if": {"properties": {"one_run": {"const": True}}, "required": ["one_run"]},
                   "then": {"properties": {"max_runs": {"const": 1}}}}],
        "$comment": "Secrets are referenced, never embedded. Effective quotas are server policy, not schema data.",
    }


def generated_documents() -> dict[Path, str]:
    lock = json.loads(LOCK.read_text())
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if lock["source_sha256"] != source_hash:
        raise ValueError(f"source hash mismatch: lock={lock['source_sha256']} actual={source_hash}")
    base = json.loads(BASE.read_text())
    profile = actor_profile_schema()
    schema = copy.deepcopy(base)
    schema["$id"] = "https://spec.starintel.actor/schema/starintel-doc-v0.9.1.2.json"
    schema["title"] = "StarIntel Document release v0.9.1.2 (base schema v0.9.0)"
    enum = schema["properties"]["dtype"]["enum"]
    if "actor-config" not in enum:
        enum.append("actor-config")
    schema["allOf"].append({
        "if": {"properties": {"dtype": {"const": "actor-config"}}},
        "then": {"properties": {"data": profile}, "required": ["data"]},
    })
    manifest = portable_manifest(SOURCE.read_text())
    return {
        PORTABLE: json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        PROFILE: json.dumps(profile, indent=2, sort_keys=True) + "\n",
        SCHEMA: json.dumps(schema, indent=2, sort_keys=True) + "\n",
    }


def write_generated(check: bool) -> None:
    failures = []
    for path, content in generated_documents().items():
        if check:
            if not path.exists() or path.read_text() != content:
                failures.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if failures:
        raise SystemExit("generated files are stale: " + ", ".join(failures))


def lock_source() -> None:
    lock = json.loads(LOCK.read_text())
    lock["source_sha256"] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    LOCK.write_text(json.dumps(lock, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["import-star", "manifest", "lock", "build", "check"])
    args = parser.parse_args()
    if args.command == "import-star":
        sys.stdout.write(import_star())
    elif args.command == "manifest":
        json.dump(portable_manifest(SOURCE.read_text()), sys.stdout, indent=2, sort_keys=True)
        print()
    elif args.command == "lock":
        lock_source()
    else:
        write_generated(check=args.command == "check")


if __name__ == "__main__":
    main()
