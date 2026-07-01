from __future__ import annotations

import json
from pathlib import Path

from aoc_cli.cli import app
from aoc_cli.runtime_pipeline import RuntimePipelineError, run_pipeline
from typer.testing import CliRunner

runner = CliRunner()


def _canonical_input() -> dict:
    return {
        "intent": "Run the minimal resolver-backed pipeline",
        "nodes": [
            {
                "id": "Api",
                "status": "KNOWN",
                "type": "service",
                "layer": 1,
                "root_permitted": True,
                "sink_permitted": False,
            }
        ],
        "edges": [
            {
                "u": "Api",
                "v": "AuditLog",
                "modality": "REQ",
                "label": "writes_to",
            }
        ],
    }


def test_runtime_pipeline_runs_end_to_end_deterministically() -> None:
    first = run_pipeline(_canonical_input())
    second = run_pipeline(
        {
            "edges": list(reversed(_canonical_input()["edges"])),
            "nodes": list(reversed(_canonical_input()["nodes"])),
            "intent": "Run the minimal resolver-backed pipeline",
        }
    )

    assert first == second
    assert first["pipeline_status"] == "COMPLETED"
    assert first["resolution"]["status"] == "CANONICAL"
    assert first["resolution"]["fault_detail"] is None
    assert first["work_units"] == [
        {
            "id": "WU-api",
            "node_id": "Api",
            "node_type": "service",
            "layer": 1,
            "root_permitted": True,
            "sink_permitted": False,
        },
        {
            "id": "WU-auditlog",
            "node_id": "AuditLog",
            "node_type": "log_sink",
            "layer": 1,
            "root_permitted": False,
            "sink_permitted": False,
        },
    ]
    assert first["executions"] == [
        {
            "unit_id": "WU-api",
            "status": "EXECUTED",
            "output": "mock-executed:WU-api:Api",
        },
        {
            "unit_id": "WU-auditlog",
            "status": "EXECUTED",
            "output": "mock-executed:WU-auditlog:AuditLog",
        },
    ]


def test_runtime_pipeline_blocks_invalid_resolved_graph_without_execution() -> None:
    payload = {
        "nodes": [
            {
                "id": "Api",
                "status": "KNOWN",
                "type": "service",
                "layer": 1,
                "root_permitted": True,
                "sink_permitted": False,
            },
            {
                "id": "AuditLog",
                "status": "KNOWN",
                "type": "log_sink",
                "layer": 1,
                "root_permitted": False,
                "sink_permitted": True,
            },
        ],
        "edges": [
            {
                "u": "Api",
                "v": "AuditLog",
                "modality": "REQ",
                "label": "calls",
            }
        ],
    }

    result = run_pipeline(payload)

    assert result["pipeline_status"] == "BLOCKED"
    assert result["resolution"]["status"] == "STUCK"
    assert result["valid"] is False
    assert result["stable"] is True
    assert result["work_units"] == []
    assert result["executions"] == []
    assert any("incompatible type 'log_sink'" in item for item in result["diagnostics"])


def test_runtime_pipeline_rejects_implicit_permission_defaults() -> None:
    payload = _canonical_input()
    del payload["nodes"][0]["root_permitted"]

    try:
        run_pipeline(payload)
    except RuntimePipelineError as error:
        assert "root_permitted must be a boolean" in str(error)
    else:
        raise AssertionError("expected RuntimePipelineError")


def test_run_pipeline_cli_emits_json(tmp_path: Path) -> None:
    input_path = tmp_path / "pipeline.json"
    input_path.write_text(json.dumps(_canonical_input()), encoding="utf-8")

    result = runner.invoke(app, ["run-pipeline", str(input_path), "--json"], color=False)

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["pipeline_status"] == "COMPLETED"
    assert payload["resolution"]["status"] == "CANONICAL"
    assert [item["unit_id"] for item in payload["executions"]] == ["WU-api", "WU-auditlog"]
