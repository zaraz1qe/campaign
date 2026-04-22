#!/usr/bin/env python3
"""Scripted smoke-test for the companion system.

Exercises:
  1. Recruit fails with no gates met (mortal, no quest, no rep).
  2. Recruit succeeds after seeding quest + rep.
  3. Companion appears in `companion` / `status`.
  4. Combat runs with companion, including an enemy turn that targets comp.
  5. Companion downed -> `cultivate` revives.
  6. Dismiss clears the slot. Save/load round-trips companion.
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO


# Drive commands explicitly; combat prompts eat from a per-step queue.
def drive(steps, seed=42):
    random.seed(seed)
    g = Game(IO())
    captured = []
    # Replace g.out with buffer; keep ask scripted via a per-step queue.
    answer_queue = []
    def _out(s=""):
        captured.append(str(s))
    def _in(prompt=""):
        captured.append(prompt)
        if answer_queue:
            a = answer_queue.pop(0)
            captured.append(a)
            return a
        captured.append("(no answer queued -> f)")
        return "f"
    g.io = IO(out_func=_out, in_func=_in)
    def say(line):
        captured.append(f"\n>>> {line}")
        g.step(line)
    return g, say, answer_queue, captured


def banner(s):
    print()
    print("=" * 70)
    print(s)
    print("=" * 70)


# -------- Scenario A: default player cannot recruit --------
banner("A. Default (mortal, no quest, no rep) — recruit refused")
g, say, q, cap = drive([])
# move to Inner Courtyard — need to walk a path. Cheat: teleport player.
g.player.location = "azure_cloud_inner_courtyard"
say("look")
say("recruit disciple_meilin")
print("\n".join(cap[-30:]))
assert g.player.companion is None
print("\n[PASS] Recruit denied; no companion set.")


# -------- Scenario B: player meets gates — recruit succeeds, status/combat --------
banner("B. Meeting gates — recruit Meilin, fight bandit at her side")
g, say, q, cap = drive([])
# Cheat: advance realm, set rep, complete the study_sutra quest.
g.player.realm_id = "qi_condensation"
g.player.max_hp = 60
g.player.hp = 60
g.player.atk = 9
g.player.defense = 4
g.player.spd = 7
g.player.reputation["azure_cloud_sect"] = 3
g.player.completed_quests.add("study_the_sutra")
g.player.location = "azure_cloud_inner_courtyard"
say("recruit disciple_meilin")
assert g.player.companion is not None, "expected recruit to succeed"
assert g.player.companion["id"] == "disciple_meilin"
assert g.player.companion["max_hp"] == 58
say("companion")
say("status")
# Walk to Bandit Road for a fight.
g.player.location = "bandit_road"
say("look")
# Fight bandit_scout. Pre-queue combat inputs: attack, attack, attack...
q.extend(["a", "a", "a", "a", "a", "a", "a", "a", "a"])
say("fight bandit_scout")
print("\n".join(cap[-80:]))
# By seed 42 we expect a resolved fight; companion should be non-None.
assert g.player.companion is not None
print("\n[PASS] Recruit succeeded, combat ran, companion survived or was reset.")


# -------- Scenario C: downed companion revived on cultivate --------
banner("C. Manually down companion -> cultivate revives")
g.player.companion["hp"] = 0
g.player.companion["downed"] = True
say("companion")
say("cultivate")
say("companion")
assert g.player.companion["downed"] is False
assert g.player.companion["hp"] == g.player.companion["max_hp"]
print("\n[PASS] Downed companion revived by cultivation.")


# -------- Scenario D: dismiss --------
banner("D. Dismiss clears companion")
say("dismiss")
assert g.player.companion is None
say("companion")
say("dismiss")  # already none
print("\n[PASS] Dismiss works.")


# -------- Scenario E: save/load round-trip with companion --------
banner("E. Save/load with companion round-trips")
# Re-recruit.
g.player.location = "azure_cloud_inner_courtyard"
say("recruit disciple_meilin")
assert g.player.companion is not None
# Serialize -> deserialize.
blob = g.player.to_json()
from game.state import Player
rehydrated = Player.from_json(blob)
assert rehydrated.companion is not None
assert rehydrated.companion["id"] == "disciple_meilin"
# Old save with no companion field still loads.
d = json.loads(blob)
d.pop("companion", None)
old = Player.from_json(json.dumps(d))
assert old.companion is None
print("\n[PASS] Save round-trips with companion; legacy saves load cleanly.")


# -------- Scenario F: recruiting Venomhand Bai --------
banner("F. Five Poisons companion — Bai requires oath_of_fangs + rep 2")
g, say, q, cap = drive([])
g.player.realm_id = "qi_condensation"
g.player.location = "poisoners_garden"
say("look")
# Gate checks: no quest completed.
say("recruit venomhand_bai")
assert g.player.companion is None
# Grant quest + rep.
g.player.completed_quests.add("oath_of_fangs")
g.player.reputation["five_poisons_sect"] = 2
say("recruit venomhand_bai")
assert g.player.companion is not None
assert g.player.companion["id"] == "venomhand_bai"
# Can't recruit second when one is bound.
g.player.location = "azure_cloud_inner_courtyard"
g.player.reputation["azure_cloud_sect"] = 3
g.player.completed_quests.add("study_the_sutra")
say("recruit disciple_meilin")
assert g.player.companion["id"] == "venomhand_bai", "should still be Bai"
print("\n[PASS] Bai recruited with proper gates; second recruit blocked.")


print("\nAll companion smoke-tests passed.")
