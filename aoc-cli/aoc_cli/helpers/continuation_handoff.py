"""Continuation handoff artifact generator (LOOM-212 / deliverable.generate_handoff).

CODEX SLICE — READ BEFORE IMPLEMENTING
--------------------------------------
Product gap (confirmed 2026-07-01): Loom ends at *validated merged code* but does not
emit a first-class *continuation intelligence layer* for the next human or AI session.

DO NOT MODIFY (out of scope for this slice):
  - curvature / gravity / GIV enforcement (aoc_cli/gravity.py, giv.py)
  - merge integrity gates (helpers/merge.py collect/validate/merge-grid)
  - orchestration partition logic (orchestrate_session.py prepare/swarm)

DO IMPLEMENT (this slice only):
  1. Gather trusted inputs AFTER merge_pipeline.phase == completed
  2. Run LLM *interpretation* audit (structure already guaranteed by merge gates)
  3. Write two artifacts under .gaijinn/handoff/:
       - handoff.json  — machine-readable continuation contract
       - handoff.md    — human-readable system explanation + next steps

Intent map law: ui/loom-deliverable-intent-map.json → action deliverable.generate_handoff
Mirror/API: optional POST /api/v1/grid/handoff (see api.py CODEX block)
CLI entry: loom handoff (see commands/handoff.py)

Verify (add when implemented):
  pytest tests/test_continuation_handoff.py -q
  pytest tests/test_loom_deliverable_intent.py -q -k handoff
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import GAIJINN_DIR

# CODEX: stable artifact paths — include in merge completion-ledger cross-ref
HANDOFF_DIR = GAIJINN_DIR / "handoff"
HANDOFF_JSON_PATH = HANDOFF_DIR / "handoff.json"
HANDOFF_MD_PATH = HANDOFF_DIR / "handoff.md"

HANDOFF_SCHEMA_VERSION = 1


@dataclass
class HandoffInputs:
    """Trusted inputs for handoff generation. CODEX: populate from disk only — never invent."""

    project_root: Path
    session_id: str = ""
    blueprint: dict[str, Any] = field(default_factory=dict)
    claims_ledger: dict[str, Any] = field(default_factory=dict)
    merge_pipeline: dict[str, Any] = field(default_factory=dict)
    merge_report: dict[str, Any] = field(default_factory=dict)
    repo_state: dict[str, Any] = field(default_factory=dict)
    teleology_receipt: dict[str, Any] = field(default_factory=dict)


def gather_handoff_inputs(project_root: Path, *, session_id: str = "") -> HandoffInputs:
    """Collect artifacts the LLM audit may *interpret* (not re-validate).

    CODEX wiring checklist:
      - .gaijinn/blueprint.json → blueprint (projection_mode, work_units)
      - .gaijinn/merge/report.json → merge_report (via load_merge_report)
      - merge_pipeline_status(project_root) → merge_pipeline (phase must be completed)
      - intent-forge session claims_ledger if intent_forge_session_id on blueprint
        (see aoc_supervisor.claims_ledger.build_claim_ledger + forge session state)
      - git rev-parse HEAD, status --porcelain → repo_state
      - optional: mirror teleology_receipt from blueprint.teleology_receipt

    Raise HandoffError (subclass MergeError or new) when phase != completed.
    """
    project_root = project_root.resolve()
    inputs = HandoffInputs(project_root=project_root, session_id=session_id)

    # CODEX: implement loaders — blueprint
    blueprint_path = project_root / GAIJINN_DIR / "blueprint.json"
    if blueprint_path.exists():
        inputs.blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))

    # CODEX: implement — merge_pipeline_status + load_merge_report
    # from .merge import load_merge_report, merge_pipeline_status
    # inputs.merge_pipeline = merge_pipeline_status(project_root)
    # report = load_merge_report(project_root)
    # if report: inputs.merge_report = report

    # CODEX: implement — claims from forge session id on blueprint when present
    # inputs.claims_ledger = ...

    # CODEX: implement — repo_state via subprocess git -C project_root
    # inputs.repo_state = {"head": "...", "dirty": bool, "branch": "..."}

    return inputs


def build_handoff_json_payload(inputs: HandoffInputs, llm_sections: dict[str, Any]) -> dict[str, Any]:
    """Assemble handoff.json. CODEX: llm_sections comes from run_handoff_llm_audit only.

    Required top-level keys (downstream continuation map consumes these):
      schema_version, generated_at, session_id, repo, blueprint_summary,
      claims_summary, merge_receipt, continuation, llm_audit

    continuation block MUST include:
      - what_was_built (plain language)
      - how_to_run (commands from blueprint.run or detected surfaces)
      - what_to_do_next (ordered list for next AI/human)
      - invariants_preserved (from GIV + merge governance)
      - attach_hint → feeds loom-continuation-intent-map intake.attach_project
    """
    return {
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": inputs.session_id,
        "repo": inputs.repo_state,
        "blueprint_summary": {
            "projection_mode": inputs.blueprint.get("projection_mode"),
            "work_unit_count": len(inputs.blueprint.get("work_units") or []),
        },
        "claims_summary": {
            "promoted_count": (inputs.claims_ledger.get("promoted_count") or 0),
        },
        "merge_receipt": inputs.merge_pipeline,
        "continuation": llm_sections.get("continuation", {}),
        "llm_audit": llm_sections.get("llm_audit", {}),
    }


def render_handoff_markdown(payload: dict[str, Any]) -> str:
    """Render handoff.md from JSON payload. CODEX: keep sections stable for human + AI skimming.

    Suggested H2 order:
      ## System summary
      ## What Loom built
      ## How to run
      ## Claims & invariants
      ## Merge receipt
      ## Continuation guide (next session)
    """
    cont = payload.get("continuation") if isinstance(payload.get("continuation"), dict) else {}
    lines = [
        "# Loom continuation handoff",
        "",
        f"Generated: {payload.get('generated_at', '')}",
        "",
        "## System summary",
        str(cont.get("what_was_built") or "_CODEX: populate from LLM audit._"),
        "",
        "## How to run",
        str(cont.get("how_to_run") or "_CODEX: from blueprint.run / surface detection._"),
        "",
        "## Continuation guide",
    ]
    next_steps = cont.get("what_to_do_next")
    if isinstance(next_steps, list):
        lines.extend(f"- {item}" for item in next_steps)
    else:
        lines.append("_CODEX: ordered next steps for attach_project / continuation._")
    lines.append("")
    return "\n".join(lines)


def run_handoff_llm_audit(inputs: HandoffInputs) -> dict[str, Any]:
    """Run probabilistic interpretation ONLY — math/merge already enforced upstream.

    CODEX:
      - Use GAIJINN_REASONING_URL / reasoning_provider (same boundary as Pipeline 3)
      - Env GAIJINN_FAKE_REASONING=1 for tests (deterministic fixture JSON)
      - Prompt must include: blueprint summary, claims promoted, merge summary, repo tree
        snapshot (not full source dump — use source-dump.sh curated mode paths)
      - Output must map to continuation + llm_audit keys in build_handoff_json_payload
      - On provider failure: fail closed with HandoffError; do NOT write partial handoff
        as success (honest accounting — same ethos as sub-unity convergence)
    """
    raise NotImplementedError("CODEX: implement run_handoff_llm_audit (LOOM-212)")


def write_handoff_artifacts(project_root: Path, *, session_id: str = "", force: bool = False) -> Path:
    """Main entry: gather → audit → write handoff.json + handoff.md.

    CODEX:
      - Gate: merge_pipeline_status(project_root)["phase"] == "completed"
      - Idempotent: skip if handoff.json exists unless force=True
      - Atomic write: temp dir then rename into HANDOFF_DIR
      - Return HANDOFF_JSON_PATH
      - Wire from: loom handoff CLI, merge_grid post-success hook (optional), API POST
    """
    inputs = gather_handoff_inputs(project_root, session_id=session_id)
    llm_sections = run_handoff_llm_audit(inputs)
    payload = build_handoff_json_payload(inputs, llm_sections)
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    HANDOFF_JSON_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    HANDOFF_MD_PATH.write_text(render_handoff_markdown(payload), encoding="utf-8")
    return HANDOFF_JSON_PATH
