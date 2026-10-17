# Architecture

## Logical subsystems

1. **Goal Manager:** translates goals into hypotheses and measurable milestones.
2. **Research Adapter:** obtains source-linked market signals and distinguishes facts from hypotheses.
3. **Agent Scheduler:** creates scoped roles with explicit budgets, time limits and tool grants.
4. **Tool Runtime:** isolated browser, terminal and file system; installs software in disposable sandboxes.
5. **Policy Broker:** a separate enforcement plane that gates side effects and all billable actions.
6. **Independent Verification:** uses fixed test datasets, deterministic validators and optional qualified review.
7. **Evidence Store:** records immutable external artifacts, task provenance and actual third-party identifiers.
8. **Financial Ledger:** reconciles payouts, fees, payments, refunds; isolates simulated and unverified amounts.
9. **Owner Control Surface:** approvals, health, progress, emergency stop, and audit review.

## MVP composition

The current repository only implements policy decisions, local artifacts, deterministic structural tests, an event store, simulation ledger and CLI. It **does not** implement an LLM/agent runtime, durable queue, remote desktop, billing broker or live market connector.

## Separation of duties

- The model cannot elevate OS privileges, read production API keys or edit the actual policy broker.
- Untrusted webpages, documents and tool outputs are data, not instructions.
- Any external action or monetary operation is submitted as a proposal to an authenticated broker.
- The verifier does not share untrusted working state with the agent being evaluated.
- A timed restart cannot automatically repeat an already submitted purchase or order.

## Future hosting

- Development: local machine or Codespaces, GitHub Actions for CI.
- Pilot: dedicated VPS with separate sandbox workers and independent credential broker.
- Scaling: disposable VMs (E2B/Daytona or KVM), message queue, Postgres and object storage.

Do not run user-credential-bearing, stateful commercial operations on the GitHub public runner.
