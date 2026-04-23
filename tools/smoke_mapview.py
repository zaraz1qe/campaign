#!/usr/bin/env python3
"""Smoke-test for the ASCII region map, `examine`, and the enriched prompt
(session 16 UX refine).

Exercises:
  A. `map` renders the player's region and marks current location with `*`.
  B. A visited location placed on the grid renders without the `?` marker;
     an unvisited but exit-visible neighbour renders WITH `?`.
  C. Connectors between placed cells reflect *actual* exits — not mere
     grid adjacency (the Pale-Lake / Hermit's-Hut false-line regression).
  D. A non-cardinally-structured hub (Azure Cloud Range) lists its cells
     under "Also in this region" with non-cardinal exits annotated.
  E. `map all` stacks every visited region.
  F. `map <substring>` resolves to a matching region.
  G. `examine <item>` surfaces items on ground, items in inventory, NPCs
     here, and enemies here — without side effects (no pickups, no quest
     ticks). Unknown names fall back to a graceful miss.
  H. The prompt line contains HP/Qi/realm/location, and companion HP when
     a companion is bonded and standing.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game import mapview


def fresh(seed=16):
    random.seed(seed)
    cap: list[str] = []
    g = Game(IO(out_func=lambda s="": cap.append(str(s)),
                in_func=lambda p="": "q"))
    return g, cap


def banner(s):
    print()
    print("=" * 70)
    print(s)
    print("=" * 70)


# ---------------------------------------------------------------------------
banner("A. `map` renders the current region with current-location marker")
g, cap = fresh()
for lid in ("verdant_bamboo_sea", "river_of_swords",
            "willowmere_village_square", "pale_lake_shore"):
    g.player.visited.add(lid)
g.player.location = "verdant_bamboo_sea"
cap.clear()
g.step("map")
text = "\n".join(cap)
assert "Southern Wilds" in text, f"region header missing; got:\n{text}"
# Current location gets the star marker.
assert "*" in text, f"current marker missing; got:\n{text}"
# The Village Square name is trimmed down (no prefix).
assert "[Village Square]" in text, \
    f"[Village Square] (no ?) should be present; got:\n{text}"
print(f"[PASS] Southern Wilds map renders; current cell marked.")


# ---------------------------------------------------------------------------
banner("B. Unvisited-but-exit-visible neighbours get `?` marker")
g, cap = fresh()
# Only visit Bamboo Sea — every cardinal neighbour is exit-visible but
# unvisited.
g.player.visited.add("verdant_bamboo_sea")
g.player.location = "verdant_bamboo_sea"
cap.clear()
g.step("map")
text = "\n".join(cap)
# Some neighbour cell should render with the `?` marker. Check a known
# neighbour name stub ("River of Swor") appears with `?`.
assert "?]" in text, f"expected at least one unvisited neighbour; got:\n{text}"
print(f"[PASS] Unvisited neighbours rendered with `?` suffix.")


# ---------------------------------------------------------------------------
banner("C. Connectors only drawn for cells with real exits between them")
g, cap = fresh()
# Visit Pale Lake Shore and Hermit's Hut. They sit in the same row on the
# BFS grid from Village Square but share no direct exit. A `─` between
# them would be a lie.
for lid in ("willowmere_village_square", "verdant_bamboo_sea",
            "pale_lake_shore", "old_hermits_hut", "drowned_willow_shrine"):
    g.player.visited.add(lid)
g.player.location = "willowmere_village_square"
cap.clear()
g.step("map")
text = "\n".join(cap)
# Extract the line that contains BOTH "Pale Lake" and "Hut" (if any). If
# they end up on the same line, there must NOT be a horizontal connector
# directly between them. We check that by verifying the rendered block
# doesn't contain "Lake…]────[Hut" sequences with only ─ between.
import re
# Strip the "Legend:" line — that line is a description, not the map.
map_region = text.split("Legend:")[0]
# Any line that has both names should have whitespace separation (at
# least 2 spaces of gap) rather than a ─ connector directly between them.
bad = re.search(r"Pale Lake[^─\n]*[─\-]+\s*\[Hut", map_region)
assert not bad, (f"false connector between Pale Lake Shore and Hermit's "
                 f"Hut — they share no exit. Got:\n{text}")
print("[PASS] No false connector between cells that don't share an exit.")


# ---------------------------------------------------------------------------
banner("D. Non-cardinal hub region lists cells under 'Also in this region'")
g, cap = fresh()
for lid in ("azure_cloud_foothills", "azure_cloud_outer_gate",
            "azure_cloud_inner_courtyard", "azure_cloud_library",
            "azure_cloud_forge", "elder_baixus_pavilion"):
    g.player.visited.add(lid)
g.player.location = "azure_cloud_library"
cap.clear()
g.step("map")
text = "\n".join(cap)
assert "Also in this region" in text, \
    f"non-cardinal hub should list detached cells; got:\n{text}"
# At least Forge and Baixu's Pavilion should be listed.
assert "Forge" in text and "Pavilion" in text, \
    f"detached cells must be named; got:\n{text}"
# Named portals should still be advertised in 'Other connections'.
assert "Other connections" in text
assert "library" in text and "forge" in text and "elder" in text, \
    f"named portals must surface as exits; got:\n{text}"
print("[PASS] Non-cardinal Azure Cloud hub lists its interior cleanly.")


# ---------------------------------------------------------------------------
banner("E. `map all` stacks every visited region")
g, cap = fresh()
for lid in ("verdant_bamboo_sea", "crimson_creek",
            "scarlet_lotus_shrine", "cloudroot_pass"):
    g.player.visited.add(lid)
g.player.location = "verdant_bamboo_sea"
cap.clear()
g.step("map all")
text = "\n".join(cap)
assert "Southern Wilds" in text
assert "Scarlet Lotus" in text
assert "Sky-Spire" in text
print("[PASS] `map all` stacks every visited region.")


# ---------------------------------------------------------------------------
banner("F. `map <substring>` resolves to a matching region")
g, cap = fresh()
g.player.visited.add("crimson_creek")
g.player.location = "crimson_creek"
cap.clear()
g.step("map sky")
text = "\n".join(cap)
# No region visited in Sky-Spire yet, so message should say "not visited".
assert ("Sky-Spire Reach" in text and
        "not visited any location in this region" in text), \
    f"unvisited region fallback should render; got:\n{text}"
# Matching their current region by substring works too.
cap.clear()
g.step("map scarlet")
text = "\n".join(cap)
assert "Scarlet Lotus Reach" in text, \
    f"scarlet substring should resolve; got:\n{text}"
print("[PASS] `map <substring>` region matching works.")


# ---------------------------------------------------------------------------
banner("G. `examine` surfaces items, NPCs, enemies — and misses gracefully")
g, cap = fresh()
g.player.location = "drowned_willow_shrine"
cap.clear()
g.step("examine moonflower bud")
text = "\n".join(cap)
assert "Moonflower Bud" in text and "on the ground" in text, \
    f"examine should find items on the ground; got:\n{text}"
# Side effect check: inventory must be unchanged; the item must remain
# on the ground.
assert g.player.inventory.get("moonflower_bud", 0) == 0, \
    "examine must not pick up the item"

# Inventory item path.
g.player.add_item("minor_healing_pill", 2)
cap.clear()
g.step("x minor healing pill")
text = "\n".join(cap)
assert "Minor Healing Pill" in text and "in your sleeves" in text, \
    f"examine should find inventory items; got:\n{text}"
assert "× 2" in text, f"count should surface when > 1; got:\n{text}"

# NPC path — Baixu is at his pavilion.
g.player.location = "elder_baixus_pavilion"
cap.clear()
g.step("look at baixu")
text = "\n".join(cap)
assert "Elder Baixu" in text, f"examine should find NPCs here; got:\n{text}"
# Side-effect check: Baixu must NOT have been added to talked_to — examine
# is read-only. (This is a common expectation that's easy to regress.)
assert "elder_baixu" not in g.player.talked_to, \
    "examine must NOT register as a `talk`"

# Enemy path — frost_wolf at Azure Cloud Foothills (or wherever it lives).
# Use a location we know has an enemy from existing content.
g.player.location = "bandit_road"
cap.clear()
g.step("examine bannerman")
text = "\n".join(cap)
assert "Black Banner Shao" in text and "enemy" in text, \
    f"examine should find enemies here; got:\n{text}"
# Combat must not have triggered.
assert g.player.hp == 30, f"examine must not trigger combat; got hp={g.player.hp}"

# Graceful miss.
cap.clear()
g.step("examine dragon of the moon")
text = "\n".join(cap)
assert "nothing called" in text, \
    f"unknown name should be a graceful miss; got:\n{text}"
print("[PASS] examine: items (ground + inventory), NPCs, enemies, miss.")


# ---------------------------------------------------------------------------
banner("H. Prompt line contains HP / Qi / realm / location — and companion")
g, cap = fresh()
p = g._prompt()
assert "HP " in p and "Qi " in p, f"prompt must show hp/qi; got {p!r}"
assert "Verdant Bamboo Sea" in p or "Mortal" in p, \
    f"prompt must show realm and location; got {p!r}"

# Attach a companion and check it's present.
g.player.companion = {
    "id": "disciple_meilin", "hp": 50, "max_hp": 58,
    "atk": 9, "def": 3, "spd": 7, "qi": 20, "max_qi": 40,
    "techniques": [], "downed": False,
}
p = g._prompt()
assert "Meilin" in p or "+" in p, \
    f"prompt must mention companion when present; got {p!r}"
# Downed state renders differently.
g.player.companion["downed"] = True
p = g._prompt()
assert "downed" in p, f"downed companion must read as 'downed'; got {p!r}"
print("[PASS] Prompt carries HP/Qi/realm/location + companion condition.")


# ---------------------------------------------------------------------------
print()
print("All mapview / examine / prompt smoke-tests passed.")
