from __future__ import annotations

from pathlib import Path

import tomllib


def test_supervisor_router_package_is_declared() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    packages = pyproject["tool"]["setuptools"]["packages"]
    assert "aoc_supervisor.routers" in packages
    assert Path("aoc_supervisor/aoc_supervisor/routers/__init__.py").is_file()
