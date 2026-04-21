# MEMORY — Wuxia Game Project

This file is the persistent memory across sessions. Read it first.

## Project Vision
A text-based wuxia cultivation RPG, played in the terminal via `python play.py`.
Heavy on content: many sects, locations, techniques, NPCs, quests, items, lore.
The engine is intentionally tiny so that 95% of work each session is **adding
content** (JSON files in `content/`) rather than touching code.

## How To Add Content (the easy path)
All content lives in `content/<category>/<anything>.json`. The loader globs
every JSON in every category folder at startup and merges them. To add content,
just drop a new JSON file in the right folder. No engine changes needed.

Categories (folder names under `content/`):
- `locations/`   — places the player can travel to
- `npcs/`        — characters
- `techniques/`  — martial arts / qi techniques
- `items/`       — weapons, pills, treasures, materials
- `sects/`       — cultivation sects
- `quests/`      — multi-step missions
- `events/`      — random encounters tied to locations
- `enemies/`     — combat-only NPCs (beasts, demons, rivals)
- `lore/`        — flavor text, legends, history (read in libraries / from elders)
- `realms/`      — cultivation realm progression

Schemas: see `SCHEMAS.md`.

## Architecture (1-paragraph)
`play.py` boots `game.engine.Game`, which loads all JSON via `game.loader`,
constructs an in-memory `World`, and runs an interactive REPL of commands
(`look`, `go <dir>`, `talk <npc>`, `cultivate`, `fight <enemy>`, `learn <tech>`,
`quest`, `inventory`, `status`, `save`, `load`, `help`). All gameplay systems
(combat, cultivation, quests, dialogue) read from data; they don't hardcode any
specific NPC or technique.

## Per-Session Workflow
1. Read this file + `ROADMAP.md`.
2. Run the game (`python play.py`) at least once to confirm nothing is broken.
3. Pick something from the "Next Up" list in `ROADMAP.md` (or invent something).
4. Either add content (JSON), polish/refine, or fix a bug.
5. Update `ROADMAP.md` with what was done and what's next.
6. Commit with a clear message and push to `claude/lucid-heisenberg-Bs2QZ`.

## Content Inventory
See `ROADMAP.md` for the running list of what exists and what to add next.
