"""CLI wrapper for the minimal resolution-backed runtime pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from aoc_cli.runtime_pipeline import RuntimePipelineError, run_pipeline


def run_pipeline_cmd(input_path: Path, json_output: bool) -> None:
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        result = run_pipeline(payload)
    except (OSError, json.JSONDecodeError, RuntimePipelineError) as error:
        raise typer.BadParameter(str(error), param_hint="input_path") from error

    if json_output:
        typer.echo(json.dumps(result, indent=2, sort_keys=True))
        return

    typer.echo(f"pipeline_status: {result['pipeline_status']}")
    typer.echo(f"resolution_status: {result['resolution']['status']}")
    typer.echo(f"work_units: {len(result['work_units'])}")
    typer.echo(f"executions: {len(result['executions'])}")
