#!/usr/bin/env python3
"""Scripted smoke-test for the Chronicler's Eye lore-reward layer.

Exercises:
  A. on_defeat_lore: defeating Willow-Step Shen records the_willow_step_cut.
  B. on_defeat_lore is silent on the second defeat (already known).
  C. grants_lore: completing The Kettle's Request records song_of_the_bamboo.
  D. lore_dialogue: Elder Baixu records the_azure_succession_dispute when
     ACS rep >= 5, but not below that threshold.
  E. lore_dialogue grants the HIGHEST met threshold (Shan at FPS +3 gives
     legend_of_the_first_poisoner; at +5 she gives the_five_poisons_refusal).
  F. read / lore command output: pre-grant state shows 0/total; post-grant
     shows the newly recorded title grouped by category.
  G. Save/load round-trip: known_lore persists.
  H. The new lore entries file loads and registers against the world.
"""
from __future__ import annotations
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game.state import Player


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
banner("H. New lore entries load and register")
g, *_ = drive()
for lid in ("the_azure_succession_dispute", "mingshus_last_silence",
            "the_pavilions_four_reasons", "the_five_poisons_refusal",
            "the_eight_point_star_ledger", "the_terrace_dancers"):
    assert lid in g.world["lore"], f"new lore entry '{lid}' failed to load"
print(f"[PASS] All 6 new lore entries loaded. Total lore: {len(g.world['lore'])}")


# ---------------------------------------------------------------------------
banner("A. on_defeat_lore — defeating Shen records the_willow_step_cut")
g, say, q, cap = drive(seed=17)
g.player.realm_id = "qi_condensation"
g.player.reputation["scarlet_lotus_pavilion"] = 3
g.player.max_hp = 400; g.player.hp = 400
g.player.atk = 45; g.player.defense = 20; g.player.spd = 20
g.player.location = "hanging_terraces_of_jadestep"
assert "the_willow_step_cut" not in g.player.known_lore
q.extend(["a"] * 40)
say("fight apostate_willow_step_shen")
assert g.player.defeated.get("apostate_willow_step_shen", 0) >= 1
assert "the_willow_step_cut" in g.player.known_lore, \
    "Defeating Shen must grant the_willow_step_cut"
# The announcement must have printed.
joined = "\n".join(cap[-60:])
assert "Lore recorded" in joined, \
    f"Lore announcement should appear in output; got tail:\n{joined[-600:]}"
print("[PASS] Shen's defeat grants the Willow-Step Cut lore with announcement.")


# ---------------------------------------------------------------------------
banner("B. on_defeat_lore is silent on already-known lore")
# Shen is auto-respawned (enemy list unchanged). Fight him again.
before_cap_len = len(cap)
q.extend(["a"] * 40)
say("fight apostate_willow_step_shen")
assert g.player.defeated.get("apostate_willow_step_shen", 0) >= 2
fresh = "\n".join(cap[before_cap_len:])
# No new lore-recorded announcement on the second fight.
assert "Lore recorded" not in fresh, \
    f"Second fight must not re-announce known lore; got:\n{fresh[-600:]}"
print("[PASS] Second defeat silent — known lore not re-announced.")


# ---------------------------------------------------------------------------
banner("C. grants_lore — Kettle's Request grants song_of_the_bamboo")
g, say, q, cap = drive(seed=3)
g.player.max_hp = 200; g.player.hp = 200
g.player.atk = 30; g.player.defense = 8; g.player.spd = 12
assert "song_of_the_bamboo" not in g.player.known_lore
# Accept quest at the hermit's hut.
g.player.location = "old_hermits_hut"
say("talk old_hermit_yun")
assert "the_kettles_request" in g.player.active_quests
# Defeat a bamboo_viper at the bamboo sea.
g.player.location = "verdant_bamboo_sea"
q.extend(["a"] * 40)
say("fight bamboo_viper")
assert g.player.defeated.get("bamboo_viper", 0) >= 1
# Return to Yun.
g.player.location = "old_hermits_hut"
say("talk old_hermit_yun")
assert "the_kettles_request" in g.player.completed_quests, \
    "Kettle's Request should be completed"
assert "song_of_the_bamboo" in g.player.known_lore, \
    "Completing the quest should grant song_of_the_bamboo"
joined = "\n".join(cap[-40:])
assert "Song of the Bamboo" in joined, \
    f"Quest-complete output should announce the lore; got:\n{joined[-400:]}"
print("[PASS] Quest completion grants song_of_the_bamboo with announcement.")


# ---------------------------------------------------------------------------
banner("D. lore_dialogue — Baixu shares succession story at ACS +5")
g, say, q, cap = drive(seed=9)
g.player.location = "elder_baixus_pavilion"
# ACS rep 0 — no trust, no lore.
assert "the_azure_succession_dispute" not in g.player.known_lore
say("talk elder_baixu")
assert "the_azure_succession_dispute" not in g.player.known_lore, \
    "Must not grant lore_dialogue below threshold"
# Bump to +5. Talk again.
g.player.reputation["azure_cloud_sect"] = 5
before_cap_len = len(cap)
say("talk elder_baixu")
assert "the_azure_succession_dispute" in g.player.known_lore, \
    "At ACS +5, Baixu must grant the_azure_succession_dispute"
fresh = "\n".join(cap[before_cap_len:])
assert "Lore recorded" in fresh, \
    f"Lore announcement should appear on talk; got:\n{fresh[-500:]}"
# Third talk — already known, silent.
before_cap_len = len(cap)
say("talk elder_baixu")
fresh = "\n".join(cap[before_cap_len:])
assert "Lore recorded" not in fresh, \
    "Re-talk must not re-announce an already-known lore"
print("[PASS] Baixu's lore_dialogue fires exactly once, at threshold.")


# ---------------------------------------------------------------------------
banner("E. lore_dialogue picks the HIGHEST met positive threshold")
g, say, q, cap = drive(seed=12)
g.player.location = "five_poisons_hall"
# At FPS +3 → legend_of_the_first_poisoner
g.player.reputation["five_poisons_sect"] = 3
say("talk matriarch_shan")
assert "legend_of_the_first_poisoner" in g.player.known_lore, \
    "At FPS +3, Shan grants the legend_of_the_first_poisoner"
assert "the_five_poisons_refusal" not in g.player.known_lore, \
    "At FPS +3, Shan should NOT grant the +5-threshold lore yet"
# Bump to +5. The new ceiling gives the higher-tier lore now.
g.player.reputation["five_poisons_sect"] = 5
say("talk matriarch_shan")
assert "the_five_poisons_refusal" in g.player.known_lore, \
    "At FPS +5, Shan grants the five refusals"
print("[PASS] Highest met threshold wins; lower-tier lore still known.")


# ---------------------------------------------------------------------------
banner("F. `read` command groups by category and shows total counter")
g, say, q, cap = drive(seed=2)
before_cap_len = len(cap)
say("read")
fresh = "\n".join(cap[before_cap_len:])
assert "0 / " in fresh and "known" in fresh, \
    f"Empty-lore readout should show 0/total; got:\n{fresh}"
# Grant two entries and re-read.
g.player.known_lore.add("song_of_the_bamboo")
g.player.known_lore.add("fall_of_jadestep")
before_cap_len = len(cap)
say("read")
fresh = "\n".join(cap[before_cap_len:])
assert "2 /" in fresh, f"Should show '2 / total'; got:\n{fresh}"
assert "-- poem --" in fresh or "poem" in fresh, \
    f"Category grouping missing; got:\n{fresh}"
assert "Song of the Bamboo" in fresh, \
    f"Title should appear; got:\n{fresh}"
# Read a specific entry.
before_cap_len = len(cap)
say("read fall_of_jadestep")
fresh = "\n".join(cap[before_cap_len:])
assert "Fall of the Jadestep" in fresh and "[history]" in fresh, \
    f"Specific read should show title and category tag; got:\n{fresh}"
print("[PASS] read shows grouped index and tagged entries.")


# ---------------------------------------------------------------------------
banner("G. known_lore persists across save/load")
g.player.name = "Test"
blob = g.player.to_json()
restored = Player.from_json(blob)
assert "song_of_the_bamboo" in restored.known_lore
assert "fall_of_jadestep" in restored.known_lore
# Also: a save from before this session (no lore-earning fields) still loads.
legacy_blob = json.dumps({"name": "Legacy"})  # minimum skeleton
legacy = Player.from_json(legacy_blob)
assert legacy.known_lore == set(), "legacy save should default to empty"
print("[PASS] known_lore round-trips; legacy saves load cleanly.")


# ---------------------------------------------------------------------------
banner("I. gale tiger grants fall_of_jadestep on defeat")
g, say, q, cap = drive(seed=21)
g.player.realm_id = "core_formation"
g.player.max_hp = 1200; g.player.hp = 1200
g.player.atk = 120; g.player.defense = 30; g.player.spd = 25
g.player.location = "spirit_gale_plateau"
assert "fall_of_jadestep" not in g.player.known_lore
q.extend(["a"] * 60)
say("fight heart_devouring_gale_tiger")
assert g.player.defeated.get("heart_devouring_gale_tiger", 0) >= 1, \
    "Tiger should fall"
assert "fall_of_jadestep" in g.player.known_lore, \
    "Gale tiger defeat must grant fall_of_jadestep"
print("[PASS] Gale Tiger defeat grants Fall of Jadestep.")


print("\nAll Chronicler's Eye lore smoke-tests passed.")
