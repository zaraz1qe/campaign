#!/usr/bin/env python3
"""Validate all content. Run me before committing new content."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game import loader  # noqa: E402


def main() -> int:
    try:
        world = loader.load_all()
    except Exception as e:
        print(f"FAIL: {e}")
        return 1

    print("Loaded OK:")
    for cat in loader.CATEGORIES:
        print(f"  {len(world[cat]):4d}  {cat}")
    print()

    errors: list[str] = []

    # 1. Every location's exits should point to known locations.
    locs = world["locations"]
    for lid, loc in locs.items():
        for d, target in (loc.get("exits") or {}).items():
            if target not in locs:
                errors.append(f"location '{lid}' exit '{d}' -> unknown '{target}'")

    # 2. Every npc/enemy/event/item id referenced by a location should exist.
    def _check_refs(loc_field: str, world_cat: str) -> None:
        for lid, loc in locs.items():
            for ref in (loc.get(loc_field) or []):
                if ref not in world[world_cat]:
                    errors.append(f"location '{lid}' {loc_field} -> unknown {world_cat[:-1]} '{ref}'")
    _check_refs("npcs", "npcs")
    _check_refs("enemies", "enemies")
    _check_refs("events", "events")
    _check_refs("items_on_ground", "items")

    # 3. NPC techniques/items/quests should exist.
    for nid, n in world["npcs"].items():
        for tid in (n.get("teaches") or []):
            if tid not in world["techniques"]:
                errors.append(f"npc '{nid}' teaches unknown technique '{tid}'")
        for iid in (n.get("sells") or []):
            if iid not in world["items"]:
                errors.append(f"npc '{nid}' sells unknown item '{iid}'")
        if n.get("gives_quest") and n["gives_quest"] not in world["quests"]:
            errors.append(f"npc '{nid}' gives unknown quest '{n['gives_quest']}'")

    # 4. Enemy drops should reference real items, techniques exist.
    for eid, e in world["enemies"].items():
        for drop in e.get("drops") or []:
            if drop.get("item") and drop["item"] not in world["items"]:
                errors.append(f"enemy '{eid}' drops unknown item '{drop['item']}'")
        for tid in e.get("techniques") or []:
            if tid not in world["techniques"]:
                errors.append(f"enemy '{eid}' uses unknown technique '{tid}'")

    # 5. Quest steps reference real things, rewards reference real items.
    for qid, q in world["quests"].items():
        for i, step in enumerate(q.get("steps") or []):
            t = step.get("type")
            tgt = step.get("target")
            cat = {"visit": "locations", "defeat": "enemies",
                   "talk": "npcs", "collect": "items"}.get(t)
            if cat is None:
                errors.append(f"quest '{qid}' step {i} unknown type '{t}'")
            elif tgt not in world[cat]:
                errors.append(f"quest '{qid}' step {i} target '{tgt}' not in {cat}")
        for iid in (q.get("reward", {}).get("items") or []):
            if iid not in world["items"]:
                errors.append(f"quest '{qid}' reward item '{iid}' unknown")

    # 6. Event referenced location exists; lore/item effects reference real ids.
    for evid, ev in world["events"].items():
        if ev.get("location") and ev["location"] not in locs:
            errors.append(f"event '{evid}' location '{ev['location']}' unknown")
        eff = ev.get("effect") or {}
        if eff.get("item") and eff["item"] not in world["items"]:
            errors.append(f"event '{evid}' grants unknown item '{eff['item']}'")
        if eff.get("lore") and eff["lore"] not in world["lore"]:
            errors.append(f"event '{evid}' grants unknown lore '{eff['lore']}'")

    # 7. Techniques requires_realm should exist (or be empty/'mortal').
    for tid, t in world["techniques"].items():
        rr = t.get("requires_realm")
        if rr and rr not in world["realms"]:
            errors.append(f"technique '{tid}' requires unknown realm '{rr}'")

    # 8. Sect references.
    for sid, s in world["sects"].items():
        for tid in s.get("signature_techniques") or []:
            if tid not in world["techniques"]:
                errors.append(f"sect '{sid}' signature technique '{tid}' unknown")
        for nid in s.get("elders") or []:
            if nid not in world["npcs"]:
                errors.append(f"sect '{sid}' elder '{nid}' unknown")
        if s.get("headquarters") and s["headquarters"] not in locs:
            errors.append(f"sect '{sid}' headquarters '{s['headquarters']}' unknown")

    if errors:
        print(f"{len(errors)} reference error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All references resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
