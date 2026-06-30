"""Strongly connected component helpers for resolution v3."""

from __future__ import annotations


def tarjan_scc(adj: dict[str, list[str]], all_nodes: list[str]) -> list[frozenset[str]]:
    """Return maximal SCCs in deterministic Tarjan order."""
    index_counter = 0
    stack: list[str] = []
    lowlink: dict[str, int] = {}
    index: dict[str, int] = {}
    on_stack: set[str] = set()
    result: list[frozenset[str]] = []

    def strongconnect(node_id: str) -> None:
        nonlocal index_counter
        index[node_id] = index_counter
        lowlink[node_id] = index_counter
        index_counter += 1
        stack.append(node_id)
        on_stack.add(node_id)

        for neighbor in sorted(adj.get(node_id, [])):
            if neighbor not in index:
                strongconnect(neighbor)
                lowlink[node_id] = min(lowlink[node_id], lowlink[neighbor])
            elif neighbor in on_stack:
                lowlink[node_id] = min(lowlink[node_id], index[neighbor])

        if lowlink[node_id] == index[node_id]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node_id:
                    break
            result.append(frozenset(component))

    for node_id in sorted(all_nodes):
        if node_id not in index:
            strongconnect(node_id)

    return result
