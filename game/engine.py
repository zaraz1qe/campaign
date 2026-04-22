"""The main REPL game engine."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import random
import sys
import textwrap
import shlex

from . import loader, cultivation, combat, quests
from .state import Player, EQUIP_SLOTS, rep_rank, affinity_tier, affinity_bonus


SAVE_DIR = Path(__file__).resolve().parent.parent / "saves"
SAVE_DIR.mkdir(exist_ok=True)


# Simple IO adapter so combat can prompt for input mid-fight.
class IO:
    def __init__(self, out_func=print, in_func=input):
        self._out = out_func
        self._in = in_func
    def out(self, s: str = "") -> None:
        self._out(s)
    def ask(self, prompt: str) -> str:
        try:
            return self._in(prompt)
        except (EOFError, KeyboardInterrupt):
            return "f"


def _wrap(text: str, width: int = 78) -> str:
    paragraphs = (text or "").split("\n")
    return "\n".join(
        textwrap.fill(p, width=width, replace_whitespace=False, drop_whitespace=False)
        if p.strip() else ""
        for p in paragraphs
    )


class Game:
    def __init__(self, io: Optional[IO] = None, seed: Optional[int] = None):
        self.io = io or IO()
        if seed is not None:
            random.seed(seed)
        self.world = loader.load_all()
        self.player = Player()
        # If the default starting location doesn't exist, fall back to first.
        if self.player.location not in self.world["locations"]:
            ids = sorted(self.world["locations"].keys())
            if ids:
                self.player.location = ids[0]

    # ------------------------------------------------------------------
    def out(self, s: str = "") -> None:
        self.io.out(s)

    # ------------------------------------------------------------------
    def banner(self) -> None:
        self.out("=" * 70)
        self.out("    JADE WIND CHRONICLES — A Wuxia Cultivation Tale")
        self.out("=" * 70)
        self.out(f"  Loaded: {loader.stats(self.world)}")
        self.out("  Type 'help' for commands. Press Enter on empty line to look.")
        self.out("")
        self.cmd_look("")

    # ------------------------------------------------------------------
    def cmd_help(self, _arg: str) -> None:
        self.out(textwrap.dedent("""
        Commands:
          look                            describe surroundings
          go <direction>                  travel via an exit
          map                             show known exits
          talk <npc>                      speak with an NPC here
          fight <enemy>                   engage an enemy here
          cultivate                       sit and gather qi
          breakthrough                    attempt to advance realm
          learn <technique>               learn a known technique (if NPC teaches)
          buy <item>                      buy an item from a vendor here
          use <item>                      use a pill from inventory
          equip <item>                    equip a weapon / robe / accessory
          unequip <slot>                  remove what's in a slot
          gear                            list what you have equipped
          craft [recipe]                  list or execute a forge / brew recipe
          recipes                         list recipes at this location
          read <lore>                     read a lore entry you've discovered
          inventory  (i)                  list possessions
          techniques (t)                  list martial arts known
          status     (s)                  player sheet
          quest                           list quests
          reputation (rep)                list standing with each sect
          recruit <npc>                   ask an able companion to walk with you
          dismiss                         release your companion
          companion (party)               show your companion's condition
          lore                            list lore you've collected
          name <yourname>                 set your name
          save [slot]                     save game (slot defaults to 'default')
          load [slot]                     load saved game
          help                            show this help
          quit                            exit
        Shorthand:  n / s / e / w / u / d  for go directions; '' (Enter) = look
        """).strip())

    # ------------------------------------------------------------------
    def _loc(self) -> Dict[str, Any]:
        return self.world["locations"].get(self.player.location, {})

    def _rep_visible(self, obj: Dict[str, Any]) -> bool:
        """True if the player's current rep meets the object's spawn gates.
        A missing field means no gate. `requires_rep` is a floor (rep >= min);
        `requires_rep_at_most` is a ceiling (rep <= max). Used to let NPCs and
        enemies appear/disappear based on faction standing — e.g. an assassin
        who only shows up once you've angered their sect, or a sect scout who
        vanishes once you're reviled enough that even they have given up."""
        req_min = obj.get("requires_rep") or {}
        if req_min and not self.player.meets_rep(req_min):
            return False
        req_max = obj.get("requires_rep_at_most") or {}
        if req_max:
            for sid, maxv in req_max.items():
                if self.player.rep(sid) > int(maxv):
                    return False
        return True

    def _visible_here(self, category: str, field: str) -> list:
        """Filter a location's npc/enemy list by per-object rep gates."""
        loc = self._loc()
        out = []
        for cid in (loc.get(field) or []):
            obj = self.world[category].get(cid)
            if obj is None:
                continue
            if self._rep_visible(obj):
                out.append(cid)
        return out

    def cmd_look(self, _arg: str) -> None:
        loc = self._loc()
        if not loc:
            self.out("(You float in a featureless void. Add some locations!)")
            return
        self.out("")
        self.out(f"~~ {loc.get('name', self.player.location)} ~~")
        if loc.get("region"):
            self.out(f"   ({loc['region']})")
        self.out(_wrap(loc.get("description", "")))
        if self.player.location not in self.player.visited:
            ft = loc.get("first_visit_text")
            if ft:
                self.out("")
                self.out(_wrap(ft))
            self.player.visited.add(self.player.location)
        npcs = self._visible_here("npcs", "npcs")
        if npcs:
            self.out("")
            self.out("Here you see:")
            for nid in npcs:
                n = self.world["npcs"].get(nid, {})
                self.out(f"  - {n.get('name', nid)}: {n.get('title','')}")
        enemies = self._visible_here("enemies", "enemies")
        if enemies:
            self.out("Threats prowl these grounds:")
            for eid in enemies:
                e = self.world["enemies"].get(eid, {})
                self.out(f"  ! {e.get('name', eid)}")
                ambush = e.get("ambush_text")
                if ambush:
                    self.out(_wrap("      " + ambush))
        items = loc.get("items_on_ground", [])
        if items:
            self.out("On the ground:")
            for iid in items:
                it = self.world["items"].get(iid, {})
                self.out(f"  * {it.get('name', iid)} (use `take {iid}`)")
        exits = loc.get("exits", {})
        if exits:
            self.out("Exits: " + ", ".join(f"{d}->{t}" for d, t in exits.items()))
        # A companion may have something to say about this particular place.
        self._maybe_companion_bark()
        # Trigger random event
        self._maybe_event(loc)
        # Quest progression triggers from visiting
        self._note_quests()

    def _maybe_companion_bark(self) -> None:
        """Print the companion's location-specific bark once per arrival.
        Barks are tracked per-companion via the runtime `last_bark_loc` — stays
        in the player save across sessions, so you hear the line once when you
        walk a companion into a place that matters to them."""
        comp = self.player.companion
        if not comp or comp.get("downed"):
            return
        npc = self.world["npcs"].get(comp.get("id", ""), {})
        barks = (npc.get("companion") or {}).get("location_barks") or {}
        loc_id = self.player.location
        line = barks.get(loc_id)
        if not line:
            return
        if comp.get("last_bark_loc") == loc_id:
            return
        comp["last_bark_loc"] = loc_id
        cname = npc.get("name", comp.get("id", "Companion"))
        self.out("")
        self.out(_wrap(f"  [{cname}] {line}"))

    def _note_quests(self) -> None:
        for note in quests.progress_quests(self.world, self.player):
            self.out(note)

    def _maybe_event(self, loc: Dict[str, Any]) -> None:
        for eid in loc.get("events", []):
            ev = self.world["events"].get(eid)
            if not ev:
                continue
            if random.random() < float(ev.get("chance", 0.0)):
                self.out("")
                self.out(_wrap("* " + ev.get("text", "")))
                eff = ev.get("effect", {}) or {}
                if "qi" in eff:
                    self.player.qi += int(eff["qi"])
                if "hp" in eff:
                    self.player.hp = max(1, min(self.player.max_hp, self.player.hp + int(eff["hp"])))
                if "spirit_stones" in eff:
                    self.player.spirit_stones += int(eff["spirit_stones"])
                if "item" in eff:
                    self.player.add_item(eff["item"], 1)
                    iname = self.world["items"].get(eff["item"], {}).get("name", eff["item"])
                    self.out(f"  (Acquired: {iname})")
                if "lore" in eff:
                    self.player.known_lore.add(eff["lore"])
                    title = self.world["lore"].get(eff["lore"], {}).get("title", eff["lore"])
                    self.out(f"  (Lore learned: {title})")

    # ------------------------------------------------------------------
    def cmd_go(self, arg: str) -> None:
        d = arg.strip().lower()
        if not d:
            self.out("Go where?")
            return
        # Direction aliases
        aliases = {"n":"north","s":"south","e":"east","w":"west","u":"up","d":"down",
                   "ne":"northeast","nw":"northwest","se":"southeast","sw":"southwest",
                   "in":"in","out":"out"}
        d = aliases.get(d, d)
        loc = self._loc()
        exits = loc.get("exits", {})
        if d not in exits:
            self.out(f"No path leads {d}.")
            return
        target = exits[d]
        if target not in self.world["locations"]:
            self.out(f"(Path leads to '{target}', but that location is undefined yet.)")
            return
        self.player.location = target
        self.cmd_look("")

    def cmd_map(self, _arg: str) -> None:
        loc = self._loc()
        exits = loc.get("exits", {})
        if not exits:
            self.out("There are no obvious paths from here.")
            return
        self.out("From here you can travel:")
        for d, t in exits.items():
            ld = self.world["locations"].get(t, {})
            mark = "" if t in self.player.visited else "  (unexplored)"
            self.out(f"  {d:10s} -> {ld.get('name', t)}{mark}")

    # ------------------------------------------------------------------
    def cmd_talk(self, arg: str) -> None:
        if not arg:
            self.out("Talk to whom?")
            return
        npc_id = self._find_in_loc("npcs", arg)
        if not npc_id:
            self.out("No such person here.")
            return
        n = self.world["npcs"][npc_id]
        self.out("")
        self.out(f"--- {n.get('name', npc_id)} ---")
        for line in n.get("dialogue", []):
            self.out(_wrap(f'  "{line}"'))
        for line in self._rep_dialogue_lines(n):
            self.out(_wrap(f'  "{line}"'))
        # A companion at your shoulder may be known to this NPC — in which case
        # the NPC speaks to them, too. The exchange reads as the NPC addressing
        # the companion; the companion's answering line (if any) follows.
        for line in self._companion_reply_lines(n):
            self.out(_wrap(f'  "{line}"'))
        if n.get("teaches"):
            names = [self.world["techniques"].get(t, {}).get("name", t) for t in n["teaches"]]
            self.out(f"  (Can teach: {', '.join(names)})")
        if n.get("sells"):
            self.out("  (Sells:")
            for iid in n["sells"]:
                it = self.world["items"].get(iid, {})
                self.out(f"     {it.get('name', iid)} — {it.get('value', '?')} stones")
            self.out("  )")
        recs = self._recipes_at(npc_id)
        if recs:
            type_tag = {"forge": "Forges", "brew": "Brews"}.get(
                next(iter(recs.values())).get("type", ""), "Crafts"
            )
            self.out(f"  ({type_tag} — try `craft` or `recipes` here):")
            for rid, r in recs.items():
                out_id = r.get("output", "?")
                out_name = self.world["items"].get(out_id, {}).get("name", out_id)
                self.out(f"     {rid} → {out_name}")
        self.player.talked_to.add(npc_id)
        if n.get("gives_quest"):
            self.out(quests.offer_quest(self.world, self.player, n["gives_quest"]))
        self._note_quests()

    def _rep_gate_msg(self, requires: Dict[str, int]) -> str:
        """Return '' if the player meets all rep requirements; otherwise a
        short gating message enumerating the shortfalls by sect name."""
        short = self.player.rep_shortfalls(requires or {})
        if not short:
            return ""
        parts = []
        for sid, s in short.items():
            sname = self.world["sects"].get(sid, {}).get("name", sid)
            have = self.player.rep(sid)
            need = have + s
            parts.append(f"{sname} (have {have:+d}, need {need:+d})")
        return "Required standing: " + "; ".join(parts) + "."

    def _companion_reply_lines(self, npc: Dict[str, Any]) -> list:
        """Return the lines an NPC adds when a specific companion is bound.
        Data shape on the npc: `companion_reply: {companion_npc_id: str | [str...]}`.
        A single string is wrapped into a one-line list; a list is returned in
        order. If no companion is active or the NPC has no entry for them,
        returns an empty list."""
        comp = self.player.companion
        if not comp or comp.get("downed"):
            return []
        replies = npc.get("companion_reply") or {}
        if not isinstance(replies, dict):
            return []
        entry = replies.get(comp.get("id", ""))
        if entry is None:
            return []
        if isinstance(entry, str):
            return [entry]
        if isinstance(entry, list):
            return [s for s in entry if isinstance(s, str) and s.strip()]
        return []

    def _rep_dialogue_lines(self, npc: Dict[str, Any]) -> list:
        """Pick one line per sect from npc['rep_dialogue'] whose threshold the
        player's rep currently meets. Positive thresholds trigger when rep >=
        threshold; negative ones trigger when rep <= threshold. The chosen
        threshold is the one closest to the player's rep — i.e. highest met
        positive, or lowest met negative."""
        out = []
        rep_lines = npc.get("rep_dialogue") or {}
        if not isinstance(rep_lines, dict):
            return out
        for sid, tiers in rep_lines.items():
            if not isinstance(tiers, dict):
                continue
            value = self.player.rep(sid)
            chosen_thr = None
            for thr_s in tiers:
                try:
                    thr = int(thr_s)
                except (TypeError, ValueError):
                    continue
                if thr >= 0 and value >= thr:
                    if chosen_thr is None or thr > chosen_thr:
                        chosen_thr = thr
                elif thr < 0 and value <= thr:
                    if chosen_thr is None or thr < chosen_thr:
                        chosen_thr = thr
            if chosen_thr is None:
                continue
            block = tiers.get(str(chosen_thr)) or tiers.get(chosen_thr) or []
            if isinstance(block, str):
                block = [block]
            for line in block:
                out.append(line)
        return out

    def _find_in_loc(self, category: str, query: str) -> Optional[str]:
        q = query.lower().replace(" ", "_")
        loc = self._loc()
        candidates = loc.get(category, []) or loc.get(category.rstrip("s") + "s", [])
        if category == "enemies":
            candidates = loc.get("enemies", [])
        elif category == "npcs":
            candidates = loc.get("npcs", [])
        # Filter out entities whose rep gates aren't met — they aren't here
        # for this player right now.
        candidates = [c for c in candidates
                      if self._rep_visible(self.world[category].get(c, {}))]
        for cid in candidates:
            if cid == q:
                return cid
            obj = self.world[category].get(cid, {})
            if obj.get("name", "").lower().replace(" ", "_") == q:
                return cid
            # also accept partial match
            if q in cid:
                return cid
        return None

    # ------------------------------------------------------------------
    def cmd_fight(self, arg: str) -> None:
        if not arg:
            # If there's exactly one (visible) enemy here, fight it.
            enemies = self._visible_here("enemies", "enemies")
            if len(enemies) == 1:
                arg = enemies[0]
            else:
                self.out("Fight whom?")
                return
        eid = self._find_in_loc("enemies", arg)
        if not eid:
            self.out("No such foe here.")
            return
        result = combat.fight(self.world, self.player, eid, self.io)
        self._note_quests()
        if result == "victory":
            # Optionally remove the enemy from the location list (one-shot foes
            # can be respawned by being re-added to the list in a content patch).
            pass

    # ------------------------------------------------------------------
    def cmd_cultivate(self, _arg: str) -> None:
        self.out(cultivation.cultivate(self.world, self.player))
        # Cultivation shares breath with your sworn companion: revive them if
        # they were downed, or top them up otherwise. Qi is *not* shared (they
        # regenerate it mid-combat on their own turn).
        comp = self.player.companion
        if comp:
            cname = self.world["npcs"].get(comp.get("id", ""), {}).get("name",
                                                                        comp.get("id", "Your companion"))
            was_downed = bool(comp.get("downed"))
            was_wounded = int(comp.get("hp", 0)) < int(comp.get("max_hp", 0))
            comp["hp"] = int(comp.get("max_hp", comp.get("hp", 0)))
            comp["downed"] = False
            if was_downed:
                self.out(f"{cname}'s meridians settle; their breath comes even again. They are ready to walk with you.")
            elif was_wounded:
                self.out(f"{cname} shares your breath; their wounds close.")

    def cmd_breakthrough(self, _arg: str) -> None:
        self.out(cultivation.breakthrough(self.world, self.player))

    # ------------------------------------------------------------------
    def cmd_learn(self, arg: str) -> None:
        if not arg:
            self.out("Learn what?")
            return
        tid = arg.strip().lower().replace(" ", "_")
        # Find an NPC here who teaches this (only visible ones).
        teacher = None
        for nid in self._visible_here("npcs", "npcs"):
            n = self.world["npcs"].get(nid, {})
            if tid in (n.get("teaches") or []):
                teacher = n
                break
            for tcand in (n.get("teaches") or []):
                tname = self.world["techniques"].get(tcand, {}).get("name", "")
                if tname.lower().replace(" ", "_") == tid:
                    teacher = n
                    tid = tcand
                    break
            if teacher:
                break
        if not teacher:
            self.out("No master here teaches that art.")
            return
        if tid in self.player.techniques:
            self.out("You already know this technique.")
            return
        t = self.world["techniques"].get(tid)
        if not t:
            self.out("(That technique isn't defined.)")
            return
        if not cultivation.realm_meets(self.world, self.player, t.get("requires_realm", "")):
            need = self.world["realms"].get(t["requires_realm"], {}).get("name", t["requires_realm"])
            self.out(f"Your realm is too low. Requires: {need}.")
            return
        gate = self._rep_gate_msg(t.get("requires_rep") or {})
        if gate:
            self.out(f"The master will not entrust this art to you yet. {gate}")
            return
        cost = int(t.get("learn_cost", 0))
        if self.player.spirit_stones < cost:
            self.out(f"You lack {cost} spirit stones.")
            return
        self.player.spirit_stones -= cost
        self.player.techniques.append(tid)
        self.out(f"You meditate under {teacher['name']} and absorb {t['name']}.")

    # ------------------------------------------------------------------
    def cmd_buy(self, arg: str) -> None:
        if not arg:
            self.out("Buy what?")
            return
        iid = arg.strip().lower().replace(" ", "_")
        for nid in self._visible_here("npcs", "npcs"):
            n = self.world["npcs"].get(nid, {})
            for cand in (n.get("sells") or []):
                cname = self.world["items"].get(cand, {}).get("name", "").lower().replace(" ", "_")
                if cand == iid or cname == iid:
                    it = self.world["items"][cand]
                    gate = self._rep_gate_msg(it.get("requires_rep") or {})
                    if gate:
                        self.out(f"{n['name']} will not sell {it['name']} to you. {gate}")
                        return
                    price = int(it.get("value", 0))
                    if self.player.spirit_stones < price:
                        self.out(f"You cannot afford {it['name']} ({price} stones).")
                        return
                    self.player.spirit_stones -= price
                    self.player.add_item(cand, 1)
                    self.out(f"You buy {it['name']} from {n['name']} for {price} stones.")
                    return
        self.out("No vendor here sells that.")

    # ------------------------------------------------------------------
    def cmd_use(self, arg: str) -> None:
        if not arg:
            self.out("Use what?")
            return
        iid = arg.strip().lower().replace(" ", "_")
        # match by id or by name
        if iid not in self.player.inventory:
            for cand in list(self.player.inventory):
                if self.world["items"].get(cand, {}).get("name", "").lower().replace(" ", "_") == iid:
                    iid = cand
                    break
        if iid not in self.player.inventory:
            self.out("You have no such item.")
            return
        it = self.world["items"].get(iid, {})
        if it.get("type") != "pill":
            self.out("You can only use pills here.")
            return
        combat._apply_pill(self.player, it, self.io)
        self.player.remove_item(iid, 1)

    # ------------------------------------------------------------------
    def _resolve_item_by_query(self, q: str) -> Optional[str]:
        """Match an item id from inventory by id or by display name."""
        if q in self.player.inventory:
            return q
        for cand in self.player.inventory:
            cname = self.world["items"].get(cand, {}).get("name", "").lower().replace(" ", "_")
            if cname == q:
                return cand
        return None

    def cmd_equip(self, arg: str) -> None:
        if not arg:
            self.out("Equip what?")
            return
        q = arg.strip().lower().replace(" ", "_")
        iid = self._resolve_item_by_query(q)
        if not iid:
            self.out("You have no such item.")
            return
        it = self.world["items"].get(iid, {})
        slot = it.get("slot")
        if slot not in EQUIP_SLOTS:
            self.out(f"{it.get('name', iid)} cannot be equipped.")
            return
        req = it.get("requires_realm")
        if req and not cultivation.realm_meets(self.world, self.player, req):
            need = self.world["realms"].get(req, {}).get("name", req)
            self.out(f"Your foundation is too thin. {it['name']} requires: {need}.")
            return
        gate = self._rep_gate_msg(it.get("requires_rep") or {})
        if gate:
            self.out(f"{it['name']} rejects your touch — its maker knows you by reputation. {gate}")
            return
        # Swap: return current to inventory, equip new.
        cur = self.player.equipped.get(slot, "")
        if cur == iid:
            self.out(f"{it.get('name', iid)} is already equipped.")
            return
        if cur:
            self.player.add_item(cur, 1)
            cur_name = self.world["items"].get(cur, {}).get("name", cur)
            self.out(f"You stow {cur_name}.")
        self.player.remove_item(iid, 1)
        self.player.equipped[slot] = iid
        # HP stays absolute; new max may raise or keep it.
        new_max = self.player.eff_max_hp(self.world)
        if self.player.hp > new_max:
            self.player.hp = new_max
        self.out(f"You equip {it['name']}. ({slot})")
        self._describe_gear_bonuses(it)

    def cmd_unequip(self, arg: str) -> None:
        slot = arg.strip().lower()
        if not slot:
            self.out(f"Unequip which slot? ({', '.join(EQUIP_SLOTS)})")
            return
        if slot not in EQUIP_SLOTS:
            self.out(f"No such slot '{slot}'.")
            return
        cur = self.player.equipped.get(slot, "")
        if not cur:
            self.out(f"Your {slot} slot is already empty.")
            return
        self.player.equipped[slot] = ""
        self.player.add_item(cur, 1)
        new_max = self.player.eff_max_hp(self.world)
        if self.player.hp > new_max:
            self.player.hp = new_max
        name = self.world["items"].get(cur, {}).get("name", cur)
        self.out(f"You unequip {name}.")

    def cmd_gear(self, _arg: str) -> None:
        self.out("Equipped:")
        any_gear = False
        for slot in EQUIP_SLOTS:
            iid = self.player.equipped.get(slot, "")
            if not iid:
                self.out(f"  {slot:10s} —")
                continue
            any_gear = True
            it = self.world["items"].get(iid, {})
            bonuses = []
            for k in ("atk", "def", "spd", "hp"):
                v = int(it.get(f"{k}_bonus", 0) or 0)
                if v:
                    bonuses.append(f"+{v} {k.upper()}")
            if it.get("on_hit_effect"):
                bonuses.append(f"on hit: {it['on_hit_effect']} {it.get('on_hit_power', 1)}")
            suffix = f"  ({', '.join(bonuses)})" if bonuses else ""
            self.out(f"  {slot:10s} {it.get('name', iid)}{suffix}")
        if not any_gear:
            self.out("  (nothing — visit a vendor or earn gear in battle)")
        gb = self.player.gear_bonuses(self.world)
        totals = ", ".join(f"+{v} {k.upper()}" for k, v in gb.items() if v)
        if totals:
            self.out(f"Gear totals: {totals}")

    def _describe_gear_bonuses(self, it: Dict[str, Any]) -> None:
        bonuses = []
        for k in ("atk", "def", "spd", "hp"):
            v = int(it.get(f"{k}_bonus", 0) or 0)
            if v:
                bonuses.append(f"+{v} {k.upper()}")
        if it.get("on_hit_effect"):
            bonuses.append(f"on hit: {it['on_hit_effect']} {it.get('on_hit_power', 1)}")
        if bonuses:
            self.out("  (" + ", ".join(bonuses) + ")")

    def cmd_take(self, arg: str) -> None:
        loc = self._loc()
        items = loc.get("items_on_ground", [])
        if not arg:
            self.out("Take what?")
            return
        iid = arg.strip().lower().replace(" ", "_")
        if iid not in items:
            self.out("That isn't here.")
            return
        items.remove(iid)
        self.player.add_item(iid, 1)
        iname = self.world["items"].get(iid, {}).get("name", iid)
        self.out(f"You pick up {iname}.")

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Crafting (forging / brewing).
    def _recipes_at(self, npc_id: str) -> Dict[str, Dict[str, Any]]:
        """Recipes keyed by id that belong to the given crafter NPC."""
        return {
            rid: r for rid, r in self.world["recipes"].items()
            if r.get("crafter") == npc_id
        }

    def _crafters_here(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """crafter_npc_id -> {recipe_id: recipe} for each crafter at this location."""
        out: Dict[str, Dict[str, Dict[str, Any]]] = {}
        for nid in self._visible_here("npcs", "npcs"):
            recs = self._recipes_at(nid)
            if recs:
                out[nid] = recs
        return out

    def _format_recipe_line(self, rid: str, r: Dict[str, Any]) -> str:
        parts = []
        for mid, qty in (r.get("inputs") or {}).items():
            mname = self.world["items"].get(mid, {}).get("name", mid)
            parts.append(f"{qty}x {mname}")
        stones = int(r.get("stones", 0))
        if stones:
            parts.append(f"{stones} stones")
        cost = ", ".join(parts) if parts else "(no cost)"
        out_id = r.get("output", "?")
        out_name = self.world["items"].get(out_id, {}).get("name", out_id)
        qty_out = int(r.get("output_qty", 1))
        out_str = out_name + (f" x{qty_out}" if qty_out > 1 else "")
        req = r.get("requires_realm")
        gate = ""
        if req:
            rname = self.world["realms"].get(req, {}).get("name", req)
            gate = f"  [{rname}+]"
        rep_req = r.get("requires_rep") or {}
        if rep_req:
            parts = []
            for sid, minv in rep_req.items():
                sname = self.world["sects"].get(sid, {}).get("name", sid)
                parts.append(f"{sname} {minv:+d}")
            gate += f"  [rep: {', '.join(parts)}]"
        return f"  {rid}: {out_str} — {cost}{gate}"

    def cmd_craft(self, arg: str) -> None:
        crafters = self._crafters_here()
        if not arg:
            if not crafters:
                self.out("No crafter tends a forge or cauldron here.")
                return
            self.out("Crafting available here:")
            for nid, recs in crafters.items():
                n = self.world["npcs"].get(nid, {})
                self.out("")
                self.out(f"--- {n.get('name', nid)} ---")
                for rid, r in recs.items():
                    self.out(self._format_recipe_line(rid, r))
            self.out("")
            self.out("Use `craft <recipe_id>` to begin.")
            return
        rid = arg.strip().lower().replace(" ", "_")
        recipe = self.world["recipes"].get(rid)
        if not recipe:
            self.out(f"No such recipe: '{rid}'.")
            return
        crafter_id = recipe.get("crafter", "")
        here = self._visible_here("npcs", "npcs")
        if crafter_id and crafter_id not in here:
            cname = self.world["npcs"].get(crafter_id, {}).get("name", crafter_id)
            cloc_id = None
            for lid, loc in self.world["locations"].items():
                if crafter_id in (loc.get("npcs") or []):
                    cloc_id = lid
                    break
            cloc = self.world["locations"].get(cloc_id or "", {}).get("name", cloc_id or "?")
            self.out(f"This craft wants {cname}'s hand. Seek them at {cloc}.")
            return
        req = recipe.get("requires_realm")
        if req and not cultivation.realm_meets(self.world, self.player, req):
            need = self.world["realms"].get(req, {}).get("name", req)
            self.out(f"Your foundation is too thin. {recipe.get('name', rid)} requires: {need}.")
            return
        gate = self._rep_gate_msg(recipe.get("requires_rep") or {})
        if gate:
            cname = self.world["npcs"].get(recipe.get("crafter", ""), {}).get("name", "The crafter")
            self.out(f"{cname} shakes their head over the plans. {gate}")
            return
        inputs = recipe.get("inputs") or {}
        missing = []
        for mid, qty in inputs.items():
            if not self.player.has_item(mid, int(qty)):
                iname = self.world["items"].get(mid, {}).get("name", mid)
                have = self.player.inventory.get(mid, 0)
                missing.append(f"{iname} x{qty} (have {have})")
        if missing:
            self.out("You lack: " + "; ".join(missing))
            return
        stones = int(recipe.get("stones", 0))
        if self.player.spirit_stones < stones:
            self.out(f"You lack {stones} spirit stones (have {self.player.spirit_stones}).")
            return
        for mid, qty in inputs.items():
            self.player.remove_item(mid, int(qty))
        self.player.spirit_stones -= stones
        output = recipe["output"]
        qty_out = int(recipe.get("output_qty", 1))
        self.player.add_item(output, qty_out)
        out_name = self.world["items"].get(output, {}).get("name", output)
        flavor = recipe.get("flavor", "")
        if flavor:
            self.out("")
            self.out(_wrap(flavor))
        suffix = f" x{qty_out}" if qty_out > 1 else ""
        self.out(f"  (Crafted: {out_name}{suffix})")

    def cmd_recipes(self, _arg: str) -> None:
        self.cmd_craft("")

    # ------------------------------------------------------------------
    def cmd_read(self, arg: str) -> None:
        if not arg:
            if not self.player.known_lore:
                self.out("You have collected no lore yet.")
                return
            self.out("Lore in your memory:")
            for lid in sorted(self.player.known_lore):
                l = self.world["lore"].get(lid, {})
                self.out(f"  - {l.get('title', lid)}")
            return
        lid = arg.strip().lower().replace(" ", "_")
        if lid not in self.player.known_lore:
            self.out("You have not heard of that.")
            return
        l = self.world["lore"].get(lid, {})
        self.out("")
        self.out(f"=== {l.get('title', lid)} ===")
        self.out(_wrap(l.get("text", "")))

    def cmd_lore(self, _arg: str) -> None:
        self.cmd_read("")

    # ------------------------------------------------------------------
    def cmd_inventory(self, _arg: str) -> None:
        self.out(f"Spirit stones: {self.player.spirit_stones}")
        if not self.player.inventory:
            self.out("Your sleeves are empty.")
            return
        self.out("Inventory:")
        for iid, n in sorted(self.player.inventory.items()):
            it = self.world["items"].get(iid, {})
            self.out(f"  {n:>3}  {it.get('name', iid)}  — {it.get('description','')}")

    def cmd_techniques(self, _arg: str) -> None:
        if not self.player.techniques:
            self.out("You know no martial techniques yet.")
            return
        self.out("Techniques known:")
        for tid in self.player.techniques:
            t = self.world["techniques"].get(tid, {})
            self.out(f"  - {t.get('name', tid)} ({t.get('type','?')}, "
                     f"qi {t.get('qi_cost',0)}, dmg {t.get('damage',0)})")
            if t.get("description"):
                self.out(_wrap("      " + t["description"]))

    def cmd_status(self, _arg: str) -> None:
        cr = cultivation.current_realm(self.world, self.player)
        nxt = cultivation.next_realm(self.world, self.player)
        gb = self.player.gear_bonuses(self.world)
        self.out("")
        self.out(f"Name:    {self.player.name}")
        self.out(f"Realm:   {cr.get('name','?')}  —  {cr.get('description','')}")
        if nxt:
            self.out(f"  Qi: {self.player.qi}/{cr.get('qi_required','?')} "
                     f"(next: {nxt.get('name','?')})")
        else:
            self.out(f"  Qi: {self.player.qi}  (no higher realm known)")
        eff_max_hp = self.player.eff_max_hp(self.world)
        hp_tag = f" (base {self.player.max_hp} +{gb['hp']} gear)" if gb["hp"] else ""
        self.out(f"HP:      {self.player.hp}/{eff_max_hp}{hp_tag}")
        def _line(label: str, base: int, bonus: int) -> str:
            if bonus:
                return f"  {label}: {base + bonus}  (base {base} +{bonus} gear)"
            return f"  {label}: {base}"
        self.out("Stats:")
        self.out(_line("ATK", self.player.atk, gb["atk"]))
        self.out(_line("DEF", self.player.defense, gb["def"]))
        self.out(_line("SPD", self.player.spd, gb["spd"]))
        self.out(f"XP:      {self.player.xp}")
        self.out(f"Stones:  {self.player.spirit_stones}")
        self.out(f"Location:{self.world['locations'].get(self.player.location,{}).get('name', self.player.location)}")
        self.out(f"Visited: {len(self.player.visited)} / {len(self.world['locations'])} locations")
        # Equipped
        equipped_names = []
        for slot in EQUIP_SLOTS:
            iid = self.player.equipped.get(slot, "")
            if iid:
                nm = self.world["items"].get(iid, {}).get("name", iid)
                equipped_names.append(f"{slot}={nm}")
        if equipped_names:
            self.out("Gear:    " + "; ".join(equipped_names))
        if self.player.reputation:
            self.out("Reputation:")
            for sid, v in sorted(self.player.reputation.items()):
                sname = self.world["sects"].get(sid, {}).get("name", sid)
                self.out(f"  {sname}: {v:+d} ({rep_rank(int(v))})")
        comp = self.player.companion
        if comp:
            cname = self.world["npcs"].get(comp.get("id", ""), {}).get("name",
                                                                        comp.get("id", "Companion"))
            tag = " [DOWNED]" if comp.get("downed") else ""
            aff = self.player.affinity(comp.get("id", ""))
            self.out(f"Companion: {cname} ({comp.get('hp',0)}/{comp.get('max_hp',0)} HP){tag}  "
                     f"— bond: {affinity_tier(aff)} ({aff:+d})")

    def cmd_quest(self, _arg: str) -> None:
        self.out(quests.quest_status(self.world, self.player))

    # ------------------------------------------------------------------
    # Companion — recruit a qualified NPC to fight at your side. Only one at a
    # time; the recruited NPC still "lives" at their home location (visible on
    # look, talk-able), but their combat shape is snapshotted onto the player.
    def cmd_recruit(self, arg: str) -> None:
        if not arg:
            self.out("Recruit whom?")
            return
        npc_id = self._find_in_loc("npcs", arg)
        if not npc_id:
            self.out("No such person stands here to recruit.")
            return
        n = self.world["npcs"][npc_id]
        comp_def = n.get("companion")
        if not comp_def:
            self.out(f"{n.get('name', npc_id)} does not walk that road with you.")
            return
        # Can only hold one companion.
        if self.player.companion:
            cur_name = self.world["npcs"].get(self.player.companion.get("id", ""),
                                               {}).get("name", "your current companion")
            if self.player.companion.get("id") == npc_id:
                self.out(f"{n['name']} already walks with you.")
                return
            self.out(f"You must first dismiss {cur_name} before binding oaths with another.")
            return
        # Gates — realm / rep / quests.
        req_realm = comp_def.get("requires_realm")
        if req_realm and not cultivation.realm_meets(self.world, self.player, req_realm):
            need = self.world["realms"].get(req_realm, {}).get("name", req_realm)
            self.out(f"{n['name']} shakes their head. 'My road waits for a {need} — no sooner.'")
            return
        gate = self._rep_gate_msg(comp_def.get("requires_rep") or {})
        if gate:
            decline = comp_def.get("decline_dialogue") or f"{n['name']} will not walk with you yet."
            self.out(decline)
            self.out(gate)
            return
        req_q = comp_def.get("requires_quest")
        if req_q and req_q not in self.player.completed_quests:
            qname = self.world["quests"].get(req_q, {}).get("name", req_q)
            decline = comp_def.get("decline_dialogue") or f"{n['name']} is not ready to travel."
            self.out(decline)
            self.out(f"(Requires completed quest: {qname}.)")
            return
        # Instance the companion.
        self.player.companion = {
            "id": npc_id,
            "hp": int(comp_def.get("hp", 40)),
            "max_hp": int(comp_def.get("hp", 40)),
            "atk": int(comp_def.get("atk", 5)),
            "def": int(comp_def.get("def", 2)),
            "spd": int(comp_def.get("spd", 5)),
            "qi": int(comp_def.get("qi", 0)),
            "max_qi": int(comp_def.get("max_qi", comp_def.get("qi", 0))),
            "techniques": list(comp_def.get("techniques", [])),
            "downed": False,
            "last_bark_loc": None,
        }
        line = comp_def.get("recruit_dialogue") or \
               f"{n['name']} nods once. 'Lead. I will stand at your shoulder.'"
        self.out("")
        self.out(_wrap(f'  "{line}"'))
        self.out(f"({n['name']} now walks at your side.)")
        aff = self.player.affinity(npc_id)
        if aff > 0:
            self.out(f"  (Your bond resumes where it left off — {affinity_tier(aff)}, {aff:+d}.)")

    def cmd_dismiss(self, _arg: str) -> None:
        comp = self.player.companion
        if not comp:
            self.out("No one walks with you to dismiss.")
            return
        cname = self.world["npcs"].get(comp.get("id", ""), {}).get("name",
                                                                    "Your companion")
        self.player.companion = None
        self.out(f"You thank {cname} and release the bond. They turn for home.")

    def cmd_companion(self, _arg: str) -> None:
        comp = self.player.companion
        if not comp:
            self.out("You walk alone.")
            return
        n = self.world["npcs"].get(comp.get("id", ""), {})
        cname = n.get("name", comp.get("id", "Companion"))
        title = n.get("title", "")
        title_str = f" — {title}" if title else ""
        self.out(f"{cname}{title_str}")
        status_tag = "  [DOWNED — rest/cultivate to revive]" if comp.get("downed") else ""
        self.out(f"  HP: {comp.get('hp',0)}/{comp.get('max_hp',0)}{status_tag}")
        if comp.get("max_qi"):
            self.out(f"  Qi: {comp.get('qi',0)}/{comp.get('max_qi',0)}")
        base_atk = comp.get("atk", 0)
        base_def = comp.get("def", 0)
        base_spd = comp.get("spd", 0)
        aff = self.player.affinity(comp.get("id", ""))
        ab = affinity_bonus(aff)
        def _stat(label: str, base: int, bonus: int) -> str:
            if bonus:
                return f"{label} {base + bonus} ({base}+{bonus})"
            return f"{label} {base}"
        self.out("  " + "   ".join([
            _stat("ATK", base_atk, ab["atk"]),
            _stat("DEF", base_def, ab["def"]),
            _stat("SPD", base_spd, ab["spd"]),
        ]))
        self.out(f"  Bond: {affinity_tier(aff)} ({aff:+d})")
        techs = comp.get("techniques") or []
        if techs:
            tnames = [self.world["techniques"].get(t, {}).get("name", t) for t in techs]
            self.out(f"  Techniques: {', '.join(tnames)}")

    def cmd_reputation(self, _arg: str) -> None:
        """Show the player's standing with each sect that knows them."""
        sects = self.world.get("sects", {})
        # Show every sect, even at 0, so the player sees the full landscape.
        rows = []
        for sid, s in sorted(sects.items(), key=lambda kv: kv[1].get("name", kv[0])):
            v = self.player.rep(sid)
            rank = rep_rank(v)
            rows.append((s.get("name", sid), v, rank, s.get("alignment", "")))
        if not rows:
            self.out("No sects are known in this world yet.")
            return
        self.out("Standing with the sects:")
        for name, v, rank, align in rows:
            align_tag = f" [{align}]" if align else ""
            self.out(f"  {name:<32s}  {v:+3d}  {rank}{align_tag}")

    # ------------------------------------------------------------------
    def cmd_name(self, arg: str) -> None:
        if not arg.strip():
            self.out(f"Your name is {self.player.name}.")
            return
        self.player.name = arg.strip()
        self.out(f"You are henceforth known as {self.player.name}.")

    # ------------------------------------------------------------------
    def cmd_save(self, arg: str) -> None:
        slot = arg.strip() or "default"
        path = SAVE_DIR / f"{slot}.json"
        path.write_text(self.player.to_json(), encoding="utf-8")
        self.out(f"Saved to {path.name}.")

    def cmd_load(self, arg: str) -> None:
        slot = arg.strip() or "default"
        path = SAVE_DIR / f"{slot}.json"
        if not path.exists():
            self.out(f"No save in slot '{slot}'.")
            return
        self.player = Player.from_json(path.read_text(encoding="utf-8"))
        self.out(f"Loaded {path.name}.")
        self.cmd_look("")

    # ------------------------------------------------------------------
    def cmd_quit(self, _arg: str) -> None:
        raise SystemExit(0)

    # ------------------------------------------------------------------
    DISPATCH: Dict[str, str] = {
        "help": "cmd_help",
        "?": "cmd_help",
        "look": "cmd_look",
        "l": "cmd_look",
        "go": "cmd_go",
        "map": "cmd_map",
        "talk": "cmd_talk",
        "fight": "cmd_fight",
        "attack": "cmd_fight",
        "cultivate": "cmd_cultivate",
        "meditate": "cmd_cultivate",
        "breakthrough": "cmd_breakthrough",
        "learn": "cmd_learn",
        "buy": "cmd_buy",
        "use": "cmd_use",
        "equip": "cmd_equip",
        "wield": "cmd_equip",
        "wear": "cmd_equip",
        "unequip": "cmd_unequip",
        "remove": "cmd_unequip",
        "gear": "cmd_gear",
        "equipment": "cmd_gear",
        "take": "cmd_take",
        "craft": "cmd_craft",
        "forge": "cmd_craft",
        "brew": "cmd_craft",
        "recipes": "cmd_recipes",
        "read": "cmd_read",
        "lore": "cmd_lore",
        "inventory": "cmd_inventory",
        "i": "cmd_inventory",
        "inv": "cmd_inventory",
        "techniques": "cmd_techniques",
        "t": "cmd_techniques",
        "tech": "cmd_techniques",
        "status": "cmd_status",
        "s": "cmd_status",
        "quest": "cmd_quest",
        "quests": "cmd_quest",
        "reputation": "cmd_reputation",
        "rep": "cmd_reputation",
        "standing": "cmd_reputation",
        "recruit": "cmd_recruit",
        "dismiss": "cmd_dismiss",
        "companion": "cmd_companion",
        "party": "cmd_companion",
        "name": "cmd_name",
        "save": "cmd_save",
        "load": "cmd_load",
        "quit": "cmd_quit",
        "exit": "cmd_quit",
    }
    DIR_SHORTCUTS = {"n","s","e","w","u","d","ne","nw","se","sw","north","south",
                     "east","west","up","down","northeast","northwest",
                     "southeast","southwest","in","out"}

    def step(self, line: str) -> None:
        line = (line or "").strip()
        if not line:
            self.cmd_look("")
            return
        # direction shortcut
        first = line.split()[0].lower()
        if first in self.DIR_SHORTCUTS and len(line.split()) == 1:
            self.cmd_go(first)
            return
        try:
            tokens = shlex.split(line)
        except ValueError:
            tokens = line.split()
        cmd = tokens[0].lower()
        arg = " ".join(tokens[1:])
        method = self.DISPATCH.get(cmd)
        if not method:
            self.out(f"Unknown command: {cmd}. Try 'help'.")
            return
        getattr(self, method)(arg)

    def _prompt(self) -> str:
        cr = cultivation.current_realm(self.world, self.player)
        qi_cap = cr.get("qi_required", self.player.max_qi)
        return (f"[HP {self.player.hp}/{self.player.eff_max_hp(self.world)}  "
                f"Qi {self.player.qi}/{qi_cap}] > ")

    def repl(self) -> None:
        self.banner()
        while True:
            try:
                line = self.io.ask("\n" + self._prompt())
            except (EOFError, KeyboardInterrupt):
                self.out("")
                self.out("The wind carries you away. Farewell.")
                return
            try:
                self.step(line)
            except SystemExit:
                self.out("Farewell, cultivator.")
                return
            except Exception as e:
                self.out(f"(error: {e})")
