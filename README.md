# BusinessOS (public engineering starter)

> **STATUS: V0.1 engineering skeleton / OFFLINE DRY RUN.** This repository is NOT a working autonomous business, NOT a verified market-research agent, and NOT connected to real customer accounts, payment processors, browsers or an LLM.

## Goal

Build a general-purpose, tool-using AI execution system that can explore lawful business opportunities, set up authorized tools, delegate scoped work, produce auditable artifacts, validate results independently, and learn from documented outcomes. The business vertical is selected based on evidence, not hardcoded in advance.

## What V0.1 actually does

- Defines an explicit default-deny action policy and approval boundary.
- Produces a 100% offline demonstration with three **synthetic** opportunities.
- Writes local example deliverables and separately checks their structure.
- Stores append-style events in SQLite, including clearly labeled *simulated* money.
- Makes no external network calls, creates no real accounts, spends no money and publishes no offers.
- Runs unit tests in a public GitHub Actions CI workflow.

## Run locally (Python 3.12+)

```bash
python -m pip install -e .
businessos demo
businessos status
businessos policy publish_external
businessos policy spend_money --cost-cents 100 --budget-cents 200
python -m unittest discover -s tests -v
```

All generated data lives under `.local/` by default and is ignored by Git.

## Why GitHub Actions is CI only

Standard GitHub-hosted runners are free and have no overall minutes limit for public repositories, but an individual job has a runtime limit; runners are ephemeral. GitHub's additional product terms restrict hosted Actions to development, testing, deployment and publication of the repository's software. We must **not** run continuous third-party commercial agent activity on Actions. A separate host will be necessary for later always-on agents.

## Planned architecture

```text
Owner control panel
      |
  Goal/Policy -> Planner/Manager -> scoped Agent/Tool Executor -> Independent Verifier
                          |                        |
                          +--> Workflow store <--+---> Event journal / Cost ledger
                                                        |
                                                   External evidence
```

Real adapters for model invocation, browser/computer use, protected credentials, payments, customer channels, and provenance must be added and tested before enabling real activity. **Prompt instructions are not security controls:** authorization and spending limits belong outside the model in a separately permissioned service.

## Non-goals for V0.1

- No promises of income or verified profitability.
- No production credentials, identities or real money.
- No unsupervised external publication, account registration, regulated professional advice or customer data processing.
- No attempt to replace qualified professional review of high-stakes outputs.

## Public repository cautions

Everything committed here is public. Never include `.env`, real customer records, API keys, credentials, prompt traces containing personal data, scraped proprietary datasets, or private business financial records. Use a separately permissioned encrypted service for secrets and private operational data when the system grows.

## Documents

- [Charter](docs/PROJECT_CHARTER.md)
- [System architecture](docs/ARCHITECTURE.md)
- [Roadmap and gates](docs/ROADMAP.md)
- [Security and threat model](docs/SECURITY.md)
- [GitHub setup](docs/GITHUB_SETUP.md)

No source license is assigned yet. Public readability is not the same as open-source reuse rights; the repository owner should explicitly select a license before accepting outside code contributions.
