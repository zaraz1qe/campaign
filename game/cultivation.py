"""Cultivation: gain qi at locations, break through realms."""
from __future__ import annotations
from typing import Dict, Any, List, Tuple
import random

from .state import Player


def realm_order(world: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return realms sorted by their `order` field."""
    return sorted(world["realms"].values(), key=lambda r: r.get("order", 0))


def current_realm(world: Dict[str, Dict[str, Any]], player: Player) -> Dict[str, Any]:
    return world["realms"].get(player.realm_id, {
        "id": "mortal", "name": "Mortal", "order": 0, "qi_required": 50,
        "hp_bonus": 0, "atk_bonus": 0, "def_bonus": 0,
        "description": "An ordinary mortal."
    })


def next_realm(world: Dict[str, Dict[str, Any]], player: Player) -> Dict[str, Any] | None:
    cr = current_realm(world, player)
    order = cr.get("order", 0)
    upcoming = [r for r in realm_order(world) if r.get("order", 0) > order]
    return upcoming[0] if upcoming else None


def cultivate(world: Dict[str, Dict[str, Any]], player: Player) -> str:
    """Sit and gather qi at the current location."""
    loc = world["locations"].get(player.location, {})
    density = max(1, int(loc.get("qi_density", 1)))
    gained = density * random.randint(2, 5)
    player.qi += gained

    msg = [f"You sit in lotus position. Qi flows... (+{gained} qi)"]

    cr = current_realm(world, player)
    needed = cr.get("qi_required", player.max_qi)
    if player.qi >= needed:
        nxt = next_realm(world, player)
        if nxt:
            msg.append("")
            msg.append(f"Your dantian trembles — you stand at the threshold of {nxt['name']}!")
            msg.append("Use `breakthrough` to attempt the realm advance.")
        else:
            msg.append("Yet there is no higher realm yet recorded in the heavens...")
    return "\n".join(msg)


def breakthrough(world: Dict[str, Dict[str, Any]], player: Player) -> str:
    cr = current_realm(world, player)
    needed = cr.get("qi_required", player.max_qi)
    if player.qi < needed:
        return f"You lack qi for breakthrough ({player.qi}/{needed})."
    nxt = next_realm(world, player)
    if not nxt:
        return "There is no higher realm to ascend to."
    # Tribulation chance — small risk
    roll = random.random()
    if roll < 0.10:
        loss = max(5, player.max_hp // 4)
        player.hp = max(1, player.hp - loss)
        player.qi = int(player.qi * 0.7)
        return (f"Heaven's tribulation strikes! You falter and lose {loss} HP. "
                f"Steady your heart and try again.")
    # Success
    player.qi = 0
    player.realm_id = nxt["id"]
    player.max_hp += int(nxt.get("hp_bonus", 0))
    player.hp = player.max_hp
    player.atk += int(nxt.get("atk_bonus", 0))
    player.defense += int(nxt.get("def_bonus", 0))
    player.max_qi = int(nxt.get("qi_required", player.max_qi))
    return (f"Heavenly thunder rolls! You ascend to **{nxt['name']}**!\n"
            f"+{nxt.get('hp_bonus',0)} HP, +{nxt.get('atk_bonus',0)} ATK, "
            f"+{nxt.get('def_bonus',0)} DEF.")


def realm_meets(world: Dict[str, Dict[str, Any]], player: Player, required_id: str) -> bool:
    """True if player.realm_id >= required_id by `order`."""
    if not required_id:
        return True
    req = world["realms"].get(required_id)
    cur = current_realm(world, player)
    if not req:
        return True
    return cur.get("order", 0) >= req.get("order", 0)
