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

> **CRITICAL — branch discipline.** The scheduled harness creates a fresh
> random branch (e.g. `claude/jolly-euler-XXX`) for each run, *forked from*
> `claude/lucid-heisenberg-Bs2QZ` (the repo's default). Your random branch
> is disposable. The **canonical** branch — the one all sessions accumulate
> into — is `claude/lucid-heisenberg-Bs2QZ`. If you don't push your work
> back to it, the next session won't see what you did. Steps 0 and 8 below
> are what makes the routine cumulative — skip them and every session
> silently resets the project.

0. **Catch up on prior work.** Before reading anything else, ensure you
   have the latest canonical state:
   ```
   git fetch origin claude/lucid-heisenberg-Bs2QZ
   git merge --ff-only origin/claude/lucid-heisenberg-Bs2QZ || \
       git merge --no-edit origin/claude/lucid-heisenberg-Bs2QZ
   ```
   The fast-forward succeeds when the harness forked from the tip of
   canonical (the normal case). The non-ff fallback covers drift.

1. **Read first**: this whole file (especially the most recent 2–3 session
   entries) → `MEMORY.md` → `ROADMAP.md`. Glance at `git log --oneline -10`.
2. **Verify the game still works**: `python3 tools/check_content.py` and
   a scripted smoke-test of `python3 play.py`.
3. **Pick something** — see "How to choose what to do" below. You have full
   latitude.
4. **Do it well, ship it**: validate, smoke-test, commit.
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
8. **Push to BOTH places.** This is how the routine accumulates:
   ```
   git push -u origin HEAD                                   # the harness branch
   git push origin HEAD:claude/lucid-heisenberg-Bs2QZ        # canonical — MANDATORY
   ```
   If the second push is rejected (non-fast-forward), someone else's run
   landed first: `git fetch origin claude/lucid-heisenberg-Bs2QZ && git
   merge --no-edit origin/claude/lucid-heisenberg-Bs2QZ` and retry. If it's
   rejected because of branch protection, open a PR via the GitHub MCP
   tools and merge it (`create_pull_request` + `merge_pull_request` or
   `enable_pr_auto_merge`). The routine is broken until canonical moves.

### How to know the routine is healthy

Run `git log --oneline origin/claude/lucid-heisenberg-Bs2QZ -5` at session
start. You should see a chain of recent session commits — session N-1,
N-2, etc. If it shows only the initial scaffold, the previous run failed
step 8 and this session is starting blind; flag it loudly in your session
log and do what you can.

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

## Session 3 — 2026-04-22 — "The First Blade"

### What I built
- **Equipment system, end-to-end.** Three slots — `weapon`, `robe`,
  `accessory`. Gear applies stat bonuses (`atk_bonus`, `def_bonus`,
  `spd_bonus`, `hp_bonus`) wherever effective stats are read: the
  prompt's HP bar, the `status` screen, every combat roll (attack,
  technique, dodge, crit, flee). Base and gear are displayed separately
  so the player can see where each point comes from.
- **Weapon on-hit effects.** A weapon can carry `on_hit_effect` = one of
  `poison` / `bleed` / `stun` with `on_hit_power`. It fires when a plain
  attack lands (not on techniques — those carry their own effect). The
  smoke test with Venom-Fanged Dagger killed a Bamboo Viper purely
  through the lingering poison its own blade applied — clean.
- **Realm gates on gear.** Equipment can require a realm (e.g. Azure
  Cloud Sword — `foundation_establishment`, Cloud Silk Robe —
  `qi_condensation`). Equipping refused with a matching line of prose.
- **Engine glue.** `equip <item>`, `unequip <slot>`, `gear`/`equipment`
  commands. Synonyms: `wield`, `wear`, `remove`. Slot-swap returns the
  old item to inventory automatically. HP is clamped down if a
  stat-granting robe is unequipped at full HP; an injured player is
  never magically healed by swapping gear. Save/load preserves
  `equipped`; pre-session-3 saves get back-filled with empty slots.
- **Content — 13 new equipment items.**
  - Weapons: Plain Iron Sword (+3 ATK), Bamboo Longstaff (+2 ATK, +1
    SPD), Venom-Fanged Dagger (+4 ATK, on-hit poison 2), Jade Serpent
    Fang Blade (+5 ATK, on-hit poison 1), Azure Cloud Sword (+6 ATK,
    +1 DEF, +1 SPD, Foundation-gated), Frostfang Sabre (+7 ATK,
    on-hit bleed 2, Qi-gated).
  - Robes: Hempspun Traveler's Robe (+3 DEF, +8 HP), Cloud Silk Robe
    (+4 DEF, +1 SPD, +12 HP, Qi-gated), Viper-Scale Sash (+3 DEF, +6
    HP).
  - Accessories: Jade Qi Pendant (+1 DEF, +5 HP, free starter on the
    ground at the hermit's hut), Azure Guardian Talisman (+2 DEF, +1
    SPD), Nine Serpents Ring (+2 ATK, on-hit poison 1), Monk's Wooden
    Beads (+1 DEF, +4 HP).
  - Upgraded existing: Rusty Dao Saber (+2 ATK, slot weapon),
    Traveler's Robe (+2 DEF, +4 HP, slot robe).
- **Placement.** Merchant Mei (plain sword, hempspun robe, jade
  pendant, plus existing traveler robe). Huilin (bamboo longstaff,
  monk's beads). Elder Baixu (azure cloud sword, cloud silk robe,
  azure talisman — gated by realm). Apothecary Qi (venom-fanged
  dagger, viper-scale sash). Oath of Fangs quest reward now includes
  the Nine Serpents Ring — fits the arc. Rare drops: frost wolf has
  an 8% chance to drop the Frostfang Sabre; Grey Disciple has 8%
  for the Jade Serpent Fang Blade.
- **Validator.** New checks for item `slot`, bonus types, on-hit
  effect name, and realm reference.
- **SCHEMAS.md** updated with equipment fields + an "Equipment slots"
  engine note.

### Current state
- Validator: 14 loc / 12 npc / 7 enemy / 15 tech / **31 item** / 3 sect /
  4 quest / 10 event / 7 lore.
- Smoke-tested: look → status → gear → take ground pendant → equip →
  status (shows +1 DEF / +5 HP breakdown) → unequip → status; buy flow
  at Mei; realm-gate refusal for Azure Cloud Sword at mortal realm;
  full combat with Venom-Fanged Dagger including on-hit poison tick;
  save/load equipment round-trip; old-save backfill; HP-clamp on
  gear-downsize of injured player.
- Old save format still loads (equipped backfill).

### What I'd do next if I had another hour
1. **Forging / simple crafting.** Materials (viper fang, venom gland,
   frost pelt, centipede shell, black lotus seed, wolf fang) now have
   *spec* — equipment exists that could be forged from them. Add a
   `forge <recipe>` or `brew <recipe>` at Pillmaster Lu or a new
   Azure Cloud smith NPC. Recipes in JSON under `content/recipes/`
   (new category → extend loader, new validator check). Session-sized.
2. **Foundation-tier content.** The Azure Cloud Sword and Frostfang
   Sabre are already realm-gated, but there's no Foundation-tier region
   to *use* them in. Sky-Spire Foothills is listed in the roadmap as
   a zone for this. One new region with 3–4 locations and a Foundation-
   or Core-tier boss would light up the realm ladder.
3. **Reputation that matters** (still from session-2 todo). Quests
   should adjust rep; Five Poisons disciples stop respawning once rep
   ≥ 2; NPC greeting lines branch. Low effort, big feel.
4. **Equipment flavor on the `look` of shop NPCs.** Mei's stall
   already shows prices; consider previewing bonuses inline, e.g.
   `Plain Iron Sword — 45 stones  (+3 ATK)`. One-liner in engine.

### Things I noticed but didn't fix
- **Equipment swap mid-combat isn't supported.** Combat snapshots
  `p_gear_*` once at the start of the fight. Gear swap from the item
  menu would need a re-snapshot. Not worth doing unless we add an
  in-combat `swap` action; for now, pills remain the only in-fight
  item interaction.
- **Inventory doesn't mark equipped items** — but since equip *moves*
  the item out of inventory and into `equipped`, the UX is consistent:
  you see it under `gear` only. Some players might want to see
  equipped gear in inventory with a (E) marker. Debatable.
- **`atk_buff` pill now stacks with gear ATK cleanly**, since the pill
  modifies base `player.atk` and gear is read separately. Verified in
  the stat line prose.
- **On-hit effect only fires on normal attacks that land.** A
  technique-and-weapon combo doesn't double-apply — techniques carry
  their own effect and skip the weapon rider, matching the intent.
- **Bandit scout drops `rusty_dao` at 30%.** That's a free +2 ATK
  equip after one fight — early game may be slightly easier now.
  Kept as-is; it's welcome power for a new character.
- **No way to drop items** yet (still on the roadmap). Weapons you
  swap out accumulate forever.

### Don'ts (lessons learned)
- Don't read `player.atk / defense / spd / max_hp` directly in combat
  code — always go through the effective accessors (`eff_atk(world)`
  etc.) or the snapshot variables, or gear bonuses silently go
  missing. Three places in combat.py were the whole-file pattern to
  update.
- Don't store equipped items as `None` in a `Dict[str, Optional[str]]`
  — `asdict` round-trips dicts but `None` vs `""` trips up field
  defaults and from_json. Used `""` as the empty sentinel; simpler.
- Don't forget `cmd_status` — the status screen is how the player
  first *sees* that equipment is a thing. A raw `ATK/DEF/SPD: 8/4/6`
  line would hide where the points came from; the base+gear split is
  why equipment *reads* as a system instead of a stat bump.

---

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
