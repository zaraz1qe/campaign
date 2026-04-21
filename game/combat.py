"""Turn-based combat. Player vs one enemy at a time."""
from __future__ import annotations
from typing import Dict, Any, List
import random

from .state import Player


def _print_bar(label: str, cur: int, mx: int, width: int = 20) -> str:
    cur = max(0, cur)
    filled = int(width * cur / mx) if mx > 0 else 0
    return f"{label} [{'#' * filled}{'.' * (width - filled)}] {cur}/{mx}"


def _enemy_atk(enemy_state: Dict[str, Any]) -> int:
    base = int(enemy_state["atk"])
    return max(1, base + random.randint(-1, 2))


def _enemy_choose_technique(world, enemy_state):
    techs = enemy_state.get("techniques", [])
    if not techs or random.random() < 0.5:
        return None
    tid = random.choice(techs)
    return world["techniques"].get(tid)


def fight(world: Dict[str, Dict[str, Any]], player: Player, enemy_id: str,
          io) -> str:
    """Run a combat encounter against `enemy_id`.

    `io` is a callable: io(prompt: str | None) -> str  for input,
    OR has methods .out(str) and .ask(prompt) -> str.
    Returns one of: "victory", "defeat", "fled".
    """
    enemy_def = world["enemies"].get(enemy_id)
    if not enemy_def:
        io.out(f"No such enemy: {enemy_id}")
        return "fled"

    e = {
        "name": enemy_def["name"],
        "hp": int(enemy_def["hp"]),
        "max_hp": int(enemy_def["hp"]),
        "atk": int(enemy_def.get("atk", 5)),
        "def": int(enemy_def.get("def", 0)),
        "spd": int(enemy_def.get("spd", 5)),
        "techniques": enemy_def.get("techniques", []),
    }

    io.out("")
    io.out(f"=== Combat begins: {e['name']} ===")
    io.out(enemy_def.get("description", ""))

    while True:
        io.out("")
        io.out(_print_bar(player.name.ljust(16), player.hp, player.max_hp))
        io.out(_print_bar(e["name"].ljust(16),    e["hp"],    e["max_hp"]))
        io.out("Actions: (a)ttack  (t)echnique  (i)tem  (f)lee")
        choice = io.ask("> ").strip().lower()

        # ------------ Player turn ------------
        player_acted = True
        if choice in ("a", "attack", ""):
            dmg = max(1, player.atk + random.randint(-1, 3) - e["def"])
            e["hp"] -= dmg
            io.out(f"You strike {e['name']} for {dmg} damage.")
        elif choice in ("t", "technique"):
            if not player.techniques:
                io.out("You know no techniques.")
                player_acted = False
            else:
                io.out("Your techniques:")
                for i, tid in enumerate(player.techniques, 1):
                    t = world["techniques"].get(tid, {})
                    io.out(f"  {i}. {t.get('name', tid)} "
                           f"(qi {t.get('qi_cost',0)}, dmg {t.get('damage',0)})")
                pick = io.ask("Use which? (number, or 0 to cancel) > ").strip()
                if not pick.isdigit() or int(pick) == 0:
                    player_acted = False
                else:
                    idx = int(pick) - 1
                    if idx < 0 or idx >= len(player.techniques):
                        io.out("No such technique.")
                        player_acted = False
                    else:
                        tid = player.techniques[idx]
                        t = world["techniques"][tid]
                        cost = int(t.get("qi_cost", 0))
                        if player.qi < cost:
                            io.out("Insufficient qi.")
                            player_acted = False
                        else:
                            player.qi -= cost
                            base = int(t.get("damage", 0))
                            dmg = max(1, base + player.atk // 2 + random.randint(0, 3) - e["def"])
                            e["hp"] -= dmg
                            io.out(f"You unleash {t['name']}! {dmg} damage.")
                            eff = t.get("effect")
                            if eff == "heal":
                                heal = int(t.get("effect_power", 5))
                                player.hp = min(player.max_hp, player.hp + heal)
                                io.out(f"You recover {heal} HP.")
                            elif eff == "stun":
                                io.out(f"{e['name']} is stunned and cannot act!")
                                # skip enemy turn after applying lethality check
                                if e["hp"] <= 0:
                                    pass
                                else:
                                    continue
        elif choice in ("i", "item"):
            usable = [iid for iid in player.inventory
                      if world["items"].get(iid, {}).get("type") == "pill"]
            if not usable:
                io.out("You have no usable pills.")
                player_acted = False
            else:
                for i, iid in enumerate(usable, 1):
                    it = world["items"][iid]
                    io.out(f"  {i}. {it['name']} x{player.inventory[iid]} — {it.get('description','')}")
                pick = io.ask("Use which? (number, or 0 to cancel) > ").strip()
                if not pick.isdigit() or int(pick) == 0:
                    player_acted = False
                else:
                    idx = int(pick) - 1
                    if idx < 0 or idx >= len(usable):
                        io.out("No such item.")
                        player_acted = False
                    else:
                        iid = usable[idx]
                        it = world["items"][iid]
                        _apply_pill(player, it, io)
                        player.remove_item(iid, 1)
        elif choice in ("f", "flee"):
            if random.random() < 0.6:
                io.out("You break away into the trees.")
                return "fled"
            else:
                io.out("You fail to escape!")
        else:
            io.out("Unknown action.")
            player_acted = False

        if e["hp"] <= 0:
            io.out("")
            io.out(f"{e['name']} collapses, defeated.")
            xp = int(enemy_def.get("xp", 10))
            player.xp += xp
            player.qi += xp // 2
            io.out(f"You gain {xp} XP and {xp // 2} qi.")
            for drop in enemy_def.get("drops", []):
                if random.random() < float(drop.get("chance", 0.5)):
                    iid = drop["item"]
                    player.add_item(iid, 1)
                    iname = world["items"].get(iid, {}).get("name", iid)
                    io.out(f"You loot: {iname}")
            player.defeated[enemy_id] = player.defeated.get(enemy_id, 0) + 1
            return "victory"

        if not player_acted:
            continue

        # ------------ Enemy turn ------------
        tech = _enemy_choose_technique(world, e)
        if tech:
            base = int(tech.get("damage", 0))
            dmg = max(1, base + e["atk"] // 2 + random.randint(0, 2) - player.defense)
            player.hp -= dmg
            io.out(f"{e['name']} uses {tech['name']}! {dmg} damage.")
        else:
            dmg = max(1, _enemy_atk(e) - player.defense)
            player.hp -= dmg
            io.out(f"{e['name']} strikes you for {dmg} damage.")

        if player.hp <= 0:
            player.hp = 1   # do not let player die outright in v1
            io.out("")
            io.out("You collapse, broken. A passing herbalist drags you back to safety...")
            io.out("(You wake at 1 HP. Rest well.)")
            return "defeat"


def _apply_pill(player: Player, item: Dict[str, Any], io) -> None:
    eff = item.get("effect", "")
    pwr = int(item.get("power", 0))
    if eff == "hp_heal":
        player.hp = min(player.max_hp, player.hp + pwr)
        io.out(f"You swallow {item['name']}; +{pwr} HP.")
    elif eff == "qi_gain":
        player.qi += pwr
        io.out(f"You swallow {item['name']}; +{pwr} qi.")
    elif eff == "atk_buff":
        player.atk += pwr
        io.out(f"You swallow {item['name']}; +{pwr} ATK (permanent).")
    else:
        io.out(f"You swallow {item['name']}, but feel no obvious change.")
