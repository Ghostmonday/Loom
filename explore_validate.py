import sys
import os
from pathlib import Path
from typing import Any

# Add the project root to sys.path
sys.path.append('vaults/gaijinn-memory-fs/aoc_supervisor')

# Mock what's needed to import orchestrate_session if it fails due to missing deps
# but let's try direct import first of just the function if possible,
# or just copy the code since it's a pure function and we want to explore ITS logic.

from aoc_supervisor.orchestrate_session import validate_loaded_context, PHASE_LABELS

def test_scenario(name, phases, loaded_context):
    print(f"--- Scenario: {name} ---")
    print(f"Phases: {phases}")
    print(f"Context: {loaded_context}")
    try:
        result = validate_loaded_context(phases, loaded_context)
        print(f"SUCCESS: {result}")
    except Exception as e:
        print(f"FAILURE: {type(e).__name__}: {e}")
    print()

# 1. Success case: no required context
test_scenario("No required context", ("backend",), None)

# 2. Success case: required context present (using existing paths)
existing_dir = str(Path(".").absolute())
test_scenario("Required context present", ("testing",), {
    "backend": {"project_path": existing_dir},
    "frontend": {"project_path": existing_dir}
})

# 3. Failure case: missing required context
test_scenario("Missing required context", ("testing",), {
    "backend": {"project_path": existing_dir}
})

# 4. Failure case: path does not exist
test_scenario("Path does not exist", ("testing",), {
    "backend": {"project_path": "/non/existent/path"},
    "frontend": {"project_path": existing_dir}
})

# 5. Failure case: invalid context structure
test_scenario("Invalid context structure", ("backend",), "not a dict")

# 6. Edge case: unknown phase labeling
test_scenario("Unknown phase labeling", ("unknown_phase", "testing"), {
    "backend": {"project_path": existing_dir},
    "frontend": {"project_path": existing_dir}
})
