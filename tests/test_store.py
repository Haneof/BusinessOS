import tempfile
import unittest
from pathlib import Path

from businessos.store import Store


class StoreTests(unittest.TestCase):
    def test_persists_events_and_separates_simulated_money(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "store.db"
            store = Store(db)
            store.event("test", {"result": "pass"})
            store.simulated_amount("income", 10000, "mock")
            store.simulated_amount("expense", 200, "mock")
            status = Store(db).stats()
            self.assertEqual(status["events"], 1)
            self.assertEqual(status["simulated_income_cents"], 10000)
            self.assertEqual(status["simulated_expense_cents"], 200)
            self.assertIsNone(status["verified_profit_cents"])

    def test_invalid_simulated_money_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Store(Path(tmp) / "store.db")
            with self.assertRaises(ValueError):
                s.simulated_amount("income", -1, "no")
            with self.assertRaises(ValueError):
                s.simulated_amount("verified_income", 100, "no")
