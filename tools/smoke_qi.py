#!/usr/bin/env python3
"""Scripted smoke-test for Apothecary Qi's Four Lesser Basins arc (session 20).

Exercises:
  A. Content loads — Qi-arc items, lore, quests, events.
  B. Qi's gives_quest is list-valued and contains the three new quests
     (was None / no quest in session 19); existing teaches/sells preserved.
  C. Centipede shed and Black-Pillar leaf both sit on the ground at
     Venom Gorge; pre-existing gorge enemies/events not clobbered.
  D. Full three-quest arc end-to-end: oath_of_fangs prereq → centipede
     in its skin → spider who will not spin → scorpion's first bite;
     FPS+3 gate on q3; capstone Keeper's Brocade Sash + 4 lore land.
  E. Rep gate regression: q3 must NOT offer at FPS+2.
  F. Keeper's Brocade Sash is a real accessory with claimed bonuses
     (ATK+1, DEF+3, HP+12, on-hit poison) and a FPS+2 rep gate.
  G. Bai's "I have had the answer for nine days" line appears in her
     dialogue list — the foreshadowing pattern.
  H. Save/load round-trip preserves Qi-arc state.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game.state import Player


def drive(seed=20):
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
banner("A. Qi-arc content loads — items, lore, quests, events")
g, *_ = drive()
for iid in ("centipede_shed_skin", "black_pillar_leaf",
            "keepers_brocade_sash"):
    assert iid in g.world["items"], f"item '{iid}' missing"
for lid in ("the_centipede_in_its_skin", "the_spider_who_remembers_silk",
            "the_scorpions_first_bite", "the_keepers_silence"):
    assert lid in g.world["lore"], f"lore '{lid}' missing"
for qid in ("the_centipede_in_its_skin", "the_spider_who_will_not_spin",
            "the_scorpions_first_bite"):
    assert qid in g.world["quests"], f"quest '{qid}' missing"
for evid in ("centipede_shed_at_the_root", "qi_kneels_at_the_third_basin",
             "black_pillar_breath"):
    assert evid in g.world["events"], f"event '{evid}' missing"
print(f"[PASS] All Qi-arc ids resolve. "
      f"Items={len(g.world['items'])}, lore={len(g.world['lore'])}, "
      f"quests={len(g.world['quests'])}, events={len(g.world['events'])}.")


# ---------------------------------------------------------------------------
banner("B. Qi's gives_quest is list-valued and contains all three quests")
g, *_ = drive()
qi = g.world["npcs"]["poisoner_qi"]
gq = qi.get("gives_quest")
assert isinstance(gq, list), f"gives_quest must be a list; got {gq!r}"
assert gq == [
    "the_centipede_in_its_skin",
    "the_spider_who_will_not_spin",
    "the_scorpions_first_bite",
], f"unexpected gives_quest order: {gq!r}"
# Existing teaches/sells must still be there.
for tid in ("serpent_strike", "web_of_silk", "black_lattice_palm"):
    assert tid in qi.get("teaches", []), f"teach '{tid}' lost"
for sid in ("antidote_pearl", "nine_serpents_pill", "minor_healing_pill",
            "venom_fanged_dagger", "viper_scale_sash"):
    assert sid in qi.get("sells", []), f"sell '{sid}' lost"
# Voice deepening.
assert len(qi.get("dialogue", [])) >= 6, \
    f"Qi must have >=6 dialogue lines; got {len(qi.get('dialogue', []))}"
assert qi.get("rep_dialogue", {}).get("five_poisons_sect"), \
    "Qi must have FPS rep_dialogue tiers"
assert qi.get("lore_dialogue", {}).get("five_poisons_sect"), \
    "Qi must have FPS lore_dialogue tiers"
cr = qi.get("companion_reply", {}) or {}
for c in ("venomhand_bai", "disciple_meilin", "blood_sworn_jin"):
    assert c in cr, f"Qi must have companion_reply for {c}"
print(f"[PASS] Qi owns the 3-quest arc; voice deepened (dlg={len(qi['dialogue'])}, "
      f"rep tiers, lore tiers, 3 companion_replies).")


# ---------------------------------------------------------------------------
banner("C. Gorge ground-items + atmospherics intact")
g, *_ = drive()
gorge = g.world["locations"]["venom_gorge"]
ground = gorge.get("items_on_ground") or []
assert "centipede_shed_skin" in ground, "centipede_shed_skin missing at gorge"
assert "black_pillar_leaf" in ground, "black_pillar_leaf missing at gorge"
assert "frog_chorus_dims" in (gorge.get("events") or []), \
    "pre-existing frog_chorus_dims event lost"
assert "giant_centipede" in (gorge.get("enemies") or []), \
    "pre-existing centipede enemy lost"
assert "poison_cultivator" in (gorge.get("enemies") or []), \
    "pre-existing poison cultivator lost"
print(f"[PASS] Venom Gorge: {ground} on ground; pre-existing content kept.")


# ---------------------------------------------------------------------------
banner("D. Full three-quest arc with FPS+3 gate")
g, say, cap = drive()
g.player.completed_quests.add("oath_of_fangs")
g.player.reputation["five_poisons_sect"] = 2  # post-oath standing

# Q1: accept by talking to Qi at the hall.
g.player.location = "five_poisons_hall"
g.player.visited.add("five_poisons_hall")
cap.clear()
say("talk poisoner_qi")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Centipede in Its Skin" in text, \
    f"q1 must auto-offer; got {text!r}"
assert "The Spider Who Will Not Spin" not in text, \
    "q2 must stay silent before q1 closes"
assert "The Scorpion's First Bite" not in text, \
    "q3 must stay silent before q2 closes + rep gate"

# Walk to gorge, take the shed, return to Qi.
g.player.location = "venom_gorge"
g.player.visited.add("venom_gorge")
cap.clear()
say("take centipede_shed_skin")
assert g.player.inventory.get("centipede_shed_skin", 0) == 1
g.player.location = "five_poisons_hall"
cap.clear()
say("talk poisoner_qi")
assert "the_centipede_in_its_skin" in g.player.completed_quests, \
    "q1 must close after visit+collect+talk"
assert "the_centipede_in_its_skin" in g.player.known_lore, \
    "q1 completion must grant centipede lore"
fps = g.player.reputation.get("five_poisons_sect", 0)
assert fps >= 3, f"q1 must grant FPS +1 (2 → 3); got {fps}"

# Q2: next talk to Qi offers the spider quest.
cap.clear()
say("talk poisoner_qi")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Spider Who Will Not Spin" in text, \
    f"q2 must auto-offer after q1 closes; got {text!r}"

# Q2 chain: visit garden, talk Bai, then talk Qi.
# Note: per session-19's "talked_to is persistent" lesson, the final
# talk-Qi step is satisfied by the original accept-talk. q2 closes
# when the player talks to Bai.
g.player.location = "poisoners_garden"
g.player.visited.add("poisoners_garden")
cap.clear()
say("talk venomhand_bai")
assert "the_spider_who_will_not_spin" in g.player.completed_quests, \
    "q2 must close on talk venomhand_bai (final non-trivial step)"
assert "the_spider_who_remembers_silk" in g.player.known_lore, \
    "q2 completion must grant spider lore"
fps = g.player.reputation.get("five_poisons_sect", 0)
assert fps >= 4, f"q2 must grant FPS +1 (3 → 4); got {fps}"

# Q3: return to Qi at the hall — offer should fire (FPS now 4 >= 3).
g.player.location = "five_poisons_hall"
cap.clear()
say("talk poisoner_qi")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Scorpion's First Bite" in text, \
    f"q3 must auto-offer at FPS>=3; got {text!r}"

# Q3 chain: back to gorge for the leaf, return to Qi.
g.player.location = "venom_gorge"
cap.clear()
say("take black_pillar_leaf")
assert g.player.inventory.get("black_pillar_leaf", 0) == 1
g.player.location = "five_poisons_hall"
cap.clear()
say("talk poisoner_qi")
assert "the_scorpions_first_bite" in g.player.completed_quests, \
    "q3 must close after visit+collect+talk"
for lid in ("the_scorpions_first_bite", "the_keepers_silence"):
    assert lid in g.player.known_lore, \
        f"q3 must grant lore '{lid}'"
assert g.player.inventory.get("keepers_brocade_sash", 0) == 1, \
    "q3 capstone must award the Keeper's Brocade Sash"
fps = g.player.reputation.get("five_poisons_sect", 0)
assert fps >= 5, f"q3 must grant FPS +1 (4 → 5); got {fps}"
print("[PASS] Three-quest Qi arc completes; capstone sash + 4 lore granted.")


# ---------------------------------------------------------------------------
banner("E. Rep-gate regression — q3 must NOT offer below FPS +3")
g2, say2, cap2 = drive()
g2.player.completed_quests.add("oath_of_fangs")
g2.player.completed_quests.add("the_centipede_in_its_skin")
g2.player.completed_quests.add("the_spider_who_will_not_spin")
g2.player.reputation["five_poisons_sect"] = 2  # explicitly below gate
g2.player.location = "five_poisons_hall"
g2.player.visited.add("five_poisons_hall")
cap2.clear()
say2("talk poisoner_qi")
text2 = "\n".join(cap2)
assert "[QUEST ACCEPTED] The Scorpion's First Bite" not in text2, \
    f"q3 must stay gated at FPS+2; got {text2!r}"
print("[PASS] q3 correctly gated at FPS+3.")


# ---------------------------------------------------------------------------
banner("F. Keeper's Brocade Sash equips with claimed bonuses")
g, say, cap = drive()
g.player.add_item("keepers_brocade_sash", 1)
g.player.reputation["five_poisons_sect"] = 2  # at the gate
cap.clear()
say("equip keepers_brocade_sash")
assert g.player.equipped.get("accessory") == "keepers_brocade_sash", \
    "sash must equip into accessory slot"
gb = g.player.gear_bonuses(g.world)
assert gb["atk"] >= 1, f"sash should grant ATK +1; got {gb}"
assert gb["def"] >= 3, f"sash should grant DEF +3; got {gb}"
assert gb["hp"]  >= 12, f"sash should grant HP +12; got {gb}"
sash = g.world["items"]["keepers_brocade_sash"]
assert sash.get("on_hit_effect") == "poison"
assert sash.get("requires_rep", {}).get("five_poisons_sect") == 2, \
    f"sash should require FPS+2; got {sash.get('requires_rep')!r}"
# Distinct from Shan's Five-Venoms Sash: defence-leaning, lower ATK,
# more HP, lower rep-gate (Qi gives keepers' tools more freely).
shans = g.world["items"]["five_venoms_sash"]
assert sash["def_bonus"] > shans["def_bonus"], \
    "Keeper's sash must be more defensive than Shan's"
assert sash["atk_bonus"] < shans["atk_bonus"], \
    "Keeper's sash must be less offensive than Shan's"
print(f"[PASS] Keeper's Brocade Sash equips with bonuses: {gb}; "
      f"distinct profile from Shan's sash.")


# ---------------------------------------------------------------------------
banner("G. Bai's foreshadowing line — 'answer for nine days' — present")
g, *_ = drive()
bai = g.world["npcs"]["venomhand_bai"]
dlg = bai.get("dialogue", [])
foreshadowing = [line for line in dlg if "nine days" in line.lower()
                 and "spider" in line.lower()]
assert foreshadowing, \
    f"Bai must foreshadow the spider answer; got dlg={dlg!r}"
print(f"[PASS] Bai foreshadows the spider — '{foreshadowing[0][:60]}...'")


# ---------------------------------------------------------------------------
banner("H. Save/load round-trip preserves Qi-arc state")
g, *_ = drive()
g.player.add_item("centipede_shed_skin", 1)
g.player.add_item("black_pillar_leaf", 1)
g.player.active_quests["the_scorpions_first_bite"] = 1
g.player.known_lore.add("the_centipede_in_its_skin")
g.player.known_lore.add("the_spider_who_remembers_silk")
g.player.completed_quests.add("the_centipede_in_its_skin")
g.player.completed_quests.add("the_spider_who_will_not_spin")
g.player.reputation["five_poisons_sect"] = 4
blob = g.player.to_json()
p2 = Player.from_json(blob)
assert p2.inventory.get("centipede_shed_skin") == 1
assert p2.inventory.get("black_pillar_leaf") == 1
assert "the_scorpions_first_bite" in p2.active_quests
assert "the_centipede_in_its_skin" in p2.known_lore
assert "the_spider_who_remembers_silk" in p2.known_lore
assert "the_centipede_in_its_skin" in p2.completed_quests
assert "the_spider_who_will_not_spin" in p2.completed_quests
assert p2.reputation.get("five_poisons_sect") == 4
print("[PASS] Save/load preserves Qi-arc state.")


# ---------------------------------------------------------------------------
print()
print("All Apothecary Qi Four-Lesser-Basins arc smoke-tests passed.")
