"""Utilities for loading article helper rules from a shared JSON file."""

from __future__ import annotations

import json
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().with_name("rules_data.json")

with _DATA_PATH.open(encoding="utf-8") as data_file:
    _rules_data = json.load(data_file)

LOOKUP_TABLE = _rules_data["lookup_table"]
DECISION_TREE = _rules_data["decision_tree"]

__all__ = ["LOOKUP_TABLE", "DECISION_TREE"]
