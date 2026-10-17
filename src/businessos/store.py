"""Local SQLite event and simulation ledger; never calls payment systems."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp_utc TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    data_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS simulated_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp_utc TEXT NOT NULL,
                    direction TEXT NOT NULL CHECK(direction IN ('income','expense')),
                    amount_cents INTEGER NOT NULL CHECK(amount_cents >= 0),
                    description TEXT NOT NULL,
                    evidence_label TEXT NOT NULL DEFAULT 'SYNTHETIC_TEST_ONLY'
                );
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def event(self, event_type: str, data: dict[str, Any]) -> None:
        if not event_type:
            raise ValueError("event_type is required")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO events (timestamp_utc,event_type,data_json) VALUES (?,?,?)",
                (self._timestamp(), event_type, json.dumps(data, sort_keys=True, ensure_ascii=True)),
            )

    def simulated_amount(self, direction: str, amount_cents: int, description: str) -> None:
        if direction not in {"income", "expense"} or amount_cents < 0:
            raise ValueError("Invalid simulated ledger entry")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO simulated_ledger (timestamp_utc,direction,amount_cents,description) VALUES (?,?,?,?)",
                (self._timestamp(), direction, amount_cents, description),
            )

    def stats(self) -> dict[str, Any]:
        with self._connect() as conn:
            events = int(conn.execute("SELECT COUNT(*) FROM events").fetchone()[0])
            rows = conn.execute(
                "SELECT direction, COALESCE(SUM(amount_cents),0) FROM simulated_ledger GROUP BY direction"
            ).fetchall()
        simulated = dict(rows)
        return {
            "events": events,
            "execution_mode": "DRY_RUN_ONLY",
            "simulated_income_cents": int(simulated.get("income", 0)),
            "simulated_expense_cents": int(simulated.get("expense", 0)),
            "verified_income_cents": None,
            "verified_profit_cents": None,
            "financial_data_note": "No payment-provider or bank reconciliation adapter is installed.",
        }
