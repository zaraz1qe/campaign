"""Quest progression. Steps are checked against player state after relevant actions."""
from __future__ import annotations
from typing import Dict, Any, List

from .state import Player, rep_rank, affinity_tier
from . import style


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
    # Silent on completed and already-accepted so a multi-quest giver (or a
    # repeat visitor to a single-quest giver) doesn't print noise on every
    # talk. The quest board (`quest` command) is the authoritative status view.
    if quest_id in player.completed_quests:
        return ""
    if quest_id in player.active_quests:
        return ""
    q = world["quests"].get(quest_id)
    if not q:
        return ""
    # Prerequisite quest gate — an arc's second step stays sealed until the
    # first is done. Silent: the giver simply doesn't speak of the second
    # errand before the first is closed.
    prereq = q.get("requires_quest")
    if prereq and prereq not in player.completed_quests:
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
    tag = style.quest("[QUEST ACCEPTED]")
    qname = style.quest(q["name"])
    return f"\n{tag} {qname}\n  {q.get('description','')}"


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
                notes.append(f"[{style.quest(q['name'])}] step complete — next: "
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
                names = [style.item(world["items"].get(i, {}).get("name", i))
                         for i in items]
                r_parts.append("items: " + ", ".join(names))
            rwd = ", ".join(r_parts) or "(no reward)"
            notes.append(f"{style.good('[QUEST COMPLETE]')} "
                         f"{style.quest(q['name'])} — reward: {rwd}")
            # Knowledge is a reward too. A quest that grants lore writes
            # it straight into the player's memory — one line per newly
            # learned entry; silent on entries already known.
            lore_grants = q.get("grants_lore") or []
            if isinstance(lore_grants, str):
                lore_grants = [lore_grants]
            for lid in lore_grants:
                if lid in player.known_lore:
                    continue
                l = world.get("lore", {}).get(lid)
                if not l:
                    continue
                player.known_lore.add(lid)
                notes.append(f"  {style.lore('[Lore recorded — ' + l.get('category','lore') + ']')} "
                             f"{style.lore(l.get('title', lid))}")
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
                    cname_c = style.companion(cname)
                    if new_tier != old_tier:
                        notes.append(f"  {style.good('[Bond]')} {cname_c} — the shared trial "
                                     f"raises your oath to {style.good(new_tier)}.")
                    else:
                        notes.append(f"  {style.good('[Bond]')} {cname_c} — the oath between "
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
                tag = style.good("[Reputation]") if delta > 0 else style.warn("[Reputation]")
                dstr = style.rep_delta(delta)
                if old_rank == new_rank:
                    notes.append(f"  {tag} {sname} {dstr}  "
                                 f"(now {style.rep_value(new)}, {new_rank})")
                else:
                    arrow = "risen" if delta > 0 else "fallen"
                    notes.append(f"  {tag} {sname} {dstr}  "
                                 f"— {arrow} from {old_rank} to "
                                 f"{style.good(new_rank) if delta > 0 else style.warn(new_rank)}")
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
