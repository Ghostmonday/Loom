from __future__ import annotations

from pathlib import Path

import pytest

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@pytest.mark.skipif(tomllib is None, reason="tomllib (Python 3.11+) or tomli required to run this test")
def test_supervisor_router_package_is_declared() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    packages = pyproject["tool"]["setuptools"]["packages"]
    assert "aoc_supervisor.routers" in packages
    assert Path("aoc_supervisor/aoc_supervisor/routers/__init__.py").is_file()
