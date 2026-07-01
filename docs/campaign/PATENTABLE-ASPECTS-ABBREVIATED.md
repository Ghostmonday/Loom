# Loom Potential Patentable Subject Matter Map

Document purpose: abbreviated invention-capture map for patent counsel and future drafting. This is not a patentability opinion and does not conclude that any item is novel, non-obvious, enabled, or claim-ready. It identifies project mechanisms that appear worth formal prior-art and claim-scope review.

Legal framing note: U.S. utility patent subject matter can include a new/useful process, machine, manufacture, composition of matter, or improvement, but claims must avoid being merely abstract ideas and should be framed as practical technical applications with concrete implementation details. See USPTO patent essentials and subject-matter eligibility guidance.

## Highest-Priority Invention Families

| ID | Candidate Invention | Patentable Technical Core | Repo Evidence | Claim Direction |
|---|---|---|---|---|
| P1 | Geometry-conditioned multi-agent code partitioning | Repository graph construction plus Ollivier-Ricci curvature / transport-based coupling detection to decide whether files may be parallelized, welded, or routed through handoff gateways. | `aoc-cli/aoc_cli/gravity.py`, `aoc-cli/aoc_cli/blueprint.py`, `README.md`, `docs/campaign/PROVISIONAL-PATENT-TECHNICAL-SPECIFICATION.md` | Claim as a computer-implemented method that computes structural gravity and curvature over code interaction graphs and generates non-overlapping work units based on dark-bridge thresholds. |
| P2 | Dark-bridge gateway mode | Converting high-risk negative-curvature edges from atomic serialization constraints into governed handoff-only gateway edges, preserving parallelism while preventing unauthorized sibling edits. | `README.md`, `aoc-cli/aoc_cli/blueprint.py`, `aoc-cli/aoc_cli/helpers/handoff.py`, `aoc-cli/aoc_cli/helpers/merge.py` | Claim as improvement over naive union-find welding: maintain separate worker scopes while enforcing transaction-mediated cross-boundary mutation. |
| P3 | Agent Intent Vector enforcement | Deterministic per-worker runtime contract with allowed paths, denied paths, sibling-denied paths, command limits, capabilities, invariants, and structural tokens, enforced before merge. | `aoc-cli/aoc_cli/giv.py`, `aoc-cli/aoc_cli/commands/validate_worker.py`, `aoc-cli/aoc_cli/helpers/merge.py` | Claim as machine-readable operational permission vector generated from graph topology and enforced against actual worker deltas. |
| P4 | Council transaction bus for autonomous code agents | Structured cross-worker mutation requests/receipts emitted through worker logs, promoted into an append-only handoff queue/ledger, and verified before integration. | `aoc-cli/aoc_cli/helpers/handoff.py`, `aoc-cli/aoc_cli/helpers/council.py`, `.gaijinn/merge/handoff-queue.json` patterns, `docs/campaign/PROVISIONAL-PATENT-TECHNICAL-SPECIFICATION.md` | Claim as asynchronous transaction bus that converts forbidden direct edits into resolvable inter-agent mutation tickets with merge-blocking receipt verification. |
| P5 | Merge governance score and preflight gate | Multi-signal merge integrity scoring based on validation pass rate, trespass detection, handoff synchronization, merge conflicts, and honest no-delta handling. | `aoc-cli/aoc_cli/commands/collect.py`, `aoc-cli/aoc_cli/commands/validate_worker.py`, `aoc-cli/aoc_cli/commands/merge_grid.py`, `aoc_supervisor/aoc_supervisor/preflight.py` | Claim as pre-merge integration gate for autonomous agent outputs that blocks unresolved transaction or scope violations before CI/deploy. |
| P6 | Operational contract compilation | Transforming probabilistic user/agent intent into a Certified Operational Contract with topology, work units, invariants, and enforceable per-agent vectors. | `aoc-cli/aoc_cli/blueprint.py`, `aoc_supervisor/aoc_supervisor/blueprint_compiler.py`, `docs/campaign/PROVISIONAL-PATENT-TECHNICAL-SPECIFICATION.md` | Claim as compilation pipeline from discovered capabilities and intent graph into executable operational contracts. |

## Resolver / Constraint-Engine Invention Families

| ID | Candidate Invention | Patentable Technical Core | Repo Evidence | Claim Direction |
|---|---|---|---|---|
| R1 | Typed-locus constraint resolution worklist | Worklist over typed node/edge loci, avoiding namespace collisions and enabling deterministic rule scheduling over mutable constraint graphs. | `aoc-cli/aoc_cli/resolution_v3/model.py`, `worklist.py`, `engine.py`, `tests/test_resolution_v3_*` | Claim as typed-locus scheduling method for constraint graph resolution in AI orchestration planning. |
| R2 | Lexicographic potential descent resolver | Resolution engine enforces strict descent over `Psi(G)=<growth_debt, unresolved_debt, cyclic_debt, clash_debt>` and returns canonical/stuck/fault states deterministically. | `aoc-cli/aoc_cli/resolution_v3/potential.py`, `engine.py`, `reporting.py` | Claim as termination-guaranteed graph rewrite process with explicit progress metric and fault boundary. |
| R3 | A1 target-level domain intersection | Required missing targets are materialized from atomic intersection of all active incoming required-edge domains, distinguishing contradictory and undeclared schema outcomes. | `aoc-cli/aoc_cli/resolution_v3/rules.py`, `validation.py`, adversarial tests | Claim as schema-consistent latent-node materialization for AI planning graphs. |
| R4 | Modality-preserving weld semantics | SCC weld rule absorbs internal `REQ` edges while preserving or exposing internal `PARTIAL`, `FORBID`, and authority obligations instead of silently deleting them. | `aoc-cli/aoc_cli/resolution_v3/rules.py`, `validation.py`, adversarial tests | Claim as graph-contraction method that preserves non-required obligations through composite-node formation. |
| R5 | Acyclic-layer SCC semantics | Cyclic violations are detected only inside the directed subgraph induced by acyclic-layer nodes, avoiding false violations caused by cross-layer traversal. | `aoc-cli/aoc_cli/resolution_v3/potential.py`, `scc.py`, unit/adversarial tests | Claim as layered acyclicity enforcement for mixed-layer constraint graphs. |
| R6 | Canonical installed-artifact parity and output serialization | Package/shim parity plus canonical payload ordering across insertion orders for reproducible AI planning results. | `loom_resolution_engine_v3.py`, `reporting.py`, `tests/test_resolution_v3_import_parity.py` | Better as dependent claim / quality-control method than standalone broad patent family. |

## Intent Forge / Blueprint Synthesis Families

| ID | Candidate Invention | Patentable Technical Core | Repo Evidence | Claim Direction |
|---|---|---|---|---|
| F1 | Adaptive requirement interrogation to executable blueprint | Interactive session tracks answers, domain coverage, confidence, contradictions, stale claims, and compiles to rich artifact plus executable projection. | `aoc_supervisor/aoc_supervisor/intent_forge_service.py`, `adaptive_question_engine.py`, `question_policy.py`, `blueprint_compiler.py` | Claim as adaptive intake process that stops questioning based on domain coverage and compiles validated requirements into executable work units. |
| F2 | Contradiction-aware requirement graph revision | Answers can invalidate dependent claims, mark stale nodes/edges, and merge contradiction resolutions into blueprint state. | `intent_forge_service.py`, `conflict_resolver.py`, `intent_blueprint_state.py` | Claim as requirement graph maintenance method for AI-generated specifications with stale-dependency propagation. |
| F3 | Teleology artifact emitter | Forge session state is transformed into canonical `teleology.json` containing goal, constraints, success criteria, domains, capabilities, invariants, states, and evidence. | `aoc_supervisor/aoc_supervisor/teleology_artifact.py`, teleology schemas/docs | Claim as machine-readable "why/what" artifact used upstream of topology and blueprint synthesis. |
| F4 | Curvature-conditioned synthesis from intent projection | Executable projection work units are converted to a graph, analyzed for dark bridges, then fed into blueprint generation with teleology receipt annotation. | `aoc_supervisor/aoc_supervisor/loom_blueprint_synthesizer.py`, `gravity.py`, `blueprint.py` | Claim as fusion of natural-language/forge projection with geometric repository planning. |
| F5 | Continuation/delta session lineage | Existing repository sessions inherit graph/blueprint lineage, ask only for bounded deltas, and freeze versioned child blueprints. | `ui/loom-continuation-intent-map.json`, `docs/operations/*`, `.loom/codex-slices/*` | Claim as versioned continuation-intake method for brownfield AI coding sessions. |

## Mirror / Interface Governance Families

| ID | Candidate Invention | Patentable Technical Core | Repo Evidence | Claim Direction |
|---|---|---|---|---|
| M1 | Intent-map universal interface contract | UI, API, CLI, worker, and tests share action contracts so behavior is declared once and mirrored across surfaces. | `ui/*intent-map.json`, `.agents/skills/loom-intent-mapping-v2/SKILL.md`, `ui/README.md` | Claim as cross-interface operational map binding UI actions to backend effects, assertions, and smoke scenarios. |
| M2 | Headless intent mirror | Browserless mirror driver evaluates UI/API assertions against an isomorphic state model using the same intent map semantics. | `aoc_supervisor/aoc_supervisor/intent_mirror.py`, `ui_intent.py`, tests around mirror coverage | Claim as automated verification method for UI/API behavior using declarative intent-map assertions. |
| M3 | Process-stage UX map with algorithm binding | UI stage progression is bound to backend algorithms, artifacts, gates, and evidence rather than static wizard steps. | `ui/process-stage-ux-map.json`, `ui/command-engine-ui-intent-map.json` | Claim as practical interface-control method for governed AI orchestration workflows. |

## Runtime Streaming / Observability Families

| ID | Candidate Invention | Patentable Technical Core | Repo Evidence | Claim Direction |
|---|---|---|---|---|
| S1 | Aggregate SSE transaction manifold | Multiplex concurrent worker logs and promoted council events into a single replayable SSE stream keyed by `Last-Event-ID`. | `aoc_supervisor/aoc_supervisor/api.py`, `docs/INNOVATION-MAPPING.md` | Claim as bounded replay stream for multi-agent worker logs and transaction events. |
| S2 | Bounded event retention for agent orchestration | Ring-buffer retention supports reconnect/replay under high-velocity log bursts while bounding memory. | `api.py`, `docs/INNOVATION-MAPPING.md` | Likely dependent claim on S1. |
| S3 | Council-event promotion from raw streams | Structured transaction markers inside worker output are promoted into first-class orchestration events. | `api.py`, `helpers/council.py`, `helpers/handoff.py` | Claim as stream parser/promoter for autonomous worker transaction blocks. |
| S4 | Async subprocess transaction piping | Real worker subprocess stdout/stderr is piped into asynchronous broadcaster with event classification. | `aoc_supervisor/aoc_supervisor/api.py`, `grid_spawn` paths | Usually dependent/supporting claim rather than standalone family. |

## Knowledge / Context-Pack Families

| ID | Candidate Invention | Patentable Technical Core | Repo Evidence | Claim Direction |
|---|---|---|---|---|
| K1 | AI session knowledge-pack generator | Dual-mode source dump that emits either full text-only source or curated deduped/category-ordered AI context pack with guardrails and recent commit trail. | `scripts/dev/source-dump.sh`, `docs/operations/deepseek-source-dump-rules.md` | Weak-to-medium patent candidate; stronger as trade secret / workflow asset unless tied to measurable AI-session performance improvement. |
| K2 | Context hygiene rules for multi-model delegation | Procedural controls for what a secondary model may scan, edit, generate, and report. | `deepseek-source-dump-upgrade-report.md` on Desktop, operations docs | More likely protectable as trade secret/process know-how than patent core. |

## Potential Design / Trade Dress / Copyright Adjacent Items

These are not utility-patent candidates by themselves, but may support other IP strategy:

- Loom visual language for topology, dark bridges, ratification, and orchestration stages.
- UI screens in `sandbox_frontend/` and `frontend-formation-complete/`.
- Brand names and terminology: Loom, Dark Bridge, Surgery Rule, Agent Intent Vector, Multi-Agent Council, Certified Operational Contract, Teleology artifact.
- Documentation, maps, and schemas as copyright/trade-secret artifacts.

## Counsel Review Priority

1. File or update claims around P1-P6 first. These are the strongest technical systems.
2. Add dependent claims from R1-R6 as resolver correctness improvements to operational-contract compilation.
3. Add F1-F5 for intent-to-blueprint and continuation workflows.
4. Add M1-M3 as interface verification and cross-surface contract claims.
5. Use S1-S4 as runtime observability/support claims.
6. Treat K1-K2 as trade-secret-first unless a concrete technical performance claim is measured.

## Evidence Checklist To Prepare

- Before/after examples showing import-graph splitting failure versus curvature/weld/gateway success.
- Dogfood run logs proving zero sibling trespass, synchronized transaction bus, and unlocked parallelism.
- Diagrams of `scan -> analyze -> plan -> isolated workers -> collect -> validate -> merge`.
- Sample GIV JSON plus worker diff showing blocked trespass.
- Example handoff ticket and matching receipt.
- Resolver v3 adversarial test matrix and `Psi` traces.
- Intent Forge session transcript leading to executable projection and teleology artifact.
- Mirror test proving browserless assertion parity with UI intent maps.

## Drafting Warnings

- Do not claim "AI orchestration" in the abstract only. Tie claims to graph construction, curvature computation, contract generation, permission vectors, transaction tickets, and merge enforcement.
- Avoid relying on mathematical formulas alone. Frame formulas as part of a practical improvement to distributed software-agent execution.
- Keep implementation variants: copy-mode and git-worktree isolation; atomic weld and handoff gateway; greenfield and brownfield sessions; CLI/API/UI surfaces.
- Separate trade-secret terminology from claim terminology. Claims should use brand-neutral phrases.
- Preserve dated evidence and test results; they help establish conception, reduction to practice, and enablement.

## Source Anchors

- USPTO patent essentials: https://www.uspto.gov/patents/basics/essentials
- USPTO subject matter eligibility: https://www.uspto.gov/patents/laws/examination-policy/subject-matter-eligibility
- USPTO MPEP 2106 eligibility framework: https://www.uspto.gov/web/offices/pac/mpep/s2106.html
- USPTO AI subject-matter eligibility examples: https://www.uspto.gov/sites/default/files/documents/2024-AI-SMEUpdateExamples47-49.pdf

