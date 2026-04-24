#!/usr/bin/env python3
"""Scripted smoke-test for Gatekeeper Chen's Second Trial arc (session 21).

Exercises:
  A. Content loads — Chen-arc items, lore, quests, events.
  B. Chen's gives_quest is list-valued and contains all three arc
     quests; his voice deepens — dialogue grew from 4 lines to >=8;
     rep_dialogue has five ACS tiers; lore_dialogue has two ACS tiers;
     three companion_reply entries (one per player-companion).
  C. Outer-gate ground-items (three night-watch tokens) are present;
     pre-existing content is not clobbered.
  D. Full three-quest arc end-to-end: broom-and-blade (mortal) →
     name-that-was-not-his (ACS+2 gate) → courtesy-bell-at-dawn
     (ACS+4 gate); capstone Outer Disciple's Broom + 3 lore land.
  E. Rep-gate regression: Q3 must NOT offer at ACS+3.
  F. Outer Disciple's Broom equips as a weapon with claimed bonuses
     (ATK+3, DEF+2, HP+8, SPD+1) and an ACS+3 rep gate.
  G. Chen's "register has three columns" foreshadowing line is in
     his dialogue list — ambient hook for Q2's first-column reveal.
  H. Save/load round-trip preserves Chen-arc state.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game.state import Player


def drive(seed=21):
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
banner("A. Chen-arc content loads — items, lore, quests, events")
g, *_ = drive()
for iid in ("pilgrims_copper_petition", "couriers_valley_slip",
            "mothers_unanswered_question", "chens_stroke_pin",
            "outer_disciples_broom"):
    assert iid in g.world["items"], f"item '{iid}' missing"
for lid in ("the_broom_and_the_blade",
            "the_first_column_of_the_register",
            "the_courtesy_bell"):
    assert lid in g.world["lore"], f"lore '{lid}' missing"
for qid in ("the_broom_and_the_blade",
            "the_name_that_was_not_his",
            "the_courtesy_bell_at_dawn"):
    assert qid in g.world["quests"], f"quest '{qid}' missing"
for evid in ("chen_ties_and_unties_the_sash",
             "foothills_willow_at_the_switchback",
             "register_second_ink_warms"):
    assert evid in g.world["events"], f"event '{evid}' missing"
print(f"[PASS] All Chen-arc ids resolve. "
      f"Items={len(g.world['items'])}, lore={len(g.world['lore'])}, "
      f"quests={len(g.world['quests'])}, events={len(g.world['events'])}.")


# ---------------------------------------------------------------------------
banner("B. Chen owns a 3-quest arc; voice deepened")
g, *_ = drive()
chen = g.world["npcs"]["gatekeeper_disciple_chen"]
gq = chen.get("gives_quest")
assert isinstance(gq, list), f"gives_quest must be a list; got {gq!r}"
assert gq == [
    "the_broom_and_the_blade",
    "the_name_that_was_not_his",
    "the_courtesy_bell_at_dawn",
], f"unexpected gives_quest order: {gq!r}"
dlg = chen.get("dialogue", [])
assert len(dlg) >= 8, f"Chen must have >=8 dialogue lines; got {len(dlg)}"
# Original four lines preserved (no rename/drift of seed voice).
for seed in ("Welcome to the Azure Cloud",
             "Elder Baixu sees few visitors",
             "Disciple-Sister Meilin",
             "Six more weeks"):
    assert any(seed in d for d in dlg), f"seed dialogue lost: {seed!r}"
rep = chen.get("rep_dialogue", {}).get("azure_cloud_sect") or {}
for thr in ("-3", "-2", "1", "2", "3", "5"):
    assert thr in rep, f"Chen missing ACS rep tier {thr}"
ld = chen.get("lore_dialogue", {}).get("azure_cloud_sect") or {}
for thr in ("3", "5"):
    assert thr in ld, f"Chen missing ACS lore tier {thr}"
assert ld["3"] == "the_broom_and_the_blade"
assert ld["5"] == "the_first_column_of_the_register"
cr = chen.get("companion_reply", {}) or {}
for c in ("disciple_meilin", "venomhand_bai", "blood_sworn_jin"):
    assert c in cr, f"Chen must have companion_reply for {c}"
print(f"[PASS] Chen owns the 3-quest arc; dlg={len(dlg)}, "
      f"rep tiers={len(rep)}, lore tiers={len(ld)}, "
      f"companion_replies={len(cr)}.")


# ---------------------------------------------------------------------------
banner("C. Outer-gate ground-items present; pre-existing content intact")
g, *_ = drive()
gate = g.world["locations"]["azure_cloud_outer_gate"]
ground = gate.get("items_on_ground") or []
for iid in ("pilgrims_copper_petition", "couriers_valley_slip",
            "mothers_unanswered_question"):
    assert iid in ground, f"{iid} missing at outer gate"
# Chen still the sole NPC listed at the gate.
assert gate.get("npcs") == ["gatekeeper_disciple_chen"], \
    f"outer-gate npcs list drifted: {gate.get('npcs')!r}"
# Original outer-gate event still resolves in the world.
assert "azure_outer_bell_tolls" in g.world["events"], \
    "pre-existing outer-gate courtesy-bell event lost"
print(f"[PASS] Outer gate: {ground} on ground; Chen still the gatekeeper.")


# ---------------------------------------------------------------------------
banner("D. Full three-quest arc with ACS+4 gate on Q3")
g, say, cap = drive()
g.player.reputation["azure_cloud_sect"] = 0  # fresh visitor

# Q1: accept by talking to Chen at the outer gate.
g.player.location = "azure_cloud_outer_gate"
g.player.visited.add("azure_cloud_outer_gate")
cap.clear()
say("talk gatekeeper_disciple_chen")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Broom and the Blade" in text, \
    f"Q1 must auto-offer; got {text!r}"
assert "The Name That Was Not His" not in text, \
    "Q2 must stay silent before Q1 closes"
assert "The Courtesy Bell at Dawn" not in text, \
    "Q3 must stay silent before Q2 closes"

# Q1 chain: visit the foothills, return, talk Chen.
g.player.location = "azure_cloud_foothills"
g.player.visited.add("azure_cloud_foothills")
g.player.location = "azure_cloud_outer_gate"
cap.clear()
say("talk gatekeeper_disciple_chen")
# Q1's final step is `talk gatekeeper_disciple_chen`. Because chen is
# already in talked_to (from the accept-talk), Q1 closes the moment the
# foothills-visit step is satisfied — i.e. on this return-talk, which
# triggers a re-run of progression after the visit. Same talked_to-is-
# persistent quirk seen on Huilin, Weilan, Shan and Qi arcs.
assert "the_broom_and_the_blade" in g.player.completed_quests, \
    "Q1 must close after visit+talk"
assert "the_broom_and_the_blade" in g.player.known_lore, \
    "Q1 completion must grant the broom-and-blade lore"
acs = g.player.reputation.get("azure_cloud_sect", 0)
assert acs >= 1, f"Q1 must grant ACS +1; got {acs}"

# Q2: next talk to Chen auto-offers (ACS+1 now, gate is ACS+2).
# Bump ACS to meet the gate — Q1 gave +1, we need +2 for Q2's rep gate.
g.player.reputation["azure_cloud_sect"] = 2
cap.clear()
say("talk gatekeeper_disciple_chen")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Name That Was Not His" in text, \
    f"Q2 must auto-offer at ACS>=2 post-Q1; got {text!r}"

# Q2 chain: visit library, talk Zhao, return-talk Chen.
g.player.location = "azure_cloud_library"
g.player.visited.add("azure_cloud_library")
cap.clear()
say("talk librarian_zhao")
# Per talked_to-is-persistent: Q2 closes when the final non-trivial
# step (talk zhao) fires. The return-talk-Chen step is trivially
# satisfied from the accept-talk.
assert "the_name_that_was_not_his" in g.player.completed_quests, \
    "Q2 must close on talk librarian_zhao"
assert "the_first_column_of_the_register" in g.player.known_lore, \
    "Q2 completion must grant first-column lore"
assert g.player.inventory.get("chens_stroke_pin", 0) >= 1, \
    "Q2 must award Chen's Stroke-Pin"

# Q3: requires ACS+4. Bump and return to Chen.
g.player.reputation["azure_cloud_sect"] = 4
g.player.location = "azure_cloud_outer_gate"
cap.clear()
say("talk gatekeeper_disciple_chen")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Courtesy Bell at Dawn" in text, \
    f"Q3 must auto-offer at ACS>=4; got {text!r}"

# Q3 chain: already at the gate (visit step trivially satisfied from
# the accept-talk). Collect the three night-watch tokens, return-talk.
cap.clear()
say("take pilgrims_copper_petition")
say("take couriers_valley_slip")
say("take mothers_unanswered_question")
for iid in ("pilgrims_copper_petition", "couriers_valley_slip",
            "mothers_unanswered_question"):
    assert g.player.inventory.get(iid, 0) >= 1, \
        f"failed to pick up {iid}"
cap.clear()
say("talk gatekeeper_disciple_chen")
assert "the_courtesy_bell_at_dawn" in g.player.completed_quests, \
    "Q3 must close after collect+talk"
assert "the_courtesy_bell" in g.player.known_lore, \
    "Q3 completion must grant the courtesy-bell lore"
assert g.player.inventory.get("outer_disciples_broom", 0) >= 1, \
    "Q3 capstone must award the Outer Disciple's Broom"
acs_final = g.player.reputation.get("azure_cloud_sect", 0)
assert acs_final >= 6, \
    f"Q3 must grant ACS +2 (4 → 6); got {acs_final}"
print("[PASS] Three-quest Chen arc completes; "
      "capstone broom + 3 lore + ACS+2 granted.")


# ---------------------------------------------------------------------------
banner("E. Rep-gate regression — Q3 must NOT offer below ACS +4")
g2, say2, cap2 = drive()
g2.player.completed_quests.add("the_broom_and_the_blade")
g2.player.completed_quests.add("the_name_that_was_not_his")
g2.player.reputation["azure_cloud_sect"] = 3  # explicitly one under the gate
g2.player.location = "azure_cloud_outer_gate"
g2.player.visited.add("azure_cloud_outer_gate")
cap2.clear()
say2("talk gatekeeper_disciple_chen")
text2 = "\n".join(cap2)
assert "[QUEST ACCEPTED] The Courtesy Bell at Dawn" not in text2, \
    f"Q3 must stay gated at ACS+3; got {text2!r}"
print("[PASS] Q3 correctly gated at ACS+4.")


# ---------------------------------------------------------------------------
banner("F. Outer Disciple's Broom equips as a weapon with claimed bonuses")
g, say, cap = drive()
g.player.add_item("outer_disciples_broom", 1)
g.player.reputation["azure_cloud_sect"] = 3  # at the gate
cap.clear()
say("equip outer_disciples_broom")
assert g.player.equipped.get("weapon") == "outer_disciples_broom", \
    "broom must equip into weapon slot"
gb = g.player.gear_bonuses(g.world)
assert gb["atk"] >= 3, f"broom should grant ATK +3; got {gb}"
assert gb["def"] >= 2, f"broom should grant DEF +2; got {gb}"
assert gb["hp"]  >= 8, f"broom should grant HP +8; got {gb}"
assert gb["spd"] >= 1, f"broom should grant SPD +1; got {gb}"
broom = g.world["items"]["outer_disciples_broom"]
assert broom.get("requires_rep", {}).get("azure_cloud_sect") == 3, \
    f"broom should require ACS+3; got {broom.get('requires_rep')!r}"
# Distinct from bamboo_longstaff — Chen's broom is a late-mortal / early-QC
# staff that should outperform the basic bamboo.
bl = g.world["items"]["bamboo_longstaff"]
assert broom["atk_bonus"] > bl.get("atk_bonus", 0), \
    "Outer Disciple's Broom must out-hit the plain longstaff"
assert broom["def_bonus"] > bl.get("def_bonus", 0), \
    "Outer Disciple's Broom must out-defend the plain longstaff"
print(f"[PASS] Outer Disciple's Broom equips with bonuses: {gb}.")


# ---------------------------------------------------------------------------
banner("G. Chen's register-columns foreshadowing line is present")
g, *_ = drive()
chen = g.world["npcs"]["gatekeeper_disciple_chen"]
foreshadowing = [
    line for line in chen.get("dialogue", [])
    if "three columns" in line.lower() or "third column" in line.lower()
]
assert foreshadowing, \
    f"Chen must foreshadow the register's columns; got dlg={chen.get('dialogue')!r}"
print(f"[PASS] Chen foreshadows the register — '{foreshadowing[0][:60]}...'")


# ---------------------------------------------------------------------------
banner("H. Save/load round-trip preserves Chen-arc state")
g, *_ = drive()
g.player.add_item("pilgrims_copper_petition", 1)
g.player.add_item("couriers_valley_slip", 1)
g.player.add_item("chens_stroke_pin", 1)
g.player.active_quests["the_courtesy_bell_at_dawn"] = 1
g.player.known_lore.add("the_broom_and_the_blade")
g.player.known_lore.add("the_first_column_of_the_register")
g.player.completed_quests.add("the_broom_and_the_blade")
g.player.completed_quests.add("the_name_that_was_not_his")
g.player.reputation["azure_cloud_sect"] = 4
blob = g.player.to_json()
p2 = Player.from_json(blob)
assert p2.inventory.get("pilgrims_copper_petition") == 1
assert p2.inventory.get("couriers_valley_slip") == 1
assert p2.inventory.get("chens_stroke_pin") == 1
assert "the_courtesy_bell_at_dawn" in p2.active_quests
assert "the_broom_and_the_blade" in p2.known_lore
assert "the_first_column_of_the_register" in p2.known_lore
assert "the_broom_and_the_blade" in p2.completed_quests
assert "the_name_that_was_not_his" in p2.completed_quests
assert p2.reputation.get("azure_cloud_sect") == 4
print("[PASS] Save/load preserves Chen-arc state.")


# ---------------------------------------------------------------------------
print()
print("All Gatekeeper Chen Second-Trial arc smoke-tests passed.")
