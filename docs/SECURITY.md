# Security and use boundaries

This repository is PUBLIC. Treat all commits, CI logs, issues, PR comments and build artifacts as readable by strangers.

## Default safety posture

- Offline dry run only in V0.1.
- No payment, refund, advert spend, account registration, mass messaging or external publication without independent broker authorization.
- Do not share credentials or browser sessions with model-accessible prompts.
- Do not store customer-identifying or regulated datasets in a public repo.
- Do not use a code-level boolean approval flag as proof of human consent.
- Keep OS-level sandbox permissions, network egress controls and resource limits independent of the model.
- Run new software and downloaded dependencies in temporary, non-privileged environments.
- Never mount host Docker socket or broad host volumes into an untrusted agent worker.
- Prompt injection in web content and dependencies is a critical risk; verify sources and treat external instructions as data.

## GitHub workflow

The CI workflow has minimal repository permissions, no secrets and a 10-minute timeout; it only installs project code and runs offline tests. It is NOT a business task runner.

## Before the real-money pilot

Require written authorization scope, financial cap brokered outside AI, identity and tax eligibility checks, platform-compliant client communication, independent result verification, and evidence of real cash reconciliation. Service providers can suspend automated accounts that violate terms.
