# HANDOFF — Session log (append-only, newest at the top)

> **This file is the conversation between sessions.** Every session reads it
> first, and **prepends** a new entry at the top. Treat each entry as the
> previous-you leaving notes for the next-you: what was just done, what
> surprised you, what you'd do next if you had another hour, what you wish
> someone would clean up.
>
> Don't delete or rewrite old entries — they're context. Just add a new one
> at the top of the "Session log" section. ROADMAP.md is the long-term
> backlog; this file is the running commentary that lets you see *how* the
> game grew, decision by decision.

---

## Standing instructions for every session

1. **Read first**: this whole file (especially the most recent 2–3 session
   entries) → `MEMORY.md` → `ROADMAP.md`. Glance at `git log --oneline -10`.
2. **Verify the game still works**: `python3 tools/check_content.py` and
   a scripted smoke-test of `python3 play.py`.
3. **Pick something** — see "How to choose what to do" below. You have full
   latitude.
4. **Do it well, ship it**: validate, smoke-test, commit, push to
   `claude/lucid-heisenberg-Bs2QZ`.
5. **Update `ROADMAP.md`**: tick boxes, add new ideas, append a dated entry
   to the "Done Log".
6. **Prepend a new entry to this file's "Session log" section** (just below
   the divider). Don't edit or delete previous entries — accumulating them
   is the point. New entry should include:
   - what you actually built (briefly)
   - the current state (anything broken? anything mid-flight?)
   - what you'd do next if you had another hour
   - things you noticed but didn't fix
   - any "don'ts" (lessons learned) worth flagging
7. Commit the docs (same commit as the work, or a separate one — your call).

---

## How to choose what to do (think broadly)

You don't have to add new content. The goal is *to make the game better*.
That can mean any of:

- **New content** — regions, sects, NPCs, quests, techniques, items,
  enemies, lore. The path of least resistance; mostly JSON.
- **Polish & feel** — better descriptions, atmospheric prose, more
  dialogue, sound-cue text ("a bronze bell tolls"), the prose equivalent
  of *juice*.
- **Visual/UI improvements** — ASCII title screen, ASCII map, health bars
  in the prompt, colored output (ANSI codes), cleaner formatting, a
  `--no-color` flag.
- **New mechanics** — equipment slots, alchemy/forging, companions,
  multi-enemy combat, day/night, weather, status effects that actually do
  something, crits, dodges.
- **Systemic depth** — make reputation matter, give NPCs schedules, make
  sects react to player choices, faction war state.
- **Bug fixes & refactors** — but only ones the player will feel.
- **Tooling** — a content generator, a "where am I stuck" auto-hint, a
  graph visualization of the world map.
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

Resist the urge to do five half-things. Better: one whole thing, shipped,
validated, committed.

---

# Session log

## Session 2 — 2026-04-22 — "Venom in the Veins"

### What I built
- **Combat depth, end-to-end.** Status effects that were silently
  ignored in the old engine now actually fire: `poison` and `bleed` tick
  each of the target's turns for 3 turns, `buff_atk`/`buff_def` give the
  attacker a 3-turn boost, `stun` skips the victim's action for N turns,
  `heal` heals the attacker. Added a new `cleanse` pill effect that
  purges poison/bleed/stun (flavored no-op outside combat).
- **Crits & dodge.** Both sides now roll for crits (5%+ scaled by SPD
  diff, capped 30%, 1.7× damage, prose flourish) and for dodges (up to
  20% based on SPD diff, cancels offensive riders like poison).
- **Prose variety.** Attack verbs rotate (strike/cut at/batter/lance
  into…), dodges have four flavor lines, crits have four. Combat reads
  less like a spreadsheet.
- **Persistent prompt.** Main REPL prompt is now
  `[HP 28/30  Qi 5/50] > `. The cultivation loop is finally visible.
- **New sect: Five Poisons Sect.** Neutral/grey faction, showcases the
  new status mechanics. Deliverables:
  - Region: **Thousand Venom Valley** (4 locations: Valley Mouth,
    Venom Gorge, Hall of Five Poisons, Poisoner's Garden).
  - 3 NPCs: Gatekeeper Wuwei, Matriarch Shan, Apothecary Qi.
  - 6 techniques: Serpent Strike (poison 3), Five Poisons Palm (poison
    6, heaven rank), Centipede Stance (buff_def 4), Web of Silk (stun),
    Bleeding Pincers and Toad's Breath (enemy-only).
  - 2 enemies: Spirit-Armored Centipede (bleeds), Grey Disciple.
  - 5 items including Antidote Pearl (cleanse) and Nine Serpents Pill.
  - 1 quest: The Oath of Fangs (collect-three scavenger arc that
    touches existing content — viper fang, venom gland, wolf fang).
  - 2 lore entries, 3 events.
  - Connected east of Bandit Road. Pillmaster Lu now sells Antidote
    Pearl so players can deal with poison before reaching the valley.
- Updated `SCHEMAS.md` to document every `effect` string and its
  semantics (this was previously only implicit in code).

### Current state
- Validator passes: 14 loc / 12 npc / 7 enemy / 15 tech / 18 item /
  3 sect / 4 quest / 10 event / 7 lore.
- Scripted smoke tests exercised: fight-with-poison, fight-with-bleed,
  centipede-stance buff, antidote-pearl cleanse (both with and without
  active poison), use-pill outside combat, prompt bar, full traversal
  Verdant → Bandit Road → Valley Mouth → Gorge → Hall → Garden.
- Old save format still loads cleanly — no new Player fields.

### What I'd do next if I had another hour
1. **Reputation that matters.** The `reputation` dict is still never
   written to nor read from. Low-hanging fruit: offering/taking certain
   quests adjusts rep; NPC greeting lines swap to hostile/friendly
   variants based on rep; Five Poisons disciples stop respawning as
   enemies in the Gorge if Five Poisons rep ≥ 2.
2. **Fix the enemy-respawn feeling.** Currently enemies persist at
   their location after being defeated. Simplest player-felt fix: add a
   `player.cleared` per-location map with a turn counter, and hide the
   enemy until `go`-actions elapse. A cooldown of ~10 player actions
   feels right. Would make exploration feel consequential.
3. **Endgame breath.** Realms above Qi Condensation are effectively
   unreachable — no content gates on them, no enemies scale up. One
   new region with Foundation-tier enemies and a Core-Formation boss
   would let the realm ladder actually matter. Sky-Spire foothills is
   the obvious candidate.
4. **Alchemy at Pillmaster Lu.** He already exists. With the new
   materials (venom_gland, centipede_shell, viper_fang, frost_pelt,
   black_lotus_seed, etc.), a one-command `brew <recipe>` against a
   small recipe list would light up the crafting branch of the roadmap
   without an engine rewrite.

### Things I noticed but didn't fix
- **"across" as a direction** — not in the DIR_SHORTCUTS set, so you
  have to type `go across` (both at the river and elsewhere). Same for
  `in`/`out`. Not a bug, just a friction point.
- **Quest completion doesn't consume items.** `collect` steps check
  `has_item` but don't remove them. The Oath of Fangs lets you keep
  all three fangs/glands after handing them in. Might be intentional
  ("show me your proofs") but worth a design call.
- **Enemy self-heal / enemy self-buff never triggers.** No enemy in the
  game uses those effects. The `_apply_tech_effect` branch is ready for
  it; just needs an enemy to hold such a technique.
- **First-visit text** is still only on 2 locations (bamboo sea, valley
  mouth, and the Hall of Five Poisons). Easy polish across the rest.
- **Fleeing balance.** Flee chance now scales with SPD diff; the base is
  0.5 + 0.05 per SPD advantage, capped 0.9. Untested against higher-tier
  enemies — keep an eye on it.
- **Combat `continue`** after a cancelled menu still re-runs the loop
  from the top *including* the DoT tick, which means poison ticks on
  both the cancelled turn and the real turn. Player-felt, but mild —
  noted it in the code comment for later.

### Don'ts (lessons learned)
- Don't carry `continue` semantics across status ticks without thinking
  about re-entry: the first refactor had dodge-with-tech-effect applying
  the effect anyway. Wrote it twice before it came out right.
- Don't assume pronoun "You" reads naturally as a noun; building a
  separate `is_player` branch beat trying to retrofit grammar.
- Don't forget: combat's `_apply_pill` is reached both from inside a
  fight and from `cmd_use` outside — any new side effect needs to be
  defined for both paths (hence the optional `status_list`).

---

## Session 1 — 2026-04-21 — "Initial scaffold"

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
  feel weightless. Consider a cooldown, or marking some enemies one-shot.
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
- Don't refactor for hypothetical future content. A bug-fix doesn't need
  surrounding cleanup.
- Don't add backwards-compat shims; this game has one branch and one
  user — change things directly.
- Don't write features the player won't notice this session.
