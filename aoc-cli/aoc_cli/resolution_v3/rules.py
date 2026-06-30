"""Deterministic resolution rules A1, A2/D1, B1, and B2."""

from __future__ import annotations

from aoc_cli.resolution_v3.model import LABEL_TYPE_DOMAIN, Modality, Node, Status
from aoc_cli.resolution_v3.worklist import NORMAL, URGENT


def check_a1(cg, locus: str):
    if not locus.startswith("edge:"):
        return None
    edge = cg.edges[int(locus.split(":", 1)[1])]
    if edge.active and edge.modality == Modality.REQ and edge.v not in cg.nodes:
        return ("A1", edge)
    return None


def check_a2_d1(cg, locus: str):
    node = cg.nodes.get(locus)
    if node and node.status == Status.LATENT_UNRESOLVED and len(node.domain) == 1:
        return ("A2_D1", node)
    return None


def check_b1(cg, locus: str):
    if not locus.startswith("edge:"):
        return None
    index = int(locus.split(":", 1)[1])
    required = cg.edges[index]
    if not (required.active and required.modality == Modality.REQ):
        return None

    candidates = cg.watch.edges_touching(required.u) & cg.watch.edges_touching(required.v)
    for candidate_index in sorted(candidates):
        forbidden = cg.edges[candidate_index]
        if (
            forbidden.active
            and forbidden.modality == Modality.FORBID
            and forbidden.u == required.u
            and forbidden.v == required.v
            and forbidden.label == required.label
        ):
            return ("B1", (required, forbidden))
    return None


def applicable_rule(cg, locus: str):
    return check_a1(cg, locus) or check_a2_d1(cg, locus) or check_b1(cg, locus)


def apply_a1(cg, worklist, edge) -> None:
    domain = set(LABEL_TYPE_DOMAIN.get(edge.label, set()))
    cg.add_node(Node(id=edge.v, status=Status.LATENT_UNRESOLVED, domain=domain))
    cg.log.append(
        f"[A1] introduced latent node '{edge.v}' "
        f"(required by {edge.u} -[{edge.label}]-> {edge.v}); "
        f"seeded domain={domain or '{unconstrained}'}"
    )
    worklist.push(edge.v, NORMAL)


def apply_a2_d1(cg, worklist, node) -> None:
    node.type = next(iter(node.domain))
    node.layer = 1
    node.status = Status.KNOWN
    cg.log.append(f"[A2->D1] instantiated '{node.id}' as type={node.type}, layer={node.layer}")

    for edge_index in sorted(cg.watch.edges_touching(node.id)):
        edge = cg.edges[edge_index]
        worklist.push(f"edge:{edge_index}", NORMAL)
        worklist.push(edge.u, NORMAL)
        worklist.push(edge.v, NORMAL)


def apply_b1(cg, worklist, required, forbidden) -> None:
    del forbidden
    required.active = False
    cg.log.append(
        f"[B1] clash on {required.u}->{required.v} '{required.label}' "
        "REQ vs FORBID; priority rule 5: FORBID wins -> REQ edge deactivated"
    )
    worklist.push(required.u, NORMAL)
    worklist.push(required.v, NORMAL)


def apply_b2(cg, worklist) -> bool:
    violating = cg.find_violating_sccs()
    if not violating:
        return False

    scc = violating[0]
    members = sorted(scc)

    if len(members) == 1:
        _remove_singleton_self_loop(cg, worklist, members[0])
        return True

    composite_id = cg.allocate_composite_id(members)
    composite_layer = min(cg.nodes[member].layer for member in members if cg.nodes[member].layer is not None)

    external_in_req = any(
        edge.active and edge.modality == Modality.REQ and edge.v in scc and edge.u not in scc for edge in cg.edges
    )
    external_out_req = any(
        edge.active and edge.modality == Modality.REQ and edge.u in scc and edge.v not in scc for edge in cg.edges
    )
    inherited_root = any(cg.nodes[member].root_permitted for member in members)
    inherited_sink = any(cg.nodes[member].sink_permitted for member in members)

    touched_indices: set[int] = set()
    for index, edge in enumerate(cg.edges):
        changed = False
        if edge.u in scc:
            edge.u = composite_id
            changed = True
        if edge.v in scc:
            edge.v = composite_id
            changed = True
        if changed:
            touched_indices.add(index)

    for index in touched_indices:
        edge = cg.edges[index]
        if edge.active and edge.u == composite_id and edge.v == composite_id:
            edge.active = False

    for member in members:
        del cg.nodes[member]

    cg.add_node(
        Node(
            id=composite_id,
            status=Status.KNOWN,
            type="composite",
            layer=composite_layer,
            root_permitted=inherited_root or not external_in_req,
            sink_permitted=inherited_sink or not external_out_req,
        )
    )

    cg.watch.rebuild()
    cg.log.append(f"[B2] welded SCC {members} (size={len(members)}) into '{composite_id}'")

    worklist.push(composite_id, URGENT)
    for index in sorted(touched_indices):
        if cg.edges[index].active:
            worklist.push(f"edge:{index}", URGENT)
    return True


def _remove_singleton_self_loop(cg, worklist, node_id: str) -> None:
    deactivated: list[int] = []
    for index, edge in enumerate(cg.edges):
        if edge.active and edge.modality == Modality.REQ and edge.u == node_id and edge.v == node_id:
            edge.active = False
            deactivated.append(index)

    if not deactivated:
        raise RuntimeError(f"violating singleton SCC '{node_id}' had no active REQ self-loop")

    node = cg.nodes[node_id]
    node.root_permitted = True
    node.sink_permitted = True
    cg.log.append(
        f"[B2-self] removed prohibited REQ self-loop(s) {deactivated} "
        f"from '{node_id}'; node preserved and tagged ROOT/SINK_PERMITTED"
    )
    worklist.push(node_id, URGENT)
