# Loom

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](#)
[![Tests](https://img.shields.io/badge/tests-795%20passing-green)](#)
[![Ruff](https://img.shields.io/badge/lint-ruff-clean-brightgreen)](#)

**Geometric orchestration engine for parallel AI coding agents.**

Loom lets you throw multiple AI coding agents at a codebase simultaneously — without them stepping on each other.

It works by measuring the *actual geometry* of your code, not just the import graph. Two files that never import each other can still be tightly coupled through shared state or data flow. Loom detects that hidden coupling mathematically, ensures those files are never assigned to different agents, and enforces the boundaries at runtime.

> Loom is an AI software-engineering orchestration system. It is not affiliated with Loom.com or any video-recording platform.

---

## Table of Contents

- [Why Loom Exists](#why-loom-exists)
- [The Problem: Hidden Coupling](#the-problem-hidden-coupling)
- [The Solution: Geometric Analysis](#the-solution-geometric-analysis)
- [Dark Bridges & Atomic Welds](#dark-bridges--atomic-welds)
- [Multi-Agent Council](#multi-agent-council)
- [Architecture](#architecture)
- [Commands](#commands)
- [Real Results](#real-results)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Runtime Pipeline](#runtime-pipeline)
- [Source Dump Workflow](#source-dump-workflow)
- [Repository Structure](#repository-structure)
- [Tests](#tests)
- [Runtime State](#runtime-state)
- [Status](#status)
- [License](#license)

---

## Why Loom Exists

Modern AI-assisted software engineering has moved beyond single-file autocomplete toward multi-agent systems executing parallel development plans. Parallel execution introduces three fundamental problems:

1. **Shared Context Degradation** — As worker count increases, implicit context needed to prevent overlap degrades. Agents make disjoint assumptions about shared state and APIs.
2. **Implicit vs. Explicit Intent** — ASTs and import DAGs do not capture high-level architectural intent. They show *how* code is wired, not *why* it was designed that way or what constraints must govern changes.
3. **Post-Hoc Verification vs. Runtime Constraints** — Most safety tools validate *after* generation. When an agent breaks an invariant or writes to unauthorized files, the compute is wasted and code review becomes the bottleneck.

Loom addresses these by making intent, authority, and validation explicit, machine-checkable contracts.

---

## The Problem: Hidden Coupling

If you give two AI agents different files to edit, you assume they're working independently. That assumption is wrong whenever those files are **functionally coupled** — they mutate the same state, share a data pipeline, or depend on the same operational cadence.

Standard dependency analysis (import graphs, DAGs) misses this entirely. It only sees explicit references. The hidden coupling looks like independence — until the agents' outputs collide at merge time.

---

## The Solution: Geometric Analysis

Loom uses **Ollivier-Ricci curvature**, a concept from differential geometry adapted to graphs. It measures how information flows between neighborhoods in the codebase graph.

The metric: **κ (kappa)**, computed via Wasserstein optimal transport distance.

### How Loom Reads Code

```
Source code
    ↓
AST parsing (structure)
    ↓
Type-flow / taint tracking (data movement)
    ↓
Reachability (Dijkstra paths)
    ↓
FRG (Function-Realization Graph)
    ↓
Curvature analysis (κ)
```

### What Curvature Means

| Curvature | Meaning | What the system does |
|-----------|---------|----------------------|
| `κ > 0` | Dense cluster — redundant paths | Heavy parallelization |
| `κ ≈ 0` | Stable pipeline — predictable | Standard splitting |
| `κ < 0` | Narrow bottleneck — hidden constraint | Increased collision risk |
| `κ < -0.30` | **Dark Bridge** — critical weld | Atomic unit or governed handoff |

---

## Dark Bridges & Atomic Welds

When curvature analysis detects dark bridges (edges with `κ < -0.30`), the system **welds** them via a union-find algorithm. Every file connected through dark bridges is fused into a single atomic work unit:

- **Before welding**: Two files connected by a dark bridge could be assigned to different agents. Both make conflicting assumptions. Merge produces broken code.
- **After welding**: Those files are fused into one work unit. One agent handles both. No conflict possible.

**The Surgery Rule**: If curvature says two files can't be parallelized, they aren't — no matter how cleanly separated their imports look. The geometry is the authority.

### Handoff Gateway Mode

Set `GAIJINN_HANDOFF_GATEWAYS=1` to replace atomic welds with structured handoff tickets. Dark bridge files stay in separate workers, but when an agent needs to modify a sibling-controlled file, it raises a structured handoff ticket through the [Multi-Agent Council](#multi-agent-council) bus. The merge gate validates every ticket before accepting output.

The environment flag uses the legacy `GAIJINN_*` prefix while Loom migration compatibility remains active.

---

## Multi-Agent Council

When agents on separate files share a dependency, the **Multi-Agent Council** (`council.py`) operates as a structured transaction bus:

1. A shared context block is injected into each worker's prompt
2. An agent writes a `HANDOFF_TRANSACTION_REQUEST` ticket into the council file
3. The sibling reads, accepts, or rejects — writing a `HANDOFF_TRANSACTION_RECEIPT`
4. The merge gate validates that every open ticket has a matching receipt

On the gateway victory lap, worker-001 raised ticket `TX-HT-84348F`, worker-002 produced the matching receipt, and convergence was **1.0** with **zero atomic weld units** and **92 handoff gateway edges**.

---

## Architecture

```
CLI layer:
  scan          Build dependency graph
  analyze       Compute curvature, detect dark bridges
  plan          Geometry-conditioned work partitioning
  run-grid      Create isolated worktrees
  grid-spawn    Launch AI agents with GIV contracts
  collect       Gather worker output
  validate      GIV compliance + handoff + invariants
  merge-grid    Validate and merge compliant output

API layer:
  orchestrate        Session lifecycle management
  preflight          Upstream CI gate
  intent-forge       Intent → blueprint synthesis
  deliverable        Output packaging and export

UI layer:
  Terminal            Intent → blueprint → sprint → merge → deliverable
  Council bus         Cross-worker handoff coordination
  Intent maps         FRG, curvature, and boundary visualization
```

### Blueprint Model

| Layer | Purpose | Artifact |
|-------|---------|----------|
| **Layer 0 — Domain Rules** | Functional domains, invariants, system constraints | `blueprint.json` |
| **Layer 1 — Reactive Structure** | Endpoints, commands, mutations, guards, state transitions | `graph.json` |
| **Layer 2 — Reflective Structure** | Lifecycles, dependency contracts, capability ceilings | `inferred.json` |

- **Greenfield:** Layer 0 → Layer 2 → Layer 1
- **Brownfield:** source scan → Layer 1 → Layer 2

### GIV Enforcement

Each work unit receives a **GIV (Agent Intent Vector)** — an enforced runtime RBAC contract defining:
- **Allowed paths** — exact files this agent may edit
- **Denied paths** — files this agent must never touch
- **Allowed/denied commands** — shell permissions
- **Capabilities** — what this agent is good at
- **Invariants** — conditions that must remain true after the agent finishes

The GIV is not advisory. Worker output is checked against it before merge.

### Merge Integrity

```
collect → validate-worker → merge-grid → structural scoring
```

Every merge gets a composite grade:

| Signal | Meaning |
|--------|---------|
| `validation_pass_rate` | Fraction of workers passing all gates |
| `convergence` | Composite structural score (honest — no ghost merges) |
| `transaction_bus_synchronized` | All handoff tickets resolved |
| `handoff_isolation` | Zero sibling path trespass |

---

## Commands

| Command | Purpose |
|---------|---------|
| `loom init` | Initialize project state and seed the build manifest |
| `loom audit` | Evaluate structural readiness without modifying source files |
| `loom scan` | Produce the repository graph |
| `loom analyze` | Run integrity preflight and write structural metrics |
| `loom plan` | Generate the blueprint and worker assignments |
| `loom run-grid` | Create isolated worker directories |
| `loom grid-spawn` | Launch coding workers with GIV injection |
| `loom collect` | Gather worker state and deltas |
| `loom validate-worker` | Apply scope, handoff, invariant, and test gates |
| `loom merge-grid` | Merge validated output into `loom/integration` |
| `loom status` | Summarize orchestration state |
| `loom doctor` | Check installation and project artifacts |
| `loom serve` | Run the hosted Loom service (FastAPI) |
| `loom council` | Use the shared agent council thread |
| `loom hermes` | Launch the interactive council-backed Hermes interface |

---

## Real Results

Loom has been dogfooded end-to-end with **live Grok Build agents** on the Loom monorepo itself.

### Phase 2 — Monorepo Dogfood (171 nodes, June 16 2026)

| Parameter | Value |
|-----------|-------|
| Target | Loom monorepo (171 code nodes) |
| Graph | 171 nodes · 92 shadow bridges · 54 work units |
| Agents | 4 concurrent copy-mode Grok workers |
| Handoff ticket | `TX-HT-6D0B24` (resolved) |
| Validation pass rate | **1.0** (4/4 workers) |
| Sibling trespass | **0** |
| Transaction bus | **synchronized** |
| Convergence | **0.8889** (honest — see below) |
| Merge conflicts | **0** |

**Gateway audit:** Legacy mode serializes **44 files** in **2 atomic welds**. Gateway mode: **0** welds, **44 files unlocked**, **47** max parallel workers.

### Honest Accounting

Loom's convergence score of **0.8889** is a badge of mathematical purity — three copy-mode workers had no fresh filesystem deltas at final merge (their work was already integrated). Loom flagged them as `PREFLIGHT_BLOCKED` rather than inflating metrics with ghost merges. Every participating worker achieved **1.0 validation compliance**, ensuring zero trespass.

---

## Installation

```bash
git clone https://github.com/Ghostmonday/Loom.git
cd Loom

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[api,dev]"

loom version
```

Core CLI only:

```bash
python -m pip install -e .
```

### Requirements

- Python 3.10+
- Git
- Linux, macOS, or WSL2
- Optional: FastAPI dependencies for the hosted service (`pip install -e ".[api]"`)

---

## Quick Start

```bash
# Audit an existing codebase
loom audit .

# Initialize a new project from intent
loom init "Build a production-ready REST API with Postgres"

# Scan and analyze the repository graph
loom scan .
loom analyze

# Plan and execute parallel work
loom plan --workers 4
loom run-grid --workers 4
loom grid-spawn --workers 4 --executor auto

# Collect, validate, and merge
loom collect
loom validate-worker
loom merge-grid --dry-run
loom merge-grid

# Check the result
loom status --strict
```

Use `loom --help` or any subcommand's `--help` for the authoritative interface.

## Runtime Pipeline

Loom now has a minimal deterministic end-to-end runtime path wired through the hardened `resolution_v3` engine:

```bash
loom run-pipeline examples/runtime-pipeline-minimal.json
```

That path covers:

```text
input -> constraint graph -> resolution_v3 -> work unit extraction -> execution -> ordered result aggregation
```

It is intentionally narrow and boring in the good way: one input, one deterministic output shape, no scheduler cleverness yet.

## Source Dump Workflow

For handing context to another model or starting a fresh session, generate the curated knowledge pack:

```bash
bash scripts/dev/source-dump.sh
```

That writes `~/Desktop/LOOMFILES2.md` plus `~/Desktop/LOOMFILES2.md.gz`.

Use full archival mode only when you truly need byte-heavy completeness:

```bash
bash scripts/dev/source-dump.sh --full /home/ghostmonday/Desktop/Loom-source-dump.txt
```

Curated mode deduplicates content-identical text files, skips empty scratch JSON, records recent commits and git status, and keeps the dump focused on files a new model can absorb quickly.

### Terminal UI (Greenfield / Demo)

```bash
bash scripts/dev/phase0-demo.sh
# Open http://127.0.0.1:8080
```

The terminal presents a full product loop:

```
Intent → Blueprint → Swarm → Sprint → Merge → Deliverable
```

Scope presets:

| Preset | What runs |
|--------|-----------|
| Backend only | 1 sprint: generate backend code |
| Frontend only | 1 sprint: generate frontend code |
| Backend + Frontend | 2 sprints: backend → context-loaded frontend |
| Full Stack | 3 sprints: backend → frontend → testing |
| Backend + Testing | 2 sprints: backend → test suite |

---

## Repository Structure

```
.
├── aoc-cli/aoc_cli/                  # CLI, graph analysis, planning, merge commands
├── aoc_supervisor/aoc_supervisor/    # API, Intent Forge, synthesis, governance
├── docs/                             # Architecture, guides, case studies, specs
│   ├── architecture/                 # Architecture decision records and blueprints
│   ├── guides/                       # How Loom thinks, why Loom exists
│   ├── reference/                    # Reference documentation
│   ├── specs/                        # Technical specifications
│   └── campaign/                     # Case studies, legal, patent materials
├── examples/                         # Example targets and demonstrations
│   └── tiny-python-service/          # Reference target for gateway testing
├── tests/                            # 795+ tests: unit, integration, contract, E2E
│   ├── conftest.py                   # Pytest fixtures (mock grid, fake reasoning)
│   └── test_*.py                     # Per-module test suites
├── scripts/                          # CI, development, and demo scripts
│   ├── ci/                           # CI pipeline scripts
│   ├── dev/                          # Development helpers and demos
│   └── codex/                        # Codex parallel task launchers
├── ui/                               # Intent maps, FRG visualizations, terminal assets
├── sandbox_frontend/                 # Standalone frontend sandbox and observatory pages
├── vaults/                           # Legacy memory FS and vault storage
├── pyproject.toml                    # Project build, linting, and test configuration
└── README.md
```

Key implementation files:

- `aoc-cli/aoc_cli/cli.py` — `loom` CLI entrypoint (Typer)
- `aoc-cli/aoc_cli/gravity.py` — Ollivier-Ricci curvature computation engine
- `aoc-cli/aoc_cli/giv.py` — Agent Intent Vector schema and enforcement
- `aoc_supervisor/aoc_supervisor/loom_pipeline.py` — Handoff and teleology sequencing
- `aoc_supervisor/aoc_supervisor/intent_forge_service.py` — Intent → blueprint synthesis
- `aoc_supervisor/aoc_supervisor/council.py` — Multi-agent handoff transaction bus
- `aoc_supervisor/aoc_supervisor/loom_blueprint_synthesizer.py` — Curvature-conditioned synthesis
- `aoc_supervisor/aoc_supervisor/loom_map_generator.py` — Deterministic contract generation
- `aoc_supervisor/aoc_supervisor/api.py` — Hosted service boundary

---

## Tests

```bash
# Run the full suite (795+ tests)
pytest

# With coverage
pytest --cov --cov-report=term-missing

# E2E golden-path validation
bash scripts/ci/acceptance.sh

# Lint
ruff check .
ruff format --check .
```

---

## Runtime State

The product and CLI are named **Loom**. During migration, legacy `.gaijinn/` state is mirrored into `.loom/`, while some current command paths retain the older directory name for compatibility.

These compatibility paths do not represent separate products. **Loom is the sole current product identity.**

The retained historical case study is at [docs/campaign/GAIJINN-PARALLEL-EXECUTION-CASE-STUDY.md](./docs/campaign/GAIJINN-PARALLEL-EXECUTION-CASE-STUDY.md).

---

## Status

Loom is under active development and is currently classified as alpha software. The Gaijinn-to-Loom migration remains visible in compatibility paths, fallback environment variables, internal names, and historical documentation filenames.

---

## License

Copyright © 2026 Neural Draft LLC. All Rights Reserved.

Proprietary software. See [LICENSE](./LICENSE), [PROPRIETARY.md](./PROPRIETARY.md), and [SECURITY.md](./SECURITY.md) for details.

This repository contains patent-pending and trade-secret material. Unauthorized copying, distribution, or public disclosure is prohibited.
