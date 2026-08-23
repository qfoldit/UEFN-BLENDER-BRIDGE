"""qFoldIT clean-room adapter boundary from UAG to Blender/UEFN assets."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any


@dataclass(frozen=True)
class UAGNode:
    node_id: str
    object_type: str
    transform: tuple[float, float, float, float, float, float, float]
    properties: dict[str, Any]


def validate_node(node: UAGNode) -> None:
    """Reject malformed visualization nodes before asset generation."""
    if not node.node_id:
        raise ValueError("UAG node_id cannot be empty")
    if len(node.transform) != 7:
        raise ValueError("UAG transform must contain location(3), rotation(3), scale(1)")
    if not node.object_type:
        raise ValueError("UAG object_type cannot be empty")


def build_visual_projection(nodes: list[UAGNode]) -> list[dict[str, Any]]:
    """Create a deterministic visualization projection; never modifies scientific truth."""
    for node in nodes:
        validate_node(node)
    return [
        {
            "id": node.node_id,
            "type": node.object_type,
            "transform": list(node.transform),
            "properties": {key: node.properties[key] for key in sorted(node.properties)},
        }
        for node in sorted(nodes, key=lambda item: item.node_id)
    ]


def projection_hash(projection: list[dict[str, Any]]) -> str:
    """Return a stable hash for deterministic asset/projection provenance."""
    canonical = json.dumps(projection, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def build_manifest(nodes: list[UAGNode], *, schema_version: str) -> dict[str, Any]:
    """Build a provenance-aware visualization manifest from canonical UAG data."""
    projection = build_visual_projection(nodes)
    return {
        "schema_version": schema_version,
        "projection": projection,
        "projection_hash": projection_hash(projection),
        "authority": "qFoldIT_UAG",
        "scientific_truth_mutable_here": False,
    }
