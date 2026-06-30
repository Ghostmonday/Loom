"""Focused unit tests for resolution v3 module seams."""

from aoc_cli.resolution_v3 import ConstraintGraph, Edge, Modality, Node, Status, Worklist, tarjan_scc
from aoc_cli.resolution_v3.potential import cyclic_debt
from aoc_cli.resolution_v3.rules import apply_b2


def test_tarjan_returns_maximal_components_deterministically() -> None:
    adj = {
        "B": ["A", "C"],
        "A": ["B"],
        "C": ["D"],
        "D": ["C"],
        "E": [],
    }

    assert tarjan_scc(adj, ["E", "D", "C", "B", "A"]) == [
        frozenset({"C", "D"}),
        frozenset({"A", "B"}),
        frozenset({"E"}),
    ]


def test_cyclic_debt_squares_violating_scc_size() -> None:
    cg = ConstraintGraph()
    for node_id in ["A", "B", "C"]:
        cg.add_node(Node(node_id, Status.KNOWN, "service", 1))
    cg.add_edge(Edge("A", "B", Modality.REQ, "ab"))
    cg.add_edge(Edge("B", "C", Modality.REQ, "bc"))
    cg.add_edge(Edge("C", "A", Modality.REQ, "ca"))

    assert cyclic_debt(cg) == 9


def test_apply_b2_welds_only_one_maximal_scc_per_call() -> None:
    cg = ConstraintGraph()
    for node_id in ["A", "B", "C", "D"]:
        cg.add_node(Node(node_id, Status.KNOWN, "service", 1))
    cg.add_edge(Edge("A", "B", Modality.REQ, "ab"))
    cg.add_edge(Edge("B", "A", Modality.REQ, "ba"))
    cg.add_edge(Edge("C", "D", Modality.REQ, "cd"))
    cg.add_edge(Edge("D", "C", Modality.REQ, "dc"))

    worklist = Worklist()
    assert apply_b2(cg, worklist) is True

    assert "WELD[A|B]" in cg.nodes
    assert "C" in cg.nodes
    assert "D" in cg.nodes
    assert cyclic_debt(cg) == 4


def test_validation_distinguishes_zero_psi_from_validity() -> None:
    cg = ConstraintGraph()
    cg.add_node(Node("Target", Status.KNOWN, "service", 1))
    cg.add_edge(Edge("MissingSource", "Target", Modality.REQ, "calls"))

    assert cg.psi() == (0, 0, 0, 0)
    assert cg.is_valid() is False
    assert any("missing source" in error for error in cg.validation_errors())
