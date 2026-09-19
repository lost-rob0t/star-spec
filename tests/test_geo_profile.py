import json
import re
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "spec" / "geo" / "profile.json"
FIXTURE_PATH = ROOT / "spec" / "geo" / "fixtures" / "geo-projection.jsonld"
PROLOG_PATH = ROOT / "spec" / "geo" / "prolog" / "geo-v1.pl"


class GeoProfileConformanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.prolog = PROLOG_PATH.read_text(encoding="utf-8")

    def test_profile_identity_and_release_axis(self):
        self.assertEqual("starintel.geo", self.profile["profileId"])
        self.assertEqual("1.0.0-draft.1", self.profile["profileVersion"])
        self.assertEqual("0.9.1.2", self.profile["parentRelease"])
        self.assertEqual("draft", self.profile["status"])
        self.assertEqual("canonical-starintel-documents", self.profile["semanticAuthority"])
        self.assertIs(False, self.profile["projectionAuthority"])

        normative = ROOT / self.profile["normativeDocument"]
        self.assertTrue(normative.is_file(), f"missing normative document: {normative}")

    def test_profile_vocabularies_are_bounded_and_unique(self):
        self.assertEqual(["direct", "anchored", "derived"], self.profile["participationKinds"])

        for key in ("geometryModels", "requiredCapabilities", "optionalCapabilities", "transports", "conformanceSuites"):
            values = self.profile[key]
            self.assertTrue(values, f"{key} must not be empty")
            self.assertEqual(len(values), len(set(values)), f"{key} contains duplicates")

        required = self.profile["requiredCapabilities"]
        optional = self.profile["optionalCapabilities"]
        self.assertTrue(all(value.startswith("geo.") for value in required + optional))
        self.assertTrue(set(required).isdisjoint(optional))

    def test_anchored_fixture_preserves_projection_only_semantics(self):
        fixture = self.fixture
        self.assertEqual("anchored", fixture["star:participationKind"])
        self.assertIn(fixture["star:participationKind"], self.profile["participationKinds"])
        self.assertEqual("explicit_relation", fixture["star:geometrySource"])
        self.assertIs(False, fixture["star:canonicalGeometry"])
        self.assertIs(True, fixture["star:projectionOnly"])

        document = fixture["star:document"]["@id"]
        anchor = fixture["star:anchor"]["@id"]
        path = [entry["@id"] for entry in fixture["star:relationPath"]]
        self.assertGreaterEqual(len(path), 3)
        self.assertEqual(document, path[0])
        self.assertEqual(anchor, path[-1])
        self.assertTrue(fixture["star:evidence"], "anchored fixture requires evidence")
        self.assertTrue(fixture["star:ruleProfile"].strip())

    def test_fixture_geometry_and_temporal_values_are_bounded(self):
        geometry = self.fixture["star:geometry"]
        self.assertIn(geometry["type"], self.profile["geometryModels"])
        self.assertEqual("Point", geometry["type"])
        self.assertEqual(2, len(geometry["coordinates"]))

        longitude, latitude = geometry["coordinates"]
        self.assertGreaterEqual(longitude, -180)
        self.assertLessEqual(longitude, 180)
        self.assertGreaterEqual(latitude, -90)
        self.assertLessEqual(latitude, 90)
        self.assertGreater(self.fixture["star:geometryAccuracyMeters"], 0)
        self.assertGreaterEqual(self.fixture["star:confidence"], 0)
        self.assertLessEqual(self.fixture["star:confidence"], 1)

        valid_from = self.fixture["star:validFrom"]
        parsed = datetime.fromisoformat(valid_from.replace("Z", "+00:00"))
        self.assertIsNotNone(parsed.tzinfo)
        self.assertIsNone(self.fixture["star:validTo"])

    def test_reference_prolog_keeps_direct_anchored_derived_precedence(self):
        exports = re.search(
            r":-\s*module\(starintel_geo_v1,\s*\[(.*?)\]\)\.",
            self.prolog,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(exports, "missing starintel_geo_v1 module declaration")
        exported_text = exports.group(1)
        for predicate in (
            "geo_participation/3",
            "projection_kind/2",
            "direct_geo/1",
            "anchored_geo/3",
            "derived_geo/4",
            "projection_explainable/1",
        ):
            self.assertIn(predicate, exported_text)

        self.assertIn("geo_participation(Doc, direct, Doc)", self.prolog)
        self.assertIn("geo_participation(Doc, anchored, Anchor) :-\n    \\+ direct_geo(Doc)", self.prolog)
        self.assertIn(
            "geo_participation(Doc, derived, Anchor) :-\n"
            "    \\+ direct_geo(Doc),\n"
            "    \\+ anchored_geo(Doc, _, _)",
            self.prolog,
        )
        self.assertIn("projection_source(Projection, direct_geometry)", self.prolog)
        self.assertIn("projection_source(Projection, explicit_relation)", self.prolog)
        self.assertIn("projection_source(Projection, expert_rule)", self.prolog)


if __name__ == "__main__":
    unittest.main()
