"""Result payload formatting for resolution v3."""

from __future__ import annotations


def report_payload(cg, status, steps: int, trace, valid=None, stable=None, fault_detail: str | None = None) -> dict:
    if valid is None:
        try:
            valid = cg.is_valid()
        except Exception:
            valid = False
    if stable is None:
        stable = False

    try:
        diagnostics = cg.validation_errors()
    except Exception as error:
        diagnostics = [f"diagnostic failure: {type(error).__name__}: {error}"]

    return {
        "status": status,
        "steps": steps,
        "psi_trace": trace,
        "valid": valid,
        "stable": stable,
        "fault_detail": fault_detail,
        "diagnostics": diagnostics,
        "final_nodes": {
            node_id: (node.status.name, node.type, node.layer, node.root_permitted, node.sink_permitted)
            for node_id, node in sorted(cg.nodes.items())
        },
        "final_edges": [(edge.u, edge.v, edge.modality.name, edge.label) for edge in cg.active_edges()],
        "log": list(cg.log),
    }
