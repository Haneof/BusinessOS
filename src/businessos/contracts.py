"""Seams for future real model, browser, tools, and external verifiers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Candidate:
    id: str
    name: str
    customer_problem: str
    sample_deliverable: str
    estimated_price_cents: int
    estimated_cost_cents: int
    source_class: str = "SYNTHETIC"


class OpportunityResearcher(Protocol):
    def candidates(self) -> list[Candidate]: ...


class OutputVerifier(Protocol):
    def verify(self, content: str, candidate: Candidate) -> tuple[bool, str]: ...


class AgentRuntime(Protocol):
    def plan(self, goal: str) -> list[str]: ...
    def execute_local_task(self, task: str) -> str: ...


class DeterministicVerifier:
    """Only checks sample structure. This cannot establish commercial quality."""

    def verify(self, content: str, candidate: Candidate) -> tuple[bool, str]:
        requirements = ["DEMONSTRATION ONLY", candidate.id, "Customer problem:", "Deliverable:"]
        if all(item in content for item in requirements):
            return True, "Formatting check passed; commercial quality NOT verified"
        return False, "Missing required sample fields"
