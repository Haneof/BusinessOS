"""Offline demonstration orchestration, deliberately no autonomous network I/O."""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path

from .contracts import Candidate, DeterministicVerifier, OpportunityResearcher
from .policy import Action, Decision, Policy, Request
from .store import Store


class SampleResearcher:
    """Synthetic examples: no claims about prices, demand or actual customers."""

    def candidates(self) -> list[Candidate]:
        return [
            Candidate("sample-sheet", "Spreadsheet cleanup", "Messy inventory sheet", "Clean XLSX and change log", 2500, 400),
            Candidate("sample-caption", "Content captions", "Inconsistent product descriptions", "Three reviewable captions", 1500, 350),
            Candidate("sample-template", "Digital checklist", "Repeated onboarding steps", "Reusable checklist template", 1900, 200),
        ]


class DemoEngine:
    def __init__(self, store: Store, policy: Policy, output_dir: str | Path) -> None:
        self.store = store
        self.policy = policy
        self.output_dir = Path(output_dir)
        self.verifier = DeterministicVerifier()

    def _check(self, action: Action, description: str) -> Decision:
        outcome = self.policy.evaluate(Request(action, description))
        self.store.event(
            "policy_decision",
            {"action": action.value, "decision": outcome.decision.value, "reason": outcome.reason},
        )
        return outcome.decision

    def run(self, researcher: OpportunityResearcher | None = None) -> dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self._check(Action.RESEARCH_PUBLIC, "Use local synthetic candidates") != Decision.ALLOW:
            raise PermissionError("Research blocked by policy")
        researcher = researcher or SampleResearcher()
        candidates = researcher.candidates()
        outcomes = []
        for item in candidates:
            if item.source_class != "SYNTHETIC":
                raise ValueError("Starter refuses purported live research sources")
            if not re.fullmatch(r"[a-z0-9-]{3,64}", item.id):
                raise ValueError("Unsafe or invalid candidate ID")
            if item.estimated_price_cents < 0 or item.estimated_cost_cents < 0:
                raise ValueError("Negative monetary estimate")
            if self._check(Action.CREATE_LOCAL_ARTIFACT, item.id) != Decision.ALLOW:
                raise PermissionError("Artifact creation blocked by policy")
            body = (
                "# DEMONSTRATION ONLY - NOT A REAL SERVICE OFFER\n\n"
                f"Candidate ID: {item.id}\n\n"
                f"Customer problem: {item.customer_problem}\n\n"
                f"Deliverable: {item.sample_deliverable}\n\n"
                "This is a placeholder illustrating an agent deliverable schema.\n"
                "No customer was contacted; no commercial research was performed.\n"
            )
            target = self.output_dir / f"{item.id}.md"
            target.write_text(body, encoding="utf-8")
            passed, message = self.verifier.verify(body, item)
            self.store.event(
                "mechanical_check",
                {"candidate": item.id, "passed": passed, "message": message},
            )
            outcomes.append({
                **asdict(item),
                "format_check_passed": passed,
                "market_validated": False,
                "delivery_quality_validated": False,
                "real_revenue_cents": None,
                "sample_file": str(target),
            })

        requested = self.policy.evaluate(Request(Action.PUBLISH_EXTERNAL, "Publish an offer"))
        self.store.event("external_publish_gate", {
            "decision": requested.decision.value,
            "performed": False,
        })
        report = {
            "program": "BusinessOS",
            "version": "0.1.0",
            "mode": "DRY_RUN_ONLY",
            "facts": "All opportunities and prices are synthetic; no external integrations are enabled.",
            "candidates": outcomes,
            "publishing_permission": requested.decision.value,
            "publishing_performed": False,
            "real_sales": "NOT_CONNECTED",
            "next_gate": "Connect verified research and independent tests before real marketing.",
        }
        report_path = self.output_dir / "report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        self.store.event("demo_completed", {"candidates": len(outcomes), "report": str(report_path)})
        return report
