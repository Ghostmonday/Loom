from unittest.mock import MagicMock, patch

import pytest
import typer
from aoc_cli.commands.promote import _find_vault_root, promote_cmd


def test_find_vault_root_detected(tmp_path):
    vault = tmp_path / "my-vault"
    gaijinn = vault / ".gaijinn"
    gaijinn.mkdir(parents=True)
    (gaijinn / "bridge").mkdir()
    (gaijinn / "bridge" / "council.md").touch()

    assert _find_vault_root(vault) == vault
    # Test walking up
    subdir = vault / "a" / "b"
    subdir.mkdir(parents=True)
    assert _find_vault_root(subdir) == vault


def test_find_vault_root_not_found(tmp_path):
    assert _find_vault_root(tmp_path) is None


@pytest.fixture
def mock_vault(tmp_path):
    vault = tmp_path / "my-vault"
    gaijinn = vault / ".gaijinn"
    gaijinn.mkdir(parents=True)
    (gaijinn / "bridge").mkdir()
    (gaijinn / "bridge" / "council.md").touch()

    ops = vault / "10_Operations"
    ops.mkdir()
    linter = ops / "knowledge-linter.py"
    linter.touch()
    promote_sh = ops / "promote.sh"
    promote_sh.touch()
    return vault


@patch("aoc_cli.commands.promote.subprocess.run")
def test_promote_cmd_success(mock_run, mock_vault):
    mock_run.return_value = MagicMock(returncode=0, stdout="linter output", stderr="")

    promote_cmd(vault_root=str(mock_vault))

    # Pre-linter, promote.sh, post-linter
    assert mock_run.call_count == 3

    # Verify promote.sh call
    promote_sh_call = mock_run.call_args_list[1]
    assert str(mock_vault / "10_Operations" / "promote.sh") in promote_sh_call.args[0]
    assert promote_sh_call.kwargs["cwd"] == str(mock_vault)


@patch("aoc_cli.commands.promote.subprocess.run")
def test_promote_cmd_check_flag(mock_run, mock_vault):
    mock_run.return_value = MagicMock(returncode=0)
    promote_cmd(vault_root=str(mock_vault), check=True)

    # promote.sh should have --check
    promote_sh_call = mock_run.call_args_list[1]
    assert "--check" in promote_sh_call.args[0]
    # No post-linter when check=True
    assert mock_run.call_count == 2


@patch("aoc_cli.commands.promote.subprocess.run")
def test_promote_cmd_file_flag(mock_run, mock_vault):
    mock_run.return_value = MagicMock(returncode=0)
    promote_cmd(vault_root=str(mock_vault), file="test.md")

    # promote.sh should have --file test.md
    promote_sh_call = mock_run.call_args_list[1]
    assert "--file" in promote_sh_call.args[0]
    assert "test.md" in promote_sh_call.args[0]
    # No post-linter when file is specified
    assert mock_run.call_count == 2


@patch("aoc_cli.commands.promote.subprocess.run")
def test_promote_cmd_list_flag(mock_run, mock_vault):
    mock_run.return_value = MagicMock(returncode=0)
    with pytest.raises(typer.Exit) as exc:
        promote_cmd(vault_root=str(mock_vault), list_files=True)
    assert exc.value.exit_code == 0

    # Only promote.sh --list should be called
    assert mock_run.call_count == 1
    assert "--list" in mock_run.call_args.args[0]


@patch("aoc_cli.commands.promote.subprocess.run")
def test_promote_cmd_skip_linter(mock_run, mock_vault):
    mock_run.return_value = MagicMock(returncode=0)
    promote_cmd(vault_root=str(mock_vault), skip_linter=True)

    # Only promote.sh should be called
    assert mock_run.call_count == 1
    assert "promote.sh" in mock_run.call_args.args[0][0]


def test_promote_cmd_no_vault_found(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(typer.Exit) as exc:
        promote_cmd()
    assert exc.value.exit_code == 1


@patch("aoc_cli.commands.promote.subprocess.run")
def test_promote_cmd_linter_fail_blocks(mock_run, mock_vault):
    # Pre-linter fails
    mock_run.return_value = MagicMock(returncode=1)

    with pytest.raises(typer.Exit) as exc:
        promote_cmd(vault_root=str(mock_vault))
    assert exc.value.exit_code == 1

    # Only 1 call to linter
    assert mock_run.call_count == 1


@patch("aoc_cli.commands.promote.subprocess.run")
def test_promote_cmd_promote_sh_fails(mock_run, mock_vault):
    # Linter passes, promote.sh fails
    mock_run.side_effect = [
        MagicMock(returncode=0),  # pre-linter
        MagicMock(returncode=1),  # promote.sh
    ]

    with pytest.raises(typer.Exit) as exc:
        promote_cmd(vault_root=str(mock_vault))
    assert exc.value.exit_code == 1
    assert mock_run.call_count == 2


def test_promote_cmd_missing_promote_sh(tmp_path):
    vault = tmp_path / "my-vault"
    (vault / ".gaijinn" / "bridge").mkdir(parents=True)
    (vault / ".gaijinn" / "bridge" / "council.md").touch()
    # No promote.sh

    with pytest.raises(typer.Exit) as exc:
        promote_cmd(vault_root=str(vault))
    assert exc.value.exit_code == 1


@patch("aoc_cli.commands.promote.subprocess.run")
def test_promote_cmd_post_linter_fail_not_blocking(mock_run, mock_vault):
    # pre-linter pass, promote.sh pass, post-linter fail
    mock_run.side_effect = [
        MagicMock(returncode=0),  # pre-linter
        MagicMock(returncode=0),  # promote.sh
        MagicMock(returncode=1),  # post-linter
    ]

    # Should NOT raise typer.Exit because post-linter is non-blocking
    promote_cmd(vault_root=str(mock_vault))
    assert mock_run.call_count == 3
