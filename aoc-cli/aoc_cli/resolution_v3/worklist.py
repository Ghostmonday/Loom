"""Versioned deterministic worklist for resolution v3."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

URGENT = 0
NORMAL = 1


@dataclass(order=True)
class _Entry:
    priority: int
    locus: str
    version: int = field(compare=False)


class Worklist:
    """Priority worklist with lazy deletion and non-downgradable promotion."""

    def __init__(self) -> None:
        self._heap: list[_Entry] = []
        self._current: dict[str, tuple[int, int]] = {}

    def push(self, locus: str, priority: int = NORMAL) -> None:
        current = self._current.get(locus)
        if current is None:
            effective_priority = priority
            version = 1
        else:
            current_priority, current_version = current
            effective_priority = min(current_priority, priority)
            version = current_version + 1

        self._current[locus] = (effective_priority, version)
        heapq.heappush(self._heap, _Entry(priority=effective_priority, locus=locus, version=version))

    def pop(self) -> str | None:
        while self._heap:
            entry = heapq.heappop(self._heap)
            current = self._current.get(entry.locus)
            if current == (entry.priority, entry.version):
                del self._current[entry.locus]
                return entry.locus
        return None

    def __bool__(self) -> bool:
        return bool(self._current)
