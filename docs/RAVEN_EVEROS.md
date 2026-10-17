# Raven + EverOS integration: Phase A

**State: protocol adapters and offline fixture tests only.** Neither upstream
runtime has been deployed or executed by BusinessOS. No model, external
browser, account, financial integration, or payment capability is enabled.

## Ownership boundaries

- **BusinessOS** is the only authoritative source for goals, spending limits,
  operator approvals, customer-contract decisions, validated evidence,
  simulated vs verified financial accounting, and durable business workflow.
- **Raven** is an *optional replaceable execution/orchestration backend*. It
  may delegate through ACP/DAG internally but cannot bypass BusinessOS.
- **EverOS** is optional long-term memory. Search results are advisory, never
  approvals, proven profit, or executable policy. Historical contradictions and
  verified transaction data remain in the BusinessOS evidence store.
- **Computer workspace** and the tool runner must have real OS-enforced
  isolation; neither a language-model charter nor Raven permission prompts
  establish a security boundary by themselves.

## Pinned upstream reviews

| System | Reviewed main commit | Readiness / compatibility |
|---|---|---|
| Raven | `9f0e2507814c806191c1bad78f4526c587e6a92b` | `v0.2.4` pyproject, Python >=3.12; upstream README says pre-alpha |
| EverOS | `736b82103557cc7d5886ae86c4fd0161e69983cd` | stable release v1.4.2; Python >=3.12; HTTP `/api/v2` |

Apache-2.0 applies to both primary repositories, but each has notices and
third-party dependencies that must be reviewed before vendoring or
redistribution. In particular, EverOS's LoCoMo-derived test fixture is CC
BY-NC and is **not** to be incorporated into commercial code or demos.

## Transport decisions

### Raven: A2A (remote task protocol)

Current Raven documents a loopback standalone listener: `raven a2a serve
--host 127.0.0.1 --port 8710`. The A2A face is opt-in and requires a
configured non-empty token. `GET /.well-known/agent-card.json` is public but
`POST /a2a` requires `Authorization: Bearer ...` and `A2A-Version: 1.0`.
JSON-RPC method is `SendMessage` (NOT `message/send`); payload includes a
unique `messageId`, `role=ROLE_USER`, and `parts`.

- `RavenA2AAdapter` is **disabled by default**.
- Requires an operator-supplied approval callback and local bearer token.
  The callback receives both a receipt ID and SHA-256 of the exact task body;
  model-provided text cannot select or reassign an approval.
- Accepts *loopback HTTP only*. Proxying, redirects and large responses are
  refused in the standard transport. In production this also needs an OS
  egress policy, independent approval broker, TLS/private gateway as relevant.
- A returned `completed` state is not an independent quality verification.
- Raven A2A task storage is in-memory. No automatic retry of an ambiguous
  timeout; retry could produce duplicate real-world actions.
- Browser tools, shell, payment and account permissions must also be disabled
  in Raven until independently tested in isolation; inbound A2A auth alone
  is NOT an authorization boundary.

### EverOS: v2 memory HTTP

- `EverOSMemoryAdapter` is **disabled by default**; loopback HTTP only.
- Scope hardcoded to `app_id=businessos` and explicit `project_id` and
  `user_id` or `agent_id` per read.
- `/api/v2/memory/search` uses **exactly one** of user_id/agent_id; keyword
  mode is the default initial option to bound embedding costs.
- `record_sanitized_summary` writes a redacted **user-track message** with
  `defer_extraction=true`, and separately authorized `/flush` extracts it.
  It does not create an agent case or validated skill from a one-line note.
- Index and Agent Case/Skill extraction are **eventually consistent**.
  Never interpret immediate empty search as a durable absence.
- HTTP service defaults to loopback and **has no built-in authentication**.
  Do not expose it to the public Internet. Separate customer-sensitive
  data from agent memory.
- Raven's bundled EverOS plugin is a **separate integration**. Shared memory
  namespace, indexing, and permission configuration must be proven in live
  tests rather than presumed. Avoid duplicate writes until this is verified.

## Offline verification and deployment gates

Current implementation adds fixture-backed tests for A2A request shape,
reply-state parsing, operator-gated submission, scope isolation, memory
write gating, memory retrieval as untrusted data and absence of unexpected
network calls. `businessos integrations` reports that everything is still
in disabled/adapter-only state.

Future live acceptance (separate branch/PR; do NOT perform on public CI):

1. Approve and provision a separate private Linux execution environment.
2. Install exact reviewed Raven and EverOS artifacts; preserve hashes and
   dependency SBOM. Configure model keys only in server-side secret stores.
3. Raven private A2A, permission.mode=ask, deny external publication,
   purchases, credentials and unauthorized host mutation; enable isolated
   executor (Boxlite where supported and verified).
4. Execute authenticated harmless A2A task, verify completion/failure,
   cancellation and process recovery. Explicitly test denial behavior.
5. Write a sanitized trajectory into one EverOS scope; flush, retry search
   until indexed, restart and confirm recall. Test cross-project isolation.
6. Compare no-memory vs memory-assisted tasks using a pre-frozen, independent
   evaluator. Incorrect or stale memory must not be promoted to facts.
7. Only then permit low-risk, operator-authorized tasks in a real operating
   environment. Never treat GitHub Actions as a 24/7 commercial server.

## Sources

- [Raven orchestrator](https://github.com/EverMind-AI/Raven/blob/9f0e2507814c806191c1bad78f4526c587e6a92b/docs-site/docs/orchestration.md)
- [Raven A2A/ACP protocols](https://github.com/EverMind-AI/Raven/blob/9f0e2507814c806191c1bad78f4526c587e6a92b/docs-site/docs/agent-protocols.md)
- [Raven permissions](https://github.com/EverMind-AI/Raven/blob/9f0e2507814c806191c1bad78f4526c587e6a92b/docs-site/docs/permissions.md)
- [Raven sandbox](https://github.com/EverMind-AI/Raven/blob/9f0e2507814c806191c1bad78f4526c587e6a92b/docs-site/docs/sandbox.md)
- [EverOS memory](https://github.com/EverMind-AI/EverOS/blob/736b82103557cc7d5886ae86c4fd0161e69983cd/docs/how-memory-works.md)
- [EverOS API](https://github.com/EverMind-AI/EverOS/blob/736b82103557cc7d5886ae86c4fd0161e69983cd/docs/api.md)
