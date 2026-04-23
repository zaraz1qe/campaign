#!/usr/bin/env python3
"""Scripted smoke-test for the Bitter Remedy arc (Weilan, session 15).

Exercises:
  A. Content loads — Weilan-arc items, lore, quests, and events.
  B. Weilan's gives_quest is list-valued and owns all three arc ids.
  C. Pale Lake Silt is on the ground at Pale Lake Shore.
  D. Sealed Blood-Lotus is on the ground at Crimson Creek.
  E. Full arc end-to-end: silt -> sealed bud -> the sister's pestle;
     quest 3 gates on Scarlet Lotus rep +3; rewards land; cross-sect rep
     bump to Azure Cloud fires on the capstone.
  F. The Red Pestle's Sister-Spoon is equippable with claimed bonuses.
  G. Save/load round-trip preserves Weilan-arc state mid-flight.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game.state import Player


def drive(seed=15):
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
banner("A. Weilan arc content loads — items, lore, quests, events")
g, *_ = drive()
for iid in ("pale_lake_silt", "sealed_blood_lotus",
            "moon_red_pill", "sisters_iron_spoon"):
    assert iid in g.world["items"], f"item '{iid}' missing"
for lid in ("the_pond_that_sleeps", "the_red_that_does_not_clot",
            "the_pestle_unbroken", "the_sisters_unspoken_cure"):
    assert lid in g.world["lore"], f"lore '{lid}' missing"
for qid in ("a_cup_of_sleeping_water", "the_bud_that_will_not_open",
            "the_pestle_my_sister_used_last"):
    assert qid in g.world["quests"], f"quest '{qid}' missing"
for evid in ("pale_lake_silt_stirs", "sealed_bud_under_the_bell",
             "weilan_hums_at_the_pestle"):
    assert evid in g.world["events"], f"event '{evid}' missing"
print(f"[PASS] All Weilan-arc ids resolve. "
      f"Items={len(g.world['items'])}, lore={len(g.world['lore'])}, "
      f"quests={len(g.world['quests'])}, events={len(g.world['events'])}.")


# ---------------------------------------------------------------------------
banner("B. Weilan's gives_quest is list-valued and owns the full arc")
g, *_ = drive()
w = g.world["npcs"]["apothecary_weilan"]
gq = w.get("gives_quest")
assert isinstance(gq, list), f"gives_quest must be a list; got {gq!r}"
for qid in ("a_cup_of_sleeping_water", "the_bud_that_will_not_open",
            "the_pestle_my_sister_used_last"):
    assert qid in gq, f"Weilan must own {qid!r}; got {gq!r}"
# He should still teach at least his original technique.
assert "crimson_tide_fist" in w.get("teaches", []), \
    "Weilan's existing teach must not be lost on deepening"
# And his new healing teaches should be there.
assert "calming_breath" in w.get("teaches", []), \
    "Weilan should now teach calming_breath for mortal players"
# Mortal-tier sell should be present so new players have a reason to visit.
assert "minor_healing_pill" in w.get("sells", []), \
    "Weilan should sell minor_healing_pill for mortal players"
print(f"[PASS] Weilan owns the 3-quest Bitter Remedy arc; teaches+sells expanded.")


# ---------------------------------------------------------------------------
banner("C. Pale Lake Silt is on the ground at Pale Lake Shore")
g, say, q, cap = drive()
pls = g.world["locations"]["pale_lake_shore"]
assert "pale_lake_silt" in (pls.get("items_on_ground") or []), \
    "pale_lake_silt must sit on the Pale Lake Shore ground"
# Shouldn't have trampled the existing ground state (which is empty, but confirm
# by checking events still carry the prior atmospheric piece).
assert "lake_surface_shivers" in (pls.get("events") or []), \
    "prior Pale Lake atmospheric event must remain"
# Fast-travel and take it.
g.player.location = "pale_lake_shore"
cap.clear()
say("take pale_lake_silt")
assert g.player.inventory.get("pale_lake_silt", 0) == 1, \
    "player must be able to pick up the silt"
print("[PASS] Pale Lake Silt is takeable at Pale Lake Shore.")


# ---------------------------------------------------------------------------
banner("D. Sealed Blood-Lotus is on the ground at Crimson Creek")
g, say, q, cap = drive()
cc = g.world["locations"]["crimson_creek"]
assert "sealed_blood_lotus" in (cc.get("items_on_ground") or []), \
    "sealed_blood_lotus must sit at Crimson Creek"
# Prior atmospheric event must not have been overwritten.
assert "crimson_wind_carries_chanting" in (cc.get("events") or []), \
    "prior Crimson Creek atmospheric event must remain"
g.player.location = "crimson_creek"
cap.clear()
say("take sealed_blood_lotus")
assert g.player.inventory.get("sealed_blood_lotus", 0) == 1
print("[PASS] Sealed Blood-Lotus is takeable at Crimson Creek.")


# ---------------------------------------------------------------------------
banner("E. Full three-quest arc progresses with Scarlet Lotus rep gate")
g, say, q, cap = drive()
# Move to the shrine. First talk offers quest 1; quests 2 and 3 stay silent.
g.player.location = "scarlet_lotus_shrine"
g.player.visited.add("scarlet_lotus_shrine")
cap.clear()
say("talk apothecary_weilan")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] A Cup of Sleeping Water" in text, \
    f"first talk must offer the silt quest; got {text!r}"
assert "The Bud That Will Not Open" not in text, \
    "chained second quest must stay silent before quest 1 closes"
assert "The Pestle My Sister Used Last" not in text, \
    "chained third quest must stay silent before prereq + rep gate"

# Quest 1: visit Pale Lake, collect the silt, return and talk. offer_quest runs
# BEFORE progress_quests in cmd_talk, so this close-talk does not yet offer
# quest 2 — the player must talk again.
g.player.location = "pale_lake_shore"
g.player.visited.add("pale_lake_shore")
cap.clear()
say("take pale_lake_silt")
g.player.location = "scarlet_lotus_shrine"
cap.clear()
say("talk apothecary_weilan")
assert "a_cup_of_sleeping_water" in g.player.completed_quests, \
    "silt quest must close after visit+collect+talk"
assert "the_pond_that_sleeps" in g.player.known_lore, \
    "quest 1 completion must grant 'the pond that sleeps' lore"
slp = g.player.reputation.get("scarlet_lotus_pavilion", 0)
assert slp >= 1, f"quest 1 must grant Scarlet Lotus rep +1; got {slp}"

# Next talk: quest 2 should auto-offer.
cap.clear()
say("talk apothecary_weilan")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Bud That Will Not Open" in text, \
    f"quest 2 must auto-offer on next talk; got {text!r}"

# Quest 2: visit Crimson Creek, collect the sealed bud, return and talk.
g.player.location = "crimson_creek"
g.player.visited.add("crimson_creek")
cap.clear()
say("take sealed_blood_lotus")
g.player.location = "scarlet_lotus_shrine"
cap.clear()
say("talk apothecary_weilan")
assert "the_bud_that_will_not_open" in g.player.completed_quests, \
    "quest 2 must close after visit+collect+talk"
assert "the_red_that_does_not_clot" in g.player.known_lore, \
    "quest 2 must grant 'the red that does not clot' lore"
# Moon-red pill should have landed.
assert g.player.inventory.get("moon_red_pill", 0) >= 1, \
    "quest 2 completion must award the Moon-Red Pill"
slp = g.player.reputation.get("scarlet_lotus_pavilion", 0)
assert slp >= 2, f"SLP rep must rise to >=2 after quest 2; got {slp}"

# Quest 3 gates on SLP +3. With only +2, next talk must NOT offer it.
if slp < 3:
    cap.clear()
    say("talk apothecary_weilan")
    text = "\n".join(cap)
    assert "[QUEST ACCEPTED] The Pestle My Sister Used Last" not in text, \
        f"quest 3 must stay rep-gated below SLP+3; got {text!r}"

# Bump rep and retry — quest 3 should now offer.
g.player.reputation["scarlet_lotus_pavilion"] = 3
cap.clear()
say("talk apothecary_weilan")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Pestle My Sister Used Last" in text, \
    f"quest 3 must auto-offer at SLP+3; got {text!r}"

# Quest 3: visit Baixu, talk to him, come back, talk to Weilan.
g.player.location = "elder_baixus_pavilion"
g.player.visited.add("elder_baixus_pavilion")
cap.clear()
say("talk elder_baixu")
g.player.location = "scarlet_lotus_shrine"
cap.clear()
say("talk apothecary_weilan")
assert "the_pestle_my_sister_used_last" in g.player.completed_quests, \
    "quest 3 must close after visit Baixu + talk Baixu + talk Weilan"
assert "the_pestle_unbroken" in g.player.known_lore, \
    "capstone must grant 'the pestle unbroken' lore"
assert "the_sisters_unspoken_cure" in g.player.known_lore, \
    "capstone must grant 'the sister's unspoken cure' lore"
# Reward item
assert g.player.inventory.get("sisters_iron_spoon", 0) == 1, \
    "capstone must award The Red Pestle's Sister-Spoon"
# Cross-sect rep bump: the quest grants Azure Cloud +2, the narrative hinge.
acs = g.player.reputation.get("azure_cloud_sect", 0)
assert acs >= 2, f"capstone must grant Azure Cloud rep +2 (cross-sect); got {acs}"
# And a further Scarlet Lotus +1.
slp = g.player.reputation.get("scarlet_lotus_pavilion", 0)
assert slp >= 4, f"capstone must grant SLP +1 on top of gate; got {slp}"
print("[PASS] Three-quest Bitter Remedy arc completes end-to-end; rep-gates "
      "quest 3 at SLP+3; cross-sect Azure Cloud rep +2 fires on capstone.")


# ---------------------------------------------------------------------------
banner("F. The Red Pestle's Sister-Spoon is equippable")
g, say, q, cap = drive()
g.player.add_item("sisters_iron_spoon", 1)
cap.clear()
say("equip sisters_iron_spoon")
text = "\n".join(cap)
assert g.player.equipped.get("accessory") == "sisters_iron_spoon", \
    f"spoon must equip into accessory slot; got {text!r}"
gb = g.player.gear_bonuses(g.world)
assert gb["hp"] >= 14, f"spoon should grant HP +14; got {gb}"
assert gb["def"] >= 2, f"spoon should grant DEF +2; got {gb}"
assert gb["spd"] >= 1, f"spoon should grant SPD +1; got {gb}"
print(f"[PASS] Sister-Spoon equips with bonuses: {gb}")


# ---------------------------------------------------------------------------
banner("G. Save/load round-trip preserves Weilan-arc state")
g, *_ = drive()
g.player.add_item("pale_lake_silt", 1)
g.player.add_item("sealed_blood_lotus", 1)
g.player.active_quests["the_bud_that_will_not_open"] = 1
g.player.known_lore.add("the_pond_that_sleeps")
g.player.completed_quests.add("a_cup_of_sleeping_water")
g.player.reputation["scarlet_lotus_pavilion"] = 2
blob = g.player.to_json()
p2 = Player.from_json(blob)
assert p2.inventory.get("pale_lake_silt") == 1
assert p2.inventory.get("sealed_blood_lotus") == 1
assert "the_bud_that_will_not_open" in p2.active_quests
assert "the_pond_that_sleeps" in p2.known_lore
assert "a_cup_of_sleeping_water" in p2.completed_quests
assert p2.reputation.get("scarlet_lotus_pavilion") == 2
print("[PASS] Save/load preserves silt, sealed-bud, quest, lore and rep state.")


# ---------------------------------------------------------------------------
print()
print("All Weilan Bitter Remedy arc smoke-tests passed.")
