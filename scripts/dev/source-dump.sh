#!/usr/bin/env bash
# Loom source dump / knowledge pack generator.
#
# Default mode is curated for AI session starts:
#   bash scripts/dev/source-dump.sh ~/Desktop/LOOMFILES2.md
#
# Full mode preserves the old complete text-only source dump behavior:
#   bash scripts/dev/source-dump.sh --full ~/Desktop/loom-source-dump.txt
#
# Never embed binaries in text dumps.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MODE="${LOOM_SOURCE_DUMP_MODE:-curated}"

if [[ "${1:-}" == "--full" ]]; then
    MODE="full"
    shift
elif [[ "${1:-}" == "--curated" ]]; then
    MODE="curated"
    shift
fi

if [[ "$MODE" != "curated" && "$MODE" != "full" ]]; then
    echo "usage: $0 [--curated|--full] [output-path]" >&2
    echo "error: mode must be 'curated' or 'full', got '$MODE'" >&2
    exit 2
fi

OUT="${1:-$HOME/Desktop/LOOMFILES2.md}"
COMMIT="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
BRANCH="$(git -C "$ROOT" branch --show-current 2>/dev/null || echo unknown)"
RECENT_COMMITS="$(git -C "$ROOT" log --oneline -8 2>/dev/null || true)"
WORKTREE_STATUS="$(git -C "$ROOT" status --short --branch 2>/dev/null || true)"

python3 - "$ROOT" "$OUT" "$BRANCH" "$COMMIT" "$MODE" "$RECENT_COMMITS" "$WORKTREE_STATUS" <<'PY'
from __future__ import annotations

import hashlib
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).expanduser().resolve()
BRANCH = sys.argv[3]
COMMIT = sys.argv[4]
MODE = sys.argv[5]
RECENT_COMMITS = sys.argv[6]
WORKTREE_STATUS = sys.argv[7]

EXTENSIONS = {
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SPECIAL_NAMES = {"Dockerfile", "LICENSE", "Makefile"}
SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
SKIP_NAMES = {
    ".coverage",
    ".DS_Store",
    "LOOMFILES.md",
    "LOOMFILES.md.gz",
    "LOOMFILES2.md",
    "LOOMFILES2.md.gz",
    "gaijinn-source-dump.txt",
    "gaijinn-source-dump.txt.gz",
}
SKIP_PREFIXES = (
    ".gaijinn/codex/",
    ".gaijinn/sessions/",
    ".gaijinn/workers/",
    "dist/",
    "vaults/",
)
EMPTY_JSONS = {"{}", "[]"}


@dataclass(frozen=True)
class DumpFile:
    category: str
    rel: str
    path: Path
    text: str
    digest: str


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def path_is_output(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except OSError:
        return False
    return resolved == OUT or resolved == Path(f"{OUT}.gz")


def skip(path: Path) -> bool:
    if path_is_output(path):
        return True
    rel = relpath(path)
    if path.name in SKIP_NAMES or rel.startswith(SKIP_PREFIXES):
        return True
    if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
        return True
    return path.suffix not in EXTENSIONS and path.name not in SPECIAL_NAMES


def is_text(path: Path) -> bool:
    try:
        data = path.read_bytes()[:8192]
    except OSError:
        return False
    if b"\x00" in data or data.startswith(b"SQLite format 3"):
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def category_for(rel: str) -> str:
    if rel in {"AGENTS.md", "README.md", "pyproject.toml"}:
        return "00-root"
    if rel.startswith(".agents/"):
        return "01-agent-skills"
    if rel.startswith(".github/"):
        return "02-ci-cd"
    if rel.startswith(".loom/frg/"):
        return "03-frg-graphs"
    if rel.startswith(".loom/contracts/"):
        return "04-intent-maps"
    if rel.startswith(".loom/codex-slices/"):
        return "05-codex-slices"
    if rel.startswith(".loom/"):
        return "06-loom-infra"
    if rel.startswith("aoc-cli/"):
        return "07-cli-package"
    if rel.startswith("aoc_supervisor/"):
        return "08-api-package"
    if rel.startswith("sandbox_frontend/"):
        return "09-sandbox-ui"
    if rel.startswith("ui/"):
        return "10-ui-intent-maps"
    if rel.startswith("tests/"):
        return "11-tests"
    if rel.startswith("docs/"):
        return "12-docs"
    if rel.startswith("scripts/"):
        return "13-scripts"
    if rel.startswith("examples/"):
        return "14-examples"
    if rel.startswith(("frontend-formation", "loom-frontend-base")):
        return "15-frontend-formation"
    return "99-other"


def label_for(category: str) -> str:
    return category.split("-", 1)[1].replace("-", " ").title()


def fmt_size(size: int) -> str:
    if size < 1024:
        return f"{size}B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f}K"
    return f"{size / (1024 * 1024):.1f}M"


def gather_candidates() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*") if path.is_file() and not skip(path) and is_text(path))


def build_dump_files(candidates: list[Path]) -> tuple[list[DumpFile], list[str], dict[str, list[str]]]:
    empty_jsons: list[str] = []
    duplicate_groups: dict[str, list[str]] = defaultdict(list)
    first_by_digest: dict[str, str] = {}
    dump_files: list[DumpFile] = []

    for path in candidates:
        rel = relpath(path)
        text = path.read_text(encoding="utf-8")
        stripped = text.strip()

        if MODE == "curated" and path.suffix == ".json" and stripped in EMPTY_JSONS:
            empty_jsons.append(rel)
            continue

        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if MODE == "curated" and digest in first_by_digest:
            duplicate_groups[first_by_digest[digest]].append(rel)
            continue

        first_by_digest[digest] = rel
        dump_files.append(DumpFile(category_for(rel), rel, path, text, digest))

    return sorted(dump_files, key=lambda item: (item.category, item.rel)), empty_jsons, duplicate_groups


def write_file_section(out, item: DumpFile) -> None:
    sep = "=" * 80
    out.write(f"\n{sep}\nFILE: {item.rel}\n{sep}\n")
    out.write(item.text)
    if not item.text.endswith("\n"):
        out.write("\n")


def write_full_dump(out, dump_files: list[DumpFile], candidate_count: int) -> None:
    header = (
        "=" * 80 + "\n"
        "GAIJINN SOURCE CODE DUMP (TEXT ONLY)\n"
        f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
        f"Repo: {ROOT}\n"
        f"Branch: {BRANCH}\n"
        f"Commit: {COMMIT}\n"
        f"Files included: {len(dump_files)}\n"
        f"Raw candidates: {candidate_count}\n"
        "SKIPPED: .git, .venv, vaults/, .gaijinn/sessions/, dist/, generated dumps, all binaries\n"
        + "=" * 80 + "\n\n"
    )
    out.write(header)
    for item in dump_files:
        write_file_section(out, item)


def write_curated_dump(
    out,
    dump_files: list[DumpFile],
    candidate_count: int,
    empty_jsons: list[str],
    duplicate_groups: dict[str, list[str]],
) -> None:
    buckets: dict[str, list[DumpFile]] = defaultdict(list)
    for item in dump_files:
        buckets[item.category].append(item)

    header = (
        "=" * 80 + "\n"
        "LOOM KNOWLEDGE PACK - CURATED SESSION START\n"
        f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
        f"Repo: {ROOT}\n"
        f"Branch: {BRANCH}\n"
        f"Commit: {COMMIT}\n"
        f"Files in dump: {len(dump_files)}\n"
        f"Filtered out: {len(empty_jsons)} empty JSON + {sum(len(v) for v in duplicate_groups.values())} duplicates\n"
        f"Raw candidates: {candidate_count}\n"
        "SKIPPED: .git, .venv, vaults/, .gaijinn/sessions/, dist/, generated dumps, all binaries\n"
        + "=" * 80 + "\n\n"
    )
    out.write(header)

    out.write("## AI CONTEXT PRIMER\n\n")
    out.write(
        "This file is a curated, text-only context pack for agent session starts. "
        "It is optimized for fast orientation, not byte-for-byte archival completeness. "
        "Use `scripts/dev/source-dump.sh --full` when a complete text dump is required.\n\n"
    )
    out.write(
        "Default output is `~/Desktop/LOOMFILES2.md`, with a sibling gzip artifact generated automatically. "
        "The curated mode is meant to be the handoff pack you give a fresh model before deeper repo exploration.\n\n"
    )
    out.write("Start resolver work by reading these files in order:\n\n")
    for path in [
        "aoc-cli/aoc_cli/resolution_v3/model.py",
        "aoc-cli/aoc_cli/resolution_v3/graph.py",
        "aoc-cli/aoc_cli/resolution_v3/worklist.py",
        "aoc-cli/aoc_cli/resolution_v3/rules.py",
        "aoc-cli/aoc_cli/resolution_v3/potential.py",
        "aoc-cli/aoc_cli/resolution_v3/validation.py",
        "aoc-cli/aoc_cli/resolution_v3/reporting.py",
        "aoc-cli/aoc_cli/resolution_v3/scc.py",
        "aoc-cli/aoc_cli/resolution_v3/engine.py",
        "loom_resolution_engine_v3.py",
        "tests/test_resolution_v3_adversarial.py",
        "tests/test_resolution_v3_units.py",
        "tests/test_resolution_v3_import_parity.py",
    ]:
        out.write(f"- `{path}`\n")

    out.write("\nGuardrails:\n\n")
    for line in [
        "Add failing regressions before semantic changes.",
        "Keep correction slices bisectable and commit separately.",
        "Do not reset or clean unrelated user work.",
        "If strict descent fails, report the exact graph and trace before changing Psi.",
        "Preserve package/shim parity for resolution_v3.",
    ]:
        out.write(f"- {line}\n")

    if RECENT_COMMITS.strip():
        out.write("\nRecent commits at dump time:\n\n")
        for line in RECENT_COMMITS.splitlines():
            out.write(f"- `{line}`\n")

    if WORKTREE_STATUS.strip():
        out.write("\nGit status at dump time:\n\n")
        for line in WORKTREE_STATUS.splitlines():
            out.write(f"- `{line}`\n")

    out.write("\n## TABLE OF CONTENTS\n\n")
    out.write("| Category | Files | Size |\n")
    out.write("|----------|------:|----:|\n")
    for category in sorted(buckets):
        total = sum(len(item.text) for item in buckets[category])
        out.write(f"| {label_for(category)} | {len(buckets[category])} | {fmt_size(total)} |\n")

    out.write(f"\n**Total: {len(dump_files)} files, {fmt_size(sum(len(item.text) for item in dump_files))}**\n\n")

    if empty_jsons:
        out.write("### Filtered: empty JSONs\n\n")
        for rel in empty_jsons:
            out.write(f"- `{rel}`\n")
        out.write("\n")

    if duplicate_groups:
        out.write("### Filtered: content duplicates\n\n")
        for first in sorted(duplicate_groups):
            duplicates = ", ".join(sorted(duplicate_groups[first]))
            out.write(f"- `{first}` <- identical: {duplicates}\n")
        out.write("\n")

    for category in sorted(buckets):
        out.write("\n" + "-" * 80 + "\n")
        out.write(f"## CATEGORY: {label_for(category)} ({len(buckets[category])} files)\n")
        out.write("-" * 80 + "\n\n")
        for item in buckets[category]:
            write_file_section(out, item)


OUT.parent.mkdir(parents=True, exist_ok=True)
candidates = gather_candidates()
dump_files, empty_jsons, duplicate_groups = build_dump_files(candidates)

with OUT.open("w", encoding="utf-8", newline="\n") as out:
    if MODE == "full":
        write_full_dump(out, dump_files, len(candidates))
    else:
        write_curated_dump(out, dump_files, len(candidates), empty_jsons, duplicate_groups)

blob = OUT.read_bytes()
nulls = blob.count(b"\x00")
if nulls:
    raise SystemExit(f"FATAL: dump contains {nulls} null bytes")

print(
    f"OK: {OUT} ({len(blob) / 1024 / 1024:.2f} MB, "
    f"{len(dump_files)} files, mode={MODE}, null bytes: 0)"
)
PY

gzip -kf "$OUT"
echo "Compressed: ${OUT}.gz"
