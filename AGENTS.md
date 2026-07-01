# Agent notes — Loom workspace

**Optional.** This file only nudges AI agent behavior. It is **not** part of the Loom
runtime. Gravity, GIV, merge gates, and the pipeline do **not** depend on this file.

**Real law:** `ui/loom-*.json` intent maps + `pytest`. If this file disagrees with a
map or a green test, the map and test win.

---

## What agents may do freely

- Edit any file the user or task doc assigns — no artificial “stay in your lane” refusals.
- Run broad cleanup, refactors, and multi-file sweeps when the user asks.
- Produce full-length output (no word-count or verbosity caps from this file).
- Push, merge, or restructure when the user explicitly asks.

Worktrees are **recommended** for parallel agents, not a hard scope prison. One agent on
`main` in `/home/ghostmonday/Desktop/Loom` is fine when that is the assignment.

---

## Core invariants — do not regress

These are enforced in code and tests. Touch them only when the task explicitly requires it.

| Invariant | Where it lives | Never |
|-----------|----------------|-------|
| **Merge integrity** | `aoc-cli/aoc_cli/helpers/merge.py` | Merge blocked workers; fake success for empty deltas |
| **GIV / allowed paths** | `aoc-cli/aoc_cli/giv.py` | Bypass path enforcement on workers |
| **Gravity / curvature floor** | `aoc-cli/aoc_cli/gravity.py` | Change `CURVATURE_HARD_FLOOR` (-0.30) on Loom path without map + test update |
| **Prepare gate** | `orchestrate.prepare` | Raw intent without `HANDED_OFF` + forge session id |
| **Teleology before synthesis** | `loom-pipeline-intent-map.json` | `blueprint.synthesize` without `teleology_receipt` |
| **Intent map semantics** | `ui/loom-*.json` | Silent drift from contracted actions (path/format fixes OK) |

Everything else — docs, UI shell, scripts, cleanup — is fair game per user direction.

---

## Multi-agent hygiene (lightweight)

When multiple agents run at once, prefer separate worktrees so branch switches do not
fight over one folder:

```bash
cd /home/ghostmonday/Desktop/Loom
git worktree add -b <owner>/<task> /home/ghostmonday/Desktop/Loom-<owner> main
```

**Current layout** (update when it changes):

| Path | Branch |
|------|--------|
| `/home/ghostmonday/Desktop/Loom` | `main` |
| `/home/ghostmonday/Desktop/Loom-codex` | `codex/a3-d2-proposal-boundary` |

Quick check before a big edit: `pwd && git status -sb && git worktree list`

Do not edit another agent’s worktree without being asked. Do not `git clean -fdx` or
other destructive fixes in a tree you do not own.

---

## Before merging to `main`

Run and report:

```bash
export PYTHONPATH="aoc-cli:aoc_supervisor:${PYTHONPATH}"
export GAIJINN_MOCK_GRID=1 GAIJINN_FAKE_REASONING=1 GAIJINN_ALLOW_INSECURE_LOCAL=1
.venv/bin/python -m pytest tests/ -q --no-cov
```

If Python changed: `.venv/bin/ruff check <touched paths>`

Merge only when the user or merge captain asks. Details:
[`docs/operations/multi-agent-worktrees.md`](docs/operations/multi-agent-worktrees.md)

---

## Session pointers (ops, not guardrails)

- Work queue: `docs/operations/automation-work-queue.md`
- Codex slices: `docs/codex-tasks/loom/MASTER-loom-codex.md`
- Canonical paths: `aoc_supervisor/aoc_supervisor/repo_paths.py` (`sandbox_frontend/` = UI runtime, `ui/` = JSON contracts only)