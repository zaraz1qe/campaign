#!/usr/bin/env python3
"""Scripted smoke-test for the Azure Cloud Library deepening (session 13).

Exercises:
  A. Library content loads — new manuals, lore, quests, Bannerman Shao.
  B. `read <manual>` on an open-shelf manual: prints a passage, grants the
     manual's lore, leaves the manual in inventory.
  C. `read <manual>` with a technique-teaching manual: teaches iff realm+rep
     are met; still grants any lore side of the manual.
  D. `buy <manual>` respects rep gates (ACS +2 required for locked-shelf).
  E. Zhao's gives_quest is list-valued and silent on completed/accepted.
  F. Quest chain: study_the_sutra → the_locked_shelves → the_committee_of_1184.
  G. Bannerman Shao drops torn_catalogue_page 100%.
  H. sister_willows_record is on the ground at Hanging Terraces.
  I. Save/load round-trip preserves library-side state.
"""
from __future__ import annotations
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game.engine import Game, IO
from game.state import Player


def drive(seed=11):
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
banner("A. Library content loads — manuals, lore, quests, boss")
g, *_ = drive()
for iid in ("manual_gatekeepers_oath", "manual_west_reading_room",
            "manual_sword_calamity_abridged", "manual_azure_cloud_commentary",
            "manual_ninefold_azure_cuts", "manual_committee_of_1184",
            "manual_stormwardens_marginalia", "torn_catalogue_page",
            "sister_willows_record", "black_banner_sash"):
    assert iid in g.world["items"], f"item '{iid}' missing"
for lid in ("the_committee_of_1184", "azure_cloud_commentary_1184",
            "the_lamplighter_of_zhao", "gatekeepers_oath",
            "the_sword_calamity", "the_west_reading_room"):
    assert lid in g.world["lore"], f"lore '{lid}' missing"
for qid in ("the_locked_shelves", "the_committee_of_1184"):
    assert qid in g.world["quests"], f"quest '{qid}' missing"
assert "bannerman_shao" in g.world["enemies"], "boss missing"
assert "bannerman_shao" in g.world["locations"]["bandit_road"]["enemies"], \
    "Bannerman Shao must be spawnable at Bandit Road"
assert "sister_willows_record" in \
    g.world["locations"]["hanging_terraces_of_jadestep"]["items_on_ground"], \
    "Sister Willow's record must be on the ground at the Hanging Terraces"
print(f"[PASS] All library ids resolve. "
      f"Items={len(g.world['items'])}, lore={len(g.world['lore'])}, "
      f"quests={len(g.world['quests'])}.")


# ---------------------------------------------------------------------------
banner("B. Reading an open-shelf manual grants lore; manual stays")
g, say, q, cap = drive()
# Put a manual straight in inventory (as if bought).
g.player.add_item("manual_gatekeepers_oath", 1)
assert "gatekeepers_oath" not in g.player.known_lore
say("read manual_gatekeepers_oath")
text = "\n".join(cap[-40:])
assert "Reading: The Gatekeeper's Oath" in text, \
    f"Manual passage must print; got: {text!r}"
assert "gatekeepers_oath" in g.player.known_lore, \
    "reading must grant the manual's lore on first read"
assert g.player.inventory.get("manual_gatekeepers_oath", 0) == 1, \
    "manual stays in inventory — a library is for returning to"
# Second read: passage still prints, lore silent.
before_lore = set(g.player.known_lore)
cap.clear()
say("read manual_gatekeepers_oath")
text = "\n".join(cap)
assert "Reading: The Gatekeeper's Oath" in text
assert g.player.known_lore == before_lore, "re-read must not re-announce lore"
# A manual with TWO lore entries grants both.
g.player.add_item("manual_west_reading_room", 1)
say("read manual_west_reading_room")
assert "the_west_reading_room" in g.player.known_lore
assert "the_lamplighter_of_zhao" in g.player.known_lore
print("[PASS] Manual passages print; first-read grants lore; "
      "re-read is silent; manual stays in inventory.")


# ---------------------------------------------------------------------------
banner("C. Technique-teaching manual respects realm/rep gates")
g, say, q, cap = drive()
# Ninefold Azure Cuts teaches azure_cloud_sword_arc (qi-condensation).
# Fresh player is mortal; the manual should refuse to teach.
g.player.add_item("manual_ninefold_azure_cuts", 1)
assert "azure_cloud_sword_arc" not in g.player.techniques
cap.clear()
say("read manual_ninefold_azure_cuts")
text = "\n".join(cap)
assert "azure_cloud_sword_arc" not in g.player.techniques, \
    "mortal must not learn a QC art from the manual"
assert "refuse" in text.lower() or "blur" in text.lower() or \
       "qi" in text.lower(), \
    f"a gate message must explain the refusal; got {text!r}"
# Advance the player to qi-condensation — the realm gate now passes, but the
# TECHNIQUE itself has its own rep gate (ACS +1). Without rep, the manual
# should refuse quietly.
g.player.realm_id = "qi_condensation"
cap.clear()
say("read manual_ninefold_azure_cuts")
text = "\n".join(cap)
assert "azure_cloud_sword_arc" not in g.player.techniques, \
    "technique's own requires_rep must still hold after realm unlocks"
assert "lineage" in text.lower() or "reputation" in text.lower() or \
       "ink" in text.lower(), \
    f"a rep-gate message must fire; got {text!r}"
# Now grant ACS rep and retry — the manual teaches.
g.player.reputation["azure_cloud_sect"] = 1
cap.clear()
say("read manual_ninefold_azure_cuts")
assert "azure_cloud_sword_arc" in g.player.techniques, \
    "QC+ACS-rep player must learn azure_cloud_sword_arc from the manual"
print("[PASS] Manual gates on both realm and the technique's own rep; "
      "teach fires only when both pass.")


# ---------------------------------------------------------------------------
banner("D. Rep-gated buy refuses until ACS rep threshold is met")
g, say, q, cap = drive()
# Travel to the library.
say("go west")  # to willowmere
say("go east")  # back to bamboo
say("go north")  # to hermit's hut? depends... instead, set directly.
g.player.location = "azure_cloud_library"
cap.clear()
say("buy manual_committee_of_1184")  # needs ACS +3
text = "\n".join(cap)
assert "will not sell" in text.lower() or "reputation" in text.lower(), \
    f"rep-gated manual must be refused; got {text!r}"
# Now set rep to +3 and retry.
g.player.reputation["azure_cloud_sect"] = 3
# Give enough stones (the locked manual is value 0 but other fields matter;
# just to be safe, top up).
g.player.spirit_stones = 500
cap.clear()
say("buy manual_committee_of_1184")
text = "\n".join(cap)
assert g.player.inventory.get("manual_committee_of_1184", 0) == 1, \
    f"rep-met buy must succeed; got {text!r}"
print("[PASS] Manuals gated by requires_rep; buy succeeds once rep met.")


# ---------------------------------------------------------------------------
banner("E. Zhao's gives_quest list is silent on completed/accepted")
g, say, q, cap = drive()
# Make sure Zhao is a list giver.
zhao = g.world["npcs"]["librarian_zhao"]
gq = zhao.get("gives_quest")
assert isinstance(gq, list), f"Zhao's gives_quest must be a list; got {gq!r}"
assert "study_the_sutra" in gq and "the_locked_shelves" in gq \
    and "the_committee_of_1184" in gq, \
    f"Zhao's gives_quest must include the whole arc; got {gq!r}"
# Jump to the library to talk.
g.player.location = "azure_cloud_library"
cap.clear()
say("talk librarian_zhao")
text = "\n".join(cap)
# First talk: study_the_sutra gets offered; the other two are gated silent.
assert "[QUEST ACCEPTED] Study the Sutra" in text, \
    f"first talk must accept the first quest; got {text!r}"
assert "The Locked Shelves" not in text, \
    "the chained second quest must not preview before its prereq is done"
assert "The Committee of 1184" not in text
# Second talk without completing — should be silent on study_the_sutra.
cap.clear()
say("talk librarian_zhao")
text = "\n".join(cap)
assert "already accepted" not in text.lower(), \
    "already-accepted quest must not re-print noise"
assert "already completed" not in text.lower()
print("[PASS] Zhao's multi-giver list is silent on completed/accepted entries.")


# ---------------------------------------------------------------------------
banner("F. Quest chain: sutra → locked_shelves → committee progresses")
g, say, q, cap = drive()
# Accept first quest and complete it via visit+talk at the library.
g.player.location = "azure_cloud_library"
g.player.visited.add("azure_cloud_library")
# On the first talk both of study_the_sutra's steps (visit+talk) are
# satisfied immediately, so progress_quests completes the quest on the
# same command. Good — that matches the original design.
cap.clear()
say("talk librarian_zhao")
text = "\n".join(cap)
assert "study_the_sutra" in g.player.completed_quests, \
    f"study_the_sutra must complete on the single entering talk; got {text!r}"
# Second talk: the_locked_shelves is now unblocked and should auto-offer.
cap.clear()
say("talk librarian_zhao")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Locked Shelves" in text, \
    f"second quest must auto-offer once prereq closes; got {text!r}"
# Fast-path the second quest: give the player the page + mark the boss down.
g.player.add_item("torn_catalogue_page", 1)
g.player.defeated["bannerman_shao"] = 1
cap.clear()
say("talk librarian_zhao")  # closing talk on the_locked_shelves
text = "\n".join(cap)
assert "the_locked_shelves" in g.player.completed_quests, \
    "the_locked_shelves must complete with page+defeat+talk"
assert "the_west_reading_room" in g.player.known_lore, \
    "completion must grant lore"
assert g.player.inventory.get("manual_west_reading_room", 0) >= 1, \
    "completion must award the west-reading-room manual"
# Third quest should offer only when ACS rep is 2+.
assert g.player.reputation["azure_cloud_sect"] >= 2, \
    f"after two ACS-rep-granting quests, rep must be >=2; got " \
    f"{g.player.reputation['azure_cloud_sect']}"
cap.clear()
say("talk librarian_zhao")
text = "\n".join(cap)
assert "[QUEST ACCEPTED] The Committee of 1184" in text, \
    f"third quest must offer once rep+prereq met; got {text!r}"
# Fast-path: grant the record and visit the terrace.
g.player.add_item("sister_willows_record", 1)
g.player.visited.add("hanging_terraces_of_jadestep")
cap.clear()
say("talk librarian_zhao")  # closing talk
assert "the_committee_of_1184" in g.player.completed_quests, \
    "the_committee_of_1184 must complete with record+visit+talk"
assert "the_committee_of_1184" in g.player.known_lore, \
    "completion must grant the committee lore"
assert "azure_cloud_commentary_1184" in g.player.known_lore, \
    "completion must grant the marginalia lore"
assert g.player.inventory.get("manual_committee_of_1184", 0) >= 1, \
    "completion must award the committee manual"
print("[PASS] Three-quest library arc completes end-to-end; rewards land.")


# ---------------------------------------------------------------------------
banner("G. Bannerman Shao drops torn_catalogue_page (chance=1.0)")
g, *_ = drive()
shao = g.world["enemies"]["bannerman_shao"]
drops = {d["item"]: d["chance"] for d in shao.get("drops", [])}
assert drops.get("torn_catalogue_page") == 1.0, \
    f"Bannerman must drop the page 100%; got {drops}"
assert drops.get("black_banner_sash") == 1.0, \
    f"Bannerman must drop the sash 100%; got {drops}"
print(f"[PASS] Bannerman Shao drops: {drops}")


# ---------------------------------------------------------------------------
banner("H. Sister Willow's record is on the ground at the Hanging Terraces")
g, say, q, cap = drive()
# Fast-travel to the terrace (skip gating combat: the test only verifies the
# breadcrumb).
g.player.location = "hanging_terraces_of_jadestep"
cap.clear()
say("take sister_willows_record")
assert g.player.inventory.get("sister_willows_record", 0) == 1, \
    "take must pick up the record"
print("[PASS] sister_willows_record is takeable at the Hanging Terraces.")


# ---------------------------------------------------------------------------
banner("I. Save/load round-trip preserves library-side state")
g, say, q, cap = drive()
g.player.add_item("manual_gatekeepers_oath", 1)
g.player.known_lore.add("gatekeepers_oath")
g.player.location = "azure_cloud_library"
g.player.active_quests["the_locked_shelves"] = 1
blob = g.player.to_json()
p2 = Player.from_json(blob)
assert "gatekeepers_oath" in p2.known_lore
assert p2.inventory.get("manual_gatekeepers_oath") == 1
assert "the_locked_shelves" in p2.active_quests
print("[PASS] Save/load preserves manual, lore, and library-arc quest state.")


# ---------------------------------------------------------------------------
print()
print("All Azure Cloud Library smoke-tests passed.")
