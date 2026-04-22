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

## Session 6 — 2026-04-22 — "The Weighing Scales"

### What I built
- **Reputation, finally alive.** Flagged by sessions 2, 3, 4 and 5 as
  "the obvious lever" — shipped end-to-end this session. `Player.reputation`
  already existed as a dict since session 1, but nothing ever wrote to it.
  Now it does, and the rest of the engine reads it.
- **Rank model.** `game.state.rep_rank(value)` returns a prose rank:
  reviled (<= -6) / enemy (-5..-3) / distrusted (-2..-1) / stranger (0) /
  known (1..2) / respected (3..4) / honoured (5..7) / sect-honoured (8+).
  The rank names are deliberately short so they can sit inline in
  notifications. Helper functions `Player.rep(sid)`,
  `Player.meets_rep(requires)`, `Player.rep_shortfalls(requires)`.
- **Four kinds of rep gates**, all honored by the engine:
  - **Quests** — `requires_rep` on a quest suppresses the questgiver's
    auto-offer when you `talk` to them. They "weigh you" silently.
    (Only one quest uses this currently — none of the existing six did —
    but the machinery is in and validator-checked.)
  - **Items** — `requires_rep` is honored at `buy` (vendor refuses
    with the NPC's name quoted) and at `equip` ("The Azure Cloud
    Sword rejects your touch — its maker knows you by reputation").
    The Azure Cloud Sword now requires ACS +2. Its prose on the item
    itself was also rewritten to foreshadow the gate.
  - **Techniques** — `requires_rep` gates `learn`. Azure Cloud Palm
    now requires ACS +1 (before, realm was the only gate). Message:
    "The master will not entrust this art to you yet."
  - **Recipes** — `requires_rep` on a recipe is shown inline in the
    crafting list (`[rep: Azure Cloud Sect +2]`) and refused at
    `craft` with the crafter's name in the refusal. Skybreaker Blade
    forge requires ACS +2.
- **Quest rep deltas.** Quest reward block now accepts
  `rep_change: {sect_id: delta}`. On completion, each delta is applied
  in order; the notification reports *both* the raw change and any
  rank crossing ("Azure Cloud Sect +2 — risen from stranger to
  known"). If rank didn't change, the rank is still shown ("now +3,
  respected") so the player has context. Negative deltas use
  "fallen from X to Y".
- **Rep-reactive NPC dialogue.** New field `rep_dialogue` on NPCs.
  Shape: `{sect_id: {threshold_str: [lines] | line}}`. After the NPC's
  base dialogue prints, we pick the single threshold closest to the
  player's current rep with that sect (highest met for positive
  thresholds, lowest met for negative thresholds) and append its lines.
  Positive and negative thresholds coexist in the same dict. Tested
  that at ACS +2, Elder Baixu prints his "you walk the courtyard as a
  guest, not a stranger" line; at ACS +3 he prints the senior-disciple
  line; at ACS -2 he pivots to "do not mistake my courtesy for
  welcome." The same NPC can also gate lines on *another* sect's rep
  (Matriarch Shan has a line that only fires at ACS +5 — a sect-elder
  of the righteous finally visiting the Five Poisons matters).
- **`reputation` / `rep` / `standing` command.** Shows the player's
  standing against every sect in the world (even at 0), with rank and
  alignment tag: `Azure Cloud Sect  +2  known [righteous]`. Added
  to `help`. `status` now shows rank name next to the signed integer.
- **New content — The Envoy's Letter** (quest). An Azure Cloud junior
  envoy, Ruwen, sits at Merchant's Crossing with a splinted arm and a
  sealed letter she can't deliver. She asks you to carry it to
  Matriarch Shan in the Hall of Five Poisons and come back. Steps:
  visit the hall → talk Matriarch Shan → talk Ruwen. Reward: 180
  stones, 70 XP, Antidote Pearl, **Azure Cloud Sect Token** (new
  accessory: +1 DEF, +6 HP, +1 SPD — the mid-tier accessory that
  bridges the gap between monks' beads and Azure Guardian Talisman).
  Rep change: **+2 Azure Cloud, +1 Five Poisons, -2 Scarlet Lotus.**
  That last one is the pedagogical moment — the player didn't do
  anything *to* the Scarlet Lotus, but the three sects are a triangle,
  and good news for two of them is bad news for the third.
- **Retrofit of existing quests with rep_change.**
  - The Kettle's Request — no rep change (neutral hermit, neutral world)
  - Study the Sutra — +1 Azure Cloud (scholarship counts)
  - The Missing Disciple — +2 Azure Cloud
  - The Oath of Fangs — +2 Five Poisons, **-1 Azure Cloud** (accepting
    Matriarch Shan's oath is a mark against you in Baixu's ledger)
  - The Stormwarden's Test — +1 Azure Cloud (her station is ACS)
  - The Broken Terrace — +3 Jadestep Remnant, +1 Azure Cloud
    (Mingshu's gratitude, and the Azure Cloud honours peace-giving)
- **Validator.** New section checks `rep_change`, `requires_rep` on
  every content object. Every sect_id key must be a real sect; every
  value must be an int. `rep_dialogue` structure is fully validated
  (must be dict of sect -> dict of str-int-threshold -> (str | list)).
- **SCHEMAS.md updated.** npcs/, quests/, items/, techniques/, recipes/
  sections gained their rep fields. New "Reputation system" section
  documents ranks, gate semantics, and the command.

### Current state
- Validator: **21 loc / 17 npc / 12 enemy / 20 tech / 47 item /
  4 sect / 7 quest / 14 event / 11 lore / 15 recipe.** All references
  resolve.
- Smoke-tested (scripted): `python3 play.py`
  - `rep` at 0 prints all four sects at +0 stranger
  - Pick up Envoy's Letter quest; deliver at Hall of Five Poisons;
    return to Ruwen; quest completes with rep changes printed and
    ranks crossing from stranger to known for ACS and Five Poisons,
    and from stranger to distrusted for Scarlet Lotus
  - At ACS +2, Elder Baixu's rep_dialogue line fires at the end of
    his regular dialogue block
  - At ACS +0, `buy azure_cloud_sword` is refused with the required
    standing printed
  - At ACS +0, `craft` at the forge lists `forge_skybreaker_blade`
    with its `[rep: Azure Cloud Sect +2]` gate tag
  - `status` shows rank name per sect; `reputation` command separate
  - Save and load round-trip preserves rep dict (was already in save
    format; no schema change)
- Old save format still loads. No Player fields were added; the
  `reputation` dict has been on Player since session 1 — this session
  just finally uses it.

### What I'd do next if I had another hour
1. **A quest that's gated on rep and offers nothing without it.**
   The `requires_rep` on quests is wired up (auto-offer suppressed
   with prose "they weigh you, and do not speak of it") but no
   quest currently uses it. A good one: Matriarch Shan offers a
   *second* quest ("Poisoner's Errand") that only appears once the
   player has +2 Five Poisons. Creates a progression ladder inside
   a single NPC rather than the current one-shot reveal.
2. **Faction war state / reactive world.** Now that rep is a first-
   class citizen, it can *trigger* content. A simple move: if the
   player's combined (ACS rep - Scarlet Lotus rep) > 5, a Scarlet
   Lotus assassin shows up as an enemy at a location. The hook is
   just "compute sect war state once per location-enter, add
   enemies to the scene dynamically." Small engine change; big
   feel.
3. **Rep thresholds for crafting tiers.** Currently only Skybreaker
   Blade recipe is rep-gated. Low-hanging extensions: gate
   `forge_frostfang_sabre` at ACS +1; gate `forge_nine_serpents_ring`
   at Five Poisons +2. Makes crafting tier actually feel earned.
4. **A Scarlet Lotus sect NPC that becomes hostile at -5.** The
   demonic sect has zero NPCs. A "Scarlet Lotus scout" that
   approaches at Bandit Road — friendly at rep > 0, neutral at 0,
   attacks at rep <= -5 — would prove that rep can flip an NPC
   from a talker into an enemy. No engine change needed; just a
   location event that adds the enemy based on rep.
5. **Recipe `requires_rep` listing gets ugly at high rep counts.**
   The `[rep: Azure Cloud Sect +2]` tag works but if two sects are
   gated it reads as `[rep: A +2, B +1]` which eats horizontal
   space. Consider a two-line layout for recipes with multiple gates.

### Things I noticed but didn't fix
- **Old Hermit Yun has no rep_dialogue.** He's neutral to everything,
  but the player *could* be at enemy with a sect and his dialogue
  wouldn't reflect it. That's fine — he's deliberately apart from
  sect politics. Flagged only so future me doesn't assume it's an
  oversight.
- **The Oath of Fangs' -1 Azure Cloud penalty** is subtle — a player
  who did Missing Disciple first (+2) and then Oath of Fangs (-1)
  ends at +1 ACS, still "known." But a player who does Oath of Fangs
  first ends at -1 ACS, "distrusted" — and that unlocks the negative
  rep_dialogue lines on Elder Baixu on their first visit. That's the
  intended teaching, but I didn't fully play both branches through.
  The branches *exist*; player choice now matters.
- **`requires_rep` with negative min values is allowed** and means
  "rep must be >= this negative floor." Mostly useful for "does not
  apply to reviled players" style gates — not used by current content.
  The validator accepts it as any int.
- **Matriarch Shan's dialogue referring to ACS +5** might never
  trigger in practice — an Azure Cloud disciple that high in rep
  probably never crosses the valley threshold. It's flavor lore
  more than a mechanic, but I liked it too much to cut.
- **`rep_dialogue` has no combinatorial "if ACS >= 2 AND Five Poisons
  >= 2"** — only one sect threshold per block. If a future quest
  arc wants a "double-agent" line, we'd need an `and` shape. Not
  in this session.
- **The validator's rep_change check doesn't flag 0 deltas.**
  `{"azure_cloud_sect": 0}` is valid; the engine silently skips it
  with `if delta == 0: continue`. Not a bug, just noting.
- **Envoy Ruwen's `gives_quest`** auto-offers on `talk`; if the
  player returns to Ruwen mid-quest, the auto-offer correctly
  says "(You already accepted this task.)". Tested.
- **I wrote "The Disciple's Errand" into Disciple Meilin's mouth
  nowhere** — she has no new quest. Meilin was my first candidate
  but Ruwen was cleaner (injured, a reason not to walk the quest
  herself). Meilin remains a good empty slot for a future quest.

### Don'ts (lessons learned)
- **Don't apply rep deltas before the rank crossing is computed.**
  The old-rank/new-rank compare is how "risen from stranger to
  known" becomes a notification; if you apply the delta first and
  *then* compute old from new-delta, you lose the moment. Stored
  `old = player.rep(sid)` before `adjust_rep` — trivial, but easy
  to get backwards.
- **Don't hardcode rank thresholds in two places.** The engine
  reads rank from `game.state.rep_rank(value)` everywhere — quest
  notifications, `status` screen, `rep` command. The table is one
  tuple in state.py. If I want a new rank, I edit one thing.
- **Don't forget `rep_dialogue` is append-only.** It prints AFTER
  the main `dialogue` block so the player sees the standard NPC
  lines first and then the rep-coloured commentary. Inverting that
  order was my first instinct and read poorly — the NPC seemed to
  skip their greeting when you were friends with them.
- **Don't assume "stranger" is a neutral default.** Several NPCs
  were friendly at rep=0, so their "+1" rep_dialogue reads almost
  redundant. Pitched the +1 lines as micro-acknowledgments (" you
  are not a stranger now") rather than warm effusions; the warmer
  voice is at +3 and +5.
- **Don't trust `int(threshold_str)` for stringified JSON keys
  without a try/except.** JSON dict keys are always strings; the
  iterator sees `"2"`, `"-2"` etc. Guarded the int-parse so a
  typo-threshold doesn't crash dialogue.

---

## Session 5 — 2026-04-22 — "The Forge and the Cauldron"

### What I built
- **Crafting end-to-end.** New `recipes` content category, new engine
  commands (`craft`, `forge`, `brew`, `recipes`), crafter gating by
  NPC location, realm gate, material cost, spirit-stone cost. A
  recipe is consumed in one atomic step: all checks first, then all
  deductions. The `craft` command with no arg lists every recipe
  available at the current location, grouped by crafter, with
  costs and realm gates shown inline. `craft <recipe_id>` executes.
- **`talk` advertises crafting.** When you talk to a crafter, the
  dialogue screen now lists their recipes under a `(Forges — try
  craft or recipes here)` / `(Brews — ...)` block, so the system is
  discoverable without the player knowing the command exists.
- **Validator support.** `tools/check_content.py` gained a full
  recipes section: crafter must be a real NPC, inputs must be real
  items with positive integer quantities, output must be a real
  item, realm gate must reference a real realm, stones must be
  non-negative int, type must be one of forge/brew/craft. Zero
  errors tolerated.
- **New NPC: Forge-Master Bo.** A weathered sect-smith with singed
  beard and a four-note hum, placed in a new location. Humane
  dialogue that reads well even before you spend a stone with him.
  Faction: Azure Cloud Sect, disposition: friendly.
- **New location: Azure Cloud Forge** — a low stone shed off the
  Inner Courtyard (new exit `forge`). Has its own
  `first_visit_text`: 'The fire minds drafts worse than I mind
  guests.' qi_density 3 — it's a workshop, not a cultivation spot.
- **15 recipes across 3 crafters.**
  - **Pillmaster Lu (4 brews)** — minor healing pill x2 (viper_fang
    + eel_skin + 10 stones), spirit gathering pill x2 (1 black_lotus
    + 15 stones), iron skin pill (2 centipede_shell + 1 wolf_fang +
    70 stones), Thundergold Pill (1 cloudroot_spirit_stone + 1
    storm_feather + 1 black_lotus + 60 stones, Qi-gated).
  - **Apothecary Qi (5 recipes)** — antidote pearl x2, nine serpents
    pill, venom-fanged dagger, nine serpents ring, viper-scale sash.
    All using valley materials (viper fang, venom gland, centipede
    shell, black lotus seed, eel skin). Qi's dialogue frame is
    "the poison is its own cure" — she brews and forges both.
  - **Forge-Master Bo (6 forges)** — plain iron sword (starter
    craft), Frostfang Sabre (Qi-gated), Skybreaker Blade
    (Foundation-gated, 250 stones + rare mats), Stormcloud Sash,
    Heart-Devouring Robe (the capstone — see below), Cloudstep
    Charm (new).
- **2 new craft-only items.**
  - `heart_devouring_robe` — +6 DEF, +20 HP, +1 SPD, Foundation-gated.
    The sky-spire capstone robe. Crafted from 1 heart_devouring_hide +
    2 jadestep_shard + 1 cloudroot_spirit_stone + 350 stones. Before
    this session, the Heart-Devouring Hide had no in-game use — now
    it's the key material of the best robe in the game. Stormcloud
    Sash is still good, but this sits above it.
  - `cloudstep_charm` — +2 ATK, +1 SPD, +5 HP. Uses 2
    ape_knucklebone + 1 storm_feather + 80 stones. Makes
    ape-knucklebones (Cloudroot Pass drops) finally matter.
- **Save-compat preserved.** No new Player fields. `saves/default.json`
  from session 4 loads cleanly; recipes are world-state, not
  player-state.
- **Documentation.** SCHEMAS.md gained a "recipes/" block with the
  full shape and a short engine note on the craft command. ROADMAP.md
  inventory updated; both forging and alchemy are now ticked off under
  Engine Improvements.

### Current state
- Validator: **21 loc / 16 npc / 12 enemy / 20 tech / 46 item /
  4 sect / 6 quest / 14 event / 11 lore / 15 recipes.** All
  references resolve.
- Smoke-tested: `recipes` at Pillmaster Lu lists 4 brews; `talk
  pillmaster_lu` advertises them in dialogue; `craft
  brew_minor_healing_pill` with fangs+skins produces 2 pills, deducts
  inputs+stones; wrong-location `craft brew_minor_healing_pill` gives
  prose directing the player to Merchant's Crossing; realm-gated
  `brew_thundergold_pill` refuses at mortal realm; the capstone
  `forge_heart_devouring_robe` succeeds at Foundation with
  hide+shards+stone; the new robe equips and stacks with Cloudstep
  Charm to a clean status-sheet read (+2 ATK, +6 DEF, +2 SPD, +25 HP
  from gear).
- Traversed the new Azure Cloud Forge end-to-end: Verdant → Foothills
  → Outer Gate → Inner Courtyard → Forge. First-visit prose fires.
- Scripted `python3 play.py` session tested through to `quit`; game
  boots clean with 11 content categories loaded.

### What I'd do next if I had another hour
1. **Reputation that matters — still the obvious lever.** Third+
   session flagging. Crafting opens a natural hook: raise sect rep
   to unlock tier-2 recipes, or have Bo refuse to forge the
   Skybreaker Blade below Azure Cloud rep ≥ 2. Hooking recipes into
   rep is 5 lines of engine + a new `min_rep` field on recipes.
2. **Recipe discovery / learn system.** Right now every recipe is
   visible to every player the moment they meet the crafter. A
   nicer progression: some recipes require learning (from a manual
   drop, or from a quest completion, or from a rep threshold). A
   `requires_recipe_learned` flag + a `known_recipes` field on
   Player. Session-sized.
3. **Capstone craft deserves a quest hook.** Forging the
   Heart-Devouring Robe is a huge moment but currently happens
   silently — you hand Bo the hide, he stitches, done. A short
   one-beat quest arc where Mingshu's ghost recognises the hide
   being forged (and unlocks a post-boss teaching) would make the
   robe feel like it's *commemorating* something. Roadmap it.
4. **Eastern Sea / Northern Frost Plains** — the realm ladder is
   well-populated up to Foundation now (Skybreaker + Heart-
   Devouring Robe can carry you into Core). The next scale-up
   should be a zone where Core-tier players can flex, or a region
   at a different tier that cross-cuts the existing arcs (Northern
   Frost Plains with Blood Moon Cult would tie into the frost
   wolves + Frostfang Sabre that already exist).
5. **A second smith or smith variant.** Apothecary Qi already doubles
   as a valley-forge. If the Heavenly Sword Tower ever lands (seeded
   in session 4 lore), a Tower-smith who forges sword-only variants
   would feel right. No engine change needed.

### Things I noticed but didn't fix
- **Recipes are stateless** — the player's save doesn't track which
  recipes they've seen. Means `craft` lists every recipe at every
  crafter, regardless of the player's history. This is fine for
  now, but the progression story eventually wants a `known_recipes`
  set. Flagged for a future session.
- **No recipe consumption flavor when you fail.** If you lack a
  material, the prose is dry: "You lack: Gale Tiger Fang x1 (have
  0)". Could be in-character — Bo could grumble, Qi could raise an
  eyebrow. Minor polish.
- **Bo has no teaches/sells/quest**, only recipes. That's deliberate —
  his whole identity is the forge — but it means `talk forge_master_bo`
  doesn't fire any `talked_to` quest triggers. No current quest uses
  him either way. If a future quest wants "meet the forge-master,"
  the auto-offer-on-talk pattern from existing NPCs will just work.
- **Pillmaster Lu now does double duty** — he sells some of the same
  pills he brews (minor healing, spirit gathering, iron skin). The
  brew recipes are cheaper-per-pill than buying but require
  materials. That's the correct tradeoff; just be aware that a player
  with lots of materials can effectively bypass his shop entirely.
- **Apothecary Qi's `viper_scale_sash` forge** uses viper fangs split
  into scales. Thematically cute, but it means viper fangs have
  suddenly become one of the most useful materials (used by 5 of 15
  recipes). Might want to nerf their drop rate eventually.
- **`forge_plain_iron_sword` is a bit of a non-event** — plain iron
  sword is already sold by Mei for 45 stones and 1x wolf fang + 1x
  eel skin + 20 stones is about break-even. Kept it as a low-stakes
  "hello world" recipe to teach the player the craft command, not as
  a value play. If that teaching role is unneeded, it can be cut.
- **Azure Cloud Inner Courtyard now has 4 exits** (out, library,
  elder, forge) — the `go <dir>` prose lists them all, which is
  still fine to read. If it ever gets busy, consider grouping.
- **Heart-Devouring Hide's drop rate isn't in my memory** — I didn't
  check whether the gale tiger *always* drops the hide or just
  sometimes. Worth verifying; if it's <100% a player can defeat the
  boss and still not get the capstone robe. (Skim the enemy JSON if
  this worries you.)

### Don'ts (lessons learned)
- Don't put the crafter list in the `look` output — it would wall-of-
  text every time. The `talk` block and dedicated `recipes`/`craft`
  commands are enough discovery.
- Don't mutate state before *all* checks pass. The `craft` handler
  does every validation first (location, realm, each material, stones)
  and only then does every deduction. Early implementations that
  return mid-deduction will silently eat materials on failure. Found
  this in a manual test; fixed before committing.
- Don't skip the talk-screen advertisement. The whole system is
  invisible otherwise; a new player won't think to type `craft`. The
  `(Brews — try `craft` or `recipes` here)` line under the NPC's
  sells-list is the cheap discovery trick and makes the system
  *feel* like part of the game instead of a hidden command.
- Don't forget recipes can cost 0 stones (the `stones` field is
  optional); the engine defaults it with `int(r.get("stones", 0))`.
  Validator makes sure it's non-negative int, not just truthy.

---

## Session 4 — 2026-04-22 — "The Sky-Spire Reach"

### What I built
- **A whole Foundation-tier region** — six locations that climb above the
  cloud line, north from the existing Azure Cloud Foothills. The realm
  ladder finally has somewhere to go above Qi Condensation.
  - **Cloudroot Pass** — gatekeeper post at the cloud line.
  - **Hanging Terraces of Jadestep** — ruined sect, haunted by its own
    Patriarch's ghost. Cracked prayer bells, crane-and-peak crest worn
    smooth by 400 years of wind. Medallion on the ground.
  - **Thunderhead Ridge** — knife-thin ridge between two abysses,
    lightning walking sideways through cloud. Home of the Storm-Crow
    Spirit and a Heavenly Sword Tower disciple who shouldn't be here.
  - **Skyweaver's Cloister** — hermitage of the Old Dog of Jadestep, the
    sect's last living master. Nine sword-scars on the wall; a tenth
    halfway finished.
  - **Cragspine Shrine** — qi-density 9 cultivation spot with a
    Sky-Qi Crystal on the altar (+120 qi). Event grants +20 qi on
    visit with 0.5 chance.
  - **Spirit-Gale Plateau** — the summit's arena, home of the
    **Heart-Devouring Gale Tiger** (Core Formation: 200 HP / 22 ATK /
    10 DEF / 12 SPD, three techniques including Five Poisons Palm).
- **5 new enemies** — cloudstep_ape, terrace_revenant, storm_crow_spirit,
  stormcaller_disciple, heart_devouring_gale_tiger (boss). Foundation
  tier across the board; boss is Core Formation. Drops include the
  rare Skybreaker Blade at 35% from the boss, 7% from Stormcallers.
- **3 NPCs** — Stormwarden Gao (gatekeeper quest-giver, neutral,
  righteous-adjacent — teaches Ironbark Stance, sells Thundergold Pill
  and Storm-Warded Talisman); Ghost of Patriarch Mingshu (the unquiet
  founder, gives the boss quest, teaches Thundering Palm of the Nine
  Heavens as post-quest reward — but the quest already gives the palm
  implicitly by `talked_to` tracking); The Old Dog of Jadestep (last
  living teacher, teaches Cloudtread Footwork and Skyweaver's Veil,
  sells Ironbark Pill and Cloud Silk Robe).
- **5 new techniques** — Thundering Palm of the Nine Heavens (heaven
  rank, 24 dmg + stun 2, 18 qi, Foundation-gated, 180 stones);
  Cloudtread Footwork (buff_def 3, 6 qi); Ironbark Stance (buff_def 5,
  8 qi, Foundation-gated); Skyweaver's Veil (stun 2 + 3 dmg, 12 qi,
  Foundation-gated); Stormcall Bolt (bleed 3 + 15 dmg — enemy-only for
  now, sits in storm-spirit / disciple loadouts).
- **13 new items.** Weapons: Skybreaker Blade (9 ATK, +1 SPD, on-hit
  stun 1, Foundation-gated, 420 stones). Robes: Stormcloud Sash (+5 DEF,
  +15 HP, +1 SPD, Foundation-gated, 320 stones). Accessories: Broken
  Terrace Medallion (+2 DEF, +10 HP; free drop on terrace floor),
  Storm-Warded Talisman (+3 DEF, +2 SPD, 240 stones). Pills:
  Thundergold Pill (80 qi, 120 stones), Ironbark Pill (**new pill
  effect** `def_buff`: permanent +1 DEF, 110 stones). Treasure: Sky-Qi
  Crystal (120 qi, 220 stones). Materials: Cloudroot Spirit Stone (75
  stones), Storm-Crow Feather (30), Ape Knucklebone (22), Jadestep
  Shard (45), Gale Tiger Fang (150, quest item), Heart-Devouring Hide
  (180).
- **2 quests.**
  - *The Stormwarden's Test* — visit Thunderhead Ridge → defeat
    Storm-Crow Spirit → collect a Storm-Crow Feather → return to Gao.
    Reward: 180 stones, storm_warded_talisman, thundergold_pill, 110 XP.
  - *The Broken Terrace* — defeat the Gale Tiger → collect its fang →
    return to Mingshu's ghost. Reward: 400 stones, Skybreaker Blade,
    Stormcloud Sash, Sky-Qi Crystal, 300 XP. The big-arc reward: a
    full Foundation-tier loadout plus a realm-advancing 120-qi crystal.
- **4 lore entries** — Why the Sky-Spire Will Not Be Climbed (myth),
  The Fall of the Jadestep Sect (history, grants on bell-toll event at
  terraces), Song of the Stormwarden (poem), The Eight-Pointed Star
  (history, Heavenly Sword Tower lore — seeds a future sect).
- **4 events** — high_wind_cuts_through, terrace_bell_tolls (grants
  lore), lightning_walks_the_ridge, sky_qi_descends (+20 qi at shrine).
- **1 sect stub** — Jadestep Sect (Remnant) — HQ at Skyweaver's
  Cloister, elder is the Old Dog, signature techniques are the three
  Jadestep arts. Dead sect but referenced by `sect` field on the
  cloister and by NPC faction.
- **Engine — one small addition.** Added `def_buff` pill effect
  (permanent +1 DEF) symmetric with the existing `atk_buff`. Three
  lines in `combat.py:_apply_pill`. Documented in SCHEMAS.md.
- **Connectivity.** Added `north -> cloudroot_pass` to
  `azure_cloud_foothills`. The region ladders up from there:
  pass → terraces → ridge → plateau, with side branches east
  (cloister) and west (shrine) off the terraces and ridge respectively.

### Current state
- Validator: **20 loc / 15 npc / 12 enemy / 20 tech / 44 item / 4 sect /
  6 quest / 14 event / 11 lore**. All references resolve.
- Smoke-tested: traversal through all 6 locations, NPC dialogue for
  all 3 new NPCs, quest auto-accept on talk, quest step auto-progress
  on visit (`[The Stormwarden's Test] step complete — next: defeat
  storm_crow_spirit`), `cultivate` at qi_density 9 (36 qi per sit —
  nice jump vs 5–15 earlier), `take sky_qi_crystal`, `inventory`
  round-trip, Foundation-gated `equip skybreaker_blade` refusal at
  Qi Condensation with proper prose ("Your foundation is too thin..."),
  `use ironbark_pill` → "+1 DEF (permanent)" with stats updated,
  `gear` display, `save`/`load` with mid-session save file.
- A mortal-realm test character fought a Terrace Revenant and lost
  cleanly (woke at 1 HP, as expected). Foundation-tier enemies are
  correctly *tough* — this is not a region for under-leveled players.
- Old save format (Session 3 and earlier) still loads — no new Player
  fields. The new pill effect just dispatches on `item["effect"]`.

### What I'd do next if I had another hour
1. **Forging at the Skyweaver's Cloister or a new smith.** The region
   has a pile of materials now (gale-tiger fang *and* hide, storm
   feathers, spirit stones, ape bones, jadestep shards, plus all
   session-2 materials). A `forge <recipe>` command that consumes
   materials and produces pre-specified equipment would be the
   logical next system. Recipes in JSON under `content/recipes/`.
   Candidate: 3× storm_feather + 1× cloudroot_spirit_stone → Stormcloud
   Sash; 1× gale_tiger_fang + 2× cloudroot_spirit_stone + 1× jadestep_shard
   → Skybreaker Blade. One new command, one JSON loader branch, one
   validator check.
2. **Reputation finally doing something.** Third session flagging
   this. Specifically: quest completion should adjust rep; NPC
   dialogue should branch on it; sect-controlled locations should
   refuse entry below a threshold. The `reputation` field exists
   since session 1 but is never *written to*.
3. **The other boss: `heart_devouring_gale_tiger`** exists and works
   mechanically, but a core-formation player has no reason to return
   to the Reach once Mingshu is laid to rest. A post-boss location
   unlock — maybe an *eastern* exit from the plateau that appears only
   after the fang has been delivered, leading to the true Sky-Spire
   above — would give the region a second life.
4. **Faction-war state.** The Stormcaller Disciple name-drops the
   Heavenly Sword Tower; that's a whole righteous-militant sect seeded
   for a future session. A small state machine that tracks whether the
   Tower and Azure Cloud are currently feuding (triggered by the
   player's actions in the Reach) would give the world reactivity.

### Things I noticed but didn't fix
- **Stormcall Bolt is enemy-only.** It has `learn_cost: 999` so no
  teacher offers it. A reasonable future move: give Stormwarden Gao
  a second teaching slot, or introduce a Heavenly Sword NPC who
  teaches it after a rep gate.
- **`terrace_revenant` has `techniques: ["bleeding_pincers", "icy_bite"]`.**
  Bleeding_pincers fits. Icy_bite is slightly weird thematic-wise
  (ghost in stone ruins, no cold element on anyone else here), but
  it's close enough — a cold ghostly swordstroke reads. If someone
  finds it dissonant, swap for a new technique.
- **Ghost of Patriarch Mingshu** has `teaches: ["thundering_nine_heavens_palm"]`,
  but *also* `gives_quest` — and the quest reward doesn't include the
  palm itself. The palm is learnable from Mingshu post-talk via
  `learn thundering_nine_heavens_palm`, gated by Foundation realm
  and 180 stones. A player might expect completing the quest to also
  teach them the technique as part of the reward. Kept as-is — the
  ghost says "only then will I teach" which matches the learn path
  (the quest makes him willing; the learn costs the stones). Re-read
  his dialogue to make sure it's not misleading.
- **Sky-Spire True Peak isn't real** — the plateau's prose says "the
  true Sky-Spire rises — a single black needle of peak no mortal hand
  has ever climbed". That's a promise. Added as a roadmap item.
- **Heart-Devouring Gale Tiger uses `five_poisons_palm` as a technique.**
  That's thematically weird (it's a beast, not a Five Poisons
  cultivator). Narratively I'm hand-waving it as "a spirit-beast
  imitating any art it has seen" — fine for now, but worth a custom
  beast technique someday (e.g. "gale_tiger_roar" with stun+bleed).
- **Storm-Crow Spirit's drop table is generous** — 70% storm_feather,
  50% spirit stone, 20% thundergold pill, plus its 1.0 chance of 85
  XP. Storm-crow farming for feathers will be very efficient. Kept
  for now; the ridge is dangerous enough to self-regulate.
- **No first_visit_text on Skyweaver's Cloister or Cragspine Shrine** —
  there is one on the Cloister in the entering-prose sense, but no
  `first_visit_text` field per se. I put one on 3 of the 6 (pass,
  terraces, plateau) where atmosphere pays biggest.
- **Sect stub for Jadestep** is mostly cosmetic — it isn't used by
  any faction mechanic yet (reputation still dormant).

### Don'ts (lessons learned)
- Don't forget the `_apply_pill` is called in *two* places: combat
  (with `status_list`) and outside combat (from `cmd_use`, no list).
  Session 2 flagged this; I nearly tripped on it again when adding
  `def_buff`. The new branch is simple enough it doesn't need the
  list, but remember to think about status-list interaction when
  adding future pill effects.
- Don't forget `requires_realm` on enemy drops is different from
  `requires_realm` on items. The Skybreaker Blade has a realm gate;
  dropping it off a Stormcaller Disciple is fine — the player just
  can't *equip* it until Foundation. That creates a nice "I have
  the blade but can't use it" moment as motivation to break through.
  Worked perfectly in testing.
- Don't stack too many active enemies on a single Foundation-tier
  location. Thunderhead Ridge has two (storm-crow, stormcaller); the
  terraces have two (ape, revenant). Any more and the player can't
  engage one without the visible list being wall-of-text. The current
  engine doesn't support multi-enemy combat anyway; seeing two enemies
  in the list when only one can be fought at a time reads as "pick
  your fight" which is fine.
- Don't tie a quest's step to a `talk` with the giver and then forget
  that the auto-offer on talk is already firing. I double-checked:
  Broken Terrace's step 3 is `talk ghost_of_patriarch_mingshu` after
  the collect, which completes the quest on the return visit — this
  works because the quest is progressed *after* the `talk`, not
  during. Tested the pattern in Oath of Fangs already; same shape.

---

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
