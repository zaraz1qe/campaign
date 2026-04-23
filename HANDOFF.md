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

## Session 12 — 2026-04-23 — "The Willow at the Gate" + Technique Deepening

### What I built
- **Two things this session**, both in service of the same complaint:
  the game was a puddle in the early and mid game. First a proper
  starter village (Willowmere — 6 locations, 8 NPCs, 5 quests).
  Then a combat-roster deepening pass: 15 new learnable techniques,
  filling an audit-exposed palette gap (zero buff_atk techniques
  existed before this session; only one bleed).
- **Willowmere**, a village hanging west of Verdant Bamboo Sea —
  the game's first real mortal-tier hub.
  - Six locations: Village Square, Willow-and-Moon Teahouse,
    Willowmere Smithy, Shen Homestead, Pale Lake Shore, Drowned
    Willow Shrine. Connected via a new `west` exit on
    verdant_bamboo_sea.
  - Eight NPCs, each with a voice: Headman Lu Pingan (a failed
    Azure disciple, wears a patched azure robe, gives the wolves
    quest, teaches farmhands_cleave), Herbalist Mingzhu (sells
    pills, gives the moonflower errand, her son sleeps under the
    counter), Little Yu (the child whose songbird escaped),
    Tea-Mother Weiyu (keeper of the ledger in two colours — red
    ink when a customer dies), Old Kuo (half-drunk, one-time
    sword-master of the Drunken Step, will not teach sober —
    hence the bottle quest), Blacksmith Ao (the sword in the
    stone is his father's; he will not finish it and will not
    put it away; gives the river-iron quest, teaches iron_ox_shrug
    + mountain_root_stance), Farmer Shen Daiyu (a widow with a
    broom whose handle has a nail crosswise), Fisher Ren (quiet
    lakeside teacher, teaches willow_root_stance).
  - Five mortal-tier quests: **Wolves at Shen's Farm** (kill the
    alpha with the pale blaze — grants +1 ACS, iron cleaver, lore);
    **Little Yu's Songbird** (Lady Moonbell was placed at Old
    Hermit's Hut — she escaped toward the kettle); **Three
    Ingots of River-Iron** (carp spirits drop them; three make a
    blade; reward: Ao's River Blade, ATK +5 with +4 HP, the best
    mortal-tier weapon in the game); **Errand of the Drowned
    Willow** (moonflower bud at the haunted shrine; reward: 2
    tonics + 1 cordial + 25 XP + lore); **A Bottle for the Corner
    Table** (buy wine from Weiyu, take to Kuo; reward: Drunken
    Step Sash — SPD +2, HP +4).
  - Four mortal-tier enemies: grey_forest_wolf (mortal, 22 HP),
    grey_pack_alpha (Qi Cond boss, 62 HP, drops the heart),
    pale_lake_carp_spirit (mortal water, drops river-iron),
    drowned_willow_revenant (spirit, 50 HP, grants
    the_drowning_of_the_willow lore on defeat).
  - 15 new items across mortal-tier gear, pills, materials, and
    quest items. Four new lore entries (village history, revenant
    backstory, tune-with-last-note-different, tea-mother's ledger).
    Eight new events for ambient flavor.
  - Smoke test `tools/smoke_willowmere.py` — 8 scenarios including
    full wolves-quest combat flow, songbird collect-return, all
    five quests end-to-end, and save-compat. All green.
- **Technique expansion** (the deepening). Audit revealed 20
  learnable techniques with **zero buff_atk**, only **one** bleed,
  and thin Mortal/Foundation rosters. Shipped 15 new in
  `content/techniques/depth.json`:
  - Mortal (4): silent_bell_strike (Huilin, 0-qi pure strike),
    settling_stone_sit (Yun, cheap heal), viper_sting (Wuwei, the
    Five Poisons mortal intro), iron_ox_shrug (Bo, the *first*
    buff_atk in the game, mortal-tier).
  - Qi Condensation (6): azure_cloud_sword_arc (Meilin, buff_atk
    sword), crane_wing_parry (Baixu, sword buff_def),
    flashing_willow_leaf (Meilin, bleed sword — "the thing Baixu
    does not like me teaching"), black_lattice_palm (Apothecary
    Qi, palm bleed — fills the righteous/neutral bleed gap),
    mountain_root_stance (Bo, heavy buff_def), crimson_hand_of_silence
    (Red Feather, stun palm at SL 2).
  - Foundation (5): nine_cloud_cranes_flight (Baixu, ACS 4 sword
    capstone at dmg 20 + buff_atk 3), five_venoms_brocade_palm
    (Shan, FPS 4 poison capstone at power 7), heart_boiling_technique
    (Red Feather, SL 3 foundation-tier life-steal), stormwarden_mantle
    (Gao, ACS 3 pure buff_atk), brass_bell_sutra (Huilin, monk
    high-tier heal).
  - Final counts: **35 learnable techniques** (was 20). Mortal 5→9,
    Qi-Condensation 9→15, Foundation 6→11. **Every effect type has
    ≥3 learnable options**. buff_atk: 0→4. bleed: 1→3. This is the
    session where the tactical palette became actually interesting.
  - Wired teaches onto: Huilin (+silent_bell_strike, brass_bell_sutra),
    Yun (+settling_stone_sit), Wuwei (+viper_sting — he had no
    teach list before), Bo (+iron_ox_shrug, mountain_root_stance —
    first teaches ever), Meilin (+azure_cloud_sword_arc,
    flashing_willow_leaf), Baixu (+crane_wing_parry,
    nine_cloud_cranes_flight), Qi (+black_lattice_palm), Shan
    (+five_venoms_brocade_palm), Red Feather (+crimson_hand_of_silence,
    heart_boiling_technique), Gao (+stormwarden_mantle).
  - Smoke test `tools/smoke_techniques.py` — 7 scenarios covering
    loads, teacher wiring (no orphans), ungated mortal learn from
    correct NPC, rep-gate refusal at -1 and success at threshold,
    realm-gate refusal at wrong realm, palette coverage assertion
    (every effect ≥3), and mortal+foundation buff_atk availability.
    All green.
- **NPC dialogue depth.** Expanded four thin NPCs: **Gatekeeper
  Chen** (a young man practising his sash-knot alone, counting the
  six weeks to his trial, senses Meilin beat him three times;
  added rep_dialogue for ACS ±2), **Librarian Zhao** (the
  committee of 1184, the locked shelves that check names, the
  library that has on three occasions found things he was going to
  turn away — plus rep_dialogue), **Raftsman Qiu** (his son, his
  lost sword, the box with nine carved fish — one per passenger
  lost; rep_dialogue for ACS and SL), **Cloth Merchant Mei**
  (added rep_dialogue across ACS / SL / FPS — three different
  kinds of quiet handling). Added rep_dialogue to **Wandering Monk
  Huilin** for all three sects — the monk finally reacts to the
  player's standing. Expanded **Forge-Master Bo** and **Gatekeeper
  Wuwei** with extra dialogue lines to match their new teach
  roles.
- **Event depth.** 9 new events in `content/events/depth.json`
  filling locations that had zero: Old Hermit's Hut, Azure Cloud
  Outer Gate, Azure Cloud Inner Courtyard, Azure Cloud Forge,
  Elder Baixu's Pavilion, Hall of Five Poisons, Skyweaver's
  Cloister, Spirit-Gale Plateau, Willowmere Smithy. **Every
  location in the game now has ≥1 event.**

### Current state
- Validator: **29 loc / 30 npc / 21 enemy / 43 tech / 70 item / 4
  sect / 14 quest / 33 event / 24 lore / 15 recipe.** From session
  11's 23/22/17/25/55/4/9/16/20/15: this session added +6 loc, +8
  npc, +4 enemy, +18 tech, +15 item, +5 quest, +17 event, +4 lore.
- All prior smoke tests (affinity, companion, companion_downed,
  lore, red_ledger) remain green. New smoke tests (willowmere,
  techniques) also green.
- `python3 play.py` boots cleanly. Fresh player sees the west
  exit from Verdant Bamboo Sea on first `look`. The teach roster
  of every major NPC is now 2+ techniques.
- Save compat preserved. Zero new Player fields this session.
- Starting mortal-tier player now has a real choice: walk north
  to the Azure Cloud, east to the river and market, or **west to
  a village with three quests and multiple teachers** (Pingan,
  Bo, Fisher Ren, Kuo, Huilin-adjacent via the bamboo). The early
  game has actual content.

### What I'd do next if I had another hour
1. **Expand the Azure Cloud Library.** Zhao now has better
   dialogue but the library still has only the Sutra of Empty
   Sleeves. A `manual` item type already exists on the sutra —
   stocking five or six more manuals (each granting lore on read,
   or teaching a technique if the player is at the right realm)
   would make the Library a real resource. Right now it's one
   quest and one scroll.
2. **An actual Huilin quest.** He has a staff, a bell he won't
   ring, a monk's history, three rep_dialogue keys, two teach
   options, one sell list — and no quest. A Shaolin-flavored
   errand (maybe "accompany him to ring the bell at the drowned
   willow shrine") would complete his NPC.
3. **Equipment variety.** There's now ample technique variety but
   weapons/robes/accessories are still fairly uniform in effect.
   Things like "on_hit_heal" or "on_crit stun" would need engine
   work, but new tiers within the existing `on_hit_effect` palette
   (poison/bleed/stun) are pure content. A mortal-tier bleed
   dagger. A Qi-Condensation stun mace. Etc.
4. **Weilan teaches more than crimson_tide_fist.** The Apothecary
   has one teach; she could have 2-3 to match her siblings in
   scope (she's the approachable Pavilion face). Perhaps
   crimson_hand_of_silence as an alternative to Red Feather.
5. **Fill out Bandit Road.** It has enemies, Rulan, and no quest
   content of its own. The bandit threat is established but there
   is no "deal with the Black Banner" errand. The Cloth Merchant
   Mei already has the hook in her dialogue. Classic escort quest.
6. **Two more early-game lore entries.** Willowmere has 4 new lore
   entries but the game's oldest lore file (`core.json`) has only
   5. The southern wilds have at most one or two legends — a
   proper per-location legend pass (as flagged in session 11) is
   still waiting.
7. **Endgame is still open.** Nascent Soul remains empty in
   practice. Do not lose sight of this; the early game is fat
   now, the late game is still bone.

### Things I noticed but didn't fix
- **The bottle-for-kuo quest keeps the rice wine.** Like other
  collect-type quests in this engine, the item is checked, not
  consumed. Player finishes with both the wine and the sash.
  Lean into it — "you drink the jar together", narratively — or
  add a per-quest consumes list (engine touch) later.
- **The River Blade is better than most Qi-Condensation weapons**
  at 5 ATK + 4 HP for 180 stones. That's Willowmere's early
  reward; it also means a smart player will skip several
  Foothills vendors. Probably fine — the River Blade is the
  capstone of a quest gated behind grinding river-iron drops, so
  it earns its power. But it does make the smithy on the Azure
  Cloud a harder sell for mid-tier players.
- **iron_ox_shrug costs 5 qi for buff_atk 2**, while the existing
  buff_def chain (willow_root_stance) costs 3 qi for buff_def 2.
  buff_atk feels pricier than buff_def. That's intentional — atk
  buffs stack with weapon damage and therefore compound harder —
  but it's a bit awkward in the lowest realm. I left it. A mortal
  player should not be spamming buff_atk every round.
- **five_venoms_brocade_palm overlaps five_poisons_palm.** The
  existing palm is dmg 20 poison 6 at Foundation + FPS 0; the new
  one is dmg 18 poison 7 at Foundation + FPS 4. The new one is
  weaker on raw damage but stronger on DOT. A player with FPS 4
  will have both and will pick the right one per fight. I think
  this is correct — the new palm is "Shan's own refinement", not
  a straight replacement — but a future balance pass might prune
  one.
- **flashing_willow_leaf is explicitly inside-sect-controversial**
  ("the thing Baixu does not like me teaching"). Right now the
  narrative doesn't consequence this. A future hook: learning it
  could cost 1 ACS rep, reflecting the controversy. Engine doesn't
  currently support "learning costs rep" — would be a small add.
- **companion techniques** (the ones on the Player.companion
  block) were not touched. Meilin's list is still
  [white_crane_sword, azure_cloud_palm, calming_breath]. She
  could have azure_cloud_sword_arc. Intentional: the runtime
  companion dict is snapshotted per-recruit, and editing it
  requires either a save migration or a soft "on reload, refresh
  from npc content" path. Flagging for later.
- **Mingshu's ghost teaches thundering_nine_heavens_palm** but
  only after The Broken Terrace closes. That quest has a
  fang-drop step. Should verify the ghost's `teaches` still fires
  after quest completion — last tested in session 4.

### Don'ts (lessons learned)
- **Don't write big content before auditing.** My first instinct
  this session was to build a whole new region. The user
  correctly pushed back — *refine existing things*. The audit
  (learnable techniques by realm and effect) surfaced a real
  palette gap I would have missed if I'd just kept adding.
  Next session, if the user says "deepen," start with a
  `by-category, by-attribute` audit before writing anything.
- **Don't orphan techniques.** The smoke test for "no orphans"
  is a cheap regression and caught zero issues this time —
  but only because I hand-checked every new id against a teach
  list during wiring. The test is now there; trust it next
  time.
- **Don't forget to add an NPC's teach block when they get a
  quest.** Gatekeeper Wuwei had dialogue and a disposition but
  no `teaches` or `sells` prior; he was narratively dead. Adding
  viper_sting (plus a new dialogue line tying the teach to the
  sting) turned him from a checkpoint gate into a person. Thin
  NPCs do not automatically become thick through being in the
  game; they need something to *give*.
- **Don't add `companion_reply` for Huilin's new rep_dialogue
  cases.** I added rep_dialogue keyed by ACS / SL / FPS, which
  is a different axis from his existing companion_reply. They
  layer fine — rep first, then companion. Don't merge them.
- **Don't balance Foundation techniques against Qi-Condensation
  baselines.** Foundation techniques should noticeably *feel*
  more expensive and more powerful than QC ones. Nine-Cloud
  Cranes at dmg 20 + buff_atk 3 is meant to read as "this is
  the capstone"; if I had worried about it overshadowing the
  QC arts, the progression would have felt flat. Trust the
  realm ladder.

---

## Session 11 — 2026-04-23 — "The Chronicler's Eye"

### What I built
- **Lore became an earned reward.** Until today the game had 14 good
  lore entries and only one way to get them: walk into an event that
  happened to carry `effect.lore`. Most lore was invisible in practice.
  Bosses dropped items; quests dropped items; high-rep NPCs gave warmer
  *dialogue*. None of them gave *knowledge*. That was the lever. This
  session shipped three new grant channels, retrofit the existing
  world onto them, and wrote six new lore entries to give the system
  weight.
- **Three new engine hooks, all data-driven.**
  - `enemy.on_defeat_lore: str | [str, ...]` — granted in `cmd_fight`
    on victory, after the XP/loot spray. String or list. Silent on
    already-known ids.
  - `quest.grants_lore: str | [str, ...]` — granted inside
    `quests.progress_quests` on completion. Lands in the
    `[QUEST COMPLETE]` note block alongside stones/XP/items/rep.
  - `npc.lore_dialogue: {sect_id: {threshold: lore_id}}` — evaluated
    in `cmd_talk` via new `_lore_dialogue_grant`. Same
    highest-met-positive / lowest-met-negative semantics as
    `rep_dialogue`. One lore id per leaf. The NPC "trusts you enough
    to tell you a thing" when the standing is right. Each sect's
    threshold is checked independently, so a single NPC can pay out
    multiple lore over time as the relationship deepens.
- **Single-entry helper:** `Game._grant_lore(lore_id, source)` is the
  shared announcer. Silent if already known or unknown id; otherwise
  adds to `Player.known_lore`, prints `[Lore recorded — category]
  title` with a `read <id>` hint. `source` is an optional lead-in
  line so bosses and NPCs can print different prose ("Among
  Willow-Step Shen's effects..." vs "Red Feather trusts you enough
  to tell you a thing.").
- **Retrofitted five bosses/named enemies with `on_defeat_lore`**:
  - Willow-Step Shen → `the_willow_step_cut` (the lore existed since
    session 10 but had no grant path; fixed.)
  - Heart-Devouring Gale Tiger → `fall_of_jadestep`
  - Terrace Revenant → `the_terrace_dancers` (new)
  - Stormcaller Disciple → `the_eight_point_star_ledger` (new)
  - Scarlet Pavilion Guardian → `the_ledger_of_red_names`
- **Retrofitted six quests with `grants_lore`**:
  - Kettle's Request → `song_of_the_bamboo`
  - Study the Sutra → `the_word_in_dust`
  - The Envoy's Letter → `founding_of_azure_cloud`
  - The Missing Disciple → `the_sword_river_legend`
  - Oath of Fangs → `oath_of_the_grey`
  - The Stormwarden's Test → `song_of_the_stormwarden`
  - The Broken Terrace → `mingshus_last_silence` (new)
  - The Red Path → `scarlet_lotus_oath`
- **Four NPCs gained `lore_dialogue`**:
  - Elder Baixu @ ACS +5 → `the_azure_succession_dispute` (new)
  - Matriarch Shan @ FPS +3 → `legend_of_the_first_poisoner`; @ +5 →
    `the_five_poisons_refusal` (new) — *tiered*: +3 gets you the
    origin myth, +5 gets you the ritual text.
  - Elder Red Feather @ SL +5 → `the_pavilions_four_reasons` (new)
  - Old Dog of Jadestep @ Jadestep Remnant +2 → `the_terrace_dancers`
  - Stormwarden Gao @ ACS +3 → `stormcallers_brand` (the lore entry
    already existed; just had no grant path.)
- **Six new lore entries** in `content/lore/earned.json`. All
  written in the game's voice:
  - `the_azure_succession_dispute` (history) — Jin's uncle, the seven
    silent days, the charter that was wrong. Anchors Baixu and
    blood-sworn Jin's otherwise-dangling reference to an uncle.
  - `mingshus_last_silence` (history) — what *actually* happened
    when the Gale Tiger fell. A quieter read than the public legend.
  - `the_pavilions_four_reasons` (sutra) — the contracts the Scarlet
    Lotus refuses. Gives the demonic sect moral texture.
  - `the_five_poisons_refusal` (sutra) — the five initiation oaths.
  - `the_eight_point_star_ledger` (history) — what the
    Stormcaller's brand actually tracks. Plants a seed: the uncle in
    iron-grey up on Sky-Spire.
  - `the_terrace_dancers` (myth) — pre-Jadestep terrace lore; the
    dancers who will come back for the cliffs.
- **`read` / `lore` command is now a proper library index.** Empty
  state: `You have collected no lore yet. (0 / 20 known.)`. With
  entries, it groups by category, shows a title + id line under each
  header, and ends with a hint. `read <id>` tags the entry with its
  `[category]`.
- **Validator** gained three checks — `enemy.on_defeat_lore`,
  `quest.grants_lore`, and `npc.lore_dialogue` — all verifying ids,
  thresholds, and shape. Hand-tested with bad ids; all three are
  caught.
- **SCHEMAS.md** updated in three places: NPC section gets
  `lore_dialogue`; Enemy section gets `on_defeat_lore`; Quest
  section gets `grants_lore`. Bottom-of-file `lore/` section now
  has a *How lore is earned* subsection that lists all four grant
  channels (events, on_defeat_lore, grants_lore, lore_dialogue) and
  their silent-on-known semantics.
- **Smoke test `tools/smoke_lore.py`** — 9 scenarios:
  (A) Shen grants the_willow_step_cut on first defeat;
  (B) silent on second defeat;
  (C) Kettle's Request grants song_of_the_bamboo with announcement;
  (D) Baixu's lore_dialogue fires exactly once at threshold;
  (E) threshold-picking works (Shan: +3 gives founder myth, +5
  upgrades to ritual text; the earlier entry stays learned);
  (F) `read` command groups by category with counter;
  (G) known_lore save-load round-trip + legacy save compat;
  (H) all 6 new entries load;
  (I) Gale Tiger → fall_of_jadestep. All pass. Prior smoke tests
  (affinity, companion, red_ledger) still green.

### Current state
- Validator: **23 loc / 22 npc / 17 enemy / 25 tech / 55 item / 4 sect /
  9 quest / 16 event / 20 lore / 15 recipe.** (+6 lore entries.)
- `python3 play.py` boots. Fresh player sees `(0 / 20 known.)` on
  `read`. Every existing boss, quest, and high-rep NPC relationship
  now pays out knowledge at the story-beats where that knowledge
  belongs.
- Save compat: **no new `Player` fields**. `known_lore` has been on
  `Player` since session 1; it just wasn't grown by anything other
  than random events. Every existing save loads unchanged.
- No changes to combat math, rep math, or companion math. The three
  new hooks are pure additions and silently no-op when a piece of
  content doesn't carry them.

### What I'd do next if I had another hour
1. **Huilin's sutra.** The Wandering Monk carries a staff and speaks
   of the Sutra of Empty Sleeves but has no lore_dialogue. He should
   give `the_word_in_dust` to any player who passes through the
   bamboo — but `lore_dialogue` is currently keyed by sect, and
   Huilin is `faction: shaolin` (not a real sect in world['sects']).
   Options: (a) add a `shaolin` stub sect; (b) teach him to key
   against a null-rep ("always") tier; (c) give him a
   one-off `gives_lore` field that fires on first talk. (c) is
   the smallest engine touch and is worth it — the "first
   conversation gifts a line" is a pattern that doesn't quite fit
   either rep_dialogue or the new lore_dialogue.
2. **Lore to affinity.** A steadfast companion could reveal their
   own lore entry at `steadfast` or `soul-sworn`. Jin could tell his
   uncle's side of `the_azure_succession_dispute`. Meilin could
   share an Azure Cloud founding poem. Bai could teach the Five
   Poisons cook-count. Bond-gated lore is a parallel channel to
   sect-rep-gated lore and would finally make affinity *pay out
   knowledge* as well as stat bumps.
3. **A cartographer NPC / map-lore.** Every location could have an
   optional `lore` id that's earned on first visit — the
   legends-of-places layer. Would roughly double the lore tapestry
   with ~20 location-tied micro-entries.
4. **The third Pavilion quest.** Still on the docket from session 10.
   Would now naturally grant `the_pavilions_four_reasons` mid-quest
   instead of gating it on rep +5 (the current channel — nothing
   wrong with it, but the lore is lush enough to deserve a cutscene).
5. **Endgame / Core-Formation content.** The Gale Tiger is the only
   Core-Formation enemy. A proper Nascent Soul region is overdue —
   explicitly flagged multiple sessions running.
6. **Sect Conference / Tournament.** The unchecked roadmap titan.
7. **Tier-up affinity barks.** Still open from session 9.

### Things I noticed but didn't fix
- **`lore_dialogue` is keyed by sect.** NPCs without a sect affinity
  can't use it — see Huilin above. That's a deliberate choice (the
  field mirrors rep_dialogue's shape) but it leaves a small
  unreachable corner.
- **A quest's `grants_lore` fires *before* the return-talk when the
  final step is a talk to the giver.** Because `progress_quests`
  runs on every action, by the time the player sees the
  `[QUEST COMPLETE]` spray, the lore is already in their
  `known_lore`. In practice this is fine — the announcement is in
  the same output block — but future quests that want a "the
  elder hands you a scroll" prose beat should note that the
  announcement comes pinned to `progress_quests`, not to the talk
  itself.
- **The Willow-Step Ring has no rep gate** (flagged in session 10;
  still true.) The on_defeat_lore does not add a new hatch: Shen
  is already SL-rep-gated, so the lore is effectively SL-gated too.
- **`lore` and `read` do the same thing.** The dispatch table has
  both pointing at the same handler. That's intentional — `lore`
  feels more natural when listing, `read` more natural when reading
  a specific entry.
- **No "new since last session" marker.** The `read` output doesn't
  distinguish freshly-learned from long-known entries. A timestamp
  or seen-flag would add polish but is not a save-compat friendly
  change without a new Player field.

### Don'ts (lessons learned)
- **Don't hook on_defeat_lore inside combat.py.** My first draft put
  it in `_victory()`; the second read made it clearer that the
  engine already owns lore plumbing (the event system lives there)
  and that the cleaner seam is `cmd_fight`, after combat returns
  "victory". Keeps combat pure, puts all four lore-grant channels
  (events, defeat, quest, talk) within the engine layer.
- **Don't forget that `_grant_lore` is silent on already-known.**
  My second defeat of Shen in smoke test B was expected to print a
  loot line but *not* a lore-recorded line — if the helper re-
  announced, the "silent on re-grant" invariant would have leaked
  into output and the player would see "Lore recorded" twice for
  the same entry.
- **Don't forget which location an NPC lives at.** My first pass at
  smoke test C put the player at verdant_bamboo_sea to `talk
  old_hermit_yun`, but he's at `old_hermits_hut` (one south). The
  `_find_in_loc` check refuses gracefully; the assert caught it.
  Small and familiar, but easy to trip on when retrofitting.
- **Don't conflate `category` with `sect`.** A `category` is lore
  metadata (myth/history/poem/sutra), a sect id is a rep key. The
  grouped `read` output uses category; `lore_dialogue` keys use
  sect. They are different axes and should stay different.
- **Don't add a new Player field if an existing one covers the
  need.** `known_lore` has been on Player since session 1; I
  almost added `read_lore` (a separate read-marker set) for an
  "unread" indicator and caught myself. Keeping the shape steady
  is why saves from session 1 still load.

---

## Session 10 — 2026-04-22 — "The Red Ledger"

### What I built
- **First multi-quest arc.** The previous handoff flagged a demonic-path
  follow-up as the obvious next step, and the game had nothing really
  "arc-shaped" — every quest stood alone. Now the Pavilion has one.
  **The Red Ledger** is Red Feather's second errand, silent until The
  Red Path is closed (new `quest.requires_quest` gate). Four steps:
  visit Hanging Terraces of Jadestep → defeat **Willow-Step Shen** (new
  enemy; a former outer petal, qi-condensation, hiding with the ghosts
  for twelve years) → collect the **Apostate's Cipher Page** (100% drop)
  → talk Red Feather. Rewards: +280 stones, +120 XP, a new accessory
  (**Pond-Drinker Sash** — +2 ATK, +1 DEF, +12 HP, bleed-on-hit, rep-
  gated at SL +3 so the item's own worldview matches the giver's), a
  cinnabar pill. Rep deltas: SL +3, ACS -2, Jadestep -1 (you did
  disturb the terraces).
- **Willow-Step Shen** placed at Hanging Terraces of Jadestep with
  `requires_rep: {SL: 3}`, so players *not* on the red path never meet
  him — he's functionally invisible and unfightable for them. Good: he
  only shows up when the quest makes sense. Drops include a small unique
  accessory (**Willow-Step Ring** — +2 SPD, +1 ATK, 75%) so even
  players who don't pick up the Sash reward get a flavored trophy.
  Techniques: crimson_tide_fist, blood_lotus_palm, pond_veil_step.
- **NPC `companion_reply` — a whole new dialogue layer.** Until today,
  your companion walked with you through the world but was invisible
  to it in conversation. Baixu never saw Jin at your shoulder; Red
  Feather never addressed Meilin. That asymmetry was the cleanest
  lever left in the companion system. New field on any NPC dialogue
  block: `companion_reply: {companion_npc_id: "line" | ["lines"]}`.
  On `talk`, if the player's bound companion's id matches any key,
  the matching line(s) print under the NPC's main dialogue and
  rep_dialogue. Downed companions get no reply — an unconscious
  companion is not a topic of conversation. Fired through
  `_companion_reply_lines()` in engine.py, parallel to
  `_rep_dialogue_lines()`; same data-shape treatment.
- **Fifteen reply lines across eight NPCs.** Red Feather (for Jin,
  Meilin, Bai), Elder Baixu (for Jin, Meilin, Bai), Matriarch Shan
  (for Bai, Meilin, Jin), Weilan (for Jin, Meilin), Rulan (for Jin,
  Meilin), Huilin (for Meilin, Bai, Jin), Mingshu's ghost (for Jin,
  Meilin, Bai), Old Dog of Jadestep (for Jin, Meilin). Each line is
  voice-specific: Red Feather tells Jin to sit for a third cup; Baixu
  speaks to his nephew without speaking of him; Shan names Bai as
  "her Sister" and warns the player about bringing the Pavilion's
  stray dog into the hall. The demonic companion gets the richest
  treatment because he has the heaviest backstory. The righteous
  companion gets the most *reassuring* lines because she is known
  everywhere.
- **Lore.** New entry `the_willow_step_cut` — Red Feather's own
  account of the stolen page twelve years ago, closing on the line
  she didn't say ("and then for the man") and the sister-elder who
  didn't ask. Discoverable in the world by... well, presently by
  hand. Not yet attached to an event or read-on-defeat hook. (A next
  session could tie it to Shen's defeat.)
- **Engine plumbing.**
  - `engine.py`: `_companion_reply_lines(npc)` added; called from
    `cmd_talk` after rep_dialogue.
  - `quests.py`: `offer_quest` checks the new `requires_quest` field
    and silently declines to offer (empty string return) if unmet.
  - No new Player fields. All save-compat preserved.
- **Validator.** Two new checks in `tools/check_content.py`:
  - `companion_reply`: must be dict; keys must be real npc ids;
    values must be non-empty strings or lists of non-empty strings.
  - `quest.requires_quest`: must point at a real quest id.
- **SCHEMAS.md.** NPC section documents `companion_reply`. Quest
  section documents `requires_quest`.
- **Smoke test.** `tools/smoke_red_ledger.py` — 7 scenarios:
  (A) quest silent before prereq, (B) auto-offered after prereq,
  (C) Shen invisible/unfightable at low rep and visible at SL +3,
  (D) full quest flow end-to-end with reward/rep delta
  verification, (E) companion_reply fires only for the bound
  companion, (F) downed companion silences it, (G) Baixu↔Meilin
  wiring works at a different location. All prior smoke tests
  (affinity, companion, companion_downed) still green.

### Current state
- Validator: **23 loc / 22 npc / 17 enemy / 25 tech / 55 item / 4 sect /
  9 quest / 16 event / 14 lore / 15 recipe.** (+1 enemy, +3 items,
  +1 quest, +1 lore.)
- `python3 play.py` boots. A fresh player sees no change; a player
  who has walked the Red Path and re-talks to Red Feather sees the
  second quest offered. A player with Jin/Meilin/Bai at their
  shoulder now hears *different* NPCs address the companion during
  talk.
- All prior saves load. No new Player fields.
- Quest data flow: auto-offer, accept on first talk, step through
  visit → defeat → collect → talk. Shen's drop is 100% on the cipher
  page so the collect step is never a luck gate.
- The Willow-Step Ring is pure drop flavor: no rep gate, stacks with
  anything. Useful as a mid-realm SPD option for non-Pavilion
  players too (if they manage to reach Shen; since he's SL-rep-gated,
  they can't).

### What I'd do next if I had another hour
1. **Tier-up affinity barks.** Session 9's first next-up item, still
   open. When Meilin first reaches `trusted`, she should say
   something Meilin-specific the next time you `look`. Cheap to
   implement (`last_bark_tier` on companion runtime dict; four lines
   per companion). I deferred because the companion_reply layer felt
   higher-value as its own session.
2. **Attach `the_willow_step_cut` lore to Shen's defeat.** Right now
   the lore entry exists but can't be acquired. Options: (a) an
   on-defeat-lore hook in combat.py (new mechanic); (b) reach it
   through a Red Feather "tell me the story" dialogue after the
   quest is done; (c) add it as an item-on-ground at the terraces
   that becomes visible after Shen's death (requires new mechanic).
   Smallest path is probably (b): a rep_dialogue tier above +5 on
   Red Feather that grants lore. But rep_dialogue doesn't currently
   grant lore — it's pure text. So (a) or (c) is a small engine add.
3. **A third quest in the arc.** Red Feather now owes you one. The
   natural step: she sends you to *deliver* the page to the sister-
   elder the page cost — a new NPC, perhaps at a new Pavilion
   location. Would start to build the Pavilion into a proper sect
   with more than two locations.
4. **Companion banter lines on `go`.** Location barks fire on
   arrival. A spare system would be `travel_barks` — a small
   percentage chance per move that the companion comments on the
   road ("the bamboo sings tonight", "I hate this stretch after
   dark"). Pure flavor; low risk.
5. **Sect Conference / Tournament** — still the top unchecked
   multi-quest project. Much larger than a session.
6. **Something above Foundation Establishment.** The Core-Formation
   tiger exists at Sky-Spire, but the *realm* above it is empty in
   practice — no locations, no NPCs, no quests. An endgame session
   is overdue.
7. **`teach <technique> to companion`.** Still on the list from
   session 8. The current companion techniques are baked at recruit
   time; letting the player pass on learned arts would be a proper
   new mechanical layer.

### Things I noticed but didn't fix
- **companion_reply doesn't chain with rep_dialogue.** If Red Feather
  has both a rep_dialogue tier triggered AND a companion_reply, she
  prints both. That's fine — they're additive commentary — but the
  *order* is: base dialogue, then rep lines, then companion reply.
  Feels right to me (world state first, companion reaction last).
- **The final talk step in the quest is redundant in practice.** See
  the session-9 note on quests: once visited/defeated/collected are
  all satisfied, progress_quests auto-closes the quest if the player
  has ever talked to the giver. Since you must talk to them to
  accept the quest, the return-talk is implicit. Works fine; feels
  slightly loose narratively. A `talk_again_required` flag would fix
  it, but that's engine work for a small feel improvement.
- **Pond-Drinker Sash is accessory slot.** Scarlet Pavilion Token is
  also accessory slot. A fully-kitted SL player can only wear one at
  a time. Probably the right call — you choose between the assassin-
  recognised token and the elder-sworn sash — but a future
  alternative could make the Sash a belt/sash sub-slot if slots ever
  expand.
- **`requires_quest` is a single string.** Multi-prereq quests ("do
  A and B first") aren't supported — intentional, scope control.
  List support is a three-line change if ever needed.
- **Willow-Step Ring has no rep gate.** Any player who somehow
  reaches Shen can loot it. Since Shen himself is rep-gated, the
  ring is effectively SL-gated too, but an aggregator would find
  this a loose hatch.
- **Red Feather's gives_quest is now `the_red_ledger`** — not the
  original Red Path. The original giver was Rulan (still is), so
  that's fine. If a future session wants Red Feather to give
  multiple quests, the `gives_quest` field would need to become a
  list.
- **Completed quests still show in `quest` output.** The player can
  see "Red Path" under "Completed:" even after The Red Ledger is
  accepted. That's fine for now, but a big quest list will eventually
  want a "most recent completed only" toggle or a cap.

### Don'ts (lessons learned)
- **Don't capture `before_stones` / `before_xp` after the quest has
  already auto-completed.** My first smoke test measured "after the
  fight" and "before the final talk", not realising the quest had
  already closed when progress_quests ran during the fight. The
  final talk gives no new reward. Right measurement is: snapshot
  everything *before* the player does anything that could trigger
  progress_quests (i.e. before the first talk or first look). This
  is a general lesson for smoke-testing multi-step quests where the
  last step can be pre-satisfied.
- **Don't forget the companion may not be at the location you expect
  when you re-recruit.** My first cut of the "downed silences
  companion_reply" test re-recruited Jin at the shrine — he lives at
  Crimson Creek, so `find_in_loc` failed. Move the player, then
  recruit, then move them back.
- **Don't wire `gives_quest` to two quests on the same NPC.** The
  field is a single string. I considered migrating it to a list but
  that's a separate infra task; easier to keep Rulan on the Red Path
  and put the Red Ledger on Red Feather herself (who had no
  gives_quest before).
- **Don't rep-gate a quest on the *same* sect's rep that the prior
  quest grants.** The Red Path grants SL +3; the Red Ledger requires
  SL +3. This looks tautological, but it isn't: a player who did the
  Red Path and then somehow lost SL rep (future content might) would
  be locked out of the Ledger until they rebuilt. That's actually
  the correct behaviour — the Pavilion doesn't trust you if you've
  cooled — but I double-checked the math to make sure I wasn't
  accidentally gating myself out of my own quest.
- **Don't forget that `talked_to` is a set, not a list of encounters.**
  Once you talk to an NPC, you've "talked" to them forever as far as
  the quest engine is concerned. Designing a final-talk step as a
  "return delivery" doesn't enforce returning — see above. Know this
  when writing multi-step quest content.

---

## Session 9 — 2026-04-22 — "The Blood-Sworn"

### What I built
- **The third companion — Blood-Sworn Jin, at Crimson Creek.** Previous
  handoff's first "if I had another hour" item: the demonic path was
  missing its walking partner. Now it has one. Jin Wuxin is a lapsed
  Azure Cloud inner disciple who burned his sash after an uncle's
  exile and fell into the Pavilion's orbit without ever being fully
  welcomed. Three dialogue lines; NPC rep_dialogue reacts to ACS +3
  (hostile), ACS -3 (kindred-bitter), and SL +5 (below his, by design).
  Combat shape is the sledgehammer the old handoff asked for: HP 48,
  ATK 11, DEF 2, SPD 6, qi 20/40. Techniques: crimson_tide_fist,
  blood_lotus_palm (life-steal), heart_rending_claw. Gates: completed
  `the_red_path` + SL rep +3 + qi_condensation. NPC itself carries
  `requires_rep: {scarlet_lotus_pavilion: 3}` so he's *invisible* below
  the gate — the player can't even see him before they've walked the
  red path. This matters: it means Jin appears as a consequence of
  choice, not as a universal passive feature.
- **Companion affinity — a bond that persists.** The old handoff named
  this "the obvious next mechanical layer." New `Player.companion_affinity:
  Dict[str, int]` maps npc_id -> score. +1 on any shared combat victory
  (but only if the companion is still standing at the final blow —
  downed companions get nothing, and neither do you if they fell);
  +2 on any quest completion while a companion is bound (downed is
  forgiven here — they walked the road). Four tiers: **bonded** (0–4),
  **trusted** (5–11), **steadfast** (12–24), **soul-sworn** (25+).
  Each tier grants flat stat bonuses applied at fight start (up to
  +2 ATK, +1 DEF, +1 SPD at soul-sworn). Crossings print a prose beat.
  Affinity persists across dismiss/recruit — a bond once earned isn't
  undone by a temporary parting. Recruit screen tells you if you're
  resuming an existing bond and shows the tier.
- **Location barks.** Each companion block can carry `location_barks:
  {loc_id: "line"}`. On `look`, if the bark loc differs from the
  companion's `last_bark_loc` (stored on the runtime companion, saved
  across sessions), the line fires and the loc is remembered. Walking
  away and returning re-arms the bark. Shipped barks for all three
  companions at the locations where they *have stakes* — Meilin at
  Scarlet shrine / creek / poisoner's garden / venom hall / bandit
  road (5 sites); Bai at Azure outer gate / inner courtyard / Scarlet
  shrine / Crimson Creek / Bandit Road (5); Jin at his former sect's
  gate / courtyard / Baixu's pavilion / library / venom valley mouth /
  the Scarlet shrine he refuses to cross into (6 — his barks are the
  most bitter, and they should be). Bark prose is short and first-
  person-voice; no floating narrator.
- **Engine plumbing.**
  - `state.py`: `companion_affinity` field (default `{}`, backfilled on
    legacy load); helpers `affinity()` / `adjust_affinity()`; shared
    `AFFINITY_TIERS`, `affinity_tier()`, `affinity_bonus()`.
  - `combat.py`: fight-start snapshots the affinity bonus into the
    runtime companion's stats (so base stats on Player never mutate);
    victory grants +1 affinity if companion still standing, with tier-
    cross messaging.
  - `quests.py`: +2 affinity on quest completion if any companion is
    bound, with a Bond note in the quest-complete spray.
  - `engine.py`: `cmd_look` calls `_maybe_companion_bark()` after
    exits; bark gated by `last_bark_loc` on the runtime companion.
    `cmd_companion` shows effective stats with (base+bonus) breakdown
    and tier line. `cmd_status` adds a bond suffix. `cmd_recruit`
    restores pre-existing bond tier on re-recruit.
- **Validator.** Checks `companion.location_barks` for valid location
  ids and non-empty strings. All existing checks still green.
- **SCHEMAS.md.** NPC companion block gains `location_barks` example;
  the Companions section gains an Affinity sub-section with the full
  tier table and a Barks sub-section.
- **Smoke tests.** New `tools/smoke_affinity.py` — 9 scenarios: Jin
  invisibility below gate; gate-met recruit; affinity 0 display;
  combat +1; tier bonus doesn't corrupt stored base stats; persistence
  across dismiss; bark fires once, doesn't re-fire on re-look; save/load
  of companion_affinity (and legacy default); quest-completion +2 bond
  with note. Prior session-8 smoke tests still green.

### Current state
- Validator: **23 loc / 22 npc / 16 enemy / 25 tech / 52 item / 4 sect /
  8 quest / 16 event / 13 lore / 15 recipe.** (+1 npc: blood_sworn_jin.)
- `python3 play.py` boots; `status`, `companion`, and combat all surface
  the bond. Fresh player sees `bonded (+0)` on their first companion;
  earning +5 through fights/quests moves them to `trusted` with a +1
  ATK stat line in the combat prelude.
- All prior saves load. The only new Player field is
  `companion_affinity`, backfilled to `{}`. The new bark-tracker is
  stored inside `companion` (`last_bark_loc`), which already lives in
  a dict we lazy-read, so legacy companion dicts without that key just
  bark on first look at every location — harmless.
- Combat math unchanged for solo players. For companion-bearing players
  the only change is a one-line "Your bond is X — +Y STAT" prelude on
  fight start, and an occasional tier-up beat on victory.

### What I'd do next if I had another hour
1. **Affinity barks.** Right now barks are location-tied. An adjacent
   layer: tier-up barks. When Meilin first reaches `trusted`, she says
   something Meilin-specific the next time you `look`. Only once per
   tier. The hook is cheap (store `last_bark_tier` on the companion
   runtime dict, same as `last_bark_loc`). The work is in the content
   — 4 lines × 3 companions × tiers above bonded = 12 lines. Could do
   it in 20 minutes.
2. **Companion banter at landmarks.** An NPC dialogue line could gain
   a `companion_reply: {npc_id: "line"}`. When the player talks to
   Elder Baixu with Jin at their shoulder, Baixu should *see* him and
   say something. Same for Red Feather / Meilin. This is a real
   piece of writing and would be a whole session of content, but it's
   where the companion system wants to grow next.
3. **Shared cultivation as a bond grower.** `cmd_cultivate` currently
   revives downed companions. Letting it also tick affinity +1 (with
   a per-session cap, or only at qi_density ≥ 5 locations) would give
   the player an explicit non-combat path to grow trust. Small; adds
   a reason to meditate somewhere beautiful *with* your companion.
4. **Teach the companion.** Same idea the session 8 handoff raised;
   still open. `teach <technique> to companion` command. Would need
   save-compat thinking — the companion's technique list would need
   to become mutable per-recruitment-session; probably a
   `Player.companion["learned_techniques"]` list additive to the
   content-defined ones.
5. **A demonic-path quest arc.** Now that there's a demonic companion,
   the Scarlet Lotus feels more playable. The obvious next quest:
   Red Feather sends the player (with Jin, if present) on a second
   errand — e.g., retrieve a Pavilion relic from the Jadestep ruins.
   If Jin is present there's unique dialogue or a branching step. This
   is where story arcs begin.
6. **Sect Conference / Tournament** — the top unchecked quest in the
   roadmap. A substantial session in its own right. Would naturally
   use companions (you bring yours to fight). Deferred.
7. **Make the prompt show the companion.** `[HP 30/30 Qi 0/50 | Jin 48/48] >`
   would be a nice "the bond is visible" touch. One-liner in
   `_prompt()`. Didn't do it because the prompt is already crowded
   and I didn't want to commit the shape before hearing it tested.

### Things I noticed but didn't fix
- **Affinity has no ceiling.** A dedicated player could push Meilin
  to affinity 50+ and nothing happens above soul-sworn (25). Fine for
  now — the bonuses cap; further numbers are just flavor. But if a
  future session wants prestige tiers ("name-bearing" at 50, "twin-
  blade" at 100), the `AFFINITY_TIERS` table in state.py is the only
  place to edit.
- **Affinity has no way to drop.** Dismissing doesn't lose any. Taking
  an action the companion would hate (e.g., Meilin present when the
  player completes the_red_path, gaining -2 ACS) doesn't cost bond.
  Dropping affinity is a whole mechanical layer I deliberately punted.
- **Jin's first dialogue line mentions his uncle**, but there's no
  lore entry about who the uncle was. Future flavor: a lore entry
  about the Azure Cloud succession dispute would anchor that line.
- **Barks don't fire in `go`** — they fire in `look`, which `go`
  calls. Works fine *if* the player doesn't use `map` to navigate
  blindly. Direct-go after a map check will trigger a look; bark
  fires. OK.
- **The bond message at fight start only prints if a bonus is
  non-zero.** A bonded (+0) companion shows no prelude. I think that's
  right — zero-bonus is the "normal" state and doesn't deserve a line.
- **Backwards-compat note for future me**: the runtime companion dict
  does NOT store affinity as a field; affinity lives on Player, looked
  up per-fight. I started with it inline and ripped it out — single
  source of truth, dismiss/recruit just works.
- **Save files from before session 8** (no `companion` field) still
  load cleanly via the `setdefault` in `from_json`. Tested.

### Don'ts (lessons learned)
- **Don't apply affinity bonuses to stored base stats.** My first
  draft mutated `player.companion["atk"] += aff_bonus["atk"]` at fight
  start, with a matching subtraction at fight end. It worked *once*;
  on a save-mid-fight-reload the subtraction would never run and the
  next fight would double-count. Right answer: snapshot base → runtime
  comp at fight start (already happening for hp/qi), add the bonus to
  the runtime only, never touch stored base. Writeback only restores
  hp/qi/downed.
- **Don't print the bark from `cmd_go`.** `go` already calls `look`,
  which is where the bark belongs. Double-hooking produced two barks
  per arrival in early testing.
- **Don't gate Jin on the quest *alone*.** My first gate was
  `requires_quest: the_red_path`, no rep. If the player did the quest
  and then killed Red Feather (losing SL rep), Jin should not walk
  with them — his entire backstory says he bends toward whoever the
  Pavilion favours at the moment. Adding `requires_rep: {SL: 3}`
  fixed that without requiring a second quest.
- **Don't forget to add the new NPC id to the location file.**
  Standard validator catch, standard fix — but the first run of the
  validator after adding Jin said "all references resolve" and I
  caught myself about to commit without the link, because Jin existed
  but wasn't referenced from anywhere. The `look` smoke-test is what
  exposed it — no NPC listed at crimson_creek.
- **Don't let the quest bond-bump announce tier changes when
  tier didn't change.** The progress_quests bond note compares
  old_tier to new_tier; if same, print the "deepens (+2)" line, not
  the "raises to X" line. Subtle, but having "raises to bonded" print
  when you were already bonded reads wrong.
- **Don't write barks longer than one short paragraph.** The feel is
  "the companion mutters / tightens up / glances at a thing"; two
  sentences max. Longer and it competes with the room description
  for the player's eye.

---

## Session 8 — 2026-04-22 — "The Sworn Oath"

### What I built
- **A companion system, end-to-end.** Until now the player fought every
  duel alone — including Foundation-tier bosses. That lonely silhouette
  was the cleanest lever left: combat already had rich status/crit/dodge
  machinery, rep already had faction colors, but nothing *walked with you*.
  Now it does. One companion at a time (the engine enforces it), snapshotted
  onto the player from an NPC's `companion:` content block and carried
  between fights as runtime state.
- **Engine — ally combat turn.** Each round after the player's action,
  an active non-downed companion ticks statuses, regenerates a trickle
  of qi (3/turn), then takes an action: ~55% chance of a random
  affordable technique, else a basic attack. Same crit/dodge math as
  the player. Technique effects route correctly — heals go to the
  companion's HP, offensive riders (bleed/poison/stun) go to the enemy.
- **Engine — split enemy targeting.** When a companion is up, 35% of
  enemy actions (both basic and technique) target the companion instead
  of the player. Damage, dodge, crit, and status effects all read the
  correct target's DEF/SPD and apply status to the correct status list.
  Enemy narration adapts ("strikes you" vs "strikes Disciple Meilin").
- **Engine — downed state.** A companion reduced to 0 HP is *downed*,
  not dead. They sit out the rest of the fight (no HP bar printed, no
  turn, no targeting) and the fight continues with the player alone.
  Downed persists through save/load. `cultivate` at any location
  revives them to full HP and resets the flag — the meditative breath
  you share is the ritual of return. A non-downed companion heals to
  full after any non-defeat outcome (the fiction says between-battle
  rest is assumed; the mechanic says "you don't have to grind HP back").
- **Engine — recruit / dismiss / companion commands.** `recruit <npc>`
  requires the NPC at your current location to have a `companion` block
  and for the player to meet every declared gate (realm, rep, quest).
  `dismiss` releases the bond. `companion` / `party` prints a full
  statblock with technique names. `status` gains a one-line companion
  summary. `help` was updated.
- **Content — Disciple Meilin (Azure Cloud).** Promoted from a one-line
  sword-hall NPC to a recruitable ally. Gates: Qi Condensation realm,
  ACS +2, completed `study_the_sutra`. Combat shape: HP 58, ATK 9, DEF
  3, SPD 7, qi 20/40. Techniques: White Crane Sword, Azure Cloud Palm,
  Calming Breath (the heal routes back onto her, so she self-mends in
  long fights — tested it saves a low-HP Meilin cleanly). I also added
  a Scarlet-Lotus-rep `rep_dialogue` line and a third base dialogue
  line that gives her voice teeth ("He does not name me soft").
- **Content — Venom-Handler Bai (Five Poisons).** New NPC at
  Poisoner's Garden — which was previously empty of people. Gates:
  completed `oath_of_fangs` + FPS rep +2. Combat shape: HP 50, ATK 7,
  DEF 2, SPD 8, qi 18/36. Techniques: Serpent Strike (poison), Venom
  Strike (poison), Centipede Stance (buff_def). She's a lean,
  poison-and-ward build — tactically different from Meilin's
  sword-and-heal. Has her own `rep_dialogue`, including a
  Scarlet-Lotus warning line.
- **Player state.** New `Player.companion: Optional[Dict]` field,
  defaults to `None`. `from_json` backfills with `setdefault` so
  pre-session-8 saves load cleanly.
- **Validator.** `tools/check_content.py` gained a companion-block
  section: stat ints must be non-negative, techniques must exist,
  gates must point at real realms / quests / sects.
- **SCHEMAS.md.** NPC section documents the `companion` block; a new
  top-level "Companions" section explains the combat model, downed
  state, and revival.
- **Smoke tests.** `tools/smoke_companion.py` runs six scripted
  scenarios (default recruit refused, gated recruit works, save/load,
  dismiss, revive, Bai-specific gates). `tools/smoke_companion_downed.py`
  drives harder combat across five seeds to exercise split targeting,
  status-on-companion, and the downed path. Both pass cleanly.

### Current state
- Validator: **23 loc / 21 npc / 16 enemy / 25 tech / 52 item / 4 sect /
  8 quest / 16 event / 13 lore / 15 recipe.** (+1 npc: venomhand_bai.)
- `python3 play.py` boots; `help` lists the new commands; `companion`
  prints "You walk alone." for a fresh player; `recruit disciple_meilin`
  at Inner Courtyard refuses politely when gates aren't met.
- All prior save files load. Combat is unchanged for solo players.
- Both new companions are tactically distinct: Meilin is the
  reliable righteous sword (high HP, sword + palm + self-heal), Bai
  is glass-cannon venom (high SPD, DOT-focused, self-buff stance).
- Smoke tests in `tools/`. Re-run as regression checks in later
  sessions.

### What I'd do next if I had another hour
1. **A third companion — demonic path.** Scarlet Lotus is the
   conspicuous gap. An NPC at Crimson Creek or the Shrine (e.g.
   "Blood-Sworn Jin", a lapsed disciple) with `requires_rep:
   {scarlet_lotus_pavilion: 3}` would complete the faction triangle.
   Combat shape should be *offensive*: crimson_tide_fist + blood_lotus_palm
   + heart_rending_claw. The demonic companion should feel like a
   sledgehammer — low DEF, huge ATK, self-heal via life-steal palm.
2. **Companion affinity / loyalty.** A simple `companion.affinity` int
   on Player, gained by completing quests together and lost by
   dismissing repeatedly or taking actions their sect would object to.
   At low affinity they start missing turns; at high affinity they
   unlock one extra technique or a small stat buff. This is the
   obvious next mechanical layer once there's more than one.
3. **Make companions react to the location.** Right now Meilin is the
   same regardless of where you walk her. A sect-location bonus (she's
   at +1 ATK inside Azure Cloud sect areas, Bai at +1 SPD in gardens)
   would start to make *where* you fight matter.
4. **Companion dialogue — barks.** One-liner under `cmd_look` when a
   companion is active and the location belongs to their sect's enemy.
   "Meilin tightens her grip on her scabbard" at the Scarlet Lotus
   shrine. Pure flavor, but it's a natural place for a small data
   field on the companion block (`location_barks: {loc_id: line}`).
5. **Companion death (as opposed to downed).** Right now they can't
   die, only be downed. A `hardcore_death: true` flag would make a
   downed companion in defeat permanently gone — spicy but risky;
   needs save hygiene. Deferred.
6. **Teach the companion.** A `teach <technique> to companion` command
   would let you share learned techniques with your ally. Meilin's
   list is fixed right now; letting the player pass on a pill-bought
   technique would make the bond grow.
7. **Test a 2-companion tag-team edge case.** Already blocked in
   cmd_recruit ("dismiss first"). Probably fine — just noting that
   multi-companion combat is a whole new problem and I intentionally
   didn't open the door.

### Things I noticed but didn't fix
- **Companion qi doesn't regenerate out of combat**, only mid-fight
  (+3/turn). So a companion who used techniques in fight N+1 starts
  with less qi. That's fine — it's a slight penalty for technique
  spamming. But it's inconsistent with "HP heals to full after
  non-defeat." If future-me wants symmetry, the `_writeback_companion`
  is the one place to restore qi too. I deliberately didn't, because
  qi scarcity is the one lever that keeps long fights from becoming
  pure technique-spam.
- **Enemies with stun techniques never stun the companion**, because
  the enemy dice-roll picks a target per round and stun lasts
  turns. If the enemy stuns the companion on round N, on round N+1
  they'll likely pick the player as target anyway. Result: stun on
  the companion mostly just eats their turn once. Fine, not worth
  special-casing.
- **The companion's basic-attack miss line says "sways away"** — same
  verb as enemy dodge lines. Tiny flavor redundancy; distinct verbs
  for each party would be nicer but the `_MISS_LINES` table is
  currently only used by player attacks.
- **Recruit dialogue bypasses `rep_dialogue`.** The recruit/decline
  strings are on the `companion` block; they fire on `recruit` but
  not on `talk`. That's intentional — the bond is its own moment —
  but a `talk`-time line for "since you bound me to your road" would
  be a nice bonus later.
- **Companion techniques with `requires_realm` are not re-checked**
  at use-time. Meilin has `azure_cloud_palm` which requires Qi
  Condensation, but she's *already* Qi Condensation (implicit from
  her recruit gate), so in practice fine. If a demonic companion with
  `heart_rending_claw` (Foundation) is added later with a Qi Condensation
  player, this would ship a technique the player couldn't learn but
  the companion uses freely. That's *thematically correct* — they're
  their own cultivator — but someone should flag it in the companion
  content if it matters.
- **No companion entries in MEMORY.md**, which is a per-file reference
  anyway. ROADMAP.md has the running inventory.
- **Meilin's `requires_realm: qi_condensation` is restrictive** — a
  mortal-tier player can't recruit her even with rep + quest. That's
  the intended pacing (the bond arrives at the second realm), but a
  future session could add a mortal-tier companion (a Huilin variant?)
  for earlier-game players.

### Don'ts (lessons learned)
- **Don't heal the companion to max *before* checking if they were
  wounded.** First draft of `cmd_cultivate` set `comp["hp"] = max_hp`
  and then checked `comp["hp"] < max_hp`, which is trivially false
  after the write. Snapshot the pre-write HP into `was_wounded` first.
  Caught on read, fixed before test.
- **Don't forget that companion status lists must live per-fight.**
  Early sketch stored companion status on `player.companion["status"]`
  (persisting across fights), which would mean a poisoned companion
  could walk into the next fight still poisoned. Wrong: status lives
  on the fight, not on the entity. The runtime `comp["status"]` inside
  `fight()` is the whole answer.
- **Don't read companion gates via `talk` logic.** `recruit` is its
  own command with its own gate checks. I considered piggy-backing on
  `talk` (" ask to join me ") but that conflates dialogue with a
  state-changing action and is harder to see in save history.
- **Don't forget to update the quest_id**. I used `the_oath_of_fangs`
  in my first draft of the Bai companion block; the real id is
  `oath_of_fangs`. The validator caught it. Validator earns its keep.
- **Don't make the ally's basic attack use `_enemy_atk`'s noise
  envelope**. First draft ran the companion through `_enemy_atk`
  (which is `base + randint(-1,2)`). That scales different from how
  the player swings (`base + randint(-1,3)`). I switched to the
  player-style envelope so ally strikes feel like ally strikes, not
  enemy strikes.

---

## Session 7 — 2026-04-22 — "The Red Path"

### What I built
- **The Scarlet Lotus Pavilion finally exists.** Before this session the
  demonic sect was a name attached to a sect file and a single unattainable
  technique (`scarlet_lotus_palm`). No NPCs, no location, no presence in the
  world. Session 6 introduced a way to *lose* rep with them (the Envoy's
  Letter quest) but there was nowhere the loss would matter. That gap is
  now closed end-to-end.
- **Engine — rep-triggered NPC/enemy spawning.** New helper
  `_rep_visible(obj)` on `Game`: checks a spawnable's `requires_rep`
  (floor) and `requires_rep_at_most` (ceiling) against the player's
  current rep. Used in `cmd_look` (NPCs + enemies lists), `_find_in_loc`
  (so you can't talk/fight an entity that isn't there for you), and
  `cmd_fight` single-enemy auto-pick. This is the mechanic the handoff
  has been asking for since session 4 — rep is now something the *world*
  can read, not just the engine's internal gates.
- **Engine — `ambush_text` on enemies.** One atmospheric sub-line printed
  under a rep-triggered enemy in `look`. Keeps the hostile-spawn from
  feeling like a stat: "A crimson silk scarf flutters from a crow-perch
  as you pass. There is no bird." The prose is the *announcement*.
- **New region: Scarlet Lotus Reach.** Two locations, connected south
  from Bandit Road via a new `south` exit.
  - **Crimson Creek** — the approach. A rust-red creek (locals blame old
    dyepits, but no dyer has worked them in a generation). A bronze bell
    with its tongue stolen hangs from a branch. Has a permanent enemy
    (`blood_sworn_cultivator` — the sect's half-forgotten castoffs) so
    the path isn't empty combat-wise.
  - **Scarlet Lotus Hidden Shrine** — sect HQ. Lacquered pavilion on an
    island in a blood-red pond. Hosts two NPCs and a conditional boss
    guardian. Crimson Registry Fragment on the ground.
- **3 NPCs.**
  - **Rulan the Thin-Smiling** (Outer Petal) — at Bandit Road. Offers the
    quest. `requires_rep_at_most: {scarlet_lotus_pavilion: 4}` — once
    you're honoured by the sect, she retreats (she was only the recruiter;
    you outrank her). Rep_dialogue reacts at SL ±2 and at ACS +3 (her
    voice sharpens when a sword-sect player pauses at her stone).
  - **Elder Red Feather** (Hong Yu, Fifth Elder) — at the shrine. Teaches
    blood_lotus_palm (SL ≥ 1) and heart_rending_claw (SL ≥ 2). Sells
    blood-petal mantle (SL ≥ 2). Rep_dialogue at SL ±2 and +5, and at
    ACS +5 (the sect will *notice* an Azure sword walking in).
  - **Apothecary Weilan** (the Red Pestle) — at the shrine. Teaches
    crimson_tide_fist (SL ≥ 0 — the entry-level demonic art). Sells
    crimson cinnabar pill, scarlet pavilion token, antidote pearl.
- **4 new enemies, 3 rep-gated.**
  - **Scarlet Lotus Assassin** — at Bandit Road, `requires_rep:
    {azure_cloud_sect: 3}`. Qi Condensation, 62 HP, hit-and-run
    poison+bleed loadout (venom_strike, scarlet_chain_lash).
  - **Scarlet Lotus Hunter** — at Merchant's Crossing, `requires_rep:
    {azure_cloud_sect: 5}`. Foundation, 110 HP, heavier tier. Carries a
    contract with a defaced azure wax seal — it's you.
  - **Scarlet Pavilion Guardian** — at the shrine, `requires_rep_at_most:
    {scarlet_lotus_pavilion: -1}`. Foundation boss, 150 HP, three
    techniques including pond_veil_step (self-buff_def). Drops the
    mantle at 25% and the token at 15%. Only appears when you've fallen
    below zero with the sect — an insulted Pavilion attacking on sight.
  - **Blood-Sworn Wretch** — always visible at Crimson Creek, regardless
    of rep. The sect's abandoned bodies — a natural hazard.
- **5 techniques.**
  - `blood_lotus_palm` (14 qi, 16 dmg + heal 6 — the life-steal signature,
    uses existing `heal` effect type, SL ≥ 1 gate, earth rank).
  - `crimson_tide_fist` (10 qi, 12 dmg + bleed 4, SL ≥ 0 gate).
  - `heart_rending_claw` (16 qi, 10 dmg + stun 2, SL ≥ 2, heaven rank,
    Foundation-gated — the capstone of the demonic palm tree).
  - `scarlet_chain_lash` (enemy-only, bleed).
  - `pond_veil_step` (enemy-only, buff_def 3).
- **5 items.** Blood Lotus Petal (material), Crimson Cinnabar Pill
  (hp_heal 45 — the demonic analog to minor healing pill, 95 stones),
  Scarlet Pavilion Token (accessory, +2 ATK, +1 SPD, on_hit poison 1,
  SL ≥ 1 gate), Blood-Petal Mantle (robe, +4 DEF, +2 ATK, +10 HP, SL ≥ 2,
  340 stones), Crimson Registry Fragment (treasure — lore only, on
  ground at the shrine).
- **1 quest — The Red Path.** Rulan asks for a tribute of three venoms
  from the southern sects' own gardens: viper_fang, venom_gland,
  black_lotus_seed. Reward: 160 stones, scarlet_pavilion_token,
  crimson_cinnabar_pill, 75 XP. Rep: **+3 Scarlet Lotus, -2 Azure Cloud,
  -1 Five Poisons.** Using existing materials means any player who has
  already done Oath of Fangs has the items on hand — the quest is a
  deliberate moral pivot, not a new grind.
- **2 lore.** The Oath of the Scarlet Petal (sect doctrine —
  "whoever owns the pain owns the world"; granted via pond event at the
  shrine), The Ledger of Red Names (history of the Crimson Registry;
  the ledger is of the sect's *debts*, which is how they've survived
  without ever winning a war).
- **2 events.** crimson_wind_carries_chanting (creek, no effect, just
  tone), lotus_pond_reflects_blood (shrine, grants scarlet_lotus_oath
  lore at 45%).
- **Retrofits.**
  - `bandit_road`: new south exit to Crimson Creek; Rulan and Assassin
    added to its npcs/enemies.
  - `merchant_crossing`: Hunter added to enemies.
  - `elder_baixu.rep_dialogue`: new "scarlet_lotus_pavilion +2" warning
    line, so the cross-sect standing finally provokes him.
  - `scarlet_lotus_pavilion` sect: headquarters set to the shrine,
    elders list includes Elder Red Feather, signature techniques
    extended with the two new SL palm arts.
- **Validator.** `tools/check_content.py` now checks `requires_rep` and
  `requires_rep_at_most` on npcs and enemies via the existing
  `_check_rep_map` helper.
- **SCHEMAS.md.** Updated NPC and Enemy sections to document the two
  new spawn gates and `ambush_text`. The "Reputation system" section
  at the bottom was extended to note spawns as one of the currently-
  honored gate categories.

### Current state
- Validator: **23 loc / 20 npc / 16 enemy / 25 tech / 52 item / 4 sect /
  8 quest / 16 event / 13 lore / 15 recipes.** All references resolve.
- Smoke-tested four scripted scenarios:
  1. **Default rep (all 0):** walk Verdant → Bandit Road → Crimson
     Creek → Shrine. Rulan visible at Bandit Road, no Assassin;
     Elder + Weilan visible at shrine, no Guardian. Quest auto-offers
     on talk. Pond event grants lore on shrine entry.
  2. **Hostile (ACS +5, SL -3):** Assassin on Bandit Road with ambush
     text; Hunter on Merchant's Crossing with ambush text; Guardian at
     shrine with ambush text. Rulan *still* visible (at -3 SL she
     hasn't retreated yet). Elder and Weilan also still visible —
     only the Guardian is hostile. Combat against Assassin confirmed
     working end-to-end (lost, as expected for a mortal test-char).
  3. **SL-friendly (SL +6, ACS -3):** Rulan has vanished from Bandit
     Road (her `requires_rep_at_most` = 4 kicks her out at +5). Elder's
     top rep_dialogue line fires ("The pond calls you home before I
     do..."). Shrine NPCs all present; Guardian absent.
  4. **Quest + gate walk:** carrying inventory matching the three
     tributes, pick up the quest — it auto-completes in one talk
     (three collect steps in a row) and fires the rep changes with
     correct rank crossings (stranger → respected / distrusted).
     After that, gates verified: equipping scarlet_pavilion_token at
     SL +0 is refused with the proper prose; learning
     blood_lotus_palm at SL +0 is refused; learning crimson_tide_fist
     at SL +0 succeeds (its gate is SL ≥ 0); buying blood_petal_mantle
     at SL +0 is refused.
- Old saves still load — no new Player fields. The rep-visibility helpers
  read `Player.reputation`, which has existed since session 1.

### What I'd do next if I had another hour
1. **Two-way feuds.** The Assassin/Hunter spawn based on ACS rep — but
   the Azure Cloud has no symmetric "righteous patrol" spawning at
   Crimson Creek for SL-friendly players. Pattern would be trivial
   now: new enemy `azure_cloud_patrol` at Crimson Creek with
   `requires_rep: {scarlet_lotus_pavilion: 3}`. Mirrors the mechanic
   and makes demonic progression feel dangerous too.
2. **Pavilion quest arc beyond the entry fee.** Rulan's quest gets you
   to +3 SL. Red Feather teaches at +1 and +2 and sells at +2. Past
   that, the sect has nothing more to say. A second quest from Elder
   Red Feather at SL ≥ 4 — "The Third Circle" (call in a debt on an
   Azure Cloud elder) — would give the SL path a middle act. Big
   reward: +4 SL, -4 ACS, unlock of a new higher-tier technique.
3. **Make the Crimson Registry matter.** It's on the ground, with
   lore, but picking it up has no consequence beyond the journal
   entry. Could trigger an event: the Pavilion notices, and Elder
   Red Feather's dialogue changes on your next visit. Would also
   give the treasure a *weight*.
4. **Guardian's drop rates are a little generous** — 25% mantle + 15%
   token on a gate-only boss. Because the Guardian only spawns when
   you're hostile to the Pavilion, and the mantle requires SL ≥ 2 to
   equip, a hostile player *cannot use* the mantle they looted. That's
   a nice thematic irony — keep it, but be aware.
5. **Scarlet Lotus Palm is still unlearnable** (the original
   technique) — `learn_cost: 0` but no NPC teaches it. I deliberately
   didn't change this session, since `blood_lotus_palm` fills the same
   functional niche. If someone later wants to de-dupe, delete
   scarlet_lotus_palm (it's the original orphan) or wire it onto Red
   Feather's teach list.

### Things I noticed but didn't fix
- **Rulan's `requires_rep_at_most` doesn't gracefully handle the moment
  she disappears.** Right now at SL +5 she simply isn't in `look`; no
  "she has gone" prose fires. A `retreat_text` field parallel to
  `ambush_text` would be the mirror — cheap engine add. Skipped for
  scope.
- **The Assassin / Hunter / Guardian all use the existing combat system**
  with no new verbs. The Hunter's contract-with-defaced-seal detail is
  in the description and nowhere else — a combat-opening line would be
  fun ("She unfolds the contract and reads your name aloud.") but needs
  an enemy-intro hook the engine doesn't have. Roadmap it as "enemy
  opening lines."
- **The Crimson Registry Fragment has `type: treasure`** but the engine
  doesn't treat treasure specially — it just sits in inventory forever.
  Same shape as the Sky-Qi Crystal. Fine for now; if treasures ever get
  their own `read` behavior, this item is the test case.
- **`blood_lotus_palm` uses `effect: heal`** to approximate life-steal.
  The heal fires on every cast — so even a missed palm (dodged) still
  heals the player. That's weird in theory but in practice it reads
  as "channeling the technique is what heals you, landing it is the
  damage." I kept it — it preserves the technique's flavor.
- **Rulan has `gives_quest: the_red_path`** which auto-offers on talk.
  At default rep she offers immediately — no SL-rep gate on the quest.
  That's intentional: she *wants* to recruit strangers. The -1 SL floor
  on the quest would add friction without adding meaning.
- **`requires_rep_at_most` permits **both** positive and negative values**
  and the validator accepts either. A negative ceiling would mean "this
  entity only appears if you're at enemy or below" — plausible but not
  used by any current content.
- **The Pond of Blood event** grants lore with 45% chance. A player
  might miss it on first visit. That's fine — it's flavor, not gating.
- **Five Poisons reaction**: completing The Red Path costs you -1 with
  the Five Poisons Sect. That's the triangle teaching from session 6:
  the demonic path costs you across factions, not just the righteous
  one. Matriarch Shan's +3 rep_dialogue will stop firing after.

### Don'ts (lessons learned)
- **Don't filter enemies in `look` but forget to filter them in
  `_find_in_loc`.** First draft had visible-in-look but also-findable
  when their rep gate wasn't met, which meant `fight scarlet_lotus_
  assassin` at default rep worked against thin air. Added the same
  `_rep_visible` filter inside `_find_in_loc` — one line fix, but an
  easy miss.
- **Don't use `requires_rep: {sect: 0}` thinking it's a no-op.** It's
  *technically* a floor at 0, which every default-rep player meets — so
  yes, effectively no-op. But any future negative-rep player (SL=-1) is
  suddenly hidden from the spawn. If you want "no gate," omit the
  field. I did use `requires_rep: {scarlet_lotus_pavilion: 0}` on
  `crimson_tide_fist` learn gate on purpose — to exclude players with
  active SL hostility from the entry-level demonic art. Noted the
  pattern here so future-me doesn't revert it by accident.
- **Don't forget to update `scarlet_lotus.json` sect file** when the
  sect gets an HQ. The signature_techniques list was also stale —
  `scarlet_lotus_palm` alone, no mention of the two new palm arts.
  Easy to miss; caught it on a second read of the sect file.
- **Don't read `loc.get("npcs")` directly in engine code now.** Going
  through `_visible_here` is the new rule. If a future code path
  iterates the raw list, it will show entities the rep gate has
  filtered out — a bug that will only manifest for players with
  non-default rep. Five call sites were updated this session:
  `cmd_look`, `_find_in_loc`, `cmd_learn`, `cmd_buy`,
  `_crafters_here`, and the in-location check inside `cmd_craft`.
  The *only* legitimate raw-list access that remains is inside
  `cmd_craft`'s "seek them at <loc>" helper — that iterates *every*
  location's npc list to find where a missing crafter fundamentally
  lives, which is rep-independent.

---

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
