"""Loads every JSON file under content/<category>/ into dict-of-dicts keyed by id."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

CONTENT_ROOT = Path(__file__).resolve().parent.parent / "content"

CATEGORIES = (
    "locations", "npcs", "enemies", "techniques",
    "items", "sects", "quests", "events", "realms", "lore",
)


def load_all() -> Dict[str, Dict[str, Any]]:
    world: Dict[str, Dict[str, Any]] = {c: {} for c in CATEGORIES}
    for cat in CATEGORIES:
        folder = CONTENT_ROOT / cat
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Bad JSON in {path}: {e}") from e
            entries = data if isinstance(data, list) else [data]
            for obj in entries:
                if "id" not in obj:
                    raise RuntimeError(f"Missing 'id' in {path}: {obj}")
                if obj["id"] in world[cat]:
                    raise RuntimeError(
                        f"Duplicate id '{obj['id']}' in category '{cat}' "
                        f"(file {path})"
                    )
                world[cat][obj["id"]] = obj
    return world


def stats(world: Dict[str, Dict[str, Any]]) -> str:
    parts = [f"{len(world[c])} {c}" for c in CATEGORIES]
    return ", ".join(parts)
