# star-spec

StarLang is the only StarIntel document specification authority. This repository
consumes the immutable generated 0.10.1 release pinned in
`schema/starintel-schema.lock.json`; its complete source, schema, bindings,
portable manifest, migration policy and fixtures are vendored under
`schemas/starintel-0.10.1/`.

Change document semantics in
[lost-rob0t/star-lang](https://github.com/lost-rob0t/star-lang/tree/agent/qa-network-capture-0.10.1/specs/starintel/0.10.1),
regenerate there, then repin consumers with the shared tool:

```sh
python3 scripts/sync-starintel-schema.py --commit FULL_IMMUTABLE_STARLANG_SHA
python3 scripts/sync-starintel-schema.py
python3 -m unittest discover -s tests -v
```

The generated schema is a definitions library. Runtime consumers select the
concrete document definition using the generated manifest, enforce
`schemaVersion` and the canonical dtype, and enforce decimal bounds/scale from
the manifest. Validating only the schema root is insufficient.

`spec/geo/` retains the historical draft projection profile and its tests.
Its `0.9.1.2` parent coordinate is historical metadata, not the current StarIntel
release. Projection guidance cannot introduce new canonical document fields;
those belong in StarLang. No independently authored document registry or local
release generator is maintained here.
