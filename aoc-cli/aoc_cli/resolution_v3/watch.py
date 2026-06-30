"""Mutable edge dependency index for the resolution graph."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aoc_cli.resolution_v3.model import Edge

if TYPE_CHECKING:
    from aoc_cli.resolution_v3.graph import ConstraintGraph


class WatchIndex:
    """Map a node id to stable edge-array indices touching that node."""

    def __init__(self, cg: ConstraintGraph):
        self.cg = cg
        self.by_node: dict[str, set[int]] = {}
        self.rebuild()

    def rebuild(self) -> None:
        self.by_node.clear()
        for index, edge in enumerate(self.cg.edges):
            self.register_edge(index, edge)

    def edges_touching(self, node_id: str) -> set[int]:
        return set(self.by_node.get(node_id, set()))

    def register_edge(self, index: int, edge: Edge) -> None:
        self.by_node.setdefault(edge.u, set()).add(index)
        self.by_node.setdefault(edge.v, set()).add(index)
