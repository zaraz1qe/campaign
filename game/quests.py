"""Quest progression. Steps are checked against player state after relevant actions."""
from __future__ import annotations
from typing import Dict, Any, List

from .state import Player, rep_rank, affinity_tier


def _step_satisfied(step: Dict[str, Any], player: Player) -> bool:
    t = step.get("type")
    target = step.get("target")
    if t == "visit":
        return target in player.visited
    if t == "defeat":
        return player.defeated.get(target, 0) >= int(step.get("count", 1))
    if t == "talk":
        return target in player.talked_to
    if t == "collect":
        return player.has_item(target, int(step.get("count", 1)))
    return False


def offer_quest(world: Dict[str, Dict[str, Any]], player: Player, quest_id: str) -> str:
    if quest_id in player.completed_quests:
        return "(You have already completed this task.)"
    if quest_id in player.active_quests:
        return "(You already accepted this task.)"
    q = world["quests"].get(quest_id)
    if not q:
        return ""
    # Rep gate — skip auto-offer quietly if the giver won't entrust it yet.
    req = q.get("requires_rep") or {}
    if not player.meets_rep(req):
        short = player.rep_shortfalls(req)
        pieces = []
        for sid, s in short.items():
            sname = world["sects"].get(sid, {}).get("name", sid)
            pieces.append(f"{sname} {s:+d}")
        return f"\n  (They weigh you, and do not speak of it. Required: {', '.join(pieces)}.)"
    player.active_quests[quest_id] = 0
    return f"\n[QUEST ACCEPTED] {q['name']}\n  {q.get('description','')}"


def progress_quests(world: Dict[str, Dict[str, Any]], player: Player) -> List[str]:
    """Advance every active quest as far as it can. Return notification strings."""
    notes: List[str] = []
    for qid in list(player.active_quests):
        q = world["quests"].get(qid)
        if not q:
            continue
        steps = q.get("steps", [])
        idx = player.active_quests[qid]
        while idx < len(steps) and _step_satisfied(steps[idx], player):
            idx += 1
            if idx < len(steps):
                nxt = steps[idx]
                notes.append(f"[{q['name']}] step complete — next: "
                             f"{nxt.get('type','?')} {nxt.get('target','')}")
        player.active_quests[qid] = idx
        if idx >= len(steps):
            del player.active_quests[qid]
            player.completed_quests.add(qid)
            reward = q.get("reward", {})
            ss = int(reward.get("spirit_stones", 0))
            xp = int(reward.get("xp", 0))
            items = reward.get("items", [])
            player.spirit_stones += ss
            player.xp += xp
            for iid in items:
                player.add_item(iid, 1)
            r_parts = []
            if ss: r_parts.append(f"{ss} spirit stones")
            if xp: r_parts.append(f"{xp} XP")
            if items:
                names = [world["items"].get(i, {}).get("name", i) for i in items]
                r_parts.append("items: " + ", ".join(names))
            rwd = ", ".join(r_parts) or "(no reward)"
            notes.append(f"[QUEST COMPLETE] {q['name']} — reward: {rwd}")
            # Affinity: if a companion stood with you through this trial,
            # the shared quest deepens the bond. Downed doesn't disqualify
            # — they walked the road even if they fell at its end.
            if player.companion:
                cid = player.companion.get("id", "")
                if cid:
                    old_tier = affinity_tier(player.affinity(cid))
                    new_aff = player.adjust_affinity(cid, 2)
                    new_tier = affinity_tier(new_aff)
                    cname = world["npcs"].get(cid, {}).get("name", "your companion")
                    if new_tier != old_tier:
                        notes.append(f"  [Bond] {cname} — the shared trial "
                                     f"raises your oath to {new_tier}.")
                    else:
                        notes.append(f"  [Bond] {cname} — the oath between "
                                     f"you deepens (+2 affinity).")
            # Apply reputation changes. Show old->new rank when the change
            # crosses a threshold so the player feels it.
            rep_changes = q.get("rep_change") or {}
            for sid, delta in rep_changes.items():
                delta = int(delta)
                if delta == 0:
                    continue
                old = player.rep(sid)
                player.adjust_rep(sid, delta)
                new = player.rep(sid)
                old_rank = rep_rank(old)
                new_rank = rep_rank(new)
                sname = world["sects"].get(sid, {}).get("name", sid)
                if old_rank == new_rank:
                    notes.append(f"  [Reputation] {sname} {delta:+d}  "
                                 f"(now {new:+d}, {new_rank})")
                else:
                    notes.append(f"  [Reputation] {sname} {delta:+d}  "
                                 f"— risen from {old_rank} to {new_rank}"
                                 if delta > 0 else
                                 f"  [Reputation] {sname} {delta:+d}  "
                                 f"— fallen from {old_rank} to {new_rank}")
    return notes


def quest_status(world: Dict[str, Dict[str, Any]], player: Player) -> str:
    if not player.active_quests and not player.completed_quests:
        return "You have undertaken no tasks."
    out = []
    if player.active_quests:
        out.append("Active quests:")
        for qid, idx in player.active_quests.items():
            q = world["quests"].get(qid, {})
            steps = q.get("steps", [])
            out.append(f"  - {q.get('name', qid)}")
            out.append(f"      {q.get('description','')}")
            if idx < len(steps):
                step = steps[idx]
                out.append(f"      Next: {step.get('type','?')} {step.get('target','')}")
    if player.completed_quests:
        out.append("")
        out.append("Completed:")
        for qid in sorted(player.completed_quests):
            q = world["quests"].get(qid, {})
            out.append(f"  - {q.get('name', qid)}")
    return "\n".join(out)
