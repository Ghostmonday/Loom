"""Asserted adversarial regression suite for the Loom resolution engine v3."""

from loom_resolution_engine_v3 import (
    ACYCLIC_LAYERS,
    NORMAL,
    URGENT,
    ConstraintGraph,
    Edge,
    EngineStatus,
    Modality,
    Node,
    Status,
    Worklist,
    resolve,
)


def assert_strict_descent(result: dict) -> None:
    values = [psi for _, psi in result["psi_trace"]]
    assert all(after < before for before, after in zip(values, values[1:])), values


def assert_terminal(
    result: dict,
    status: EngineStatus,
    *,
    valid: bool,
    stable: bool,
    steps: int | None = None,
) -> None:
    assert result["status"] == status, result
    assert result["valid"] is valid, result
    assert result["stable"] is stable, result
    if steps is not None:
        assert result["steps"] == steps, result
    if status != EngineStatus.ENGINE_FAULT:
        assert_strict_descent(result)


def test_original_regression() -> None:
    cg = ConstraintGraph()
    cg.add_node(Node("OrderService", Status.KNOWN, "service", 1))
    cg.add_node(Node("PaymentGateway", Status.KNOWN, "service", 1))
    cg.add_edge(Edge("OrderService", "PaymentGateway", Modality.REQ, "calls"))
    cg.add_edge(Edge("OrderService", "AuditLog", Modality.REQ, "writes_to"))
    cg.add_edge(Edge("PaymentGateway", "OrderService", Modality.REQ, "calls_back"))
    cg.add_edge(Edge("PaymentGateway", "OrderService", Modality.FORBID, "calls_back"))
    cg.add_edge(Edge("AuditLog", "OrderService", Modality.REQ, "flushes_to"))

    result = resolve(cg)
    assert_terminal(result, EngineStatus.CANONICAL, valid=True, stable=True, steps=4)
    assert result["psi_trace"][-1][1] == (0, 0, 0, 0)


def test_two_disjoint_cycles() -> None:
    cg = ConstraintGraph()
    for node_id in ["A", "B", "C", "D"]:
        cg.add_node(Node(node_id, Status.KNOWN, "service", 1))
    cg.add_edge(Edge("A", "B", Modality.REQ, "x"))
    cg.add_edge(Edge("B", "A", Modality.REQ, "y"))
    cg.add_edge(Edge("C", "D", Modality.REQ, "x"))
    cg.add_edge(Edge("D", "C", Modality.REQ, "y"))

    result = resolve(cg)
    assert_terminal(result, EngineStatus.CANONICAL, valid=True, stable=True, steps=2)
    assert [psi for _, psi in result["psi_trace"]] == [
        (0, 0, 8, 0),
        (0, 0, 4, 0),
        (0, 0, 0, 0),
    ]


def test_overlapping_cycles_one_scc() -> None:
    cg = ConstraintGraph()
    for node_id in ["A", "B", "C", "D"]:
        cg.add_node(Node(node_id, Status.KNOWN, "service", 1))
    cg.add_edge(Edge("A", "B", Modality.REQ, "p"))
    cg.add_edge(Edge("B", "C", Modality.REQ, "q"))
    cg.add_edge(Edge("C", "A", Modality.REQ, "r"))
    cg.add_edge(Edge("B", "D", Modality.REQ, "s"))
    cg.add_edge(Edge("D", "C", Modality.REQ, "t"))

    result = resolve(cg)
    assert_terminal(result, EngineStatus.CANONICAL, valid=True, stable=True, steps=1)
    assert result["psi_trace"] == [(0, (0, 0, 16, 0)), (1, (0, 0, 0, 0))]
    assert any("size=4" in line for line in result["log"])


def test_weld_manufactures_clash() -> None:
    cg = ConstraintGraph()
    for node_id in ["A", "B", "X"]:
        cg.add_node(Node(node_id, Status.KNOWN, "service", 1))
    cg.add_edge(Edge("A", "B", Modality.REQ, "cyc"))
    cg.add_edge(Edge("B", "A", Modality.REQ, "cyc2"))
    cg.add_edge(Edge("A", "X", Modality.REQ, "uses"))
    cg.add_edge(Edge("B", "X", Modality.FORBID, "uses"))

    result = resolve(cg)
    assert_terminal(result, EngineStatus.CANONICAL, valid=True, stable=True, steps=2)
    assert [psi for _, psi in result["psi_trace"]] == [
        (0, 0, 4, 0),
        (0, 0, 0, 1),
        (0, 0, 0, 0),
    ]


def test_honest_stuck_ambiguity() -> None:
    cg = ConstraintGraph()
    cg.add_node(Node("AuditLog", Status.KNOWN, "log_sink", 1))
    cg.add_edge(Edge("AuditLog", "Downstream", Modality.REQ, "flushes_to"))

    result = resolve(cg)
    assert_terminal(result, EngineStatus.STUCK, valid=False, stable=True, steps=1)
    assert result["psi_trace"] == [(0, (1, 0, 0, 0)), (1, (0, 1, 0, 0))]


def test_injected_engine_fault() -> None:
    cg = ConstraintGraph()
    cg.add_node(Node("OrderService", Status.KNOWN, "service", 1))
    cg.add_edge(Edge("OrderService", "AuditLog", Modality.REQ, "writes_to"))

    result = resolve(cg, injected_fault=True)
    assert result["status"] == EngineStatus.ENGINE_FAULT, result
    assert result["steps"] == 2, result
    assert result["fault_detail"] and "INJECTED" in result["fault_detail"]


def test_clash_resolution_splits_scc() -> None:
    cg = ConstraintGraph()
    for node_id in ["A", "B", "C", "D"]:
        cg.add_node(Node(node_id, Status.KNOWN, "service", 1))

    cg.add_edge(Edge("A", "B", Modality.REQ, "ab"))
    cg.add_edge(Edge("B", "A", Modality.REQ, "ba"))
    cg.add_edge(Edge("C", "D", Modality.REQ, "cd"))
    cg.add_edge(Edge("D", "C", Modality.REQ, "dc"))
    cg.add_edge(Edge("B", "C", Modality.REQ, "bridge"))
    cg.add_edge(Edge("B", "C", Modality.FORBID, "bridge"))
    cg.add_edge(Edge("D", "A", Modality.REQ, "return"))

    result = resolve(cg)
    assert_terminal(result, EngineStatus.CANONICAL, valid=True, stable=True, steps=3)
    assert [psi for _, psi in result["psi_trace"]] == [
        (0, 0, 16, 1),
        (0, 0, 8, 0),
        (0, 0, 4, 0),
        (0, 0, 0, 0),
    ]


def test_singleton_prohibited_self_loop() -> None:
    assert 1 in ACYCLIC_LAYERS
    cg = ConstraintGraph()
    cg.add_node(Node("A", Status.KNOWN, "service", 1))
    cg.add_edge(Edge("A", "A", Modality.REQ, "recursive"))

    result = resolve(cg)
    assert_terminal(result, EngineStatus.CANONICAL, valid=True, stable=True, steps=1)
    assert result["psi_trace"] == [(0, (0, 0, 1, 0)), (1, (0, 0, 0, 0))]
    assert "A" in result["final_nodes"]
    assert result["final_nodes"]["A"][0] == "KNOWN"
    assert any("node preserved" in line for line in result["log"])


def test_missing_source_is_stuck_not_canonical() -> None:
    cg = ConstraintGraph()
    cg.add_node(Node("Target", Status.KNOWN, "service", 1))
    cg.add_edge(Edge("MissingSource", "Target", Modality.REQ, "calls"))

    result = resolve(cg)
    assert_terminal(result, EngineStatus.STUCK, valid=False, stable=True, steps=0)
    assert any("missing source" in error for error in result["diagnostics"])


def test_unpermitted_orphan_is_stuck() -> None:
    cg = ConstraintGraph()
    cg.add_node(Node("Orphan", Status.KNOWN, "service", 1))

    result = resolve(cg)
    assert_terminal(result, EngineStatus.STUCK, valid=False, stable=True, steps=0)
    assert any("orphan node" in error for error in result["diagnostics"])

    permitted = ConstraintGraph()
    permitted.add_node(Node("PermittedRoot", Status.KNOWN, "service", 1, root_permitted=True))
    permitted_result = resolve(permitted)
    assert_terminal(permitted_result, EngineStatus.CANONICAL, valid=True, stable=True, steps=0)


def test_urgent_promotion_cannot_be_downgraded() -> None:
    worklist = Worklist()
    worklist.push("z", URGENT)
    worklist.push("z", NORMAL)
    worklist.push("a", NORMAL)
    assert worklist.pop() == "z"
    assert worklist.pop() == "a"


def test_composite_identifier_collision_is_safe() -> None:
    cg = ConstraintGraph()
    cg.add_node(Node("A", Status.KNOWN, "service", 1))
    cg.add_node(Node("B", Status.KNOWN, "service", 1))
    cg.add_node(Node("WELD[A|B]", Status.KNOWN, "preexisting", 1, root_permitted=True))
    cg.add_edge(Edge("A", "B", Modality.REQ, "x"))
    cg.add_edge(Edge("B", "A", Modality.REQ, "y"))

    result = resolve(cg)
    assert_terminal(result, EngineStatus.CANONICAL, valid=True, stable=True, steps=1)
    assert "WELD[A|B]" in result["final_nodes"]
    assert "WELD[A|B]#2" in result["final_nodes"]
    assert result["final_nodes"]["WELD[A|B]"][1] == "preexisting"
