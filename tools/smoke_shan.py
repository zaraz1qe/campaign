#!/usr/bin/env python3
"""Scripted smoke-test for the Grey That Does Not Lie arc (Shan, session 19).

Exercises:
  A. Content loads — Shan-arc items, lore, quests, events.
  B. Shan's gives_quest is list-valued, leads with oath_of_fangs,
     and appends the three new arc quests.
  C. Bloodmarked cloth sits on the ground at Merchant's Crossing.
  D. Hundred-grass sits on the ground at the Poisoner's Garden.
  E. Full arc end-to-end: oath_of_fangs prereq → honest venom → sword
     that would not strike → hand that empties the heart; FPS+3 gate
     on quest 3; cross-sect rep deltas land (SLP-1 on Q1, ACS+1 on
     Q2); capstone sash + lore land.
  F. Five-Venoms Brocade Sash is a real accessory with claimed bonuses.
  G. Save/load round-trip preserves Shan-arc state.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game.state import Player


def drive(seed=19):
    random.seed(seed)
    g = Game(IO())
    cap: list[str] = []

    def _out(s=""):
        cap.append(str(s))

    def _in(prompt=""):
        cap.append(prompt)
        return "f"

    g.io = IO(out_func=_out, in_func=_in)

    def say(line):
        cap.append(f"\n>>> {line}")
        g.step(line)

    return g, say, cap


def banner(s):
    print()
    print("=" * 70)
    print(s)
    print("=" * 70)


# ---------------------------------------------------------------------------
banner("A. Shan arc content loads — items, lore, quests, events")
g, *_ = drive()
for iid in ("bloodmarked_cloth", "hundred_grass",
            "five_venoms_sash", "shans_dispensary_ledger"):
    assert iid in g.world["items"], f"item '{iid}' missing"
for lid in ("the_honest_venom", "the_sword_that_would_not_strike",
            "the_hand_that_empties_the_heart", "the_hundred_grass"):
    assert lid in g.world["lore"], f"lore '{lid}' missing"
for qid in ("the_honest_venom", "the_sword_that_would_not_strike",
            "the_hand_that_empties_the_heart"):
    assert qid in g.world["quests"], f"quest '{qid}' missing"
for evid in ("garden_silence_listens", "basin_viper_silence",
             "market_paper_seal_fresh"):
    assert evid in g.world["events"], f"event '{evid}' missing"
print(f"[PASS] All Shan-arc ids resolve. "
      f"Items={len(g.world['items'])}, lore={len(g.world['lore'])}, "
      f"quests={len(g.world['quests'])}, events={len(g.world['events'])}.")


# ---------------------------------------------------------------------------
banner("B. Shan's gives_quest is list-valued and contains all four quests")
g, *_ = drive()
shan = g.world["npcs"]["matriarch_shan"]
gq = shan.get("gives_quest")
assert isinstance(gq, list), f"gives_quest must be a list; got {gq!r}"
assert gq[0] == "oath_of_fangs", \
    f"oath_of_fangs must be the first entry; got {gq!r}"
for qid in ("the_honest_venom", "the_sword_that_would_not_strike",
            "the_hand_that_empties_the_heart"):
    assert qid in gq, f"Shan must own {qid!r}; got {gq!r}"
# The existing teaches should still be there.
assert "five_poisons_palm" in shan.get("teaches", [])
print(f"[PASS] Shan owns oath_of_fangs + the 3-quest Grey arc.")


# ---------------------------------------------------------------------------
banner("C. Bloodmarked cloth is on the ground at Merchant's Crossing")
g, say, cap = drive()
mc = g.world["locations"]["merchant_crossing"]
assert "bloodmarked_cloth" in (mc.get("items_on_ground") or []), \
    "bloodmarked_cloth must sit at Merchant's Crossing"
g.player.location = "merchant_crossing"
cap.clear()
say("take bloodmarked_cloth")
assert g.player.inventory.get("bloodmarked_cloth", 0) == 1
print("[PASS] bloodmarked_cloth takeable at Merchant's Crossing.")


# ---------------------------------------------------------------------------
banner("D. Hundred-grass sits on the ground at the Poisoner's Garden")
g, say, cap = drive()
pg = g.world["locations"]["poisoners_garden"]
assert "hundred_grass" in (pg.get("items_on_ground") or []), \
    "hundred_grass must sit at the Poisoner's Garden"
# Prior atmospheric content not overwritten.
assert "black_lotus_seed" in (pg.get("items_on_ground") or []), \
    "pre-existing black_lotus_seed must remain"
g.player.location = "poisoners_garden"
cap.clear()
say("take hundred_grass")
assert g.player.inventory.get("hundred_grass", 0) == 1
print("[PASS] hundred_grass takeable at Poisoner's Garden.")


# ---------------------------------------------------------------------------
banner("E. Full three-quest arc with FPS+3 gate and cross-sect rep")
g, say, cap = drive()
# Oath of Fangs is the prerequisite for the new arc. Shortcut: set it
# complete so we can focus on the new content.
g.player.completed_quests.add("oath_of_fangs")
g.player.reputation["five_poisons_sect"] = 2  # post-oath standing

# Q1: accept at the hall.
g.player.location = "five_poisons_hall"
g.player.visited.add("five_poisons_hall")
cap.clear()
say("talk matriarch_shan")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Honest Venom" in text, \
    f"q1 must auto-offer; got {text!r}"
# q2 and q3 must stay silent.
assert "The Sword That Would Not Strike" not in text, \
    "q2 must stay silent before q1 closes"
assert "The Hand That Empties the Heart" not in text, \
    "q3 must stay silent before q2 closes + rep +3"

# Visit Merchant Crossing, take the cloth, back to Shan.
g.player.location = "merchant_crossing"
g.player.visited.add("merchant_crossing")
cap.clear()
say("take bloodmarked_cloth")
g.player.location = "five_poisons_hall"
cap.clear()
say("talk matriarch_shan")
assert "the_honest_venom" in g.player.completed_quests, \
    "q1 must close after visit+collect+talk"
assert "the_honest_venom" in g.player.known_lore, \
    "q1 completion must grant honest_venom lore"
slp = g.player.reputation.get("scarlet_lotus_pavilion", 0)
assert slp <= -1, f"q1 must drop Scarlet Lotus rep by 1; got {slp}"
fps = g.player.reputation.get("five_poisons_sect", 0)
assert fps >= 3, f"q1 must grant FPS +1 (2 → 3); got {fps}"

# Next talk offers q2.
cap.clear()
say("talk matriarch_shan")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Sword That Would Not Strike" in text, \
    f"q2 must auto-offer; got {text!r}"

# Q2 chain: visit TVV mouth, talk Wuwei, visit Baixu's pavilion, talk Baixu.
# Because Shan's `talk` step is already satisfied from q2 acceptance, the
# final step closes the moment the player talks to Baixu — a subtle side-
# effect of `talked_to` being a persistent set. The player then returns
# to Shan for narrative closure AND the q3 offer.
g.player.location = "thousand_venom_valley_mouth"
g.player.visited.add("thousand_venom_valley_mouth")
cap.clear()
say("talk gatekeeper_wuwei")
g.player.location = "elder_baixus_pavilion"
g.player.visited.add("elder_baixus_pavilion")
cap.clear()
say("talk elder_baixu")
# q2 closes here — the `talk Shan` step was satisfied from the original
# accept-talk.
assert "the_sword_that_would_not_strike" in g.player.completed_quests, \
    "q2 must close when the final-before-talk_shan step is satisfied"
assert "the_sword_that_would_not_strike" in g.player.known_lore, \
    "q2 must grant sword-that-would-not-strike lore"
acs = g.player.reputation.get("azure_cloud_sect", 0)
assert acs >= 1, f"q2 must grant ACS +1 (cross-sect); got {acs}"
fps = g.player.reputation.get("five_poisons_sect", 0)
assert fps >= 4, f"q2 must grant FPS +1 (3 → 4); got {fps}"

# Back at Shan's hall, q3 should now auto-offer (prereq met, FPS>=3).
g.player.location = "five_poisons_hall"
cap.clear()
say("talk matriarch_shan")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Hand That Empties the Heart" in text, \
    f"q3 must auto-offer at FPS+3 when player returns to Shan; got {text!r}"

# Rep-gate regression: verify q3 would NOT have offered below FPS +3.
g2, say2, cap2 = drive()
g2.player.completed_quests.add("oath_of_fangs")
g2.player.completed_quests.add("the_honest_venom")
g2.player.completed_quests.add("the_sword_that_would_not_strike")
g2.player.reputation["five_poisons_sect"] = 2  # below gate
g2.player.location = "five_poisons_hall"
g2.player.visited.add("five_poisons_hall")
cap2.clear()
say2("talk matriarch_shan")
text2 = "\n".join(cap2)
assert "[QUEST ACCEPTED] The Hand That Empties the Heart" not in text2, \
    f"q3 must stay gated at FPS+2; got {text2!r}"

# Back to main thread: q3 step 1 — visit garden, collect grass, return.
g.player.location = "poisoners_garden"
g.player.visited.add("poisoners_garden")
cap.clear()
say("take hundred_grass")
g.player.location = "five_poisons_hall"
cap.clear()
say("talk matriarch_shan")
assert "the_hand_that_empties_the_heart" in g.player.completed_quests, \
    "q3 must close after visit+collect+talk"
assert "the_hand_that_empties_the_heart" in g.player.known_lore, \
    "q3 completion must grant hand-that-empties lore"
assert "the_hundred_grass" in g.player.known_lore, \
    "q3 must also grant hundred-grass lore"
assert g.player.inventory.get("five_venoms_sash", 0) == 1, \
    "q3 capstone must award the Five-Venoms Brocade Sash"
fps = g.player.reputation.get("five_poisons_sect", 0)
assert fps >= 5, f"q3 must grant FPS +1 (4 → 5); got {fps}"
print("[PASS] Three-quest arc completes; rep-gated q3; cross-sect deltas land.")


# ---------------------------------------------------------------------------
banner("F. Five-Venoms Brocade Sash equips with claimed bonuses")
g, say, cap = drive()
g.player.add_item("five_venoms_sash", 1)
g.player.reputation["five_poisons_sect"] = 3
cap.clear()
say("equip five_venoms_sash")
text = "\n".join(cap)
assert g.player.equipped.get("accessory") == "five_venoms_sash", \
    f"sash must equip into accessory slot; got {text!r}"
gb = g.player.gear_bonuses(g.world)
assert gb["atk"] >= 2, f"sash should grant ATK +2; got {gb}"
assert gb["def"] >= 1, f"sash should grant DEF +1; got {gb}"
assert gb["hp"]  >= 10, f"sash should grant HP +10; got {gb}"
# On-hit poison 1 is defined on the item itself.
sash = g.world["items"]["five_venoms_sash"]
assert sash.get("on_hit_effect") == "poison"
print(f"[PASS] Five-Venoms Sash equips with bonuses: {gb}")


# ---------------------------------------------------------------------------
banner("G. Save/load round-trip preserves Shan-arc state")
g, *_ = drive()
g.player.add_item("bloodmarked_cloth", 1)
g.player.add_item("hundred_grass", 1)
g.player.active_quests["the_sword_that_would_not_strike"] = 2
g.player.known_lore.add("the_honest_venom")
g.player.completed_quests.add("the_honest_venom")
g.player.reputation["five_poisons_sect"] = 3
g.player.reputation["scarlet_lotus_pavilion"] = -1
blob = g.player.to_json()
p2 = Player.from_json(blob)
assert p2.inventory.get("bloodmarked_cloth") == 1
assert p2.inventory.get("hundred_grass") == 1
assert "the_sword_that_would_not_strike" in p2.active_quests
assert p2.active_quests["the_sword_that_would_not_strike"] == 2
assert "the_honest_venom" in p2.known_lore
assert "the_honest_venom" in p2.completed_quests
assert p2.reputation.get("five_poisons_sect") == 3
assert p2.reputation.get("scarlet_lotus_pavilion") == -1
print("[PASS] Save/load preserves Shan-arc state.")


# ---------------------------------------------------------------------------
print()
print("All Shan Grey-That-Does-Not-Lie arc smoke-tests passed.")
