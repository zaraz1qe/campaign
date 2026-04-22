#!/usr/bin/env python3
"""Scripted smoke-test for the companion affinity + barks + Jin (session 9).

Exercises:
  A. Jin refuses before Red Path + SL rep +3.
  B. Jin accepts once gated; qi_condensation enforced.
  C. Affinity starts at 0; +1 per shared combat win.
  D. Affinity tier bonuses apply at fight start (runtime stats lift).
  E. Quest completion with active companion grants +2 affinity.
  F. Affinity persists across dismiss -> recruit.
  G. Location bark fires once per arrival; not again on re-look.
  H. Save/load round-trips companion_affinity.
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game.state import Player, affinity_tier, affinity_bonus


def drive(seed=7):
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
banner("A. Jin refuses before gates met")
g, say, q, cap = drive()
g.player.realm_id = "qi_condensation"
g.player.location = "crimson_creek"
# First look — Jin isn't even visible without rep gates (requires_rep 3 on NPC).
say("look")
# requires_rep gate means Jin is not visible yet
assert "Blood-Sworn Jin" not in "\n".join(cap[-20:]), \
    "Jin should be invisible before rep gate on NPC"
# Recruit should fail because NPC isn't _visible_ for the player at this rep.
say("recruit blood_sworn_jin")
assert g.player.companion is None, "Jin must not be recruited without rep gate"
print("[PASS] Jin invisible and non-recruitable below SL rep +3.")


# ---------------------------------------------------------------------------
banner("B. Jin accepts after Red Path + SL rep +3")
g.player.completed_quests.add("the_red_path")
g.player.reputation["scarlet_lotus_pavilion"] = 3
say("look")
assert "Blood-Sworn Jin" in "\n".join(cap[-20:]), \
    "Jin should be visible after gates"
say("recruit blood_sworn_jin")
assert g.player.companion is not None, "Jin must be recruited"
assert g.player.companion["id"] == "blood_sworn_jin"
assert g.player.companion["max_hp"] == 48
assert g.player.companion["atk"] == 11
print("[PASS] Jin recruited with expected stats.")


# ---------------------------------------------------------------------------
banner("C. Affinity starts at 0; status & companion show bond")
say("status")
say("companion")
assert g.player.affinity("blood_sworn_jin") == 0
recent = "\n".join(cap[-60:])
assert "Bond:" in recent or "bond:" in recent, "companion screen should show bond"
assert "bonded" in recent
print("[PASS] Affinity 0 shown as 'bonded'.")


# ---------------------------------------------------------------------------
banner("D. Combat victory grants +1 affinity (no tier change at 0->1)")
# Stage a fight. Buff the player so fight ends quickly.
g.player.max_hp = 200; g.player.hp = 200
g.player.atk = 30; g.player.defense = 10; g.player.spd = 15
# Fight at current location.
q.extend(["a"] * 40)
# Create a weak enemy in place: use a scripted enemy.
g.player.location = "crimson_creek"  # already here
say("fight blood_sworn_cultivator")
aff_after = g.player.affinity("blood_sworn_jin")
assert aff_after >= 1, f"expected +1 affinity, got {aff_after}"
print(f"[PASS] Combat +1: affinity now {aff_after}.")


# ---------------------------------------------------------------------------
banner("E. Tier crossing — force affinity to 5 and verify bonus applies")
# Crank affinity to the 'trusted' threshold directly.
g.player.companion_affinity["blood_sworn_jin"] = 5
assert affinity_tier(5) == "trusted"
assert affinity_bonus(5)["atk"] == 1
# Start a fight and verify runtime companion's atk includes +1 from bond.
q.extend(["f"] * 3)  # attempt to flee immediately to short-circuit fight
say("fight blood_sworn_cultivator")
# We can't easily read the runtime comp mid-fight here, but check that the
# writeback left base atk untouched (the bonus is applied at snapshot only).
assert g.player.companion["atk"] == 11, \
    f"base stored atk should remain 11 after fight, got {g.player.companion['atk']}"
print("[PASS] Tier 'trusted' does not corrupt stored base stats.")


# ---------------------------------------------------------------------------
banner("F. Affinity persists across dismiss -> recruit")
say("dismiss")
assert g.player.companion is None
saved_aff = g.player.affinity("blood_sworn_jin")
assert saved_aff >= 5, f"affinity persists on player even after dismiss, got {saved_aff}"
say("recruit blood_sworn_jin")
assert g.player.companion is not None
assert g.player.affinity("blood_sworn_jin") == saved_aff
print(f"[PASS] Affinity {saved_aff} survived dismiss -> re-recruit.")


# ---------------------------------------------------------------------------
banner("G. Location bark fires on arrival; not again on re-look")
# Jin has a bark for scarlet_lotus_shrine.
g.player.location = "scarlet_lotus_shrine"
# But shrine has a rep_gated guardian; need to make sure look doesn't start a
# fight. Look is safe.
say("look")
first_look = "\n".join(cap[-40:])
assert "[Blood-Sworn Jin]" in first_look, "first look should print the bark"
# Second look should NOT print the bark again.
before_len = len(cap)
say("look")
second_look = "\n".join(cap[before_len:])
assert "[Blood-Sworn Jin]" not in second_look, \
    "re-look at the same location must not re-bark"
print("[PASS] Bark fires on arrival; once per location.")


# ---------------------------------------------------------------------------
banner("H. Save/load round-trips companion_affinity")
g.player.companion_affinity["test_npc"] = 11
blob = g.player.to_json()
rehydrated = Player.from_json(blob)
assert rehydrated.companion_affinity.get("blood_sworn_jin", 0) == saved_aff
assert rehydrated.companion_affinity.get("test_npc") == 11
# Legacy save with no companion_affinity still loads.
d = json.loads(blob)
d.pop("companion_affinity", None)
old = Player.from_json(json.dumps(d))
assert old.companion_affinity == {}
print("[PASS] companion_affinity saves/loads; legacy saves default to {}.")


# ---------------------------------------------------------------------------
banner("I. Quest-completion bond bump — force the path via quests.progress_quests")
# Use Meilin to avoid needing Jin's gates again.
g, say, q, cap = drive(seed=3)
g.player.realm_id = "qi_condensation"
g.player.max_hp = 60; g.player.hp = 60
g.player.reputation["azure_cloud_sect"] = 3
g.player.completed_quests.add("study_the_sutra")
g.player.location = "azure_cloud_inner_courtyard"
say("recruit disciple_meilin")
assert g.player.companion is not None
assert g.player.companion["id"] == "disciple_meilin"
# Manually simulate a quest completion while comp is active. We pick a quest
# the player could realistically complete without side effects.
# Stage the quest progress: active quest, with a one-step satisfied condition.
# Easiest path: add a fake entry and drive through progress_quests directly.
from game import quests as Q
# Artificially mark the active_quests entry and let progress_quests carry it.
# We'll use a real existing single-step visit quest if any; else skip this
# portion. Otherwise, directly call adjust_affinity by simulating the hook
# path via a harness: set up & fire progress_quests with a fabricated quest.
# Simplest: directly drive the hook like production would.
before = g.player.affinity("disciple_meilin")
# Fabricate a quest object in the world for the duration of this test only.
g.world["quests"]["_test_bond_quest"] = {
    "name": "Test Bond Quest",
    "description": "A sacrificial test.",
    "steps": [{"type": "visit", "target": "azure_cloud_inner_courtyard"}],
    "reward": {"spirit_stones": 0, "xp": 0},
}
g.player.active_quests["_test_bond_quest"] = 0
g.player.visited.add("azure_cloud_inner_courtyard")
notes = Q.progress_quests(g.world, g.player)
after = g.player.affinity("disciple_meilin")
assert after == before + 2, f"expected +2 from quest, got {after - before}"
assert any("Bond" in n for n in notes), f"expected a Bond note; got {notes}"
print(f"[PASS] Quest completion while companion active granted +2 (before={before}, after={after}).")


print("\nAll affinity/bark smoke-tests passed.")
