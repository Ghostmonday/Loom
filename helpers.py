def _create_initial_work_units(
    blocks: Iterable[frozenset[str]],
    nodes: Mapping[str, Mapping[str, Any]],
    node_risks: Mapping[str, str],
    giv_profile: GIV,
    graph: Mapping[str, Any],
) -> list[WorkUnit]:
    work_units: list[WorkUnit] = []
    grouped: dict[tuple[str, str, str], list[str]] = {}

    for block in blocks:
        if len(block) > 1:
            paths = tuple(sorted(block))
            work_units.append(_dark_bridge_block_work_unit(len(work_units) + 1, paths, giv_profile, node_risks))
            continue
        path = sorted(block)[0]
        node = nodes[path]
        key = (_directory(path), str(node.get("language") or "unknown"), node_risks[path])
        grouped.setdefault(key, []).append(path)

    for key, paths_list in _refine_grouped_blocks(grouped, graph):
        directory, language, risk = key
        paths = tuple(sorted(paths_list))
        work_units.append(_group_work_unit(len(work_units) + 1, directory, language, risk, paths, giv_profile))

    return work_units


def _build_blueprint_assumptions(
    gateway_mode: bool,
    serialization_events: list[tuple[str, str]],
) -> list[str]:
    from .helpers.stealth import dark_bridge_blueprint_assumption, stealth_mode

    if gateway_mode:
        geometry_assumption = (
            "Handoff gateway mode: dark-bridge couplings are HANDOFF_ONLY transaction boundaries, not atomic welds."
        )
    elif stealth_mode():
        geometry_assumption = (
            "Negative-curvature coupling welds are consolidated into atomic work units before parallel dispatch."
        )
    else:
        geometry_assumption = "Dark Bridge endpoints below the curvature hard floor are bound into atomic work units."

    assumptions = [
        "Work units are generated from the scanned graph, integrity preflight, and scope lock.",
        "Allowed paths are write scopes; workers may read broader project context as needed.",
        geometry_assumption,
    ]
    binding_note = dark_bridge_blueprint_assumption(len(serialization_events))
    if binding_note and not gateway_mode:
        assumptions.append(binding_note)

    return assumptions
