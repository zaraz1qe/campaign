# ROADMAP — Jade Wind Chronicles

A living checklist for what's been done and what to add next.
**Each session: pick something below, do it, update this file.**

---

## Current Content Inventory
(Auto-countable — run `python3 -c "from game import loader; print(loader.stats(loader.load_all()))"`.)

- **Locations**: 29 total. Southern Wilds (9: Verdant Bamboo Sea, Old
  Hermit's Hut, River of Swords, Merchant's Crossing, Bandit Road, and
  the new Willowmere hub — Village Square, Willow-and-Moon Teahouse,
  Willowmere Smithy, Shen Homestead, Pale Lake Shore, Drowned Willow
  Shrine), Azure Cloud Range (5: Foothills, Outer Gate, Inner Courtyard,
  Library, Elder's Pavilion, Forge), Thousand Venom Valley (4), Sky-Spire
  Reach (6), Scarlet Lotus Reach (2).
- **Regions**: Southern Wilds (now properly populated with a village
  hub — session 12), Azure Cloud Range, Thousand Venom Valley, Sky-Spire
  Reach, Scarlet Lotus Reach
- **Sects**: Azure Cloud Sect (righteous), Scarlet Lotus Pavilion (demonic
  — now with HQ, elders, NPCs, techniques), Five Poisons Sect (neutral/grey),
  Jadestep Sect Remnant (dead-but-haunted)
- **Companions** (3): Disciple Meilin (Azure Cloud), Venom-Handler Bai
  (Five Poisons), Blood-Sworn Jin (Scarlet Lotus). Affinity/bond system
  active across all three.
- **Items**: 88 (equipment, pills, materials, treasures, **manuals**,
  Silent Bell Charm, Moon-Red Pill, Sister-Spoon)
- **Recipes**: 15 (Forge-Master Bo: 6, Pillmaster Lu: 4, Apothecary Qi: 5)
- **Quests**: 22. Single-givers: Kettle's Request, Missing Disciple,
  Envoy's Letter, Oath of Fangs, Stormwarden's Test, Broken Terrace,
  Red Path, and the five Willowmere starters (Wolves at Shen's Farm,
  Little Yu's Songbird, Three Ingots of River-Iron, Errand of the
  Drowned Willow, A Bottle for the Corner Table). **Multi-quest arcs**:
  Red Ledger (Rulan → Red Feather), **Zhao's Library arc**
  (Study the Sutra → The Locked Shelves → The Committee of 1184 —
  session 13), **Huilin's Silent Bell arc** (The Bell Beneath the
  Willow → A Bowl on the Broken Bridge → The Name the Wind Would
  Not Give — session 14), **Weilan's Bitter Remedy arc** (A Cup
  of Sleeping Water → The Bud That Will Not Open → The Pestle My
  Sister Used Last — session 15). Four of the game's mid-game NPCs
  now own a proper three-quest spine. Scarlet Lotus is now the
  best-quested sect in the game after the Willowmere hub.
- **Techniques**: 43 total, **35 learnable** across all tiers. Every
  combat effect (poison/bleed/stun/heal/buff_def/buff_atk) has ≥3
  learnable options. Mortal 9 / Qi-Condensation 15 / Foundation 11.
- **Events**: 45 (ambient + qi-grant + lore-grant; every location has
  at least one. Session 15 additions: pale_lake_silt_stirs at the
  lake, sealed_bud_under_the_bell at Crimson Creek,
  weilan_hums_at_the_pestle at the Scarlet Lotus Shrine).
- **Lore**: 37 (earnable via boss defeats, quest rewards, high-rep NPC
  trust, village story, and **manuals**). Session-15 additions:
  the_pond_that_sleeps, the_red_that_does_not_clot, the_pestle_unbroken,
  the_sisters_unspoken_cure. Session-14 additions:
  the_bell_that_came_too_late, the_broken_bridge_tea,
  the_wind_that_named_itself. Session-13 additions:
  committee_of_1184, azure_cloud_commentary_1184, lamplighter_of_zhao,
  gatekeepers_oath, sword_calamity, west_reading_room.
- **Manuals**: 7 (library-only: open shelf 2, mid 3, locked 2 — gated
  by ACS rep, priced against the labour of copying, not the weight
  of the words).
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
- [x] **Willowmere** — mortal-tier village hub west of Verdant Bamboo (s12)
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
- [x] **The Locked Shelves** — Zhao's first follow-up; retrieve a torn
      catalogue page from Bannerman Shao on the Bandit Road (s13)
- [x] **The Committee of 1184** — Zhao's second follow-up; recover Sister
      Willow's Record from the Hanging Terraces of Jadestep (s13)
- [ ] Multi-part sect tournament (Azure Cloud vs Scarlet Lotus)
- [ ] Find the lost manual at the bottom of the River of Swords
- [ ] Investigate why frost wolves descended on the foothills (link to Blood Moon Cult)
- [ ] Escort Cloth Merchant Mei past the Bandit Road  — partially paid off
      by s13 (Bandit Road now has its own quest giver via Zhao's arc;
      an escort for Mei would still be worth writing)
- [ ] Brew the Nine-Cloud Pill (gather 5 ingredients)
- [ ] Settle the feud between two villages
- [ ] Avenge Old Hermit Yun's slain disciple (long arc)
- [ ] Climb the Sky-Spire (capstone, requires Nascent Soul)
- [x] **Huilin's errand** — paid off s14 as a 3-quest arc (The Bell
      Beneath the Willow → A Bowl on the Broken Bridge → The Name the
      Wind Would Not Give). Reward: Silent Bell Charm (HP+12, SPD+1,
      DEF+1), 3 new lore entries, ACS rep +2 across the arc. The Drowned
      Willow Shrine, Elder Baixu's Pavilion, and the Cragspine Shrine
      all picked up new events + items-on-ground as part of the arc.
- [ ] **A second Baixu errand** — post-*the_missing_disciple*;
      close the loop with the rival envoy who held Meilin.
- [x] The Stormwarden's Test — storm-crow feather from Thunderhead Ridge (s4)
- [x] The Broken Terrace — slay the Heart-Devouring Gale Tiger for Mingshu (s4)

### 4. Enemy Bestiary Expansion
- [ ] Spirit beasts at every realm tier (one per realm, scaling)
- [ ] Demonic cultivators (humanoid mid-tier)
- [ ] Ghosts (Yellow Springs region)
- [ ] Sea-tier: Crab King, Tide Serpent, Pirate Captain
- [ ] Ancient: Awakened Stone Beast, Heart-Devouring Vine, Sky Crane
- [ ] Boss: Sect Patriarch tier (named, unique drops)

### 5. Techniques (target: 50+ total; now at 43, with 35 learnable)
- [x] **Session 12 deepening pass** — 15 new learnable techniques: 4 mortal,
      6 qi-condensation, 5 foundation. Closed the buff_atk gap (was zero,
      now four — iron_ox_shrug, azure_cloud_sword_arc, nine_cloud_cranes_flight,
      stormwarden_mantle). Tripled bleed options. Every effect (poison/bleed/
      stun/heal/buff_def/buff_atk) has ≥3 learnable techniques now.
- [ ] Saber arts (Blood Moon, Crimson Tide)
- [ ] Spear arts (Iron Buddha, Heavenly Sword)
- [~] Body cultivation arts (iron_ox_shrug, mountain_root_stance shipped;
      Vajra / Mountain-Bearing remain open)
- [ ] Mental / illusion arts (Phantom Shadow)
- [~] Healing arts (calming_breath, settling_stone_sit, blood_lotus_palm,
      heart_boiling_technique, brass_bell_sutra — five options now spanning
      mortal → foundation; Frozen Mirror / Iron Buddha remain open)
- [ ] Forbidden arts that hurt the player to use (high risk/reward)

### 6. Items / Pills / Treasures
- [ ] Tier 2 pills (each effect at +1 power tier)
- [ ] Spirit weapons (named blades with unique flavor)
- [ ] Materials for an alchemy/crafting system (deferred, see below)
- [ ] Treasure maps (lead to specific lore + treasure caches)
- [~] **Manuals**: library manuals now real items that `read` can open —
      grant lore and/or teach techniques with realm+rep gates; Zhao's
      shelf has 7 (s13). Open: *dropped* manuals (rare drops from named
      foes that unlock specific techniques outside any library).

### 7. Lore / Worldbuilding
- [ ] One legend per region (per-location `lore` hook, first-visit grant)
- [~] Sect founding stories (Azure Cloud, Scarlet Lotus, Five Poisons —
      all have at least one founder story; Jadestep has two. Need: more
      of the minor regions' legends.)
- [ ] Poems (one per sect)
- [~] Sutras (have: Empty Sleeves/Word in Dust, Oath of the Grey, Scarlet
      Lotus Oath, Five Refusals, Four Reasons, Stormwarden, Gatekeeper's
      Oath, Azure Cloud Commentary 1184. Missing: a righteous-orthodox
      sutra beyond Azure Cloud / Shaolin-flavor.)
- [~] Histories of major wars (the Sword Calamity abridged shipped s13;
      Blood Moon Rising still open).

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
- [x] **Lore as earned reward** — on_defeat_lore on enemies, grants_lore
      on quests, lore_dialogue on NPCs; the `read` command is now a
      proper library index grouped by category with a known/total
      counter (s11).
- [x] **Manuals as readable items** — `read <manual>` prints the manual's
      passage, grants `grants_lore`, and teaches `teaches_technique`
      with realm+rep gates; the manual stays in inventory (s13).
- [x] **Multi-quest givers** — `gives_quest` accepts a list so one NPC
      can own a whole arc; `offer_quest` silent on gated / completed /
      accepted entries (s13).
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
- **2026-04-23 (session 15)** — "The Bitter Remedy" — Weilan's
  three-quest arc. Session 12, 13 AND 14 all flagged Apothecary
  Weilan as the next obvious deepening target: she had voice, a
  teach, three sells, two companion_reply lines — and no
  rep_dialogue, no lore_dialogue, no quest. Sect-wise, Scarlet
  Lotus was the most quest-starved of the four sects (2 quests vs
  Azure Cloud's 6). This session closed both gaps at once. Three
  connected quests giving Weilan a spine and giving Scarlet Lotus
  a second full arc:
  - **A Cup of Sleeping Water** (mortal-tier, no gate). Weilan
    needs silt from Pale Lake Shore for the Pavilion's
    Sleeping-Water pill. Player walks south, picks up the cup,
    returns. Reward: 80 stones, minor_healing_pill + antidote_pearl,
    Scarlet Lotus +1, the_pond_that_sleeps lore (what the
    Sleeping-Water pill actually does, and for whom).
  - **The Bud That Will Not Open** (QC-tier, prereq only). An
    apothecaries' secret: in every creek of blood-lotus, one bud
    refuses to open — "the red that does not clot," a thing that
    will stop the worst bleeding in a body that has already
    stopped fighting. One such bud sits under the tongueless bell
    at Crimson Creek. Reward: 200 stones, Moon-Red Pill (new
    heal, power 70) + crimson_cinnabar_pill, Scarlet Lotus +1,
    the_red_that_does_not_clot lore.
  - **The Pestle My Sister Used Last** (Foundation-ready,
    Scarlet Lotus +3 gate). Weilan's sister Weiyan was an Azure
    Cloud physician. She died at the last Crane-Lotus clash. He
    has her iron pestle with the last residue she ever ground
    still in the bowl, and he cannot read what it was. Only
    Baixu's hand could. Player carries the pestle to Baixu's
    Pavilion; Baixu identifies the residue (a cure for the
    Pavilion's Heart-Boiling Technique, a thing that crossed
    sect lines the way a good physician's hand should). Reward:
    360 stones, sisters_iron_spoon accessory (HP+14, DEF+2,
    SPD+1, with an Azure Cloud physician's knot on a
    Pavilion-plain hemp cord), Scarlet Lotus +1 AND **Azure
    Cloud +2** — the arc's emotional hinge is a cross-sect rep
    bump earned by honoring a dead physician across faction
    lines. Two new lore entries: the_pestle_unbroken,
    the_sisters_unspoken_cure.
  Content: 4 new items (pale_lake_silt and sealed_blood_lotus
  as quest materials on-ground at Pale Lake / Crimson Creek;
  moon_red_pill as a strong heal reward; sisters_iron_spoon
  as the capstone accessory), 4 new lore entries, 3 new quests,
  3 new events (pale_lake_silt_stirs at the lake,
  sealed_bud_under_the_bell at the creek, weilan_hums_at_the_pestle
  at the shrine). Weilan's NPC expanded from 3 to 6 dialogue lines
  (about the pond, about poison-vs-cure, about a sister who did
  not leave their southern village with him), gained rep_dialogue
  tiers at SLP +2/+3/+5 and -2, a new cross-sect line at ACS +3,
  lore_dialogue at SLP +4, and one new companion_reply for
  venomhand_bai. Teaches expanded from 1 to 3 (added
  calming_breath and settling_stone_sit — heals an apothecary
  should of course know), sells expanded from 3 to 5 (added
  minor_healing_pill and moonflower_tonic — so a mortal player
  walking into the shrine now has something to buy). Weilan's
  gives_quest became a list of three — he joins Huilin and Zhao
  as the third multi-quest giver in the game. Baixu got one new
  standing dialogue line about "the physician we could not bring
  home, whose pestle went to a brother she had not seen in a
  lifetime" — ambient before the arc, fulfilment during/after.
  New smoke test `tools/smoke_weilan.py` — 7 scenarios covering
  content-load, list-gives, items-on-ground placement, the full
  arc with SLP+3 gate and cross-sect ACS +2 payoff,
  accessory-equip, and save/load. All green. All 9 prior smoke
  tests remain green.

- **2026-04-23 (session 14)** — "The Silent Bell's Return" — Huilin's
  quest. Huilin had voice, teaches, sells, rep_dialogue for three
  sects, and companion_reply for all three companions — but no
  gives_quest. Session 13's handoff flagged him as the most
  under-used voiced NPC in the game. Built him a proper three-quest
  arc that threads from Willowmere (mortal-tier) through Azure Cloud
  (QC-tier) to the Sky-Spire Reach (Foundation-tier), paying off
  three lines of his existing dialogue:
  - **The Bell Beneath the Willow.** Huilin's title is "Brother of
    the Silent Bell." The bell is silent because it cracked at the
    wedding-that-became-a-drowning at what is now the Drowned Willow
    Shrine. Huilin's master Brother Mo gave it back to the water that
    night. The cracked bell now sits as `items_on_ground` at the
    shrine. Reward: minor pills + the_bell_that_came_too_late lore.
  - **A Bowl on the Broken Bridge.** Huilin's existing dialogue
    says Baixu owes him a bowl of tea from a meeting on the Broken
    Bridge fifty years ago. The player carries a folded paper (a
    flavor item, not mechanically swapped) to Baixu, returns to
    Huilin. Reward: willowmere_cordial + ACS +1 + the_broken_bridge_tea
    lore. Baixu's pavilion description now mentions the tea-bowl on
    his west sill, and a new event rings it once without a hand.
  - **The Name the Wind Would Not Give.** Huilin said his master
    climbed the Heaven-Reaching Spire to ask the wind a name — the
    wind would not give it, and his master did not come down. Player
    climbs to the Cragspine Shrine (gated ACS +2) and retrieves the
    wind-named stone from the altar's wind-scoured depression.
    Reward: the Silent Bell Charm accessory (HP+12, SPD+1, DEF+1),
    spirit-stone pouch, ACS +1, the_wind_that_named_itself lore.
  Content: 4 new items (cracked_brass_bell quest item,
  folded_tea_invitation flavor item, wind_named_stone quest item,
  silent_bell_charm accessory reward). 3 new lore entries. 3 new
  quests. 4 new events (shrine_bell_surface_breathes,
  pavilion_monks_bowl, plateau_wind_holds_its_breath,
  cragspine_stone_warms). Huilin's NPC description and dialogue
  expanded — +2 dialogue lines (about his master, about the bowl
  Baixu keeps) and +1 line for Baixu (tying the pavilion's tea-bowl
  to "the old brother"). Baixu's pavilion description itself
  expanded to mention the bowl on the west sill. Huilin's
  gives_quest became a list of three — the second NPC in the game
  (after Zhao) to own a full three-quest arc. New smoke test
  `tools/smoke_huilin.py` — 7 scenarios covering content-load,
  list-gives, items-on-ground placement, the full arc with
  rep-gated quest 3, charm-equip, and save/load. All green. All
  8 prior smoke tests remain green.

- **2026-04-23 (session 13)** — "The Committee of 1184" — the Azure
  Cloud Library deepening. The session's complaint: the library had
  been a textbook example of surface-but-no-depth — a full location,
  a voiced librarian, and a single consumable scroll. Zhao had already
  scaffolded the deepening in his own dialogue (locked shelves, the
  committee of 1184 that died in 1184, things the library "finds" for
  refused guests) but none of it was paid off mechanically. This
  session pays it off. One small engine change makes `read <manual>`
  do the work the `manual` item type had only been tagging for; one
  other makes `gives_quest` a list so one NPC owns a whole arc.
  Content: 7 manuals (each with its own passage and lore), 6 new
  lore entries (Committee of 1184, the Sutra marginalia, the
  Lamplighter of Zhao, the Sword Calamity abridgment, the Gatekeeper's
  Oath, the West Reading-Room), 3-quest Zhao arc (Study the Sutra →
  The Locked Shelves → The Committee of 1184) that finally uses the
  dead Bandit Road (Bannerman Shao, new mini-boss) and sends the
  player back up to the Hanging Terraces for Sister Willow's Record.
  5 new events (library brass bell, catalogue writing itself, locked
  shelf peg humming, foothills disciple passing, bandit road's distant
  banner). Azure Cloud went from 2 single-errand quests to a 4-quest
  region anchored on one NPC's arc; Bandit Road went from 0 quests to
  1; the Hanging Terraces picked up a second use. Smoke test
  `tools/smoke_library.py` — 9 scenarios — green. All 7 prior smoke
  tests remain green.

- **2026-04-23 (session 12)** — "The Willow at the Gate" **+ technique
  deepening pass**. Two things in one session, both pulling on the same
  thread: *stop being a puddle in the early game*. First, the starter
  hub the game had never had — **Willowmere** — a village west of
  Verdant Bamboo Sea. Second, a combat-roster deepening pass: **15 new
  learnable techniques** filling the gaps an audit exposed (zero buff_atk
  techniques prior to this session; one bleed; thin mortal tier).

  **Technique deepening.** New `content/techniques/depth.json` ships 15
  techniques across all three playable realms. Mortal tier (4): Silent
  Bell Strike (Huilin, 0 qi pure strike), Settling-Stone Sit (Yun, cheap
  self-heal meditation), Viper-Sting Jab (Wuwei, the mortal-tier Five
  Poisons intro), Iron-Ox Shrug (Bo, the first buff_atk in the game).
  Qi Condensation (6): Azure Cloud Sword-Arc (Meilin, buff_atk sword),
  Crane-Wing Parry (Baixu, defensive sword), Flashing Willow-Leaf
  (Meilin, bleed sword that Baixu disapproves of), Black-Lattice Palm
  (Apothecary Qi, poisonless-but-bleeds palm), Mountain-Root Stance
  (Bo, heavy buff_def), Crimson Hand of Silence (Red Feather, stun
  palm). Foundation (5): Nine-Cloud Cranes' Flight (Baixu, ACS-4
  sword capstone with buff_atk 3), Five-Venoms Brocade Palm (Shan,
  FPS-4 poison capstone at power 7), Heart-Boiling Technique (Red
  Feather, SL-3 foundation-tier life-steal), Stormwarden's Mantle
  (Gao, ACS-3 pure buff_atk 3), Brass-Bell Sutra (Huilin, monastic
  high-tier heal). Roster goes from 20 → 35 learnable (75% increase).
  Every combat effect now has ≥3 learnable options. buff_atk went from
  0 → 4. Mortal tier went from 5 → 9. Foundation tier from 6 → 11.
  New smoke test `tools/smoke_techniques.py` — 7 scenarios covering
  loads, teacher wiring, ungated mortal learns, rep-gate refusal,
  realm-gate refusal, palette coverage, and per-tier buff_atk
  availability. All green.

  **NPC dialogue depth.** Expanded thin dialogue on four characters
  (Gatekeeper Chen — now with nerves, a crane stitched above his
  heart, and rep_dialogue for both directions; Librarian Zhao — a
  west reading-room, a committee from 1184, the locked shelves that
  check names; Raftsman Qiu — his son, the lost sword, the box with
  nine carved fish, rep_dialogue for ACS and SL; Cloth Merchant Mei
  — rep_dialogue across three sects for three different kinds of
  quiet handling). Added rep_dialogue to Wandering Monk Huilin for
  Azure / Scarlet / Five Poisons — the monk finally reacts to the
  player's sect standing. Expanded Forge-Master Bo and Gatekeeper
  Wuwei with extra dialogue lines to match their new teaching roles.

  **Event depth.** `content/events/depth.json` ships 9 new ambient
  events filling locations that had zero: Old Hermit's Hut (the
  kettle watches the water), Azure Cloud Outer Gate (the courtesy
  bell tolls), Azure Cloud Inner Courtyard (eight basic cuts
  drilling), Azure Cloud Forge (sparks write and un-write), Elder
  Baixu's Pavilion (wind-chimes change key), Hall of Five Poisons
  (incense shifts colour; a scorpion walks), Skyweaver's Cloister
  (the tenth scar hums), Spirit-Gale Plateau (four yellow eyes open
  and close), Willowmere Smithy (Ao's three-quick-one-slow forge-
  prayer). Every location in the game now has ≥1 event.

  **Willowmere (the starter hub).** A new village — Willowmere
  — hangs west of Verdant Bamboo Sea as six locations (Village Square,
  Willow-and-Moon Teahouse, Willowmere Smithy, Shen Homestead, Pale Lake
  Shore, Drowned Willow Shrine). Eight new NPCs (Headman Lu Pingan — an
  azure disciple who failed breakthrough and stayed; Herbalist Mingzhu;
  Little Yu with her escaped songbird; Tea-Mother Weiyu of the ledger in
  two colours of ink; Old Kuo the half-drunk in the corner, one-time
  master of Drunken Step; Blacksmith Ao and the river-iron trade; Farmer
  Shen Daiyu and her broom with the nail crosswise; Fisher Ren, who
  teaches the willow-root stance and will not quite fish). Five mortal-
  tier quests tuned for the earliest realms: The Wolves at Shen's Farm
  (auto-accepted from Pingan; clear the pack, slay the alpha with the
  pale blaze, return; +1 ACS rep, iron cleaver reward); Little Yu's
  Songbird (fetch Lady Moonbell from the hermit's hut — she escaped
  toward the kettle); Three Ingots of River-Iron (harvest from the carp
  spirits of Pale Lake, return to Ao for the River Blade reward); Errand
  of the Drowned Willow (moonflower bud at the shrine — bow before
  cutting); A Bottle for the Corner Table (teach-gate: Kuo won't remember
  Drunken Step sober, the rice wine is on the counter three paces away;
  reward: Drunken Step Sash). Four mortal-tier enemies: grey_forest_wolf,
  grey_pack_alpha (Qi-Condensation boss), pale_lake_carp_spirit,
  drowned_willow_revenant. Three new techniques, all learnable by mortal-
  tier players: Drunken Step (stun 1), Willow-Root Stance (buff_def 2),
  Farmhand's Cleave (honest damage). Fifteen new items: iron cleaver, wide-
  brim hat, Willowmere cordial (village-tier heal), moonflower tonic,
  tea-mother's warm cup (cheap heal), rice wine, drunken step sash, Ao's
  River Blade (quest-reward weapon), four materials (grey wolf pelt, alpha
  heart, carp scale, river-iron ingot, drowned silk scrap), moonflower
  bud, and Lady Moonbell herself. Four lore entries: Why Willowmere
  Forgot Its Name, The Drowning of the Willow, The Tune with the Last
  Note Different, Tea-Mother Weiyu's Ledger. Eight events — cricket song
  at dusk, laundry-gossip at the well, teahouse rumour of a thrice-
  rejected disciple, Kuo ringing his empty cup (+qi), the three-howl
  count on the ridge, the lake surface shivering, a moon-face in the
  water, the willow remembering (lore grant). Region is connected west
  from Verdant Bamboo Sea; Lady Moonbell is placed on the ground at
  Old Hermit's Hut. Validator + 8-scenario smoke test
  (tools/smoke_willowmere.py) all green. Save-compat preserved — zero
  new Player fields.
- **2026-04-23 (session 11)** — "The Chronicler's Eye." Lore finally
  became an earned reward, not just library flavor. Three new data-
  driven grant channels: `enemy.on_defeat_lore` (victory-paid), 
  `quest.grants_lore` (completion-paid), `npc.lore_dialogue` (trust-
  paid, shape mirrors `rep_dialogue` with lore ids at the leaves). 
  All three are additive and silent on already-known ids. Retrofit 5
  bosses, 8 quests, and 4 NPCs — Shen → Willow-Step Cut, Gale Tiger
  → Fall of Jadestep, Terrace Revenant → new Terrace Dancers, 
  Stormcaller Disciple → new Eight-Point Star Ledger, Pavilion 
  Guardian → Ledger of Red Names; Kettle's Request → Song of the 
  Bamboo, Study Sutra → Word in Dust, Envoy's Letter → Founding of 
  Azure Cloud, Missing Disciple → River of Swords legend, Oath of 
  Fangs → Oath of the Grey, Stormwarden's Test → Song of the 
  Stormwarden, Broken Terrace → new Mingshu's Last Silence, Red Path
  → Scarlet Lotus Oath; Baixu (ACS +5) → Azure Succession Dispute
  [new], Shan (FPS +3/+5, tiered) → First Poisoner myth + Five
  Refusals [new], Red Feather (SL +5) → Four Reasons [new], Old Dog
  (Jadestep +2) → Terrace Dancers, Stormwarden Gao (ACS +3) → 
  Stormcaller's Brand. Six new lore entries in 
  `content/lore/earned.json`: Azure Succession Dispute, Mingshu's
  Last Silence, Pavilion's Four Reasons, Five Poisons' Refusals, 
  Eight-Point Star Ledger, Terrace Dancers. Engine: new 
  `Game._grant_lore(id, source)` helper handles the announcement
  and silent re-grant; `_lore_dialogue_grant` evaluates a `talk`
  against sect thresholds. `cmd_read` / `cmd_lore` grouped by
  category with a `known/total` counter and per-entry category
  tag. Validator gained three checks (on_defeat_lore types,
  grants_lore types, lore_dialogue shape + lore-id resolution).
  SCHEMAS.md updated in three sections plus a new "How lore is
  earned" subsection at the bottom. Smoke test 
  `tools/smoke_lore.py` — 9 scenarios covering every channel,
  the "silent on known" invariant, the tier-picking at Shan, the
  `read` UI, and save-compat. Save-compat preserved — zero new
  Player fields; `known_lore` was already there.
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
