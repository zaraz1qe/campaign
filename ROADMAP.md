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
- **Items**: 52 (equipment, pills, materials, treasures)
- **Recipes**: 15 (Forge-Master Bo: 6, Pillmaster Lu: 4, Apothecary Qi: 5)
- **Quests**: 8 (Kettle's Request, Study Sutra, Missing Disciple, Envoy's
  Letter, Oath of Fangs, Stormwarden's Test, Broken Terrace, Red Path)
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
- [ ] **Faction war state**: more than spawns — sect patrols that pursue
      between locations, trade embargoes, sect-tournament triggers
- [ ] **Auto-respawn enemies** so locations don't go empty after one fight
- [ ] **Multi-enemy combat** (1v many)
- [ ] **Companions**: a fellow cultivator who fights with you
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
