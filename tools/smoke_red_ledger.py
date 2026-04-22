#!/usr/bin/env python3
"""Scripted smoke-test for The Red Ledger quest arc + companion_reply layer.

Exercises:
  A. The Red Ledger is not offered before The Red Path is completed.
  B. After Red Path + SL rep +3, Red Feather offers The Red Ledger on talk.
  C. Willow-Step Shen is gated on SL rep +3 (invisible otherwise).
  D. Defeating Shen drops the cipher page; the quest can then complete.
  E. companion_reply fires on talk when a listed companion is bound,
     and only for that specific companion.
  F. A downed companion does NOT trigger companion_reply.
  G. Quest rewards land (stones, xp, rep deltas, items).
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game import quests as Q


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
banner("A. Red Ledger is silent before Red Path is completed")
g, say, q, cap = drive()
g.player.realm_id = "qi_condensation"
g.player.reputation["scarlet_lotus_pavilion"] = 3
g.player.location = "scarlet_lotus_shrine"
say("talk elder_red_feather")
assert "the_red_ledger" not in g.player.active_quests, \
    "Red Ledger should not auto-offer without prereq quest"
joined = "\n".join(cap[-50:])
# The word 'QUEST ACCEPTED' must not appear in Red Feather's talk output.
assert "QUEST ACCEPTED" not in joined, "No quest should have been offered"
print("[PASS] Red Feather does not offer Red Ledger before Red Path is done.")


# ---------------------------------------------------------------------------
banner("B. Once Red Path done + SL rep +3, Red Ledger auto-offers on talk")
g.player.completed_quests.add("the_red_path")
# Rep already +3 from before.
say("talk elder_red_feather")
assert "the_red_ledger" in g.player.active_quests, \
    "Red Ledger should auto-offer once prereq is met"
# Step 0 = visit hanging_terraces_of_jadestep
idx = g.player.active_quests["the_red_ledger"]
assert idx == 0, f"expected step 0 pending, got {idx}"
print("[PASS] Red Ledger offered; first step is the Jadestep visit.")


# ---------------------------------------------------------------------------
banner("C. Willow-Step Shen is rep-gated — invisible at low SL rep")
g2, say2, q2, cap2 = drive(seed=2)
g2.player.realm_id = "qi_condensation"
g2.player.location = "hanging_terraces_of_jadestep"
# No SL rep -> Shen invisible
say2("look")
recent = "\n".join(cap2[-40:])
assert "Willow-Step Shen" not in recent, "Shen must be invisible below SL rep +3"
# Attack attempt should fail — enemy not here for this player.
say2("fight apostate_willow_step_shen")
recent = "\n".join(cap2[-8:])
assert "No such foe" in recent, f"expected 'No such foe', got: {recent}"
print("[PASS] Shen invisible + unfightable below SL rep +3.")

# Grant rep; now he appears.
g2.player.reputation["scarlet_lotus_pavilion"] = 3
say2("look")
recent = "\n".join(cap2[-40:])
assert "Willow-Step Shen" in recent, "Shen should appear at SL rep +3"
print("[PASS] Shen visible once SL rep +3 is held.")


# ---------------------------------------------------------------------------
banner("D. Full quest flow — visit, defeat, deliver")
g, say, q, cap = drive(seed=17)
g.player.realm_id = "qi_condensation"
g.player.completed_quests.add("the_red_path")
g.player.reputation["scarlet_lotus_pavilion"] = 3
# Make the player strong enough to win a scripted combat quickly.
g.player.max_hp = 400; g.player.hp = 400
g.player.atk = 45; g.player.defense = 20; g.player.spd = 20
# Capture starting rewards/rep state BEFORE anything that could complete the quest.
before_stones = g.player.spirit_stones
before_xp = g.player.xp
before_sl_rep = g.player.rep("scarlet_lotus_pavilion")
before_acs_rep = g.player.rep("azure_cloud_sect")
before_jade_rep = g.player.rep("jadestep_remnant")

g.player.location = "scarlet_lotus_shrine"
say("talk elder_red_feather")
assert "the_red_ledger" in g.player.active_quests

# Step 1: visit the terraces.
g.player.location = "hanging_terraces_of_jadestep"
say("look")
assert "hanging_terraces_of_jadestep" in g.player.visited

# Step 2: defeat Shen.
q.extend(["a"] * 40)  # attack spam
say("fight apostate_willow_step_shen")
assert g.player.defeated.get("apostate_willow_step_shen", 0) >= 1, \
    "Shen should be defeated"
# Step 3: collect cipher page — drop is 1.0 so guaranteed.
assert g.player.has_item("apostates_cipher_page"), \
    "Cipher page should drop 100%"
# Because the player talked to Red Feather at accept-time, the talk step is
# already satisfied: progress_quests inside cmd_fight may close the quest as
# soon as the collect satisfies. Either way, it MUST be complete by now.
# (If not yet, a return-and-talk will close it.)
if "the_red_ledger" not in g.player.completed_quests:
    g.player.location = "scarlet_lotus_shrine"
    say("talk elder_red_feather")
assert "the_red_ledger" in g.player.completed_quests, "Quest should complete"
assert "the_red_ledger" not in g.player.active_quests
# Quest gives 280 stones. Shen may also drop a spirit_stone_pouch (variable),
# so the floor is +280.
assert g.player.spirit_stones >= before_stones + 280, \
    f"expected at least +280 stones from quest, got {g.player.spirit_stones - before_stones}"
# Quest gives 120 XP; combat with Shen (xp 110) may also be credited.
assert g.player.xp >= before_xp + 120, \
    f"expected at least +120 xp from quest, got {g.player.xp - before_xp}"
assert g.player.rep("scarlet_lotus_pavilion") == before_sl_rep + 3
assert g.player.rep("azure_cloud_sect") == before_acs_rep - 2
assert g.player.rep("jadestep_remnant") == before_jade_rep - 1
assert g.player.has_item("pond_drinker_sash"), "Reward should include Pond-Drinker Sash"
assert g.player.has_item("crimson_cinnabar_pill"), "Reward should include Crimson Cinnabar Pill"
print("[PASS] Full Red Ledger quest completes with correct rewards + rep deltas.")


# ---------------------------------------------------------------------------
banner("E. companion_reply fires on talk — only for the bound companion")
g, say, q, cap = drive(seed=5)
g.player.realm_id = "qi_condensation"
# Place the player where Red Feather stands, with Jin recruitable conditions.
g.player.completed_quests.add("the_red_path")
g.player.reputation["scarlet_lotus_pavilion"] = 3
g.player.location = "crimson_creek"
say("recruit blood_sworn_jin")
assert g.player.companion is not None and g.player.companion["id"] == "blood_sworn_jin"

# Walk to the shrine and talk to Red Feather. Her companion_reply includes Jin.
g.player.location = "scarlet_lotus_shrine"
cap_before = len(cap)
say("talk elder_red_feather")
talk_out = "\n".join(cap[cap_before:])
# The Jin-specific line about the "third cup" is our marker.
assert "third cup" in talk_out, \
    f"Expected Red Feather's Jin-specific companion_reply; got:\n{talk_out}"

# Now dismiss Jin and talk again — the companion_reply must NOT fire.
say("dismiss")
cap_before = len(cap)
say("talk elder_red_feather")
no_comp = "\n".join(cap[cap_before:])
assert "third cup" not in no_comp, \
    "companion_reply must not fire when no companion is bound"
print("[PASS] companion_reply fires iff the bound companion matches the key.")


# ---------------------------------------------------------------------------
banner("F. A downed companion does NOT trigger companion_reply")
# Re-recruit Jin at his home location.
g.player.location = "crimson_creek"
say("recruit blood_sworn_jin")
assert g.player.companion is not None
# Mark him downed, walk back to the shrine, and talk — the Jin line must not fire.
g.player.companion["downed"] = True
g.player.location = "scarlet_lotus_shrine"
cap_before = len(cap)
say("talk elder_red_feather")
downed_out = "\n".join(cap[cap_before:])
assert "third cup" not in downed_out, \
    "Downed companion should not trigger companion_reply"
print("[PASS] Downed companion silences companion_reply.")


# ---------------------------------------------------------------------------
banner("G. companion_reply on Baixu — verify cross-faction wiring")
g, say, q, cap = drive(seed=11)
g.player.realm_id = "qi_condensation"
g.player.reputation["azure_cloud_sect"] = 3
g.player.completed_quests.add("study_the_sutra")
g.player.location = "azure_cloud_inner_courtyard"
say("recruit disciple_meilin")
assert g.player.companion is not None and g.player.companion["id"] == "disciple_meilin"
# Walk to Baixu's pavilion.
g.player.location = "elder_baixus_pavilion"
cap_before = len(cap)
say("talk elder_baixu")
baixu_out = "\n".join(cap[cap_before:])
assert "Meilin walks at your shoulder" in baixu_out, \
    f"Baixu should address Meilin when she is at the player's side; got:\n{baixu_out}"
print("[PASS] Baixu's companion_reply fires for Meilin.")


print("\nAll Red Ledger + companion_reply smoke-tests passed.")
