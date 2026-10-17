# Engineering roadmap

## M0 - Public repository bootstrap

- [x] Source layout, packaging, docs and CI workflow authored
- [x] Offline event log and simulation ledger
- [x] Fail-closed policy tests
- [x] Independent mechanical sample checks
- [ ] Owner creates GitHub public repository
- [ ] Upload project and verify hosted CI passes

## M1 - Agent computer prototype

- [ ] Choose one framework (Agent Zero candidate) and isolate from owner machine
- [ ] Define ToolRuntime contract and installer allowlist
- [ ] Create limited-permission Linux worker; browser/terminal/file tools
- [ ] Restart and resume test, bounded CPU/memory/API cost
- [ ] No shared root/admin credentials

## M2 - Autonomous planning and independent experiments

- [ ] Source-linked public research (timestamps, URLs and origin checks)
- [ ] Bounded spawn/delegate/reap workflow; per-agent cost ledger
- [ ] Executable success criteria frozen before the agent runs
- [ ] Evaluate success/failure with separate verification worker
- [ ] Reject income claims unsupported by reconciled payout evidence

## M3 - Controlled first real-world pilot

- [ ] Select business channel based on research and lawful eligibility
- [ ] Human completes identity/financial-account setup
- [ ] Explicit per-action approval for external writes and payments
- [ ] Payout/fee/refund reconciliation and stop conditions
- [ ] Audit + incident response + rollbacks

## M4 - Continuous operation

- [ ] Durable queue, scheduler, idempotent external writes
- [ ] Daily reports, monitored error budget, kill switch
- [ ] Business outcome evaluation using observed net contribution

Each gate requires objective pass/fail evidence. A report from the same agent that did the work is not sufficient on its own.
