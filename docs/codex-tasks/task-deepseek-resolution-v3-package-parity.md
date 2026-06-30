# DeepSeek Task — Resolution v3 Package Parity & Clean Verification

## Objective

Verify the modular `aoc_cli.resolution_v3` implementation and the root compatibility shim `loom_resolution_engine_v3.py` are behaviorally identical, package correctly, and remain isolated from unrelated dirty worktree changes.

## Hard Constraints

- Run the full test suite.
- Inspect the packaged v3 implementation and compatibility shim before editing.
- Add parity tests across import paths.
- Verify identical statuses, traces, nodes, edges, and logs.
- Build and install the package in a clean environment.
- Keep unrelated dirty changes separate.
- Do not change the resolution formula.
- Do not change `Psi(G) = <growth_debt, unresolved_debt, cyclic_debt, clash_debt>`.
- Do not change `cyclic_debt = sum(|SCC|^2 for every acyclicity-violating SCC)`.
- Do not weaken strict-descent assertions.

## Current Relevant Files

- `aoc-cli/aoc_cli/resolution_v3/__init__.py`
- `aoc-cli/aoc_cli/resolution_v3/engine.py`
- `aoc-cli/aoc_cli/resolution_v3/graph.py`
- `aoc-cli/aoc_cli/resolution_v3/model.py`
- `aoc-cli/aoc_cli/resolution_v3/potential.py`
- `aoc-cli/aoc_cli/resolution_v3/reporting.py`
- `aoc-cli/aoc_cli/resolution_v3/rules.py`
- `aoc-cli/aoc_cli/resolution_v3/scc.py`
- `aoc-cli/aoc_cli/resolution_v3/validation.py`
- `aoc-cli/aoc_cli/resolution_v3/watch.py`
- `aoc-cli/aoc_cli/resolution_v3/worklist.py`
- `loom_resolution_engine_v3.py`
- `tests/test_resolution_v3_adversarial.py`
- `tests/test_resolution_v3_units.py`
- `pyproject.toml`

## Plan

1. Capture current worktree state.

   ```bash
   git status --short
   git diff --stat
   ```

   Record which files are part of resolution v3/package parity and which are unrelated dirty changes. Do not revert unrelated files.

2. Inspect package registration.

   Check that `pyproject.toml` includes:

   - `aoc_cli.resolution_v3` in `tool.setuptools.packages`
   - `loom_resolution_engine_v3` in `tool.setuptools.py-modules`

3. Inspect shim exports.

   Confirm `loom_resolution_engine_v3.py` re-exports the same public API as `aoc_cli.resolution_v3`, including:

   - `ACYCLIC_LAYERS`
   - `NORMAL`
   - `URGENT`
   - `ConstraintGraph`
   - `Edge`
   - `Engine`
   - `EngineStatus`
   - `Modality`
   - `Node`
   - `Provenance`
   - `Status`
   - `Worklist`
   - `resolve`
   - `tarjan_scc`

4. Add parity tests.

   Add a focused test file, suggested path:

   ```text
   tests/test_resolution_v3_import_parity.py
   ```

   Required assertions:

   - Import `aoc_cli.resolution_v3` as the package path.
   - Import `loom_resolution_engine_v3` as the compatibility path.
   - Assert public symbol names exist on both paths.
   - Build equivalent graphs using each import path, run `resolve`, and compare:
     - `status`
     - `steps`
     - `psi_trace`
     - `valid`
     - `stable`
     - `diagnostics`
     - `final_nodes`
     - `final_edges`
     - `log`
   - Include at least these graph cases:
     - original A1/A2/B1/B2 regression
     - weld manufactures a clash
     - missing source is `STUCK`
     - singleton prohibited self-loop
     - composite identifier collision

5. Run targeted tests first.

   ```bash
   .venv/bin/python -m pytest \
     tests/test_resolution_v3_adversarial.py \
     tests/test_resolution_v3_units.py \
     tests/test_resolution_v3_import_parity.py \
     --no-cov
   ```

6. Run full test suite.

   ```bash
   .venv/bin/python -m pytest
   ```

   If the full suite fails due to unrelated dirty work, report the failure with file/test names and avoid broad changes outside this task.

7. Build package artifacts.

   Use an isolated output path so tracked `dist/provisional-filing` artifacts are not touched.

   ```bash
   .venv/bin/python -m pip install --upgrade build
   rm -rf /tmp/loom-build-artifacts
   mkdir -p /tmp/loom-build-artifacts
   .venv/bin/python -m build --outdir /tmp/loom-build-artifacts
   ```

   If installing `build` changes lockfiles or dependency state, report it. Do not commit generated `build/` or cache directories.

8. Install in a clean environment.

   Suggested wheel flow:

   ```bash
   tmpenv="$(mktemp -d)"
   python3 -m venv "$tmpenv/venv"
   "$tmpenv/venv/bin/python" -m pip install --upgrade pip
   "$tmpenv/venv/bin/python" -m pip install /tmp/loom-build-artifacts/*.whl
   "$tmpenv/venv/bin/python" - <<'PY'
   import aoc_cli.resolution_v3 as pkg
   import loom_resolution_engine_v3 as shim

   assert pkg.resolve is shim.resolve
   assert pkg.ConstraintGraph is shim.ConstraintGraph
   print("resolution v3 package/shim import OK")
   PY
   rm -rf "$tmpenv"
   ```

   Suggested sdist flow:

   ```bash
   tmpenv="$(mktemp -d)"
   python3 -m venv "$tmpenv/venv"
   "$tmpenv/venv/bin/python" -m pip install --upgrade pip
   "$tmpenv/venv/bin/python" -m pip install /tmp/loom-build-artifacts/*.tar.gz
   "$tmpenv/venv/bin/python" - <<'PY'
   import aoc_cli.resolution_v3 as pkg
   import loom_resolution_engine_v3 as shim

   assert pkg.resolve is shim.resolve
   assert pkg.ConstraintGraph is shim.ConstraintGraph
   print("resolution v3 sdist package/shim import OK")
   PY
   rm -rf "$tmpenv"
   ```

9. Clean generated artifacts.

   Remove generated files unless the repo convention says to keep them:

   ```bash
   rm -rf build
   find . -path './.git' -prune -o -path './.venv' -prune -o -type d -name __pycache__ -prune -exec rm -rf {} +
   ```

   Keep `/tmp/loom-build-artifacts` only if explicitly needed for review; otherwise remove it too.

10. Final checks.

    ```bash
    git diff --check
    .venv/bin/ruff check aoc-cli/aoc_cli/resolution_v3 loom_resolution_engine_v3.py tests/test_resolution_v3_import_parity.py
    .venv/bin/ruff format --check aoc-cli/aoc_cli/resolution_v3 loom_resolution_engine_v3.py tests/test_resolution_v3_import_parity.py
    git status --short
    ```

## Acceptance Criteria

- Full test suite has been run and result reported.
- Targeted resolution v3 tests pass.
- New import parity tests pass.
- Built wheel installs in a clean environment.
- Both import paths expose the expected API.
- Equivalent graphs produce identical result payloads across import paths.
- No resolution formula changes.
- No unrelated dirty files reverted or mixed into the parity change.
- Temporary guidance comments from this file are removed if this plan file itself is edited into a final task artifact.

## Report Format

When finished, report:

- Tests run and pass/fail counts.
- Build/install commands run.
- Any full-suite failures, with whether they appear related or unrelated.
- Files changed.
- Confirmation that `Psi` formula and cyclic debt formula were not changed.
- Confirmation that unrelated dirty work remained untouched.
