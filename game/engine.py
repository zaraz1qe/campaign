"""The main REPL game engine."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import random
import sys
import textwrap
import shlex

from . import loader, cultivation, combat, quests
from .state import Player


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
          read <lore>                     read a lore entry you've discovered
          inventory  (i)                  list possessions
          techniques (t)                  list martial arts known
          status     (s)                  player sheet
          quest                           list quests
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
        npcs = loc.get("npcs", [])
        if npcs:
            self.out("")
            self.out("Here you see:")
            for nid in npcs:
                n = self.world["npcs"].get(nid, {})
                self.out(f"  - {n.get('name', nid)}: {n.get('title','')}")
        enemies = loc.get("enemies", [])
        if enemies:
            self.out("Threats prowl these grounds:")
            for eid in enemies:
                e = self.world["enemies"].get(eid, {})
                self.out(f"  ! {e.get('name', eid)}")
        items = loc.get("items_on_ground", [])
        if items:
            self.out("On the ground:")
            for iid in items:
                it = self.world["items"].get(iid, {})
                self.out(f"  * {it.get('name', iid)} (use `take {iid}`)")
        exits = loc.get("exits", {})
        if exits:
            self.out("Exits: " + ", ".join(f"{d}->{t}" for d, t in exits.items()))
        # Trigger random event
        self._maybe_event(loc)
        # Quest progression triggers from visiting
        self._note_quests()

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
        if n.get("teaches"):
            names = [self.world["techniques"].get(t, {}).get("name", t) for t in n["teaches"]]
            self.out(f"  (Can teach: {', '.join(names)})")
        if n.get("sells"):
            self.out("  (Sells:")
            for iid in n["sells"]:
                it = self.world["items"].get(iid, {})
                self.out(f"     {it.get('name', iid)} — {it.get('value', '?')} stones")
            self.out("  )")
        self.player.talked_to.add(npc_id)
        if n.get("gives_quest"):
            self.out(quests.offer_quest(self.world, self.player, n["gives_quest"]))
        self._note_quests()

    def _find_in_loc(self, category: str, query: str) -> Optional[str]:
        q = query.lower().replace(" ", "_")
        loc = self._loc()
        candidates = loc.get(category, []) or loc.get(category.rstrip("s") + "s", [])
        if category == "enemies":
            candidates = loc.get("enemies", [])
        elif category == "npcs":
            candidates = loc.get("npcs", [])
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
            # If there's exactly one enemy here, fight it.
            enemies = self._loc().get("enemies", [])
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

    def cmd_breakthrough(self, _arg: str) -> None:
        self.out(cultivation.breakthrough(self.world, self.player))

    # ------------------------------------------------------------------
    def cmd_learn(self, arg: str) -> None:
        if not arg:
            self.out("Learn what?")
            return
        tid = arg.strip().lower().replace(" ", "_")
        # Find an NPC here who teaches this
        loc = self._loc()
        teacher = None
        for nid in loc.get("npcs", []):
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
        for nid in self._loc().get("npcs", []):
            n = self.world["npcs"].get(nid, {})
            for cand in (n.get("sells") or []):
                cname = self.world["items"].get(cand, {}).get("name", "").lower().replace(" ", "_")
                if cand == iid or cname == iid:
                    it = self.world["items"][cand]
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
        self.out("")
        self.out(f"Name:    {self.player.name}")
        self.out(f"Realm:   {cr.get('name','?')}  —  {cr.get('description','')}")
        if nxt:
            self.out(f"  Qi: {self.player.qi}/{cr.get('qi_required','?')} "
                     f"(next: {nxt.get('name','?')})")
        else:
            self.out(f"  Qi: {self.player.qi}  (no higher realm known)")
        self.out(f"HP:      {self.player.hp}/{self.player.max_hp}")
        self.out(f"ATK/DEF/SPD: {self.player.atk} / {self.player.defense} / {self.player.spd}")
        self.out(f"XP:      {self.player.xp}")
        self.out(f"Stones:  {self.player.spirit_stones}")
        self.out(f"Location:{self.world['locations'].get(self.player.location,{}).get('name', self.player.location)}")
        self.out(f"Visited: {len(self.player.visited)} / {len(self.world['locations'])} locations")
        if self.player.reputation:
            self.out("Reputation:")
            for sid, v in sorted(self.player.reputation.items()):
                sname = self.world["sects"].get(sid, {}).get("name", sid)
                self.out(f"  {sname}: {v:+d}")

    def cmd_quest(self, _arg: str) -> None:
        self.out(quests.quest_status(self.world, self.player))

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
        "take": "cmd_take",
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

    def repl(self) -> None:
        self.banner()
        while True:
            try:
                line = self.io.ask("\n> ")
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
