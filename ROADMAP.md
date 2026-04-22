# ROADMAP — Jade Wind Chronicles

A living checklist for what's been done and what to add next.
**Each session: pick something below, do it, update this file.**

---

## Current Content Inventory
(Auto-countable — run `python3 -c "from game import loader; print(loader.stats(loader.load_all()))"`.)

- **Locations**: Verdant Bamboo Sea, Old Hermit's Hut, River of Swords,
  Merchant's Crossing, Bandit Road, Azure Cloud Foothills, Outer Gate,
  Inner Courtyard, Library, Elder Baixu's Pavilion, Azure Cloud Forge,
  Thousand Venom Valley Mouth, Venom Gorge, Hall of Five Poisons,
  Poisoner's Garden, Cloudroot Pass, Hanging Terraces of Jadestep,
  Thunderhead Ridge, Skyweaver's Cloister, Cragspine Shrine, Spirit-Gale
  Plateau, Crimson Creek, Scarlet Lotus Hidden Shrine (23 total)
- **Regions**: Southern Wilds, Azure Cloud Range, Thousand Venom Valley,
  Sky-Spire Reach, Scarlet Lotus Reach
- **Sects**: Azure Cloud Sect (righteous), Scarlet Lotus Pavilion (demonic
  — now with HQ, elders, NPCs, techniques), Five Poisons Sect (neutral/grey),
  Jadestep Sect Remnant (dead-but-haunted)
- **Companions** (3): Disciple Meilin (Azure Cloud), Venom-Handler Bai
  (Five Poisons), Blood-Sworn Jin (Scarlet Lotus). Affinity/bond system
  active across all three.
- **Items**: 55 (equipment, pills, materials, treasures)
- **Recipes**: 15 (Forge-Master Bo: 6, Pillmaster Lu: 4, Apothecary Qi: 5)
- **Quests**: 9 (Kettle's Request, Study Sutra, Missing Disciple, Envoy's
  Letter, Oath of Fangs, Stormwarden's Test, Broken Terrace, Red Path,
  **Red Ledger** — the first multi-quest arc)
- **Realms**: 8 (Mortal → Ascendant Immortal)

## How to Add Content (the path of least resistance)
1. `python3 tools/check_content.py` to see current state and validate JSON.
2. Pick a folder under `content/` matching the kind of thing you're adding.
3. Drop in a new JSON file (or append objects to an existing one).
4. Re-run the validator. Re-run the game (`python play.py`) and `look`.
5. Update this file's "Done" log.

---

## Next Up — Big Buckets

### 1. New Regions to Build (each = ~6–10 locations)
- [ ] **Northern Frost Plains** — Frostfang Tribe, ice-cultivators, mammoth beasts
- [ ] **Eastern Sea of Cloud** — pirate sects, sword-sailors, sea-dragon
- [ ] **Western Demon Wastes** — heretical cultivators, blood-cultivation
- [ ] **Imperial Capital** — politics, the Emperor's Hidden Guard, court intrigue
- [x] **Sky-Spire Reach** — Foundation-tier foothills + Core boss (s4)
- [ ] **Sky-Spire True Peak** — higher than the Reach, the summit itself (Nascent Soul)
- [ ] **Underworld of Yellow Springs** — ghost-cultivators, judges of the dead
- [ ] **Hundred-Thousand-Mountains** — beast tide, ancient ruins
- [ ] **Sect Conference Grounds** — neutral meeting place for sect tournaments

### 2. New Sects to Add (5+ techniques each, 1+ HQ location, ~3 NPCs)
- [ ] Frozen Mirror Palace (orthodox, ice/water, righteous)
- [ ] Blood Moon Cult (demonic, body cultivation)
- [ ] Heavenly Sword Tower (orthodox, sword-only, militant)
- [x] Five Poisons Sect (neutral/grey, alchemy + venom)  **(s2)**
- [x] Scarlet Lotus Pavilion (demonic, physical presence) **(s7)**
- [ ] Wandering Cloud Pavilion (neutral, scholar-cultivators)
- [ ] Iron Buddha Temple (righteous, body + qi monks)
- [ ] Phantom Shadow Pavilion (assassins-for-hire, neutral)

### 3. Quests to Write
- [x] The Envoy's Letter — deliver a sealed letter from Azure Cloud to Five Poisons (s6)
- [x] **The Red Ledger** — Red Feather's second errand; recover a stolen page
      of the Crimson Registry from an apostate hiding at Jadestep (s10)
- [ ] Multi-part sect tournament (Azure Cloud vs Scarlet Lotus)
- [ ] Find the lost manual at the bottom of the River of Swords
- [ ] Investigate why frost wolves descended on the foothills (link to Blood Moon Cult)
- [ ] Escort Cloth Merchant Mei past the Bandit Road
- [ ] Brew the Nine-Cloud Pill (gather 5 ingredients)
- [ ] Settle the feud between two villages
- [ ] Avenge Old Hermit Yun's slain disciple (long arc)
- [ ] Climb the Sky-Spire (capstone, requires Nascent Soul)
- [x] The Stormwarden's Test — storm-crow feather from Thunderhead Ridge (s4)
- [x] The Broken Terrace — slay the Heart-Devouring Gale Tiger for Mingshu (s4)

### 4. Enemy Bestiary Expansion
- [ ] Spirit beasts at every realm tier (one per realm, scaling)
- [ ] Demonic cultivators (humanoid mid-tier)
- [ ] Ghosts (Yellow Springs region)
- [ ] Sea-tier: Crab King, Tide Serpent, Pirate Captain
- [ ] Ancient: Awakened Stone Beast, Heart-Devouring Vine, Sky Crane
- [ ] Boss: Sect Patriarch tier (named, unique drops)

### 5. Techniques (target: 50+ total)
- [ ] Saber arts (Blood Moon, Crimson Tide)
- [ ] Spear arts (Iron Buddha, Heavenly Sword)
- [ ] Body cultivation arts (Vajra Body, Mountain-Bearing Stance)
- [ ] Mental / illusion arts (Phantom Shadow)
- [ ] Healing arts (Frozen Mirror, Iron Buddha)
- [ ] Forbidden arts that hurt the player to use (high risk/reward)

### 6. Items / Pills / Treasures
- [ ] Tier 2 pills (each effect at +1 power tier)
- [ ] Spirit weapons (named blades with unique flavor)
- [ ] Materials for an alchemy/crafting system (deferred, see below)
- [ ] Treasure maps (lead to specific lore + treasure caches)
- [ ] Manuals: rare dropped manuals that unlock specific techniques

### 7. Lore / Worldbuilding
- [ ] One legend per region
- [ ] Sect founding stories
- [ ] Poems (one per sect)
- [ ] Sutras (4–5 of varying schools)
- [ ] Histories of major wars (the Sword Calamity, the Blood Moon Rising)

---

## Engine Improvements (only when content alone won't fix it)
- [x] **Alchemy crafting**: combine materials into pills at Pillmaster Lu (s5)
- [x] **Forging**: combine materials into spirit weapons at Forge-Master Bo (s5)
- [x] **Equipment slots**: weapon, robe, accessory — affect stats (s3)
- [x] **Reputation effects on dialogue**: NPCs respond differently (s6)
- [x] **Reputation gates on items / techniques / recipes / quest offers** (s6)
- [x] **Rep-triggered NPC/enemy spawns** — assassins appear after you anger
      a sect; guardians drop their welcome when you fall below zero (s7)
- [x] **Companions**: a fellow cultivator who fights with you — recruit,
      dismiss, split targeting, downed state, save/load (s8)
- [x] **Third companion (demonic)** — Blood-Sworn Jin, at Crimson Creek,
      gated by The Red Path + SL rep +3 + qi_condensation (s9)
- [x] **Companion affinity / loyalty system** — bond that grows with
      shared victories and quests; four tiers with stat bonuses; persists
      across dismiss/recruit (s9)
- [x] **Companion location barks** — one-line reactions when a companion
      walks into a place that matters to them (s9)
- [x] **NPC companion_reply** — NPCs acknowledge the specific companion
      at the player's shoulder during `talk`. Red Feather, Baixu, Shan,
      Rulan, Weilan, Huilin, and the Jadestep ghosts all speak to Jin,
      Meilin, or Bai when relevant (s10).
- [x] **requires_quest gate on quests** — quest arcs can chain. A second
      errand stays silent until the first is closed (s10).
- [ ] **Faction war state**: more than spawns — sect patrols that pursue
      between locations, trade embargoes, sect-tournament triggers
- [ ] **Auto-respawn enemies** so locations don't go empty after one fight
- [ ] **Multi-enemy combat** (1v many)
- [ ] **Time/day system**: some events require specific times
- [ ] **Random dungeon generation**: procedural caves with loot
- [ ] **Achievement/milestone system**: track major life events
- [ ] **Help text per command** (e.g., `help fight`)
- [ ] **Better tab completion** (unlikely needed for now)

---

## Bugs / Polish (refresh each session)
- [ ] After winning a one-shot fight, the enemy is still listed at the location
      next visit. Decide: respawn vs. one-shot. Currently respawns.
- [ ] If two NPCs in same location both teach the same technique, `learn`
      picks the first. Fine for now.
- [ ] No way to drop items.
- [ ] No way to give items to NPCs (would enable barter-style quests).

---

## Done Log (most recent first)
- **2026-04-22 (session 10)** — "The Red Ledger." First multi-quest arc,
  plus a new engine layer that makes companions *visible in dialogue*. New
  quest **The Red Ledger** from Elder Red Feather — a 4-step follow-up to
  The Red Path, gated by the prior quest + SL rep +3. Retrieves a stolen
  page of the Crimson Registry from an apostate (Willow-Step Shen, new
  enemy at Jadestep, rep-gated on SL +3 so he's invisible to non-Pavilion
  players). Shen is a qi-condensation cultivator with stolen Pavilion arts
  (crimson_tide_fist / blood_lotus_palm / pond_veil_step). Drops cipher
  page (100%), spirit-stone pouch, willow-step-ring, a cinnabar pill,
  blood-lotus petal. Quest rewards: +280 stones, +120 XP, new accessory
  **Pond-Drinker Sash** (+2 ATK, +1 DEF, +12 HP, bleed-on-hit, SL-rep-3
  gated), a cinnabar pill, and rep deltas (SL +3, ACS -2, Jadestep -1).
  Engine: `quest.requires_quest` gates a quest offer silently until the
  prior quest is closed — the first real "arc" support. Companion
  system: NPCs gain an optional **`companion_reply: {companion_id: line|[lines]}`**
  field; on `talk`, the matching companion's line prints after the
  NPC's main dialogue and rep_dialogue. Downed companions are silent.
  Wired lines for Red Feather (Jin / Meilin / Bai), Baixu (Jin /
  Meilin / Bai), Matriarch Shan (Bai / Meilin / Jin), Weilan, Rulan,
  Huilin, Mingshu's ghost, and the Old Dog of Jadestep — fifteen
  companion-reply entries across eight NPCs. New lore entry:
  **The Willow-Step Cut** — the twelve-year-old backstory of the stolen
  page, told in Red Feather's own voice. Validator: checks
  `companion_reply` shape (keys are real npcs; values are strings or
  lists of strings) and `quest.requires_quest` points at a real quest.
  SCHEMAS.md documents both new fields. Smoke test `tools/smoke_red_ledger.py`
  covers 7 scenarios: gate before prereq, offer after prereq, Shen
  invisible at low rep, full quest flow with reward verification,
  companion_reply fires only for bound companion, downed silences it,
  and Baixu↔Meilin wiring. Save-compat preserved — no new Player
  fields.
- **2026-04-22 (session 9)** — "The Blood-Sworn." Completes the
  companion triangle and adds a persistent bond layer on top. New
  companion **Blood-Sworn Jin** (Prodigal of the Red Path) at Crimson
  Creek, gated by the Red Path + SL rep +3 + qi_condensation. Sledge-
  hammer shape: HP 48, ATK 11, DEF 2, SPD 6, techniques crimson_tide_fist
  + blood_lotus_palm + heart_rending_claw (self-heal palm and stun claw).
  **Affinity system**: each NPC tracks a bond score in a new
  `Player.companion_affinity` map; +1 per shared combat win (if still
  standing), +2 per quest completion while active. Four tiers (bonded /
  trusted / steadfast / soul-sworn) with flat stat bonuses applied at
  fight start (up to +2 ATK, +1 DEF, +1 SPD). Bond persists across
  dismiss/recruit. Tier crossings print a prose beat; `companion`
  / `status` surface the current bond. **Location barks**: optional
  `companion.location_barks: {loc_id: line}` fires once per arrival under
  `look`. Shipped barks for Meilin (5 sites — hostile-sect locations),
  Bai (5 sites), Jin (6 sites — his former sect + the Pavilion). New
  rep_dialogue on Jin for ACS ±3 and SL +5. Validator checks bark
  locations + strings. Smoke test `tools/smoke_affinity.py` covers the
  gate, tier math, persistence across dismiss, bark once-per-arrival,
  and save/load round-trip. Save-compat: `companion_affinity` backfills
  to `{}`, `last_bark_loc` defaults to None.
- **2026-04-22 (session 8)** — "The Sworn Oath." End-to-end companion
  system. A recruitable NPC can walk at the player's side: combat gains
  an ally turn after the player, the enemy splits fire (~35% at the
  companion), status effects apply to whoever was targeted, and a
  companion reduced to 0 HP is *downed* (out of the fight, not dead).
  `cultivate` revives downed companions to full HP. After any
  non-defeat, the companion heals fully — no grinding. New commands:
  `recruit <npc>`, `dismiss`, `companion` / `party`. `status` shows
  a companion summary. Save/load round-trips via a new
  `Player.companion` field (old saves default to None). Two
  companions shipped: **Disciple Meilin** (Azure Cloud, at Inner
  Courtyard — gated by Qi Condensation + ACS +2 + Study the Sutra;
  HP 58, sword + palm + heal) and **Venom-Handler Bai** (Five
  Poisons, new NPC at Poisoner's Garden — gated by Oath of Fangs +
  FPS +2; HP 50, venom + stance, glass-cannon shape). Validator
  checks the new `companion` content block; SCHEMAS.md grew an NPC
  section and a Companions system section. Smoke tests in `tools/`
  (`smoke_companion.py` + `smoke_companion_downed.py`) cover the
  gate logic, combat flow, downed path, and save-compat across
  multiple seeds.
- **2026-04-22 (session 7)** — "The Red Path." The Scarlet Lotus Pavilion
  finally walks the earth. New region (Scarlet Lotus Reach) with two
  locations (Crimson Creek, Scarlet Lotus Hidden Shrine), three NPCs
  (Rulan the Thin-Smiling, Elder Red Feather, Apothecary Weilan), four
  enemies (Scarlet Lotus Assassin, Scarlet Lotus Hunter, Blood-Sworn
  Wretch, Scarlet Pavilion Guardian — boss), five techniques (Blood
  Lotus Palm, Crimson Tide Fist, Heart-Rending Claw + 2 enemy-only),
  five items (blood lotus petal, crimson cinnabar pill, scarlet pavilion
  token, blood-petal mantle, crimson registry fragment), one quest
  (The Red Path — tribute of venoms), two lore entries, two events.
  Engine: rep-triggered spawning. NPCs and enemies now support
  `requires_rep` (floor) and `requires_rep_at_most` (ceiling) — they
  appear/disappear based on the player's sect standing. Enemies can
  carry `ambush_text`, an atmospheric sub-line shown under them in
  `look`. Assassins spawn at Bandit Road once ACS rep ≥ 3, hunters at
  Merchant's Crossing at ACS rep ≥ 5, guardians at the shrine at SL
  rep ≤ -1, Rulan retreats above SL rep > 4. Elder Baixu now also has
  a Scarlet-Lotus-rep warning line. Validator covers the new fields.
  SCHEMAS.md updated. Save-compat preserved (no new Player fields).
- **2026-04-22 (session 6)** — "The Weighing Scales." End-to-end reputation
  system. Every sect is now a live rep bucket (`Player.reputation`, already
  present, finally used). Ranks: reviled / enemy / distrusted / stranger /
  known / respected / honoured / sect-honoured. New `rep` / `reputation` /
  `standing` command; rep rank shown in `status`. Quest completion applies
  `rep_change: {sect_id: delta}` with a prose beat on rank crossings
  ("risen from stranger to known"). `requires_rep: {sect_id: min}` gates
  honored on quests (auto-offer suppressed), items (buy + equip),
  techniques (learn), and recipes (craft). NPCs can carry
  `rep_dialogue: {sect_id: {threshold: [lines]}}` that branches on
  player standing (positive and negative thresholds both work). Retrofit:
  6 existing quests got thoughtful rep deltas; Azure Cloud Sword now
  requires ACS +2 to buy; Azure Cloud Palm requires ACS +1 to learn;
  Skybreaker Blade forge requires ACS +2. New content: quest "The
  Envoy's Letter" (Envoy Ruwen at Merchant's Crossing carries a letter
  to Matriarch Shan — +2 ACS, +1 Five Poisons, -2 Scarlet Lotus), new
  accessory Azure Cloud Sect Token (+1 DEF, +6 HP, +1 SPD). New
  rep_dialogue on Elder Baixu, Matriarch Shan, Gatekeeper Wuwei,
  Stormwarden Gao. Validator checks rep fields. Save-compat preserved
  (no new Player fields; `reputation` was there since session 1).
- **2026-04-22 (session 5)** — "The Forge and the Cauldron." End-to-end
  crafting system: a new `recipes` content category, `craft` /
  `forge` / `brew` / `recipes` commands, NPC `talk` screens advertise
  their recipes, crafters gated by location + realm + materials +
  spirit stones. Shipped 15 recipes across three crafters: Pillmaster
  Lu (4 brews), Apothecary Qi (5 brews + venom-forges), and a new
  Forge-Master Bo (6 weapon/robe/accessory forges) at a new location
  Azure Cloud Forge (off Inner Courtyard). Two new craft-only items:
  Heart-Devouring Robe (+6 DEF, +20 HP, +1 SPD, Foundation-gated —
  the sky-spire capstone) and Cloudstep Charm (+2 ATK, +1 SPD, +5 HP).
  Validator gained a recipes section. SCHEMAS.md documents the
  recipe shape. Save compat preserved (no new Player fields).
- **2026-04-22 (session 4)** — "The Sky-Spire Reach." A Foundation-tier
  region to give the realm ladder somewhere to go. Six locations:
  Cloudroot Pass (gated by Stormwarden Gao), Hanging Terraces of Jadestep
  (ruined sect, haunted by Patriarch Mingshu's ghost), Thunderhead Ridge
  (lightning + rival-sect disciples), Skyweaver's Cloister (the last
  living Jadestep teacher, the Old Dog), Cragspine Shrine (a qi-9
  cultivation spot with a Sky-Qi Crystal on the altar), and Spirit-Gale
  Plateau (the boss arena). 5 new enemies including the Core-Formation
  Heart-Devouring Gale Tiger boss. 3 NPCs. 5 techniques — including the
  heaven-rank Thundering Palm of the Nine Heavens (damage 24, stun 2).
  13 new items: Skybreaker Blade (9 ATK, on-hit stun, Foundation-gated),
  Stormcloud Sash, Broken Terrace Medallion, Storm-Warded Talisman,
  Thundergold Pill (80 qi), Ironbark Pill (def_buff — new pill effect),
  Sky-Qi Crystal (120 qi), Cloudroot Spirit Stone, Storm-Crow Feather,
  Ape Knucklebone, Jadestep Shard, Gale Tiger Fang, Heart-Devouring Hide.
  2 quests (Stormwarden's Test, Broken Terrace — big rewards, sect-worthy).
  1 sect stub (Jadestep Remnant). 4 lore entries, 4 events.
  Engine: added `def_buff` pill effect (symmetric with `atk_buff`).
  Connected: north from Azure Cloud Foothills.
- **2026-04-22 (session 3)** — "The First Blade." Equipment system end-to-end:
  three slots (weapon / robe / accessory), `equip` / `unequip` / `gear` commands,
  status screen shows base+gear breakdown, prompt HP bar reflects gear HP.
  Weapons can carry an `on_hit_effect` (poison/bleed/stun) that fires on normal
  attacks. 13 new gear items with 2 tiers of robes, 5 weapons (including two
  rare spirit-weapon drops), and 4 accessories. Existing `rusty_dao` and
  `traveler_robe` upgraded to real equipment. Validator now checks slot values,
  on_hit effect name, bonus integer types, and realm requirement. Saves from
  session 2 back-fill an empty equipped dict.
- **2026-04-22 (session 2)** — "Venom in the Veins." Wired up status effects
  end-to-end in combat (poison, bleed, buff_atk, buff_def, and a new
  `cleanse` pill effect); added critical hits and SPD-based dodge; put
  HP/Qi in the persistent REPL prompt. Shipped the Five Poisons Sect as a
  neutral/grey faction to showcase the new mechanics: Thousand Venom Valley
  region (4 locations), 3 NPCs, 6 new techniques, 2 enemies, 5 items, 1
  quest ("Oath of Fangs"), 2 lore entries, 3 events. Connected the valley
  east of Bandit Road; Pillmaster Lu now stocks Antidote Pearl too.
  SCHEMAS.md updated to document the effect semantics.
- **2026-04-21 (session 1)** — Initial commit. Built engine, seeded
  Southern Wilds + Azure Cloud Range starter regions, 2 sects, 3 quests,
  9 techniques, 13 items, 5 enemies, 8 realms, 7 events, 5 lore. Smoke-tested
  navigation, combat, cultivation, save/load.
