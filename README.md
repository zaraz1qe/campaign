# Jade Wind Chronicles

A text-based wuxia cultivation RPG, played in the terminal. Heavy on content,
light on engine — almost everything is JSON in `content/`.

```sh
python3 play.py
```

Type `help` once you're inside.

## Layout
- `play.py` — entry point
- `game/` — engine (loader, state, combat, cultivation, quests, REPL)
- `content/` — all data (locations, npcs, enemies, techniques, items, sects,
  quests, events, realms, lore). One JSON file per logical bundle; the loader
  globs everything.
- `tools/check_content.py` — validates IDs and cross-references
- `saves/` — saves go here

## For maintainers (humans or AI)
- `MEMORY.md` — short project memory; read first.
- `SCHEMAS.md` — JSON schema for every content type.
- `ROADMAP.md` — what's done, what's next.

## Adding content (90-second tour)
1. `python3 tools/check_content.py` (sanity check current state).
2. Drop a new JSON file into the appropriate `content/<category>/` folder.
3. `python3 tools/check_content.py` again.
4. `python3 play.py` and look around.
