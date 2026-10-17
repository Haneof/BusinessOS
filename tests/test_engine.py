import json
import tempfile
import unittest
from pathlib import Path

from businessos.contracts import Candidate, DeterministicVerifier
from businessos.engine import DemoEngine
from businessos.policy import Policy
from businessos.store import Store


class EngineTests(unittest.TestCase):
    def test_demo_generates_only_mock_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "artifacts"
            db = Path(tmp) / "state.db"
            result = DemoEngine(Store(db), Policy(), out).run()
            self.assertEqual(result["mode"], "DRY_RUN_ONLY")
            self.assertEqual(len(result["candidates"]), 3)
            self.assertTrue(all(not x["market_validated"] for x in result["candidates"]))
            self.assertFalse(result["publishing_performed"])
            self.assertEqual(result["publishing_permission"], "require_approval")
            self.assertIsNone(Store(db).stats()["verified_income_cents"])
            self.assertTrue((out / "report.json").is_file())
            self.assertEqual(json.loads((out / "report.json").read_text())["real_sales"], "NOT_CONNECTED")

    def test_verifier_does_not_claim_market_validation(self):
        v = DeterministicVerifier()
        item = Candidate("example-id", "Example", "Problem", "Sample", 100, 10)
        passed, why = v.verify("Hello", item)
        self.assertFalse(passed)
        self.assertIn("Missing", why)

    def test_rejects_unverified_external_research(self):
        class FakeResearch:
            def candidates(self):
                return [Candidate("sample", "Example", "Problem", "Sample", 100, 10, "EXTERNAL")]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                DemoEngine(Store(Path(tmp) / "db"), Policy(), Path(tmp) / "out").run(FakeResearch())

    def test_candidate_id_cannot_traverse_filesystem(self):
        class BadResearch:
            def candidates(self):
                return [Candidate("../escape", "Example", "Problem", "Sample", 100, 10)]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                DemoEngine(Store(Path(tmp) / "db"), Policy(), Path(tmp) / "out").run(BadResearch())
