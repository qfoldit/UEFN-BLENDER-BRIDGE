"""qFoldIT clean-room adapter boundary from UAG to Blender/UEFN assets."""

from dataclasses import dataclass
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
            "properties": dict(sorted(node.properties.items())),
        }
        for node in nodes
    ]
