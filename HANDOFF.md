# HANDOFF — for the next scheduled session

> **Read order each session:** this file → `MEMORY.md` → `ROADMAP.md`.
> Then run `python3 tools/check_content.py` and `python3 play.py` to see the
> current state before changing anything.

---

## Where we are right now

The game (Jade Wind Chronicles, a text-based wuxia cultivation RPG) is running.
The architecture is intentionally **data-driven**: nearly all content lives in
JSON files under `content/<category>/`. The engine in `game/` is small and
should rarely need editing — most of your work each session is adding JSON.

### Current size (as of last session)
```
10 locations · 9 npcs · 5 enemies · 9 techniques · 13 items
2 sects · 3 quests · 7 events · 8 realms · 5 lore
```
Run `python3 -c "from game import loader; print(loader.stats(loader.load_all()))"`
to get a fresh count.

### What works
- REPL with: look, go (n/s/e/w/u/d aliases), map, talk, fight, cultivate,
  breakthrough, learn, buy, use, take, read, lore, inventory, techniques,
  status, quest, name, save, load, help, quit
- Turn-based combat with attack / technique / item / flee
- Cultivation: gain qi at locations (qi_density modifier), breakthrough with
  small tribulation chance
- Quests with visit/defeat/talk/collect step types, auto-progressed and
  auto-rewarded when steps complete
- Random ambient events on entering a location
- Save/load to `saves/<slot>.json`
- Content validator (`tools/check_content.py`) catches dangling references

### What does NOT exist yet (intentional — to be added)
- Equipment slots (weapons/armor are inventory-only)
- Alchemy/forging crafting system
- Companions, multi-enemy combat, day/night, achievements
- Reputation effects on dialogue (rep is tracked but unused)
- Any region beyond the Southern Wilds + Azure Cloud Range
- Most sects, most NPCs, most quests — see `ROADMAP.md` "Next Up"

---

## What to do this session

Pick **one or two** items from `ROADMAP.md` "Next Up" — the highest-leverage
ones are usually:

1. **A new region** (~6–10 linked locations + ~3–6 NPCs + ~3–5 enemies +
   2–4 events + 1–2 quests + 1–3 lore). One region per session is a
   great unit of work — it feels substantial and the content all
   reinforces itself.
2. **A new sect** (1 sect file + HQ location + 3+ NPCs + 3–5 signature
   techniques + 1 quest tied to them).
3. **Polish/refine** an existing area: deepen NPC dialogue, add events,
   fill in missing lore, add a side-quest.
4. **A bug fix or engine improvement** from `ROADMAP.md` "Engine
   Improvements" — but only if you can implement it cleanly without
   breaking saves or content.

When you're done, **always**:
1. Run `python3 tools/check_content.py` — fix any errors.
2. Run a scripted smoke-test of `play.py` with a few commands.
3. Update `ROADMAP.md`: tick what you did, add anything new you noticed.
4. Update the "Done Log" at the bottom of `ROADMAP.md` with date + summary.
5. Commit with a clear message and push to `claude/lucid-heisenberg-Bs2QZ`.

---

## Important conventions (don't break these)

- **IDs**: lowercase, snake_case, unique within their category. Used as
  primary keys; renaming an id will break saves and references.
- **Files**: any number of JSON files per category — group however makes
  sense (by region, by tier, by sect). Loader globs them all.
- **A file may contain a single object OR a list of objects.** Both work.
- **Cross-references must resolve.** Run the validator.
- **Don't hardcode content names in `game/` code.** If you find yourself
  writing `if npc_id == "elder_baixu"`, stop and reconsider — it should
  be data-driven.
- **Save format**: dataclass-of-Player serialized to JSON. Adding new
  fields to `Player` requires they default to something sensible so
  old saves still load (use `field(default=...)` or `field(default_factory=...)`).

---

## Idea seeds, free for the taking

If you're stuck for inspiration on a new region:

- **Northern Frost Plains** — an ice-locked steppe ruled by the Frostfang
  Tribe. Ice-cultivators who treat blood as currency. A buried Frozen
  Mirror Palace beneath the ice. Mammoth-scale beasts. A captive ghost
  trapped in an ice-mirror who teaches a forbidden art for help breaking
  free.
- **Eastern Sea of Cloud** — an archipelago above an actual sea of
  permanent cloud. Sword-sailors who ride flying ships. The legend of
  the Sea-Dragon, which surfaces once a century. Pirate-cultivators of
  the Crimson Tide. A lighthouse run by a blind monk who sees in qi.
- **Imperial Capital** — political intrigue, the Emperor's Hidden Guard
  who hunt rogue cultivators, a tournament held every five years, an
  underground market in stolen manuals. Reputation matters most here.
- **Yellow Springs Underworld** — accessed only via a specific ritual or
  a rare item. Ghost-cultivators, judges of the dead, the chance to
  speak with someone you have lost. A whole realm of cultivation
  available only to ghosts.
- **Hundred-Thousand-Mountains** — a beast-tide region full of spirit
  beasts at every realm tier. Ancient ruins of a fallen civilization.
  A mountain that shifts location each visit (procedurally generated
  variant — engine work required).
- **Sky-Spire** — capstone vertical dungeon. One floor per realm tier.
  Boss on each floor. Final floor is the Heaven Tribulation arena.

---

## A polish micro-checklist

If you have spare context after the main work, sweep:

- [ ] Every NPC has at least 3 dialogue lines.
- [ ] Every region has at least one ambient event.
- [ ] Every sect has at least one signature technique that's actually
      learnable somewhere.
- [ ] Every enemy has at least one drop (so combat feels rewarding).
- [ ] Every realm transition has a unique-feeling reward (a unique
      technique unlocked, a new location accessible).
- [ ] No location is a dead-end with nothing in it (no NPCs, no
      enemies, no events, no items).

---

## Final reminder

Don't refactor the engine just to refactor it. Don't add abstractions that
aren't needed. The whole point is: **the game grows by accretion of JSON**.
Every session should ideally end with the game being measurably bigger or
more polished than it started.
