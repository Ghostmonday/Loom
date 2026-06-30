"""Core data types for the Loom constraint resolution engine v3."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class Modality(Enum):
    REQ = auto()
    FORBID = auto()
    PARTIAL = auto()


class Status(Enum):
    KNOWN = auto()
    LATENT_UNRESOLVED = auto()
    REJECTED = auto()


class Provenance(Enum):
    EXPLICIT = auto()
    INFERRED = auto()
    LLM_PROPOSED = auto()


class EngineStatus(Enum):
    CANONICAL = auto()
    STUCK = auto()
    ENGINE_FAULT = auto()


@dataclass
class Node:
    id: str
    status: Status
    type: str | None = None
    layer: int | None = None
    domain: set[str] = field(default_factory=set)
    root_permitted: bool = False
    sink_permitted: bool = False


@dataclass
class Edge:
    u: str
    v: str
    modality: Modality
    label: str
    provenance: Provenance = Provenance.EXPLICIT
    active: bool = True


LABEL_TYPE_DOMAIN: dict[str, set[str]] = {
    "writes_to": {"log_sink"},
    "calls": {"service"},
    "calls_back": {"service"},
    "flushes_to": {"service", "log_sink"},
}

ACYCLIC_LAYERS = {1}
