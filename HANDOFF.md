# HANDOFF — Rolling note from the previous session to the next

> **This file is the conversation between sessions.** Every session reads it
> first, and rewrites it last. Treat it as the previous-you leaving notes for
> the next-you: what was just done, what surprised you, what you'd do next if
> you had another hour, what you wish someone would clean up.
>
> It is intentionally short and opinionated. If it's getting long, prune the
> stale parts — `ROADMAP.md` is for the long lists, this is for *what's hot
> right now*.

---

## Last session — 2026-04-21 — "Initial scaffold"

### What I built
- The whole engine and starter content, from an empty repo. See the initial
  commit message for the full inventory.
- `MEMORY.md` (project memory), `SCHEMAS.md` (JSON shapes), `ROADMAP.md`
  (long backlog), `tools/check_content.py` (validator), and this file.

### Current state
- Game runs cleanly: `python3 play.py`. Smoke-tested navigation, combat,
  cultivation, quests, save/load.
- Validator passes: `python3 tools/check_content.py`.
- Branch: `claude/lucid-heisenberg-Bs2QZ`. Pushed.

### What I'd do next if I had another hour
1. **Polish the opening 30 seconds** — the very first `look` at Verdant
   Bamboo Sea is the player's first impression. Could use a cinematic
   intro screen (ASCII title art? a brief story crawl?) and a one-line
   tutorial nudge ("try `talk wandering_monk_huilin` or `cultivate`").
2. **One whole new region** — pick the *shape* before the names. The
   Northern Frost Plains feels like the obvious next door (cold, hostile,
   first taste of a hostile sect). I'd prefer a region with an actual
   *arc* over a region that's just rooms.
3. **A tiny ASCII map** rendered by the `map` command, not just a list
   of exits — would make navigation feel less like a database.
4. **Visible HP/qi bar in the prompt** — currently you only see HP in
   combat and via `status`. A persistent `[HP 30/30  Qi 5/50]> ` prompt
   would make the cultivation loop tangible.

### Things I noticed but didn't fix
- After defeating an enemy at a location, it's still listed there next
  visit. I left this as "respawn" but it's a design call — encounters
  feel weightless. Consider a cooldown, or marking some enemies
  one-shot.
- The `cultivate` command has no diminishing returns. You can spam it.
  Maybe each cultivation should consume a "stamina" or have a
  cooldown-by-actions.
- Combat is a little dry — no crits, no status effects beyond stun (and
  even that just skips one turn). `effect: poison/bleed` exist in the
  schema but aren't actually applied by combat.py — see
  `combat.py:_apply_pill` for where pills happen, but tech effects
  besides "heal" and "stun" are silently ignored.
- The first-visit_text mechanic is great but only one location uses it.
- Reputation is tracked but never used.

### Don'ts (lessons learned)
- Don't refactor for hypothetical future content. A bug-fix doesn't
  need surrounding cleanup.
- Don't add backwards-compat shims; this game has one branch and one
  user — change things directly.
- Don't write features the player won't notice this session.

---

## Standing instructions for every session

1. **Read first**: this file → `MEMORY.md` → `ROADMAP.md`. Glance at
   recent commits with `git log --oneline -10`.
2. **Verify the game still works**: `python3 tools/check_content.py`
   and a scripted smoke-test of `python3 play.py`.
3. **Pick something** — see "How to choose what to do" below. You have
   full latitude.
4. **Do it well, ship it**: validate, smoke-test, commit, push to
   `claude/lucid-heisenberg-Bs2QZ`.
5. **Update `ROADMAP.md`**: tick boxes, add new ideas, append a dated
   entry to the "Done Log".
6. **Rewrite this `HANDOFF.md`** with notes for the next session:
   - what you actually built (briefly)
   - the current state (anything broken? anything mid-flight?)
   - what you'd do next if you had another hour
   - things you noticed but didn't fix
7. Commit the docs (can be the same commit as the work or a separate
   one — your call).

---

## How to choose what to do (think broadly)

You don't have to add new content. The goal is *to make the game better*.
That can mean any of:

- **New content** — regions, sects, NPCs, quests, techniques, items,
  enemies, lore. The path of least resistance; mostly JSON.
- **Polish & feel** — better descriptions, atmospheric prose,
  more dialogue, sound-cue text ("a bronze bell tolls"), the prose
  equivalent of *juice*.
- **Visual/UI improvements** — ASCII title screen, ASCII map,
  health bars in the prompt, colored output (ANSI codes),
  cleaner formatting, a `--no-color` flag.
- **New mechanics** — equipment slots, alchemy/forging, companions,
  multi-enemy combat, day/night, weather, status effects that actually
  do something, crits, dodges.
- **Systemic depth** — make reputation matter, give NPCs schedules,
  make sects react to player choices, faction war state.
- **Bug fixes & refactors** — but only ones the player will feel.
- **Tooling** — a content generator, a "where am I stuck" auto-hint,
  a graph visualization of the world map.
- **Story arcs** — multi-quest narratives that give the game a spine.
- **Endgame** — the realm ladder is empty above Qi Condensation in
  practice; what does Nascent Soul *feel* like?

Mix it up across sessions. A run of pure-content sessions makes a wide
but shallow game; a run of pure-engine sessions makes a deep but empty
one. Look at what the game needs *most* right now, not what's easiest.

---

## How big is "one session of work"?

Aim for one **substantial** unit. Examples that would each be a good session:

- A new region with ~6 locations and the NPCs/enemies/events to fill it
- A new sect with HQ + 3 NPCs + 4 techniques + 1 quest
- An ASCII title screen + a redesigned opening + tutorial nudges
- An equipment system: schema + loader + engine + a few starter weapons
- Wiring up status effects (poison, bleed, buff) end-to-end in combat
- An ASCII map renderer for the `map` command
- A second whole quest line for an existing sect

Resist the urge to do five half-things. Better: one whole thing,
shipped, validated, committed.
