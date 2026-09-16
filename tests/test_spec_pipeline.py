import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("spec_pipeline", ROOT / "tools" / "spec_pipeline.py")
PIPELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PIPELINE)


class SpecPipelineTest(unittest.TestCase):
    def test_release_axes_are_distinct(self):
        lock = json.loads(PIPELINE.LOCK.read_text())
        self.assertEqual("0.9.1.2", lock["release_version"])
        self.assertEqual("0.9.0", lock["base_schema_version"])
        self.assertEqual("0.9.2", lock["actor_config_profile_version"])

    def test_source_lock_matches(self):
        lock = json.loads(PIPELINE.LOCK.read_text())
        self.assertEqual(lock["source_sha256"], hashlib.sha256(PIPELINE.SOURCE.read_bytes()).hexdigest())

    def test_canonical_hashes_match_lock(self):
        lock = json.loads(PIPELINE.LOCK.read_text())["canonical"]
        expected = {
            PIPELINE.BASE: lock["schema_sha256"],
            PIPELINE.EXPANSION: lock["expansion_sha256"],
            PIPELINE.BASE.with_name("starintel-doc-v0.9.0.manifest.json"): lock["manifest_sha256"],
        }
        for path, digest in expected.items():
            self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest(), str(path))

    def test_all_canonical_dtypes_survive(self):
        base = json.loads(PIPELINE.BASE.read_text())
        generated = PIPELINE.generated_documents()
        current = json.loads(generated[PIPELINE.SCHEMA])
        old_dtypes = set(base["properties"]["dtype"]["enum"])
        new_dtypes = set(current["properties"]["dtype"]["enum"])
        self.assertEqual(old_dtypes | {"actor-config"}, new_dtypes)
        old_branches = PIPELINE.dtype_branches(base)
        new_branches = PIPELINE.dtype_branches(current)
        for dtype, contract in old_branches.items():
            self.assertEqual(contract, new_branches[dtype], dtype)

    def test_actor_config_is_tenant_scoped_and_secret_free(self):
        profile = PIPELINE.actor_profile_schema()
        properties = profile["properties"]
        self.assertIn("tenant_id", profile["required"])
        self.assertIn("credential_ref", properties)
        self.assertNotIn("access_token", properties)
        self.assertNotIn("client_secret", properties)
        self.assertEqual(
            ["basic", "plus", "professional", "enterprise"],
            properties["actor_group"]["enum"],
        )
        self.assertFalse(any("price" in key or "quota" in key for key in properties))

    def test_profile_and_hashtag_targets_exist(self):
        properties = PIPELINE.actor_profile_schema()["properties"]
        self.assertIn("profile_targets", properties)
        self.assertIn("hashtag_targets", properties)
        self.assertIn("one_run", properties)

    def test_starlang_manifest_covers_every_dtype(self):
        manifest = PIPELINE.portable_manifest(PIPELINE.SOURCE.read_text())
        names = {item["name"].rsplit("/", 1)[-1] for item in manifest["types"] if item["kind"] == "document"}
        base = json.loads(PIPELINE.BASE.read_text())
        self.assertTrue(set(base["properties"]["dtype"]["enum"]).issubset(names))
        self.assertIn("actor-config", names)

    def test_portable_manifest_preserves_field_markers(self):
        manifest = PIPELINE.portable_manifest(PIPELINE.SOURCE.read_text())
        self.assertNotIn("digest", manifest["library"])
        actor_config = next(
            item for item in manifest["types"]
            if item["name"].endswith("/actor-config-data")
        )
        fields = {field["name"]: field for field in actor_config["fields"]}
        self.assertTrue(fields["tenantId"]["required"])
        self.assertFalse(fields["credentialRef"]["required"])


if __name__ == "__main__":
    unittest.main()
