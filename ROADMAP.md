# ROADMAP — Jade Wind Chronicles

A living checklist for what's been done and what to add next.
**Each session: pick something below, do it, update this file.**

---

## Current Content Inventory
(Auto-countable — run `python3 -c "from game import loader; print(loader.stats(loader.load_all()))"`.)

- **Locations**: Verdant Bamboo Sea, Old Hermit's Hut, River of Swords,
  Merchant's Crossing, Bandit Road, Azure Cloud Foothills, Outer Gate,
  Inner Courtyard, Library, Elder Baixu's Pavilion (10 total)
- **Regions**: Southern Wilds, Azure Cloud Range
- **Sects**: Azure Cloud Sect (righteous), Scarlet Lotus Pavilion (demonic)
- **Quests**: 3 starter quests
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
- [ ] **Sky-Spire** — late-game vertical dungeon, Heaven Tribulation arena
- [ ] **Underworld of Yellow Springs** — ghost-cultivators, judges of the dead
- [ ] **Hundred-Thousand-Mountains** — beast tide, ancient ruins
- [ ] **Sect Conference Grounds** — neutral meeting place for sect tournaments

### 2. New Sects to Add (5+ techniques each, 1+ HQ location, ~3 NPCs)
- [ ] Frozen Mirror Palace (orthodox, ice/water, righteous)
- [ ] Blood Moon Cult (demonic, body cultivation)
- [ ] Heavenly Sword Tower (orthodox, sword-only, militant)
- [ ] Five Poisons Sect (neutral/grey, alchemy + venom)
- [ ] Wandering Cloud Pavilion (neutral, scholar-cultivators)
- [ ] Iron Buddha Temple (righteous, body + qi monks)
- [ ] Phantom Shadow Pavilion (assassins-for-hire, neutral)

### 3. Quests to Write
- [ ] Multi-part sect tournament (Azure Cloud vs Scarlet Lotus)
- [ ] Find the lost manual at the bottom of the River of Swords
- [ ] Investigate why frost wolves descended on the foothills (link to Blood Moon Cult)
- [ ] Escort Cloth Merchant Mei past the Bandit Road
- [ ] Brew the Nine-Cloud Pill (gather 5 ingredients)
- [ ] Settle the feud between two villages
- [ ] Avenge Old Hermit Yun's slain disciple (long arc)
- [ ] Climb the Sky-Spire (capstone, requires Nascent Soul)

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
- [ ] **Alchemy crafting**: combine materials into pills at Pillmaster Lu
- [ ] **Forging**: combine materials into spirit weapons; equip slot
- [ ] **Equipment slots**: weapon, robe, accessory — affect stats
- [ ] **Reputation effects on dialogue**: NPCs respond differently
- [ ] **Faction war state**: world events triggered by player progression
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
- **2026-04-21 (session 1)** — Initial commit. Built engine, seeded
  Southern Wilds + Azure Cloud Range starter regions, 2 sects, 3 quests,
  9 techniques, 13 items, 5 enemies, 8 realms, 7 events, 5 lore. Smoke-tested
  navigation, combat, cultivation, save/load.
