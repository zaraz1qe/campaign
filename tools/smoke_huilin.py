#!/usr/bin/env python3
"""Scripted smoke-test for the Silent Bell arc (session 14).

Exercises:
  A. Content loads — new items, lore, quests, and events.
  B. Huilin's `gives_quest` is list-valued and includes all three arc ids.
  C. Cracked brass bell is on the ground at the Drowned Willow Shrine.
  D. Wind-named stone is on the ground at the Cragspine Shrine.
  E. Full arc end-to-end: bell → bowl → stone; ACS rep gating; rewards land.
  F. Silent Bell Charm is a real accessory that can be equipped.
  G. Save/load round-trip preserves arc state mid-flight.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game.state import Player


def drive(seed=14):
    random.seed(seed)
    g = Game(IO())
    cap: list[str] = []
    answer_queue: list[str] = []

    def _out(s=""):
        cap.append(str(s))

    def _in(prompt=""):
        cap.append(prompt)
        if answer_queue:
            a = answer_queue.pop(0)
            cap.append(a)
            return a
        cap.append("(no answer queued -> f)")
        return "f"

    g.io = IO(out_func=_out, in_func=_in)

    def say(line):
        cap.append(f"\n>>> {line}")
        g.step(line)

    return g, say, answer_queue, cap


def banner(s):
    print()
    print("=" * 70)
    print(s)
    print("=" * 70)


# ---------------------------------------------------------------------------
banner("A. Huilin arc content loads — items, lore, quests, events")
g, *_ = drive()
for iid in ("cracked_brass_bell", "folded_tea_invitation",
            "wind_named_stone", "silent_bell_charm"):
    assert iid in g.world["items"], f"item '{iid}' missing"
for lid in ("the_bell_that_came_too_late", "the_broken_bridge_tea",
            "the_wind_that_named_itself"):
    assert lid in g.world["lore"], f"lore '{lid}' missing"
for qid in ("the_bell_beneath_the_willow", "a_bowl_on_the_broken_bridge",
            "the_name_the_wind_would_not_give"):
    assert qid in g.world["quests"], f"quest '{qid}' missing"
for evid in ("shrine_bell_surface_breathes", "pavilion_monks_bowl",
             "plateau_wind_holds_its_breath", "cragspine_stone_warms"):
    assert evid in g.world["events"], f"event '{evid}' missing"
print(f"[PASS] All Huilin-arc ids resolve. "
      f"Items={len(g.world['items'])}, lore={len(g.world['lore'])}, "
      f"quests={len(g.world['quests'])}, events={len(g.world['events'])}.")


# ---------------------------------------------------------------------------
banner("B. Huilin's gives_quest is list-valued and owns the full arc")
g, *_ = drive()
huilin = g.world["npcs"]["wandering_monk_huilin"]
gq = huilin.get("gives_quest")
assert isinstance(gq, list), f"gives_quest must be a list; got {gq!r}"
for qid in ("the_bell_beneath_the_willow", "a_bowl_on_the_broken_bridge",
            "the_name_the_wind_would_not_give"):
    assert qid in gq, f"Huilin must own {qid!r} in gives_quest; got {gq!r}"
print(f"[PASS] Huilin owns the 3-quest bell arc as a list giver.")


# ---------------------------------------------------------------------------
banner("C. Cracked brass bell is on the ground at the shrine")
g, say, q, cap = drive()
shrine = g.world["locations"]["drowned_willow_shrine"]
assert "cracked_brass_bell" in (shrine.get("items_on_ground") or []), \
    "cracked_brass_bell must sit on the shrine ground for the player to recover"
# The shrine should ALSO still have the moonflower_bud — the prior Willowmere
# content must not have been overwritten.
assert "moonflower_bud" in (shrine.get("items_on_ground") or []), \
    "moonflower_bud from the existing Drowned Willow quest must still sit here"
# Fast-travel and take it.
g.player.location = "drowned_willow_shrine"
cap.clear()
say("take cracked_brass_bell")
assert g.player.inventory.get("cracked_brass_bell", 0) == 1, \
    "player must be able to pick up the bell"
print("[PASS] Cracked brass bell is takeable at the Drowned Willow Shrine.")


# ---------------------------------------------------------------------------
banner("D. Wind-named stone is on the ground at the Cragspine Shrine")
g, say, q, cap = drive()
cragspine = g.world["locations"]["cragspine_shrine"]
assert "wind_named_stone" in (cragspine.get("items_on_ground") or []), \
    "wind_named_stone must sit at the shrine's altar"
assert "sky_qi_crystal" in (cragspine.get("items_on_ground") or []), \
    "the existing sky_qi_crystal must still be here"
g.player.location = "cragspine_shrine"
cap.clear()
say("take wind_named_stone")
assert g.player.inventory.get("wind_named_stone", 0) == 1
print("[PASS] wind_named_stone is takeable at the Cragspine Shrine.")


# ---------------------------------------------------------------------------
banner("E. Full three-quest arc progresses with rep gating")
g, say, q, cap = drive()
# Move Huilin-adjacent. First talk offers quest 1; quests 2 and 3 are gated
# silent (no prereq complete).
g.player.location = "verdant_bamboo_sea"
g.player.visited.add("verdant_bamboo_sea")
cap.clear()
say("talk wandering_monk_huilin")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Bell Beneath the Willow" in text, \
    f"first talk must offer the bell quest; got {text!r}"
assert "A Bowl on the Broken Bridge" not in text, \
    "chained second quest must stay silent until prereq closes"
assert "The Name the Wind Would Not Give" not in text, \
    "chained third quest must stay silent until prereq closes"

# Fast-path step 1: visit shrine, collect the bell, come back for closing
# talk. offer_quest runs BEFORE progress_quests in cmd_talk, so this talk
# closes quest 1 but does not yet offer quest 2 — the player must talk again.
g.player.location = "drowned_willow_shrine"
g.player.visited.add("drowned_willow_shrine")
cap.clear()
say("take cracked_brass_bell")
g.player.location = "verdant_bamboo_sea"
cap.clear()
say("talk wandering_monk_huilin")
text = "\n".join(cap)
assert "the_bell_beneath_the_willow" in g.player.completed_quests, \
    f"bell quest must close after visit+collect+talk; got {text!r}"
assert "the_bell_that_came_too_late" in g.player.known_lore, \
    "first quest completion must grant 'the bell that came too late' lore"
# Next talk: quest 2 should now auto-offer.
cap.clear()
say("talk wandering_monk_huilin")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] A Bowl on the Broken Bridge" in text, \
    f"second quest must auto-offer on next talk once bell quest closes; got {text!r}"

# Step 2: deliver the folded invitation. Engine is visit-and-talk-based, so
# no quest item exchange is needed; going to the pavilion and talking to
# Baixu satisfies the middle step. Then another talk closes it.
g.player.location = "elder_baixus_pavilion"
g.player.visited.add("elder_baixus_pavilion")
cap.clear()
say("talk elder_baixu")
g.player.location = "verdant_bamboo_sea"
cap.clear()
say("talk wandering_monk_huilin")
text = "\n".join(cap)
assert "a_bowl_on_the_broken_bridge" in g.player.completed_quests, \
    f"bowl quest must close after visit+talk+talk; got {text!r}"
assert "the_broken_bridge_tea" in g.player.known_lore, \
    "second quest completion must grant 'the broken bridge tea' lore"
# ACS rep should have risen by at least 1 from the quest reward.
acs = g.player.reputation.get("azure_cloud_sect", 0)
assert acs >= 1, f"ACS rep must rise to >=1 after bowl quest; got {acs}"

# Quest 3 requires ACS rep +2. With only ACS +1, next talk should keep it
# silent (rep-gated auto-offer).
if acs < 2:
    cap.clear()
    say("talk wandering_monk_huilin")
    text = "\n".join(cap)
    assert "[QUEST ACCEPTED] The Name the Wind Would Not Give" not in text, \
        f"quest 3 must stay rep-gated below ACS+2; got {text!r}"

# Bump rep and retry — third quest should now offer.
g.player.reputation["azure_cloud_sect"] = 2
cap.clear()
say("talk wandering_monk_huilin")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Name the Wind Would Not Give" in text, \
    f"quest 3 must auto-offer at ACS+2; got {text!r}"

# Step 3: go take the stone, come back.
g.player.location = "cragspine_shrine"
g.player.visited.add("cragspine_shrine")
cap.clear()
say("take wind_named_stone")
g.player.location = "verdant_bamboo_sea"
cap.clear()
say("talk wandering_monk_huilin")
assert "the_name_the_wind_would_not_give" in g.player.completed_quests, \
    "third quest must close after visit+collect+talk"
assert "the_wind_that_named_itself" in g.player.known_lore, \
    "third quest completion must grant the capstone lore"
assert g.player.inventory.get("silent_bell_charm", 0) == 1, \
    "third quest completion must award the Silent Bell Charm"
# Capstone quest should have bumped ACS rep by another +1.
assert g.player.reputation.get("azure_cloud_sect", 0) >= 3, \
    f"ACS rep must reach >=3 after capstone; got {g.player.reputation.get('azure_cloud_sect', 0)}"
print("[PASS] Three-quest bell arc completes end-to-end; rep-gates quest 3; "
      "rewards and lore land.")


# ---------------------------------------------------------------------------
banner("F. Silent Bell Charm is equippable")
g, say, q, cap = drive()
g.player.add_item("silent_bell_charm", 1)
cap.clear()
say("equip silent_bell_charm")
text = "\n".join(cap)
assert g.player.equipped.get("accessory") == "silent_bell_charm", \
    f"charm must equip into accessory slot; got {text!r}"
# HP +12, DEF +1, SPD +1.
gb = g.player.gear_bonuses(g.world)
assert gb["hp"] >= 12, f"charm should give HP +12; got {gb}"
assert gb["spd"] >= 1, f"charm should give SPD +1; got {gb}"
assert gb["def"] >= 1, f"charm should give DEF +1; got {gb}"
print(f"[PASS] Silent Bell Charm equips with bonuses: {gb}")


# ---------------------------------------------------------------------------
banner("G. Save/load round-trip preserves arc state")
g, *_ = drive()
g.player.add_item("cracked_brass_bell", 1)
g.player.active_quests["a_bowl_on_the_broken_bridge"] = 1
g.player.known_lore.add("the_bell_that_came_too_late")
g.player.completed_quests.add("the_bell_beneath_the_willow")
g.player.reputation["azure_cloud_sect"] = 1
blob = g.player.to_json()
p2 = Player.from_json(blob)
assert p2.inventory.get("cracked_brass_bell") == 1
assert "a_bowl_on_the_broken_bridge" in p2.active_quests
assert "the_bell_that_came_too_late" in p2.known_lore
assert "the_bell_beneath_the_willow" in p2.completed_quests
assert p2.reputation.get("azure_cloud_sect") == 1
print("[PASS] Save/load preserves bell, bowl, stone, quest and rep state.")


# ---------------------------------------------------------------------------
print()
print("All Huilin Silent Bell arc smoke-tests passed.")
