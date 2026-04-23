#!/usr/bin/env python3
"""Scripted smoke-test for the Willowmere starter hub (session 12).

Exercises:
  A. Region loads — every new location/npc/enemy/item id resolves.
  B. Western exit from Verdant Bamboo Sea reaches the village square.
  C. Little Yu's Songbird — Lady Moonbell at Old Hermit's hut; pick it up,
     return, quest completes end-to-end with reward + lore grant.
  D. Errand of the Drowned Willow — visit shrine, collect moonflower,
     return to Mingzhu, quest completes with reward + lore grant.
  E. Bottle for the Corner Table — quest auto-offers from Kuo, completes
     on rice-wine purchase + return-talk, reward includes Drunken Step Sash.
  F. The Wolves at Shen's Farm — auto-offer from Headman, completes via
     visit + defeat(grey_pack_alpha) + talk. Rep +1 ACS applied.
  G. Three Ingots of River-Iron — collect x3 river-iron + talk, reward is
     Ao's River Blade, quest rep-neutral.
  H. Save/load round-trip with active Willowmere quest state + inventory.
"""
from __future__ import annotations
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
banner("A. Willowmere region loads — every id resolves")
g, *_ = drive()
for lid in ("willowmere_village_square", "willow_and_moon_teahouse",
            "willowmere_smithy", "shen_homestead", "pale_lake_shore",
            "drowned_willow_shrine"):
    assert lid in g.world["locations"], f"location '{lid}' missing"
for nid in ("headman_lu_pingan", "herbalist_mingzhu", "little_yu",
            "matron_weiyu", "drunken_rogue_kuo", "blacksmith_ao",
            "farmer_shen_daiyu", "fisher_ren"):
    assert nid in g.world["npcs"], f"npc '{nid}' missing"
for eid in ("grey_forest_wolf", "grey_pack_alpha",
            "pale_lake_carp_spirit", "drowned_willow_revenant"):
    assert eid in g.world["enemies"], f"enemy '{eid}' missing"
for qid in ("wolves_at_shens_farm", "the_lost_songbird",
            "the_river_iron", "errand_of_the_drowned_willow",
            "bottle_for_the_corner_table"):
    assert qid in g.world["quests"], f"quest '{qid}' missing"
for iid in ("iron_cleaver", "willowmere_cordial", "aos_river_blade",
            "drunken_step_sash", "lady_moonbell", "moonflower_bud",
            "river_iron_ingot", "alpha_wolf_heart"):
    assert iid in g.world["items"], f"item '{iid}' missing"
for tid in ("drunken_step", "willow_root_stance", "farmhands_cleave"):
    assert tid in g.world["techniques"], f"technique '{tid}' missing"
for loreid in ("why_willowmere_forgot_its_name",
               "the_drowning_of_the_willow",
               "the_tune_with_the_last_note_different",
               "tea_mothers_ledger"):
    assert loreid in g.world["lore"], f"lore '{loreid}' missing"
print(f"[PASS] Willowmere region loaded. "
      f"{len(g.world['locations'])} locations, "
      f"{len(g.world['npcs'])} npcs, {len(g.world['quests'])} quests.")


# ---------------------------------------------------------------------------
banner("B. Western exit from Verdant Bamboo Sea reaches Willowmere")
g, say, q, cap = drive()
assert g.player.location == "verdant_bamboo_sea"
bamboo = g.world["locations"]["verdant_bamboo_sea"]
assert bamboo["exits"].get("west") == "willowmere_village_square", \
    "Bamboo Sea must have west exit to Willowmere"
say("go west")
assert g.player.location == "willowmere_village_square", \
    f"go west should land at the square; at {g.player.location}"
print("[PASS] Verdant Bamboo Sea → west → Willowmere Village Square.")


# ---------------------------------------------------------------------------
banner("C. Songbird quest — pick up Lady Moonbell + return to Yu")
g, say, q, cap = drive()
assert "lady_moonbell" in g.world["locations"]["old_hermits_hut"]["items_on_ground"], \
    "Lady Moonbell must be on the ground at Old Hermit's hut"
assert "the_lost_songbird" not in g.player.completed_quests
# Accept quest.
g.player.location = "willowmere_village_square"
say("talk little_yu")
assert "the_lost_songbird" in g.player.active_quests, "Talking to Yu should offer the quest"
# Fetch the bird.
g.player.location = "old_hermits_hut"
say("look")
say("take lady_moonbell")
assert g.player.has_item("lady_moonbell"), "Player should have picked up Lady Moonbell"
# Return and talk — auto-completes via talked_to set.
g.player.location = "willowmere_village_square"
say("talk little_yu")
assert "the_lost_songbird" in g.player.completed_quests, \
    "Returning with the bird should complete the quest"
assert "the_tune_with_the_last_note_different" in g.player.known_lore, \
    "Quest completion should grant the tune lore"
print("[PASS] Songbird quest ran end-to-end; lore granted.")


# ---------------------------------------------------------------------------
banner("D. Drowned Willow Errand — moonflower on ground + return")
g, say, q, cap = drive()
g.player.location = "willowmere_village_square"
say("talk herbalist_mingzhu")
assert "errand_of_the_drowned_willow" in g.player.active_quests
# Walk to shrine.
g.player.location = "pale_lake_shore"
say("go west")
assert g.player.location == "drowned_willow_shrine"
say("look")
say("take moonflower_bud")
assert g.player.has_item("moonflower_bud"), "Should have picked up moonflower bud"
# Return.
g.player.location = "willowmere_village_square"
say("talk herbalist_mingzhu")
assert "errand_of_the_drowned_willow" in g.player.completed_quests
assert "the_drowning_of_the_willow" in g.player.known_lore, \
    "Errand completion should grant the drowning lore"
# Reward check — 2 moonflower tonics + 1 cordial.
assert g.player.has_item("moonflower_tonic", 2), "Should have 2 moonflower tonics"
assert g.player.has_item("willowmere_cordial", 1), "Should have 1 cordial"
print("[PASS] Drowned Willow errand ran end-to-end; reward + lore delivered.")


# ---------------------------------------------------------------------------
banner("E. Bottle for the Corner Table — rice wine + return to Kuo")
g, say, q, cap = drive()
g.player.location = "willowmere_village_square"
say("go in")
assert g.player.location == "willow_and_moon_teahouse"
say("talk drunken_rogue_kuo")
assert "bottle_for_the_corner_table" in g.player.active_quests, \
    "Kuo should offer the bottle quest on talk"
# Give the player enough stones to afford rice wine.
g.player.spirit_stones = 50
say("buy willowmere_rice_wine")
assert g.player.has_item("willowmere_rice_wine"), "Player should hold rice wine"
# Return-talk to Kuo.
say("talk drunken_rogue_kuo")
assert "bottle_for_the_corner_table" in g.player.completed_quests
assert g.player.has_item("drunken_step_sash"), \
    "Reward: Drunken Step Sash should be in inventory"
print("[PASS] Bottle quest ran end-to-end; Drunken Step Sash awarded.")


# ---------------------------------------------------------------------------
banner("F. Wolves at Shen's Farm — visit + defeat alpha + talk")
g, say, q, cap = drive(seed=11)
# Make the player strong enough to kill the alpha without dying.
g.player.max_hp = 300; g.player.hp = 300
g.player.atk = 60; g.player.defense = 20; g.player.spd = 20
g.player.realm_id = "qi_condensation"
# Accept quest at the square.
g.player.location = "willowmere_village_square"
say("talk headman_lu_pingan")
assert "wolves_at_shens_farm" in g.player.active_quests
# Walk north, fight the alpha.
say("go north")
assert g.player.location == "shen_homestead"
before_rep = g.player.rep("azure_cloud_sect")
q.extend(["a"] * 40)
say("fight grey_pack_alpha")
assert g.player.defeated.get("grey_pack_alpha", 0) >= 1, \
    "Alpha should be defeated"
# Return to Pingan.
g.player.location = "willowmere_village_square"
say("talk headman_lu_pingan")
assert "wolves_at_shens_farm" in g.player.completed_quests, \
    "Returning after alpha-kill should complete the quest"
assert "why_willowmere_forgot_its_name" in g.player.known_lore, \
    "Quest should grant the village-name lore"
after_rep = g.player.rep("azure_cloud_sect")
assert after_rep - before_rep == 1, \
    f"Wolves quest should grant +1 ACS rep (got {after_rep - before_rep})"
print(f"[PASS] Wolves quest ran end-to-end; "
      f"+{after_rep - before_rep} ACS rep; lore granted.")


# ---------------------------------------------------------------------------
banner("G. Three Ingots of River-Iron — collect x3 + talk")
g, say, q, cap = drive(seed=4)
g.player.location = "willowmere_village_square"
say("go smithy")
assert g.player.location == "willowmere_smithy"
say("talk blacksmith_ao")
assert "the_river_iron" in g.player.active_quests
# Granting 3 ingots directly (drop-rate grinding is too flaky to script).
g.player.add_item("river_iron_ingot", 3)
say("talk blacksmith_ao")
assert "the_river_iron" in g.player.completed_quests
assert g.player.has_item("aos_river_blade"), \
    "Reward: Ao's River Blade should be in inventory"
# Rep neutral.
assert g.player.rep("azure_cloud_sect") == 0, \
    "River-iron quest should not move any sect rep"
print("[PASS] River-iron quest ran end-to-end; River Blade awarded.")


# ---------------------------------------------------------------------------
banner("H. Save/load round-trip with active Willowmere state")
g, say, q, cap = drive()
g.player.location = "willowmere_village_square"
say("talk headman_lu_pingan")
say("talk little_yu")
g.player.add_item("willowmere_rice_wine", 1)
g.player.add_item("river_iron_ingot", 2)
g.player.known_lore.add("why_willowmere_forgot_its_name")
g.player.reputation["azure_cloud_sect"] = 2
# Round-trip through JSON.
blob = g.player.to_json()
p2 = Player.from_json(blob)
assert p2.location == "willowmere_village_square"
assert "wolves_at_shens_farm" in p2.active_quests
assert "the_lost_songbird" in p2.active_quests
assert p2.has_item("willowmere_rice_wine")
assert p2.has_item("river_iron_ingot", 2)
assert "why_willowmere_forgot_its_name" in p2.known_lore
assert p2.rep("azure_cloud_sect") == 2
print("[PASS] Save/load round-trip preserves all Willowmere-side state.")


print()
print("All Willowmere smoke-tests passed.")
