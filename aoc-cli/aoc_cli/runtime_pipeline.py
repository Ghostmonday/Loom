"""Minimal deterministic runtime pipeline built on resolution v3."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from aoc_cli.resolution_v3 import ConstraintGraph, Edge, EngineStatus, Modality, Node, Status, resolve


class RuntimePipelineError(ValueError):
    """Raised when runtime pipeline input is incomplete or unsupported."""


def run_pipeline(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Run input -> graph -> resolution -> units -> mock execution -> result."""
    normalized_input = _normalize_input(payload)
    graph = build_constraint_graph(normalized_input)
    resolution = resolve(graph)
    units = derive_work_units(resolution)
    executions = execute_units(units) if resolution["status"] == EngineStatus.CANONICAL else []

    return {
        "pipeline_status": "COMPLETED" if resolution["status"] == EngineStatus.CANONICAL else "BLOCKED",
        "input_digest": _digest(normalized_input),
        "resolution": _serializable_resolution(resolution),
        "work_units": units,
        "executions": executions,
        "valid": resolution["valid"],
        "stable": resolution["stable"],
        "diagnostics": list(resolution["diagnostics"]),
    }


def build_constraint_graph(payload: Mapping[str, Any]) -> ConstraintGraph:
    """Build a constraint graph from the minimal runtime input format."""
    graph = ConstraintGraph()
    for raw_node in payload["nodes"]:
        graph.add_node(_node_from_payload(raw_node))
    for raw_edge in payload["edges"]:
        graph.add_edge(_edge_from_payload(raw_edge))
    return graph


def derive_work_units(resolution: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Extract one deterministic mock-executable unit per known final node."""
    if resolution["status"] != EngineStatus.CANONICAL:
        return []

    units: list[dict[str, Any]] = []
    final_nodes = resolution["final_nodes"]
    for node_id in sorted(final_nodes):
        status, node_type, layer, root_permitted, sink_permitted = final_nodes[node_id]
        if status != Status.KNOWN.name:
            continue
        units.append(
            {
                "id": _unit_id(node_id),
                "node_id": node_id,
                "node_type": node_type,
                "layer": layer,
                "root_permitted": root_permitted,
                "sink_permitted": sink_permitted,
            }
        )
    return units


def execute_units(units: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Run the minimal deterministic executor."""
    outputs: list[dict[str, str]] = []
    for unit in sorted(units, key=lambda item: str(item["id"])):
        unit_id = str(unit["id"])
        node_id = str(unit["node_id"])
        outputs.append(
            {
                "unit_id": unit_id,
                "status": "EXECUTED",
                "output": f"mock-executed:{unit_id}:{node_id}",
            }
        )
    return outputs


def _normalize_input(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise RuntimePipelineError("pipeline input must be a JSON object")

    nodes = _required_list(payload, "nodes")
    edges = _required_list(payload, "edges")
    normalized_nodes = sorted((_normalize_node(item) for item in nodes), key=lambda item: item["id"])
    normalized_edges = sorted(
        (_normalize_edge(item) for item in edges),
        key=lambda item: (item["u"], item["v"], item["modality"], item["label"]),
    )
    return {
        "intent": _optional_text(payload, "intent"),
        "nodes": normalized_nodes,
        "edges": normalized_edges,
    }


def _normalize_node(raw_node: Any) -> dict[str, Any]:
    if not isinstance(raw_node, Mapping):
        raise RuntimePipelineError("each node must be a JSON object")
    node_id = _required_text(raw_node, "id")
    status = _required_enum(raw_node, "status", Status)

    normalized: dict[str, Any] = {"id": node_id, "status": status.name}
    if status == Status.KNOWN:
        normalized["type"] = _required_text(raw_node, "type")
        normalized["layer"] = _required_int(raw_node, "layer")
    else:
        normalized["type"] = _optional_text(raw_node, "type") or None
        normalized["layer"] = _optional_int(raw_node, "layer")
    normalized["domain"] = sorted(_domain(raw_node, status))
    normalized["root_permitted"] = _required_bool(raw_node, "root_permitted")
    normalized["sink_permitted"] = _required_bool(raw_node, "sink_permitted")
    return normalized


def _normalize_edge(raw_edge: Any) -> dict[str, str]:
    if not isinstance(raw_edge, Mapping):
        raise RuntimePipelineError("each edge must be a JSON object")
    return {
        "u": _required_text(raw_edge, "u"),
        "v": _required_text(raw_edge, "v"),
        "modality": _required_enum(raw_edge, "modality", Modality).name,
        "label": _required_text(raw_edge, "label"),
    }


def _node_from_payload(raw_node: Mapping[str, Any]) -> Node:
    return Node(
        id=str(raw_node["id"]),
        status=Status[str(raw_node["status"])],
        type=raw_node["type"],
        layer=raw_node["layer"],
        domain=set(raw_node["domain"]),
        root_permitted=bool(raw_node["root_permitted"]),
        sink_permitted=bool(raw_node["sink_permitted"]),
    )


def _edge_from_payload(raw_edge: Mapping[str, str]) -> Edge:
    return Edge(
        u=raw_edge["u"],
        v=raw_edge["v"],
        modality=Modality[raw_edge["modality"]],
        label=raw_edge["label"],
    )


def _serializable_resolution(resolution: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": resolution["status"].name,
        "steps": resolution["steps"],
        "psi_trace": [[step, list(psi)] for step, psi in resolution["psi_trace"]],
        "valid": resolution["valid"],
        "stable": resolution["stable"],
        "fault_detail": resolution["fault_detail"],
        "diagnostics": list(resolution["diagnostics"]),
        "final_nodes": {
            node_id: list(values)
            for node_id, values in sorted(resolution["final_nodes"].items(), key=lambda item: item[0])
        },
        "final_edges": [list(edge) for edge in resolution["final_edges"]],
        "log": list(resolution["log"]),
    }


def _digest(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _unit_id(node_id: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in node_id).strip("-")
    return "WU-" + (normalized or hashlib.sha256(node_id.encode("utf-8")).hexdigest()[:8])


def _required_list(payload: Mapping[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise RuntimePipelineError(f"{key} must be a list")
    return value


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimePipelineError(f"{key} is required")
    return value.strip()


def _optional_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise RuntimePipelineError(f"{key} must be text")
    return value.strip()


def _required_int(payload: Mapping[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise RuntimePipelineError(f"{key} must be an integer")
    return value


def _optional_int(payload: Mapping[str, Any], key: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise RuntimePipelineError(f"{key} must be an integer")
    return value


def _required_bool(payload: Mapping[str, Any], key: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise RuntimePipelineError(f"{key} must be a boolean")
    return value


def _domain(payload: Mapping[str, Any], status: Status) -> set[str]:
    if "domain" not in payload:
        if status == Status.KNOWN:
            return set()
        raise RuntimePipelineError("domain is required for non-KNOWN nodes")
    return _text_set(payload, "domain")


def _text_set(payload: Mapping[str, Any], key: str) -> set[str]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise RuntimePipelineError(f"{key} must be a list")
    return {_text_item(item, key) for item in value}


def _text_item(value: Any, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimePipelineError(f"{key} entries must be non-empty text")
    return value.strip()


def _required_enum(payload: Mapping[str, Any], key: str, enum_type):
    value = _required_text(payload, key).upper()
    try:
        return enum_type[value]
    except KeyError as error:
        choices = ", ".join(sorted(enum_type.__members__))
        raise RuntimePipelineError(f"{key} must be one of: {choices}") from error
