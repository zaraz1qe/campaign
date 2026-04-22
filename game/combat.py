"""Turn-based combat. Player vs one enemy at a time.

Status effects live only inside a fight:
  { "type": "poison"|"bleed"|"stun"|"buff_atk"|"buff_def",
    "power": int,
    "turns_left": int }
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import random

from .state import Player


# ---------------------------------------------------------------------------
# Prose helpers — little touches so every swing doesn't read the same.

_STRIKE_VERBS = (
    "strike", "cut at", "batter", "drive into",
    "hammer", "lash out at", "lance into",
)
_MISS_LINES = (
    "but {name} slips aside like smoke.",
    "but {name} sways back, untouched.",
    "but your blow finds only empty air.",
    "but {name} flows around it.",
)
_CRIT_LINES = (
    "A clean strike — qi bursts where flesh should be!",
    "Your technique finds the gap between heartbeats!",
    "The blow lands true; you feel it ring through bone.",
    "A perfect angle — force doubles at the point of contact.",
)


def _print_bar(label: str, cur: int, mx: int, width: int = 20) -> str:
    cur = max(0, cur)
    filled = int(width * cur / mx) if mx > 0 else 0
    return f"{label} [{'#' * filled}{'.' * (width - filled)}] {cur}/{mx}"


# ---------------------------------------------------------------------------
# Status effect plumbing.

_DOT_KINDS = ("poison", "bleed")
_NEGATIVE = ("poison", "bleed", "stun")


def _status_summary(status: List[Dict[str, Any]]) -> str:
    if not status:
        return ""
    parts = []
    for s in status:
        t = s["type"]
        if t in _DOT_KINDS:
            parts.append(f"{t} {s['power']}/{s['turns_left']}t")
        elif t == "stun":
            parts.append(f"stunned {s['turns_left']}t")
        elif t.startswith("buff_"):
            stat = t.split("_", 1)[1].upper()
            parts.append(f"+{s['power']} {stat} ({s['turns_left']}t)")
    return " [" + ", ".join(parts) + "]"


def _apply_status(target_status: List[Dict[str, Any]], kind: str,
                  power: int, turns: int) -> None:
    """Add or refresh a status on `target_status` (a mutable list)."""
    for s in target_status:
        if s["type"] == kind:
            s["power"] = max(s["power"], power)
            s["turns_left"] = max(s["turns_left"], turns)
            return
    target_status.append({"type": kind, "power": power, "turns_left": turns})


def _tick_status(status: List[Dict[str, Any]], label: str, io,
                 take_damage, is_player: bool = False) -> bool:
    """Apply DoT damage and decrement durations. Returns True if stunned."""
    stunned = False
    keep: List[Dict[str, Any]] = []
    for s in status:
        t = s["type"]
        if t == "poison":
            take_damage(s["power"])
            if is_player:
                io.out(f"  (Venom burns through you — {s['power']} dmg)")
            else:
                io.out(f"  ({label} is burned by venom — {s['power']} dmg)")
        elif t == "bleed":
            take_damage(s["power"])
            if is_player:
                io.out(f"  (Your wounds bleed — {s['power']} dmg)")
            else:
                io.out(f"  ({label}'s wounds bleed — {s['power']} dmg)")
        elif t == "stun":
            stunned = True
            if is_player:
                io.out("  (You are stunned and cannot act!)")
            else:
                io.out(f"  ({label} is stunned and cannot move!)")
        s["turns_left"] -= 1
        if s["turns_left"] > 0:
            keep.append(s)
    status[:] = keep
    return stunned


def _active_buff(status: List[Dict[str, Any]], kind: str) -> int:
    return sum(s["power"] for s in status if s["type"] == kind)


# ---------------------------------------------------------------------------
# Crit / dodge rolls.

def _crit_chance(atk_spd: int, def_spd: int) -> float:
    base = 0.05 + max(0, atk_spd - def_spd) * 0.015
    return min(0.30, base)


def _dodge_chance(atk_spd: int, def_spd: int) -> float:
    return min(0.20, max(0, def_spd - atk_spd) * 0.025)


# ---------------------------------------------------------------------------
# Apply a technique's effect payload (beyond raw damage).

def _apply_tech_effect(t: Dict[str, Any], attacker_status: List[Dict[str, Any]],
                       defender_status: List[Dict[str, Any]],
                       attacker_is_player: bool, defender_name: str,
                       attacker_name: str,
                       attacker_heal, io,
                       include_offensive: bool = True) -> None:
    """Apply a technique's effect. Self-buffs/heals always fire; offensive
    effects (poison/bleed/stun) can be skipped on a dodge."""
    eff = t.get("effect")
    if not eff:
        return
    pwr = int(t.get("effect_power", 0) or 0)
    if eff == "heal":
        attacker_heal(pwr or 5)
        subj = "You recover" if attacker_is_player else f"{attacker_name} recovers"
        io.out(f"  ({subj} {pwr or 5} HP)")
    elif eff == "poison" and include_offensive:
        _apply_status(defender_status, "poison", max(1, pwr), 3)
        subj = "You are poisoned" if defender_name == "You" else f"{defender_name} is poisoned"
        io.out(f"  ({subj} — {max(1,pwr)}/turn for 3 turns)")
    elif eff == "bleed" and include_offensive:
        _apply_status(defender_status, "bleed", max(1, pwr), 3)
        subj = "You begin to bleed" if defender_name == "You" else f"{defender_name} begins to bleed"
        io.out(f"  ({subj} — {max(1,pwr)}/turn for 3 turns)")
    elif eff == "stun" and include_offensive:
        turns = max(1, pwr)
        _apply_status(defender_status, "stun", 1, turns)
        subj = "You are" if defender_name == "You" else f"{defender_name} is"
        io.out(f"  ({subj} stunned for {turns} turn(s))")
    elif eff == "buff_atk":
        _apply_status(attacker_status, "buff_atk", max(1, pwr), 3)
        subj = "You gather" if attacker_is_player else f"{attacker_name} gathers"
        io.out(f"  ({subj} force: +{max(1,pwr)} ATK for 3 turns)")
    elif eff == "buff_def":
        _apply_status(attacker_status, "buff_def", max(1, pwr), 3)
        subj = "You set" if attacker_is_player else f"{attacker_name} sets"
        io.out(f"  ({subj} an unshakable stance: +{max(1,pwr)} DEF for 3 turns)")


def _apply_weapon_on_hit(kind: str, power: int,
                         defender_status: List[Dict[str, Any]],
                         defender_name: str, io) -> None:
    """A weapon's on_hit_effect: fires on normal attacks that actually land."""
    if kind in ("poison", "bleed"):
        _apply_status(defender_status, kind, max(1, power), 3)
        flavor = "venom" if kind == "poison" else "blood"
        io.out(f"  (The blade's edge draws {flavor} from {defender_name}.)")
    elif kind == "stun":
        turns = max(1, power)
        _apply_status(defender_status, "stun", 1, turns)
        io.out(f"  ({defender_name} reels, stunned for {turns} turn(s).)")


# ---------------------------------------------------------------------------

def fight(world: Dict[str, Dict[str, Any]], player: Player, enemy_id: str,
          io) -> str:
    """Run a combat encounter against `enemy_id`. Returns 'victory'|'defeat'|'fled'."""
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
        "status": [],
    }
    player_status: List[Dict[str, Any]] = []

    # Freeze effective player stats for this encounter. Changing gear mid-fight
    # isn't a supported action, so we snapshot once and read from these.
    p_gear_atk = player.eff_atk(world)
    p_gear_def = player.eff_def(world)
    p_gear_spd = player.eff_spd(world)
    p_gear_hp_max = player.eff_max_hp(world)
    # Clamp current HP to whatever gear allows (should already match).
    if player.hp > p_gear_hp_max:
        player.hp = p_gear_hp_max
    weapon = player.weapon(world)
    weapon_name = weapon.get("name") if weapon else None
    weapon_on_hit = weapon.get("on_hit_effect") if weapon else None
    weapon_on_hit_pwr = int(weapon.get("on_hit_power", 0) or 0) if weapon else 0

    io.out("")
    io.out(f"=== Combat begins: {e['name']} ===")
    desc = enemy_def.get("description", "")
    if desc:
        io.out(desc)
    if weapon_name:
        io.out(f"(You draw {weapon_name}.)")

    def _player_take(dmg: int) -> None:
        player.hp -= dmg
    def _enemy_take(dmg: int) -> None:
        e["hp"] -= dmg
    def _player_heal(amt: int) -> None:
        player.hp = min(p_gear_hp_max, player.hp + amt)
    def _enemy_heal(amt: int) -> None:
        e["hp"] = min(e["max_hp"], e["hp"] + amt)

    while True:
        io.out("")
        io.out(_print_bar(player.name.ljust(16), player.hp, p_gear_hp_max)
               + _status_summary(player_status))
        io.out(_print_bar(e["name"].ljust(16), e["hp"], e["max_hp"])
               + _status_summary(e["status"]))

        # -------- Player start-of-turn status tick --------
        stunned = _tick_status(player_status, "You", io, _player_take, is_player=True)
        if player.hp <= 0:
            player.hp = 1
            io.out("")
            io.out("You collapse, broken. A passing herbalist drags you back to safety...")
            io.out("(You wake at 1 HP. Rest well.)")
            return "defeat"

        player_acted = True
        if stunned:
            player_acted = False
        else:
            io.out("Actions: (a)ttack  (t)echnique  (i)tem  (f)lee")
            choice = io.ask("> ").strip().lower()

            if choice in ("a", "attack", ""):
                atk_total = p_gear_atk + _active_buff(player_status, "buff_atk")
                if random.random() < _dodge_chance(e["spd"], p_gear_spd):
                    io.out("You strike — " + random.choice(_MISS_LINES).format(name=e["name"]))
                else:
                    base = max(1, atk_total + random.randint(-1, 3) - e["def"])
                    crit = random.random() < _crit_chance(p_gear_spd, e["spd"])
                    dmg = int(base * 1.7) if crit else base
                    _enemy_take(dmg)
                    verb = random.choice(_STRIKE_VERBS)
                    with_weapon = f" with {weapon_name}" if weapon_name else ""
                    if crit:
                        io.out(f"** {random.choice(_CRIT_LINES)} ** "
                               f"You {verb} {e['name']}{with_weapon} for {dmg} damage.")
                    else:
                        io.out(f"You {verb} {e['name']}{with_weapon} for {dmg} damage.")
                    # Weapon on-hit rider (poison/bleed/stun from the blade itself).
                    if weapon_on_hit and weapon_on_hit_pwr > 0:
                        _apply_weapon_on_hit(weapon_on_hit, weapon_on_hit_pwr,
                                             e["status"], e["name"], io)
            elif choice in ("t", "technique"):
                if not player.techniques:
                    io.out("You know no techniques.")
                    player_acted = False
                else:
                    io.out("Your techniques:")
                    for i, tid in enumerate(player.techniques, 1):
                        t = world["techniques"].get(tid, {})
                        eff = t.get("effect") or ""
                        eff_s = f" [{eff} {t.get('effect_power','')}]".rstrip() if eff else ""
                        io.out(f"  {i}. {t.get('name', tid)} "
                               f"(qi {t.get('qi_cost',0)}, dmg {t.get('damage',0)}){eff_s}")
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
                                atk_total = p_gear_atk + _active_buff(player_status, "buff_atk")
                                base = int(t.get("damage", 0))
                                if base > 0:
                                    raw = max(1, base + atk_total // 2
                                              + random.randint(0, 3) - e["def"])
                                    crit = random.random() < _crit_chance(p_gear_spd, e["spd"])
                                    dmg = int(raw * 1.7) if crit else raw
                                    _enemy_take(dmg)
                                    if crit:
                                        io.out(f"** {random.choice(_CRIT_LINES)} ** "
                                               f"You unleash {t['name']}! {dmg} damage.")
                                    else:
                                        io.out(f"You unleash {t['name']}! {dmg} damage.")
                                else:
                                    io.out(f"You perform {t['name']}.")
                                _apply_tech_effect(t, player_status, e["status"],
                                                   attacker_is_player=True,
                                                   defender_name=e["name"],
                                                   attacker_name="You",
                                                   attacker_heal=_player_heal, io=io)
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
                            _apply_pill(player, it, io, player_status)
                            player.remove_item(iid, 1)
            elif choice in ("f", "flee"):
                flee_chance = 0.5 + max(0, p_gear_spd - e["spd"]) * 0.05
                if random.random() < min(0.9, flee_chance):
                    io.out("You break away into cover. The duel is broken.")
                    return "fled"
                io.out("You try to disengage — but the foe closes the distance!")
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
            # still do enemy turn — otherwise cancelling a menu is a free skip
            pass

        # -------- Enemy start-of-turn status tick --------
        e_stunned = _tick_status(e["status"], e["name"], io, _enemy_take, is_player=False)
        if e["hp"] <= 0:
            io.out("")
            io.out(f"{e['name']} succumbs to the lingering toxin.")
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

        if e_stunned:
            continue

        # -------- Enemy action --------
        tech = _enemy_choose_technique(world, e)
        player_def_total = p_gear_def + _active_buff(player_status, "buff_def")
        if tech:
            base = int(tech.get("damage", 0))
            landed = True
            if base > 0:
                if random.random() < _dodge_chance(p_gear_spd, e["spd"]):
                    io.out(f"{e['name']} unleashes {tech['name']} — "
                           "but you slip the path of their qi.")
                    landed = False
                else:
                    raw = max(1, base + e["atk"] // 2 + random.randint(0, 2) - player_def_total)
                    crit = random.random() < _crit_chance(e["spd"], p_gear_spd)
                    dmg = int(raw * 1.7) if crit else raw
                    _player_take(dmg)
                    if crit:
                        io.out(f"** {e['name']} finds a seam! ** "
                               f"{tech['name']} lands for {dmg} damage.")
                    else:
                        io.out(f"{e['name']} uses {tech['name']}! {dmg} damage.")
            else:
                io.out(f"{e['name']} weaves {tech['name']}.")
            _apply_tech_effect(tech, e["status"], player_status,
                               attacker_is_player=False,
                               defender_name="You",
                               attacker_name=e["name"],
                               attacker_heal=_enemy_heal, io=io,
                               include_offensive=landed)
        else:
            if random.random() < _dodge_chance(p_gear_spd, e["spd"]):
                io.out(f"{e['name']} lunges — but you slide under the arc of the blow.")
            else:
                base = max(1, _enemy_atk(e) - player_def_total)
                crit = random.random() < _crit_chance(e["spd"], p_gear_spd)
                dmg = int(base * 1.7) if crit else base
                _player_take(dmg)
                if crit:
                    io.out(f"** {e['name']} strikes with sudden cruelty! ** {dmg} damage.")
                else:
                    io.out(f"{e['name']} strikes you for {dmg} damage.")

        if player.hp <= 0:
            player.hp = 1
            io.out("")
            io.out("You collapse, broken. A passing herbalist drags you back to safety...")
            io.out("(You wake at 1 HP. Rest well.)")
            return "defeat"


def _enemy_atk(enemy_state: Dict[str, Any]) -> int:
    base = int(enemy_state["atk"])
    return max(1, base + random.randint(-1, 2))


def _enemy_choose_technique(world, enemy_state):
    techs = enemy_state.get("techniques", [])
    if not techs or random.random() < 0.5:
        return None
    tid = random.choice(techs)
    return world["techniques"].get(tid)


def _apply_pill(player: Player, item: Dict[str, Any], io,
                status_list: Optional[List[Dict[str, Any]]] = None) -> None:
    eff = item.get("effect", "")
    pwr = int(item.get("power", 0))
    if eff == "hp_heal":
        healed = min(player.max_hp, player.hp + pwr) - player.hp
        player.hp += healed
        io.out(f"You swallow {item['name']}; +{healed} HP.")
    elif eff == "qi_gain":
        player.qi += pwr
        io.out(f"You swallow {item['name']}; +{pwr} qi.")
    elif eff == "atk_buff":
        player.atk += pwr
        io.out(f"You swallow {item['name']}; +{pwr} ATK (permanent).")
    elif eff == "cleanse":
        if status_list is None:
            io.out(f"You swallow {item['name']}. A cool stillness settles in your chest.")
        else:
            before = len(status_list)
            status_list[:] = [s for s in status_list if s["type"] not in _NEGATIVE]
            cleared = before - len(status_list)
            if cleared:
                io.out(f"You swallow {item['name']}; {cleared} toxin(s) are purged from your meridians.")
            else:
                io.out(f"You swallow {item['name']}; finding no poison, it leaves only clarity.")
    else:
        io.out(f"You swallow {item['name']}, but feel no obvious change.")
