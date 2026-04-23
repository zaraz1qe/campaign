#!/usr/bin/env python3
"""Smoke-test for session 17 polish: ANSI colour, inventory grouping,
`where` / `here` command.

Exercises:
  A. Colour is OFF by default when tests construct Game (no ESC in output).
  B. Colour helpers are no-ops when disabled and wrap when enabled.
  C. style.auto_detect honors NO_COLOR and CLICOLOR_FORCE.
  D. `color on` / `color off` toggles work and are marked explicit.
  E. Inventory groups items by type — pills, gear, materials, etc.
  F. Equipped gear shows an [equipped] indicator.
  G. `where` names active quest steps that can progress at the current
     location (visit, talk, collect, defeat) with a helpful hint.
  H. `where` uses a read-only look-ahead so a collect-already-done quest
     still shows the return-talk as actionable at the giver's location.
  I. `where` surfaces NPCs of interest (giver, vendor, teacher, crafter,
     recruitable) and items on the ground + enemies present.
  J. Reputation render uses sect-alignment colours when enabled and
     plain text when disabled.
"""
from __future__ import annotations
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game import style


def fresh(seed=17):
    random.seed(seed)
    # Start with colour off so assertions on raw text are reliable.
    style.auto_detect(force=False)
    cap: list[str] = []
    g = Game(IO(out_func=lambda s="": cap.append(str(s)),
                in_func=lambda p="": "q"))
    return g, cap


def banner(s):
    print()
    print("=" * 70)
    print(s)
    print("=" * 70)


ESC = "\033["


# ---------------------------------------------------------------------------
banner("A. Colour OFF by default in test harness — no ESC sequences emitted")
g, cap = fresh()
assert not style.enabled(), "colour must default to off in tests"
g.player.location = "verdant_bamboo_sea"
g.step("look")
text = "\n".join(cap)
assert ESC not in text, f"expected no ANSI codes in off-mode; got: {text[:200]!r}"
print("[PASS] No ANSI sequences in output when colour is off.")


# ---------------------------------------------------------------------------
banner("B. Colour helpers: no-op when off, wrap when on")
style.auto_detect(force=False)
assert style.npc("Weilan") == "Weilan"
assert style.enemy("Shao") == "Shao"
style.auto_detect(force=True)
assert ESC in style.npc("Weilan"), "npc() must wrap when enabled"
assert "Weilan" in style.npc("Weilan")
assert ESC in style.hp_bar(10, 100), "hp_bar must wrap"
assert ESC in style.quest("[QUEST ACCEPTED]")
# Reset
style.auto_detect(force=False)
print("[PASS] style helpers are no-ops when disabled and wrap when enabled.")


# ---------------------------------------------------------------------------
banner("C. auto_detect honors NO_COLOR and CLICOLOR_FORCE")
# Save and clear env.
saved = {k: os.environ.get(k) for k in ("NO_COLOR", "CLICOLOR", "CLICOLOR_FORCE")}
for k in list(saved):
    os.environ.pop(k, None)

os.environ["NO_COLOR"] = "1"
assert style.auto_detect() is False, "NO_COLOR must force off"
os.environ.pop("NO_COLOR")

os.environ["CLICOLOR_FORCE"] = "1"
assert style.auto_detect() is True, "CLICOLOR_FORCE=1 must force on"
os.environ.pop("CLICOLOR_FORCE")

# Restore
for k, v in saved.items():
    if v is not None:
        os.environ[k] = v
style.auto_detect(force=False)
print("[PASS] auto_detect honors NO_COLOR / CLICOLOR_FORCE.")


# ---------------------------------------------------------------------------
banner("D. `color on` / `color off` toggles and mark explicit")
g, cap = fresh()
assert not style.enabled()
cap.clear()
g.step("color on")
assert style.enabled(), "color on must enable"
assert style.is_explicit(), "color on must mark explicit"
cap.clear()
g.step("color off")
assert not style.enabled(), "color off must disable"
print("[PASS] color command toggles state and marks it explicit.")


# ---------------------------------------------------------------------------
banner("E. Inventory groups items by type")
g, cap = fresh()
# Stuff the sleeves with one of each type.
g.player.add_item("minor_healing_pill", 3)    # pill
g.player.add_item("moon_red_pill", 1)          # pill
g.player.add_item("moonflower_bud", 2)         # material
g.player.add_item("cracked_brass_bell", 1)     # quest
g.player.add_item("azure_cloud_sword", 1)      # weapon
g.player.add_item("blood_petal_mantle", 1)     # armor
g.player.add_item("silent_bell_charm", 1)      # accessory
g.player.add_item("manual_gatekeepers_oath", 1)  # manual
g.player.add_item("crimson_registry", 1)       # treasure
cap.clear()
g.step("inventory")
text = "\n".join(cap)
# Every group header should appear.
for header in ("Weapons", "Robes & Armor", "Accessories",
               "Pills", "Manuals", "Materials",
               "Treasures", "Quest items"):
    assert header in text, f"inventory missing group header {header!r}; got:\n{text}"
# Group header ordering: Weapons before Pills before Materials before Treasures.
w_idx = text.index("Weapons")
p_idx = text.index("Pills")
m_idx = text.index("Materials")
t_idx = text.index("Treasures")
assert w_idx < p_idx < m_idx < t_idx, \
    f"inventory groups out of order: W={w_idx} P={p_idx} M={m_idx} T={t_idx}"
print("[PASS] Inventory groups items by type in the declared order.")


# ---------------------------------------------------------------------------
banner("F. Equipped gear shows [equipped] indicator in inventory")
g, cap = fresh()
g.player.add_item("azure_cloud_sword", 1)
g.player.equipped["weapon"] = "azure_cloud_sword"
cap.clear()
g.step("inventory")
text = "\n".join(cap)
assert "Azure Cloud Sword" in text
assert "[equipped]" in text, f"expected [equipped] indicator; got:\n{text}"
# Non-equipped gear should NOT carry the tag.
g.player.add_item("silent_bell_charm", 1)
cap.clear()
g.step("inventory")
text = "\n".join(cap)
# Find the Silent Bell Charm line — it should not have [equipped].
for line in text.splitlines():
    if "Silent Bell Charm" in line:
        assert "[equipped]" not in line, \
            f"non-equipped gear should not carry tag; got:\n{line}"
print("[PASS] Equipped gear is flagged; non-equipped gear is not.")


# ---------------------------------------------------------------------------
banner("G. `where` names actionable quest steps at the current location")
g, cap = fresh()
g.player.location = "scarlet_lotus_shrine"
g.player.visited.add("scarlet_lotus_shrine")
# Accept Weilan's first quest — step 0 = visit pale_lake_shore.
g.step("talk apothecary_weilan")
# At the shrine, nothing actionable yet.
cap.clear()
g.step("where")
text = "\n".join(cap)
assert "No active quest step resolves here" in text, \
    f"expected no-step at shrine; got:\n{text}"

# Move to Pale Lake Shore — the visit step should be actionable here.
g.player.location = "pale_lake_shore"
g.player.visited.add("pale_lake_shore")
cap.clear()
g.step("where")
text = "\n".join(cap)
assert "A Cup of Sleeping Water" in text, \
    f"quest name must surface; got:\n{text}"
assert "just being here will close this step" in text or \
       "take A Cup of Pale-Lake Silt" in text, \
    f"hint must name the action; got:\n{text}"
print("[PASS] `where` names the actionable quest + hint per location.")


# ---------------------------------------------------------------------------
banner("H. `where` look-ahead surfaces return-talk at giver's location")
g, cap = fresh()
g.player.location = "scarlet_lotus_shrine"
g.player.visited.add("scarlet_lotus_shrine")
g.step("talk apothecary_weilan")
# Go pick up silt. This satisfies visit + collect but the engine waits on
# the return-talk to close the quest.
g.player.location = "pale_lake_shore"
g.player.visited.add("pale_lake_shore")
g.step("take pale_lake_silt")
# Return to the shrine; the where command should now cue the talk.
g.player.location = "scarlet_lotus_shrine"
cap.clear()
g.step("where")
text = "\n".join(cap)
assert "A Cup of Sleeping Water" in text, \
    f"where must show the still-active quest; got:\n{text}"
assert "talk to Weilan" in text, \
    f"where look-ahead must cue the return-talk; got:\n{text}"
print("[PASS] `where` look-ahead shows return-talk when all prior steps satisfied.")


# ---------------------------------------------------------------------------
banner("I. `where` surfaces people of interest + items + threats")
g, cap = fresh()
g.player.location = "bandit_road"
g.player.visited.add("bandit_road")
cap.clear()
g.step("where")
text = "\n".join(cap)
# Rulan is a quest-giver and stands on the Bandit Road (at some rep states).
# Bandit Road has enemies including Bannerman Shao.
assert "Threats" in text, f"where must flag threats; got:\n{text}"
assert "Black Banner" in text, f"expected enemy names surfaced; got:\n{text}"

# Vendor + teacher detection — Merchant Crossing has Pillmaster Lu (sells)
# and Cloth Merchant Mei (sells).
g.player.location = "merchant_crossing"
g.player.visited.add("merchant_crossing")
cap.clear()
g.step("where")
text = "\n".join(cap)
assert "sells" in text, f"where must flag vendors with 'sells'; got:\n{text}"
assert "People of interest" in text
print("[PASS] `where` surfaces people of interest, threats, ground items.")


# ---------------------------------------------------------------------------
banner("J. Reputation render uses color helpers when enabled (and not otherwise)")
g, cap = fresh()
g.player.reputation["scarlet_lotus_pavilion"] = 3
g.player.reputation["azure_cloud_sect"] = -2
# Off: plain text, no ESC.
style.auto_detect(force=False)
cap.clear()
g.step("reputation")
text_off = "\n".join(cap)
assert ESC not in text_off, "no colour codes when off"
assert "Scarlet Lotus Pavilion" in text_off
assert "+3" in text_off and "-2" in text_off

# On: ESC present, but the underlying names/numbers still substring-findable.
style.auto_detect(force=True)
cap.clear()
g.step("reputation")
text_on = "\n".join(cap)
assert ESC in text_on, "colour codes must be present when on"
assert "Scarlet Lotus Pavilion" in text_on
# "+3" is still present as substring inside the coloured wrap.
assert "+3" in text_on and "-2" in text_on
style.auto_detect(force=False)
print("[PASS] reputation renders cleanly off and colorised on.")


# ---------------------------------------------------------------------------
print()
print("All colour / inventory / where smoke-tests passed.")
