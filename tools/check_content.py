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

    # 7b. Equipment items: slot must be valid; bonuses must be ints; on_hit
    # effect must be a known combat effect; requires_realm must exist.
    from game.state import EQUIP_SLOTS
    valid_on_hit = {"poison", "bleed", "stun"}
    for iid, it in world["items"].items():
        slot = it.get("slot")
        if slot is not None and slot not in EQUIP_SLOTS:
            errors.append(f"item '{iid}' has invalid slot '{slot}' (expected {EQUIP_SLOTS})")
        for k in ("atk_bonus", "def_bonus", "spd_bonus", "hp_bonus", "on_hit_power"):
            v = it.get(k)
            if v is not None and not isinstance(v, int):
                errors.append(f"item '{iid}' field '{k}' must be an integer, got {type(v).__name__}")
        on_hit = it.get("on_hit_effect")
        if on_hit is not None and on_hit not in valid_on_hit:
            errors.append(f"item '{iid}' on_hit_effect '{on_hit}' not one of {sorted(valid_on_hit)}")
        rr = it.get("requires_realm")
        if rr and rr not in world["realms"]:
            errors.append(f"item '{iid}' requires unknown realm '{rr}'")

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

    # 9. Recipes: crafter NPC exists, inputs/outputs are items, realm gate
    # references a real realm, type is one of the accepted flavor tags.
    valid_recipe_types = {"forge", "brew", "craft"}
    for rid, r in world["recipes"].items():
        rtype = r.get("type")
        if rtype and rtype not in valid_recipe_types:
            errors.append(f"recipe '{rid}' type '{rtype}' not in {sorted(valid_recipe_types)}")
        crafter = r.get("crafter")
        if crafter and crafter not in world["npcs"]:
            errors.append(f"recipe '{rid}' crafter '{crafter}' not an npc")
        output = r.get("output")
        if not output:
            errors.append(f"recipe '{rid}' has no output")
        elif output not in world["items"]:
            errors.append(f"recipe '{rid}' output '{output}' unknown item")
        inputs = r.get("inputs") or {}
        if not isinstance(inputs, dict):
            errors.append(f"recipe '{rid}' inputs must be an object, got {type(inputs).__name__}")
        else:
            for iid, qty in inputs.items():
                if iid not in world["items"]:
                    errors.append(f"recipe '{rid}' input '{iid}' unknown item")
                if not isinstance(qty, int) or qty < 1:
                    errors.append(f"recipe '{rid}' input '{iid}' qty must be positive int")
        rr = r.get("requires_realm")
        if rr and rr not in world["realms"]:
            errors.append(f"recipe '{rid}' requires unknown realm '{rr}'")
        stones = r.get("stones", 0)
        if not isinstance(stones, int) or stones < 0:
            errors.append(f"recipe '{rid}' stones must be non-negative int")

    if errors:
        print(f"{len(errors)} reference error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All references resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
