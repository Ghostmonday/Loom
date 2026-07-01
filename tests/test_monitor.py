from __future__ import annotations

import unittest.mock as mock

import pytest
import typer
from aoc_cli.commands.monitor import _worker_output_status, monitor_cmd


def test_worker_output_status_no_dirs(tmp_path, monkeypatch):
    workers_dir = tmp_path / "workers"
    workers_dir.mkdir()

    # Mock WORKERS_DIR in the monitor module
    monkeypatch.setattr("aoc_cli.commands.monitor.WORKERS_DIR", workers_dir)

    assert _worker_output_status() == "no worker directories"


def test_worker_output_status_with_logs(tmp_path, monkeypatch):
    workers_dir = tmp_path / "workers"
    workers_dir.mkdir()
    (workers_dir / "worker-001").mkdir()
    (workers_dir / "worker-002").mkdir()

    log_filename = "output.log"
    (workers_dir / "worker-001" / log_filename).write_text("log1")

    monkeypatch.setattr("aoc_cli.commands.monitor.WORKERS_DIR", workers_dir)
    monkeypatch.setattr("aoc_cli.commands.monitor.OUTPUT_LOG_FILENAME", log_filename)

    assert _worker_output_status() == "1/2 worker output logs present"


def test_monitor_cmd_loop_and_interrupt(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("initial")

    with (
        mock.patch("aoc_cli.commands.monitor._load_validate_system_state") as mock_load,
        mock.patch("aoc_cli.commands.monitor._file_signature") as mock_sig,
        mock.patch("aoc_cli.commands.monitor._run_validation") as mock_val,
        mock.patch("aoc_cli.commands.monitor.shadow_bridge_summary") as mock_summary,
        mock.patch("aoc_cli.commands.monitor._echo_status") as mock_echo,
        mock.patch("aoc_cli.commands.monitor._worker_output_status") as mock_worker_status,
        mock.patch("time.sleep") as mock_sleep,
    ):
        # Setup mocks
        mock_load.return_value = "state"
        mock_sig.side_effect = [(1, 2, 3), (1, 2, 3), (4, 5, 6)]
        mock_summary.return_value = {"shadow_bridge_count": 2, "rejected_node_count": 0}
        mock_worker_status.return_value = "2/2 logs"

        # Raise KeyboardInterrupt on the 3rd sleep to break the loop
        mock_sleep.side_effect = [None, None, KeyboardInterrupt()]

        with pytest.raises(typer.Exit) as excinfo:
            monitor_cmd(manifest, 0.1)

        assert excinfo.value.exit_code == 0

        # Verify initial echoes
        mock_echo.assert_any_call(f"monitoring {manifest}")
        mock_echo.assert_any_call("terminal bridge: 2/2 logs")

        # Verify validation and summary were called when signature changed
        # Initial signature (1, 2, 3) is different from None, so it triggers once
        # Second call (1, 2, 3) is same, no trigger
        # Third call (4, 5, 6) is different, triggers again
        assert mock_val.call_count == 2
        assert mock_summary.call_count == 2

        mock_echo.assert_any_call("metrics update: shadow_bridges=2 rejected=0")


def test_monitor_cmd_handles_missing_manifest(tmp_path):
    manifest = tmp_path / "missing.json"

    with (
        mock.patch("aoc_cli.commands.monitor._load_validate_system_state"),
        mock.patch("aoc_cli.commands.monitor._file_signature") as mock_sig,
        mock.patch("aoc_cli.commands.monitor._run_validation") as mock_val,
        mock.patch("aoc_cli.commands.monitor._echo_status"),
        mock.patch("time.sleep") as mock_sleep,
    ):
        mock_sig.return_value = None
        mock_sleep.side_effect = KeyboardInterrupt()

        with pytest.raises(typer.Exit):
            monitor_cmd(manifest, 0.1)

        mock_val.assert_not_called()
