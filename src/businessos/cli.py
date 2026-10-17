"""Minimal, dependency-free CLI for reproducible offline tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import DemoEngine
from .policy import Action, Policy, Request
from .store import Store


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="BusinessOS starter (offline tests only)")
    sub = p.add_subparsers(dest="cmd", required=True)
    demo = sub.add_parser("demo", help="Produce mock business experiments, without network calls")
    demo.add_argument("--db", default=".local/businessos.sqlite3")
    demo.add_argument("--output", default=".local/artifacts")
    status = sub.add_parser("status", help="Show saved experiment/ledger status")
    status.add_argument("--db", default=".local/businessos.sqlite3")
    policy = sub.add_parser("policy", help="Evaluate a proposed action (no execution)")
    policy.add_argument("action")
    policy.add_argument("--cost-cents", type=int, default=0)
    policy.add_argument("--budget-cents", type=int, default=0)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.cmd == "demo":
        result = DemoEngine(Store(args.db), Policy(), Path(args.output)).run()
        print(json.dumps({"mode": result["mode"], "samples": len(result["candidates"]),
                          "report": str(Path(args.output) / "report.json")}, indent=2))
        return 0
    if args.cmd == "status":
        print(json.dumps(Store(args.db).stats(), indent=2))
        return 0
    if args.cmd == "policy":
        result = Policy(args.budget_cents).evaluate(Request(args.action, "CLI policy inspection", args.cost_cents))
        print(json.dumps({"decision": result.decision.value, "reason": result.reason}, indent=2))
        return 0
    return 2
