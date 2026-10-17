"""Fail-closed policy gate. NOT a replacement for OS-level sandboxing."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Action(str, Enum):
    RESEARCH_PUBLIC = "research_public"
    READ_LOCAL_TEST_DATA = "read_local_test_data"
    CREATE_LOCAL_ARTIFACT = "create_local_artifact"
    RUN_LOCAL_TEST = "run_local_test"
    DRAFT_PROPOSAL = "draft_proposal"
    SPAWN_SCOPED_AGENT = "spawn_scoped_agent"
    DELEGATE_EXTERNAL_AGENT = "delegate_external_agent"
    WRITE_EXTERNAL_MEMORY = "write_external_memory"
    INSTALL_SOFTWARE = "install_software"
    PUBLISH_EXTERNAL = "publish_external"
    CONTACT_CUSTOMER = "contact_customer"
    REGISTER_ACCOUNT = "register_account"
    SPEND_MONEY = "spend_money"
    ACCESS_CUSTOMER_DATA = "access_customer_data"
    MODIFY_POLICY = "modify_policy"
    HANDLE_CREDENTIALS = "handle_credentials"
    PROVIDE_REGULATED_ADVICE = "provide_regulated_advice"


class Decision(str, Enum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


@dataclass(frozen=True)
class Request:
    action: Action | str
    description: str
    estimated_cost_cents: int = 0


@dataclass(frozen=True)
class Result:
    decision: Decision
    reason: str


class Policy:
    # Budget is a cap on requests; a real financial cap requires an external broker.
    def __init__(self, experiment_budget_cents: int = 0) -> None:
        if experiment_budget_cents < 0:
            raise ValueError("Budget cannot be negative")
        self.experiment_budget_cents = experiment_budget_cents

    def evaluate(self, request: Request) -> Result:
        if not isinstance(request.estimated_cost_cents, int) or request.estimated_cost_cents < 0:
            return Result(Decision.DENY, "Invalid estimated cost")
        try:
            action = Action(request.action)
        except (ValueError, TypeError):
            return Result(Decision.DENY, "Unknown action (fail closed)")

        if action in {
            Action.MODIFY_POLICY,
            Action.HANDLE_CREDENTIALS,
            Action.PROVIDE_REGULATED_ADVICE,
        }:
            return Result(Decision.DENY, "Prohibited in starter mode")

        if request.estimated_cost_cents > self.experiment_budget_cents:
            return Result(Decision.DENY, "Exceeds configured experiment budget")

        if action in {
            Action.INSTALL_SOFTWARE,
            Action.PUBLISH_EXTERNAL,
            Action.CONTACT_CUSTOMER,
            Action.REGISTER_ACCOUNT,
            Action.SPEND_MONEY,
            Action.ACCESS_CUSTOMER_DATA,
            Action.DELEGATE_EXTERNAL_AGENT,
            Action.WRITE_EXTERNAL_MEMORY,
        }:
            return Result(Decision.REQUIRE_APPROVAL, "Requires out-of-band authorization")

        if request.estimated_cost_cents > 0:
            return Result(Decision.REQUIRE_APPROVAL, "Any nonzero estimated cost requires approval")

        if action in {
            Action.RESEARCH_PUBLIC,
            Action.READ_LOCAL_TEST_DATA,
            Action.CREATE_LOCAL_ARTIFACT,
            Action.RUN_LOCAL_TEST,
            Action.DRAFT_PROPOSAL,
            Action.SPAWN_SCOPED_AGENT,
        }:
            return Result(Decision.ALLOW, "Offline/local-only action")

        return Result(Decision.DENY, "No permission rule matched")
