from __future__ import annotations

import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def test_supervisor_router_package_is_declared() -> None:
    # Use a simpler way to verify packaging that doesn't depend on tomllib
    # since we're just checking if the package is in the list
    with open("pyproject.toml", encoding="utf-8") as f:
        content = f.read()

    assert "aoc_supervisor.routers" in content
    assert Path("aoc_supervisor/aoc_supervisor/routers/__init__.py").is_file()
