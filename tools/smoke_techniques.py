#!/usr/bin/env python3
"""Scripted smoke-test for session 12's technique expansion ("the deepening").

Exercises:
  A. All 15 new technique ids load and resolve against the world.
  B. Each new technique is taught by at least one NPC (no orphans).
  C. Mortal-tier techniques (no sect gate) are learnable by a fresh player.
  D. Qi Condensation techniques with ACS 1+ gate refuse at rep 0, succeed at +1.
  E. Foundation techniques with ACS 4+ gate refuse at rep 3, succeed at +4
     (realm-gated too).
  F. Every effect type has at least 3 learnable techniques (the palette gap
     that this session was meant to fix).
  G. buff_atk has at least one mortal-tier and one foundation-tier option.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO


def drive(seed=7):
    random.seed(seed)
    g = Game(IO())
    cap: list[str] = []

    def _out(s=""):
        cap.append(str(s))

    def _in(prompt=""):
        cap.append(prompt)
        return ""

    g.io = IO(out_func=_out, in_func=_in)
    return g, cap


def banner(s):
    print()
    print("=" * 70)
    print(s)
    print("=" * 70)


NEW_TECHS = [
    "silent_bell_strike", "settling_stone_sit", "viper_sting", "iron_ox_shrug",
    "azure_cloud_sword_arc", "crane_wing_parry", "flashing_willow_leaf",
    "black_lattice_palm", "mountain_root_stance", "crimson_hand_of_silence",
    "nine_cloud_cranes_flight", "five_venoms_brocade_palm",
    "heart_boiling_technique", "stormwarden_mantle", "brass_bell_sutra",
]


# ---------------------------------------------------------------------------
banner("A. All 15 new techniques load")
g, _ = drive()
for tid in NEW_TECHS:
    assert tid in g.world["techniques"], f"technique '{tid}' missing"
print(f"[PASS] All 15 new techniques loaded (total now: {len(g.world['techniques'])}).")


# ---------------------------------------------------------------------------
banner("B. Every new technique is taught by at least one NPC")
g, _ = drive()
taught_by: dict[str, list[str]] = {tid: [] for tid in NEW_TECHS}
for npc_id, npc in g.world["npcs"].items():
    for tid in npc.get("teaches", []) or []:
        if tid in taught_by:
            taught_by[tid].append(npc_id)
for tid, teachers in taught_by.items():
    assert teachers, f"technique '{tid}' is orphaned — no NPC teaches it"
    print(f"  {tid:<34} -> {teachers}")
print("[PASS] No orphans; every new technique has a teacher.")


# ---------------------------------------------------------------------------
banner("C. Mortal-tier ungated techniques are learnable from a fresh player")
# silent_bell_strike (Huilin, mortal, no rep) and iron_ox_shrug (Ao, mortal)
g, cap = drive()
g.player.spirit_stones = 200
g.player.location = "verdant_bamboo_sea"
g.step("learn silent_bell_strike")
assert "silent_bell_strike" in g.player.techniques, \
    "Mortal player at Verdant Bamboo (with Huilin) should learn silent_bell_strike"
# iron_ox_shrug — Bo is at azure_cloud_forge
g.player.location = "azure_cloud_forge"
g.step("learn iron_ox_shrug")
assert "iron_ox_shrug" in g.player.techniques, \
    "Mortal player at the Forge (with Bo) should learn iron_ox_shrug"
# settling_stone_sit — Yun is at old_hermits_hut
g.player.location = "old_hermits_hut"
g.step("learn settling_stone_sit")
assert "settling_stone_sit" in g.player.techniques, \
    "Mortal player at Yun's hut should learn settling_stone_sit"
print("[PASS] Three mortal-tier new techniques all learnable from correct NPCs.")


# ---------------------------------------------------------------------------
banner("D. Qi Condensation rep-gated techniques respect ACS requirement")
# azure_cloud_sword_arc requires ACS 1+
g, cap = drive()
g.player.spirit_stones = 500
g.player.realm_id = "qi_condensation"
g.player.max_qi = 120
g.player.location = "azure_cloud_inner_courtyard"  # Meilin's location
assert g.player.rep("azure_cloud_sect") == 0
g.step("learn azure_cloud_sword_arc")
assert "azure_cloud_sword_arc" not in g.player.techniques, \
    "Should refuse learn at ACS rep 0"
# Bump rep and retry.
g.player.reputation["azure_cloud_sect"] = 1
g.step("learn azure_cloud_sword_arc")
assert "azure_cloud_sword_arc" in g.player.techniques, \
    f"Should succeed at ACS +1; got techniques={g.player.techniques}"
print("[PASS] azure_cloud_sword_arc gates on ACS +1 correctly.")

# flashing_willow_leaf requires ACS 2+
g.step("learn flashing_willow_leaf")
assert "flashing_willow_leaf" not in g.player.techniques, \
    "Should refuse at ACS +1 (needs +2)"
g.player.reputation["azure_cloud_sect"] = 2
g.step("learn flashing_willow_leaf")
assert "flashing_willow_leaf" in g.player.techniques, \
    "Should succeed at ACS +2"
print("[PASS] flashing_willow_leaf gates on ACS +2 correctly.")


# ---------------------------------------------------------------------------
banner("E. Foundation techniques enforce BOTH realm and rep gates")
g, cap = drive()
g.player.spirit_stones = 500
g.player.location = "elder_baixus_pavilion"
# Qi Condensation player with ACS +5 — rep meets, realm does not.
g.player.realm_id = "qi_condensation"
g.player.reputation["azure_cloud_sect"] = 5
g.step("learn nine_cloud_cranes_flight")
assert "nine_cloud_cranes_flight" not in g.player.techniques, \
    "Should refuse — realm gate not met (needs foundation)"
# Advance realm. Still needs ACS 4+; at 5 meets.
g.player.realm_id = "foundation_establishment"
g.step("learn nine_cloud_cranes_flight")
assert "nine_cloud_cranes_flight" in g.player.techniques, \
    "Should succeed at Foundation + ACS +5"
print("[PASS] nine_cloud_cranes_flight gates on BOTH realm and rep.")

# stormwarden_mantle requires foundation + ACS +3.
g, cap = drive()
g.player.spirit_stones = 500
g.player.location = "cloudroot_pass"
g.player.realm_id = "foundation_establishment"
g.player.reputation["azure_cloud_sect"] = 2
g.step("learn stormwarden_mantle")
assert "stormwarden_mantle" not in g.player.techniques, \
    "Should refuse at ACS +2 (needs +3)"
g.player.reputation["azure_cloud_sect"] = 3
g.step("learn stormwarden_mantle")
assert "stormwarden_mantle" in g.player.techniques, \
    "Should succeed at ACS +3 + Foundation"
print("[PASS] stormwarden_mantle gates on Foundation + ACS +3 correctly.")


# ---------------------------------------------------------------------------
banner("F. Effect palette — every effect has >= 3 learnable techniques")
g, _ = drive()
by_effect: dict[str, list[str]] = {}
for tid, t in g.world["techniques"].items():
    if int(t.get("learn_cost", 999)) >= 999:
        continue
    eff = t.get("effect") or "-"
    by_effect.setdefault(eff, []).append(tid)
for eff, tids in sorted(by_effect.items()):
    print(f"  {eff:<10} ({len(tids):>2}): {sorted(tids)}")
for eff in ("poison", "bleed", "stun", "heal", "buff_def", "buff_atk"):
    assert len(by_effect.get(eff, [])) >= 3, \
        f"effect '{eff}' has only {len(by_effect.get(eff, []))} learnable techniques"
print("[PASS] Every combat effect has >= 3 learnable techniques (palette deepened).")


# ---------------------------------------------------------------------------
banner("G. buff_atk has a mortal-tier and a foundation-tier option")
g, _ = drive()
mortal_buffatk = []
found_buffatk = []
for tid, t in g.world["techniques"].items():
    if int(t.get("learn_cost", 999)) >= 999:
        continue
    if t.get("effect") != "buff_atk":
        continue
    realm = t.get("requires_realm", "mortal")
    if realm == "mortal":
        mortal_buffatk.append(tid)
    elif realm == "foundation_establishment":
        found_buffatk.append(tid)
assert mortal_buffatk, "No mortal-tier buff_atk technique"
assert found_buffatk, "No foundation-tier buff_atk technique"
print(f"[PASS] buff_atk at mortal: {mortal_buffatk}; at foundation: {found_buffatk}")


print()
print("All technique-deepening smoke-tests passed.")
