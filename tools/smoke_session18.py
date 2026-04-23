#!/usr/bin/env python3
"""Smoke-test for session 18 UX polish: coloured combat bars, compass
overlay on look, `saves` slot listing, and the `status` unfinished-
business block.

Exercises:
  A. `_print_bar` wraps HP bar glyphs in green/yellow/red bands by
     fraction when colour is on; passes through plain when off.
  B. Combat's status summary still contains timer counters for
     poison/bleed/stun/buff_atk/buff_def.
  C. `look` renders a compass overlay naming cardinal neighbours.
  D. Compass folds up/down onto N/S (matches map renderer).
  E. A location with no cardinal exits renders no compass.
  F. `saves` prints slot / name / realm / location / timestamp for
     every slot on disk.
  G. `saves` on a fresh box with no slots prints a friendly empty-state.
  H. `status` appends an "Unfinished business" block listing next-step
     hints for active quests, using the same read-only look-ahead as
     `where` so a ready-to-close quest shows its giver-talk.
  I. `status` omits the block when the player has no active quests.
"""
from __future__ import annotations
import os
import random
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO, SAVE_DIR
from game import style, combat


def fresh(seed=18):
    random.seed(seed)
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
banner("A. combat._print_bar colour bands by HP fraction")
# Colour off — plain text.
style.auto_detect(force=False)
plain = combat._print_bar("X", 30, 30)
assert ESC not in plain, f"no colour when off; got {plain!r}"
assert "30/30" in plain

# Colour on — glyphs wrapped with SGR. Green for high, yellow mid, red low.
style.auto_detect(force=True)
high = combat._print_bar("X", 30, 30)
mid  = combat._print_bar("X", 15, 30)
low  = combat._print_bar("X", 3, 30)
assert style.BRIGHT_GREEN in high, f"high should be green; got {high!r}"
assert style.BRIGHT_YELLOW in mid, f"mid should be yellow; got {mid!r}"
assert style.BRIGHT_RED in low, f"low should be red; got {low!r}"
style.auto_detect(force=False)
print("[PASS] _print_bar colours the fill by HP fraction.")


# ---------------------------------------------------------------------------
banner("B. _status_summary preserves timer counters (DoT/stun/buff)")
st = [
    {"type": "poison", "power": 2, "turns_left": 3},
    {"type": "stun",   "power": 1, "turns_left": 1},
    {"type": "buff_atk", "power": 3, "turns_left": 2},
]
text = combat._status_summary(st)
assert "poison 2/3t" in text, f"poison timer missing; got {text!r}"
assert "stunned 1t" in text, f"stun timer missing; got {text!r}"
assert "+3 ATK (2t)" in text, f"buff timer missing; got {text!r}"
print("[PASS] status summary surfaces timer counters for each kind.")


# ---------------------------------------------------------------------------
banner("C. `look` renders compass overlay with cardinal neighbour names")
g, cap = fresh()
# Verdant Bamboo Sea has N/S/E/W neighbours. Place there and look.
g.player.location = "verdant_bamboo_sea"
cap.clear()
g.step("look")
text = "\n".join(cap)
# Compass lines use direction tags. At least N, W, E, S should appear.
# Each direction tag renders as "N:", "W:", "E:", "S:" somewhere in
# output. The precise surrounding characters depend on colour state;
# substring on the tag itself is the stable shape.
assert "N:" in text, f"compass missing N; got:\n{text}"
assert "S:" in text, f"compass missing S; got:\n{text}"
assert "E:" in text, f"compass missing E; got:\n{text}"
assert "W:" in text, f"compass missing W; got:\n{text}"
# And the neighbour names should surface in the compass block.
assert "Azure Cloud Foothills" in text
assert "River of Swords" in text
print("[PASS] Compass overlay renders N/S/E/W with neighbour names.")


# ---------------------------------------------------------------------------
banner("D. Compass folds up/down onto N/S")
g, cap = fresh()
# Thunderhead Ridge: down → Jadestep, up → Spirit-Gale Plateau.
g.player.location = "thunderhead_ridge"
cap.clear()
g.step("look")
text = "\n".join(cap)
# With up/down folded onto N/S, the compass should show both directions.
assert "N:" in text, f"up should fold onto N; got:\n{text}"
assert "S:" in text, f"down should fold onto S; got:\n{text}"
assert "Spirit-Gale Plateau" in text
assert "Hanging Terraces of Jadestep" in text
print("[PASS] up/down fold onto N/S on the compass.")


# ---------------------------------------------------------------------------
banner("E. No cardinal exits -> no compass")
g, cap = fresh()
# Azure Cloud Library's only exit is `out` → Inner Courtyard. No cardinals.
g.player.location = "azure_cloud_library"
cap.clear()
g.step("look")
text = "\n".join(cap)
# No direction tags should appear in compass form. (But the word "out"
# appears in the "Exits:" line, which is fine.)
# Our compass uses bare "N:" / "S:" / "E:" / "W:" tokens; those must NOT
# be present here.
for tag in ("N:", "S:", "E:", "W:"):
    assert tag not in text, \
        f"no compass expected at library; got {tag} in:\n{text}"
print("[PASS] No compass when there are no cardinal exits.")


# ---------------------------------------------------------------------------
banner("F. `saves` lists slot / name / realm / location / timestamp")
# Isolate save dir manipulation with a try/finally sweep.
existing = list(SAVE_DIR.glob("*.json"))
moved: list[tuple[Path, Path]] = []
try:
    # Move existing saves aside.
    for p in existing:
        bak = p.with_suffix(".json.bak_s18")
        p.rename(bak)
        moved.append((p, bak))

    g, cap = fresh()
    g.player.name = "Testborn"
    g.player.location = "verdant_bamboo_sea"
    cap.clear()
    g.step("save demo_a")
    g.player.name = "Second"
    g.player.location = "scarlet_lotus_shrine"
    g.step("save demo_b")
    cap.clear()
    g.step("saves")
    text = "\n".join(cap)
    assert "Save slots (2)" in text, f"expected two-slot header; got:\n{text}"
    assert "demo_a" in text and "demo_b" in text
    assert "Testborn" in text and "Second" in text
    assert "Verdant Bamboo Sea" in text
    assert "Scarlet Lotus Hidden Shrine" in text
    assert "Mortal" in text  # both saves are at mortal realm
    # Timestamp format YYYY-MM-DD HH:MM
    assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", text), \
        f"expected timestamp; got:\n{text}"

    # Clean up the two demo saves before restoring.
    for slot in ("demo_a", "demo_b"):
        (SAVE_DIR / f"{slot}.json").unlink(missing_ok=True)

    # G: Empty-state message when no saves exist.
    g, cap = fresh()
    cap.clear()
    g.step("saves")
    text = "\n".join(cap)
    assert "No save slots yet" in text, \
        f"expected empty-state message; got:\n{text}"
finally:
    # Restore moved saves.
    for orig, bak in moved:
        bak.rename(orig)

print("[PASS] `saves` lists slots + empty-state message.")


# ---------------------------------------------------------------------------
banner("H. `status` appends Unfinished business for active quests")
g, cap = fresh()
# Accept a quest.
g.player.location = "scarlet_lotus_shrine"
g.player.visited.add("scarlet_lotus_shrine")
g.step("talk apothecary_weilan")
# Accept a second one.
g.player.location = "verdant_bamboo_sea"
g.player.visited.add("verdant_bamboo_sea")
g.step("talk wandering_monk_huilin")
cap.clear()
g.step("status")
text = "\n".join(cap)
assert "Unfinished business" in text, \
    f"expected unfinished-business block; got:\n{text}"
assert "A Cup of Sleeping Water" in text
assert "visit Pale Lake Shore" in text, \
    f"expected visit-hint; got:\n{text}"
assert "The Bell Beneath the Willow" in text
print("[PASS] status lists active quests with next-step hints.")


# ---------------------------------------------------------------------------
banner("I. `status` omits the block when no active quests")
g, cap = fresh()
g.player.location = "verdant_bamboo_sea"
cap.clear()
g.step("status")
text = "\n".join(cap)
assert "Unfinished business" not in text, \
    f"no block expected when no active quests; got:\n{text}"
print("[PASS] status omits the block with no active quests.")


# ---------------------------------------------------------------------------
print()
print("All session-18 polish smoke-tests passed.")
