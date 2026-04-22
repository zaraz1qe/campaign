#!/usr/bin/env python3
"""Run a harder fight where the companion can plausibly be targeted/downed.

Uses the Scarlet Lotus Assassin against a weak companion + a weakly-built
player, so over several rounds we should see the enemy split fire. Mostly a
liveness check: does combat resolve cleanly when the companion is targeted,
gets poisoned, bleeds, or is downed?
"""
from __future__ import annotations
import random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from game.engine import Game, IO


def drive(seed=123):
    random.seed(seed)
    g = Game(IO())
    cap = []
    q = []
    def _out(s=""):
        cap.append(str(s))
    def _in(prompt=""):
        cap.append(prompt)
        if q:
            a = q.pop(0)
            cap.append(a)
            return a
        return "f"
    g.io = IO(out_func=_out, in_func=_in)
    def say(line):
        cap.append(f"\n>>> {line}")
        g.step(line)
    return g, say, q, cap


for seed in [7, 11, 23, 41, 77]:
    g, say, q, cap = drive(seed=seed)
    g.player.realm_id = "qi_condensation"
    g.player.max_hp, g.player.hp = 60, 60
    g.player.atk, g.player.defense, g.player.spd = 9, 3, 7
    g.player.reputation["azure_cloud_sect"] = 3
    g.player.completed_quests.add("study_the_sutra")
    g.player.location = "azure_cloud_inner_courtyard"
    say("recruit disciple_meilin")
    # Force companion to lower HP so enemy has a chance to down them.
    g.player.companion["hp"] = 20
    g.player.companion["max_hp"] = 20
    # Heavy enemy — put a Scarlet Lotus Assassin as guaranteed target.
    # We'll pick a tough enemy and fight till resolved.
    g.player.location = "bandit_road"
    # Force rep to summon the assassin.
    g.player.reputation["azure_cloud_sect"] = 5
    q.extend(["a"] * 40)
    say("fight scarlet_lotus_assassin")
    print("=" * 60)
    print(f"seed={seed} outcome: ", end="")
    comp = g.player.companion
    if comp:
        print(f"comp HP={comp['hp']}/{comp['max_hp']} downed={comp.get('downed')}, "
              f"player HP={g.player.hp}")
    else:
        print("no companion")
    # Print last 40 lines so we can eyeball.
    print("\n".join(cap[-40:]))
    print()
