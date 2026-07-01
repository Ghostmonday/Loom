"""loom handoff — continuation artifact generator after validated merge.

CODEX SLICE LOOM-212
--------------------
User-facing command:

    loom handoff [--session-id ID] [--project-root PATH] [--force] [--json]

Runs AFTER the pipeline produces structurally correct merged code. This command does
not replace merge-grid, collect, or validate-worker. It adds the missing product layer:

    Intent → Blueprint → Grid → Merge (existing)
    → codebase audit + handoff artifacts (THIS COMMAND)
    → Deliverable / Continuation attach (loom-deliverable-intent-map.json)

Outputs (under <project>/.gaijinn/handoff/):
    handoff.md   — human: system explanation, how to run, what to do next
    handoff.json — machine: AI-readable continuation contract for intake.attach_project

See aoc_cli.helpers.continuation_handoff for implementation hooks.
"""

from __future__ import annotations

from pathlib import Path

import typer

from ..helpers.continuation_handoff import HANDOFF_JSON_PATH, write_handoff_artifacts


def handoff_cmd(
    session_id: str = typer.Option(
        "",
        "--session-id",
        help="Orchestrate session id when project root is managed by aoc_supervisor store.",
    ),
    project_root: Path | None = typer.Option(
        None,
        "--project-root",
        help="Merged project directory (default: current working directory).",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Regenerate handoff even if handoff.json already exists.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Print handoff.json to stdout after generation.",
    ),
) -> None:
    """Generate continuation handoff artifacts after merge completion."""
    root = (project_root or Path.cwd()).resolve()

    # CODEX: before write_handoff_artifacts, assert merge phase completed:
    #   from ..helpers.merge import merge_pipeline_status
    #   status = merge_pipeline_status(root)
    #   if status.get("phase") != "completed": raise typer.Exit(1) with clear message

    if HANDOFF_JSON_PATH.exists() and not force:
        typer.echo(f"Handoff exists: {HANDOFF_JSON_PATH} (use --force to regenerate)")
        if json_output:
            typer.echo(HANDOFF_JSON_PATH.read_text(encoding="utf-8"))
        return

    # CODEX: uncomment when write_handoff_artifacts is fully implemented
    try:
        path = write_handoff_artifacts(root, session_id=session_id, force=force)
    except NotImplementedError as exc:
        typer.echo(f"CODEX: {exc}", err=True)
        raise typer.Exit(2) from exc

    typer.echo(f"Wrote {path}")
    if json_output:
        typer.echo(path.read_text(encoding="utf-8"))
