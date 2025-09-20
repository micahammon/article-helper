"""Utilities for loading article helper rules from a shared JSON file."""

from __future__ import annotations

import json
from pathlib import Path

GUIDANCE_NODE_TYPE = "guidance"
_GUIDANCE_SENTINEL = "GUIDANCE"


def _normalize_guidance_nodes(decision_tree):
    """Ensure guidance-only nodes share a consistent structure."""

    for node in decision_tree.values():
        if not isinstance(node, dict):
            continue

        node_type = node.get("type")
        article_value = node.get("article")

        # If the node is already marked as guidance, force ``article`` to ``None``.
        if node_type == GUIDANCE_NODE_TYPE:
            if article_value is not None:
                node["article"] = None
            continue

        # Older datasets used a sentinel string in the ``article`` slot. Convert them.
        if isinstance(article_value, str) and article_value.upper() == _GUIDANCE_SENTINEL:
            node["type"] = GUIDANCE_NODE_TYPE
            node["article"] = None


_DATA_PATH = Path(__file__).resolve().with_name("rules_data.json")

with _DATA_PATH.open(encoding="utf-8") as data_file:
    _rules_data = json.load(data_file)

decision_tree = _rules_data["decision_tree"]
_normalize_guidance_nodes(decision_tree)

LOOKUP_TABLE = _rules_data["lookup_table"]
DECISION_TREE = decision_tree

__all__ = ["LOOKUP_TABLE", "DECISION_TREE", "GUIDANCE_NODE_TYPE"]
