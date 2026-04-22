# Content Schemas

All content files are JSON. Each file holds a single object **or** a list of
objects. The loader auto-detects. Every object MUST have an `id` (lowercase,
underscores). IDs must be unique within a category.

Optional fields can be omitted. Unknown fields are ignored (forward-compatible).

---

## locations/  — `Location`
```jsonc
{
  "id": "verdant_bamboo_sea",
  "name": "Verdant Bamboo Sea",
  "region": "Southern Wilds",
  "description": "Endless emerald stalks sway in a perfumed wind...",
  "exits": { "north": "azure_cloud_peak", "east": "river_of_swords" },
  "npcs": ["wandering_monk_huilin"],          // ids in npcs/
  "enemies": ["jade_serpent", "bandit_scout"], // ids in enemies/, may appear here
  "events": ["bamboo_flute_song"],             // ids in events/
  "items_on_ground": ["bamboo_qi_crystal"],    // free pickups
  "qi_density": 3,                             // 1-10, affects cultivation here
  "sect": null,                                // optional: sect that controls it
  "first_visit_text": "...",                   // optional, shown once
  "tags": ["forest", "tranquil"]
}
```

## npcs/  — `NPC`
```jsonc
{
  "id": "wandering_monk_huilin",
  "name": "Wandering Monk Huilin",
  "title": "Brother of the Silent Bell",
  "description": "A bald monk with sun-darkened skin...",
  "dialogue": [
    "All paths lead inward, friend.",
    "I once climbed the Heaven-Reaching Spire."
  ],
  "teaches": ["technique_id"],     // optional techniques he can teach
  "sells": ["item_id"],            // optional items he sells
  "gives_quest": "quest_id",       // optional quest start
  "faction": "shaolin",            // optional
  "disposition": "friendly",       // friendly | neutral | hostile

  // Optional rep spawn gates. If present, the NPC only appears at their
  // location when the player's rep meets the condition. Used for scouts
  // or recruiters who retreat once a player has become hostile enough.
  // `requires_rep`: rep floor (player.rep(sid) >= min).
  // `requires_rep_at_most`: rep ceiling (player.rep(sid) <= max).
  // Both may be combined. Missing field = no gate.
  "requires_rep": { "scarlet_lotus_pavilion": -2 },
  "requires_rep_at_most": { "scarlet_lotus_pavilion": 4 },

  // Optional rep-reactive dialogue. Lines show AFTER the main dialogue
  // block when the player's rep with the sect passes the threshold.
  // Positive thresholds fire when rep >= threshold; negative fire when
  // rep <= threshold. Only the single closest-to-current met threshold
  // per sect is used. Keys are stringified ints.
  "rep_dialogue": {
    "azure_cloud_sect": {
      "2":  ["Welcome, friend of the sect."],
      "-2": ["You have stood too often with those who owe us blood."]
    }
  },

  // Optional per-companion reactions — an extra line or two the NPC adds
  // to `talk` when the player's bound companion matches a key here. The
  // key is the companion NPC's id. Value is a string (one line) or list
  // (multiple lines). Fires for whichever companion is active; silently
  // absent otherwise. Downed companions do NOT trigger this.
  "companion_reply": {
    "blood_sworn_jin": [
      "Jin. So. The nephew walks with a stranger now.",
      "I will not speak of your uncle while you stand at my pillar."
    ],
    "disciple_meilin": "Meilin at your shoulder. Good — she is better at the road than I was at her age."
  },

  // Optional companion block. Makes this NPC recruitable via the `recruit`
  // command. At most one companion walks with the player at a time. A
  // recruited NPC still lives at their home location (still visible/talk-able);
  // only their combat shape is snapshotted onto the player. Gates (realm,
  // rep, quest) are all optional; all present must be met.
  "companion": {
    "recruit_dialogue": "She grins. 'Yours, then — until one of us falls.'",
    "decline_dialogue": "She bows. 'Come back when the sect has weighed you.'",
    "requires_realm":   "qi_condensation",    // optional
    "requires_quest":   "study_the_sutra",    // optional
    "requires_rep":     { "azure_cloud_sect": 2 },  // optional
    "hp":      58,
    "atk":     9, "def": 3, "spd": 7,
    "qi":      20, "max_qi": 40,
    "techniques": ["white_crane_sword", "azure_cloud_palm"],
    // Optional per-location barks — a one-line reaction printed under `look`
    // when the player walks this companion into a specific place. Fires once
    // per arrival; re-looking does not re-bark. Used for flavor when a
    // companion has history (positive or negative) with a location.
    "location_barks": {
      "scarlet_lotus_shrine": "Meilin breathes out slowly, once. 'If she moves, I will.'"
    }
  }
}
```

## enemies/  — `Enemy`
```jsonc
{
  "id": "jade_serpent",
  "name": "Jade Serpent",
  "description": "A coil of green muscle with ruby eyes.",
  "realm": "qi_condensation",      // pegs power; see realms/
  "hp": 40, "atk": 8, "def": 3, "spd": 6,
  "techniques": ["venom_lash"],    // optional, technique ids
  "drops": [
    { "item": "serpent_gallbladder", "chance": 0.4 },
    { "item": "jade_scale",          "chance": 0.7 }
  ],

  // Optional rep spawn gates. Same shape as on NPCs. Use for enemies that
  // only appear after the player has angered (or endeared themselves to)
  // a sect — hunters, assassins, sect guardians that attack outsiders.
  "requires_rep": { "azure_cloud_sect": 3 },
  "requires_rep_at_most": { "scarlet_lotus_pavilion": -1 },

  // Optional single-line atmospheric announcement shown under the enemy
  // in `look` when they are visible. Useful for ambush-spawned foes.
  "ambush_text": "A crimson silk scarf flutters from a crow-perch as you pass. There is no bird.",

  "xp": 30,
  "tags": ["beast", "venomous"]
}
```

## techniques/  — `Technique`
```jsonc
{
  "id": "azure_dragon_palm",
  "name": "Azure Dragon Palm",
  "type": "martial",                // martial | qi | sword | saber | body | mental
  "rank": "earth",                  // mortal | earth | heaven | mystic | divine
  "description": "A palm strike imitating the dragon's roar.",
  "qi_cost": 8,
  "damage": 14,
  "effect": null,                   // see "Effects" below
  "effect_power": 0,
  "requires_realm": "foundation_establishment",
  "requires_rep": { "azure_cloud_sect": 1 },  // optional; rep gate to learn
  "learn_cost": 50                  // spirit stones
}
```

### Technique effects (in combat)
Set `effect` to one of:
- `"heal"` — attacker heals `effect_power` HP immediately.
- `"poison"` — inflicts poison on the defender: `effect_power` dmg/turn, 3 turns. Refreshes on reapply.
- `"bleed"` — inflicts bleed on the defender: `effect_power` dmg/turn, 3 turns.
- `"stun"` — stuns the defender for `effect_power` turns (min 1). They skip their action.
- `"buff_atk"` — attacker gains `+effect_power` ATK for 3 turns (combat-local).
- `"buff_def"` — attacker gains `+effect_power` DEF for 3 turns (combat-local).

Offensive effects (poison/bleed/stun) are cancelled if the attack is dodged.
Self-effects (heal/buff_atk/buff_def) always fire when the technique is used.

## items/  — `Item`
```jsonc
{
  "id": "spirit_gathering_pill",
  "name": "Spirit Gathering Pill",
  "type": "pill",                   // pill | weapon | armor | accessory | material | treasure | manual
  "description": "A jade-green pill smelling of pine.",
  "effect": "qi_gain",              // qi_gain | hp_heal | atk_buff | def_buff | cleanse | unlock_technique | breakthrough_aid
  "power": 25,
  "value": 30,                      // sell price in spirit stones
  "tags": ["consumable"],

  // --- Equipment fields (optional; omit for non-gear items) ---
  "slot": "weapon",                 // weapon | robe | accessory
  "atk_bonus": 3,                   // integer, default 0
  "def_bonus": 0,
  "spd_bonus": 0,
  "hp_bonus": 0,
  "requires_realm": "qi_condensation",  // optional; realm gate to equip
  "requires_rep": { "azure_cloud_sect": 2 },  // optional; rep gate to buy or equip
  "on_hit_effect": "poison",        // poison | bleed | stun — fires on successful normal attacks
  "on_hit_power": 1                 // dmg/turn for poison/bleed, turns stunned for stun
}
```

### Equipment slots (engine)
The Player has three slots: `weapon`, `robe`, `accessory`. Only one item
per slot. `equip <item>` moves an item from inventory into its slot;
`unequip <slot>` moves it back out. Gear bonuses apply whenever the
effective stat is read (combat rolls, the prompt bar, the `status`
screen). Weapon `on_hit_effect` fires only on plain `attack` actions
that actually land — not on techniques (which carry their own effects).
Unequipping gear that bumps `max_hp` clamps current HP down if over.


## sects/  — `Sect`
```jsonc
{
  "id": "azure_cloud_sect",
  "name": "Azure Cloud Sect",
  "alignment": "righteous",         // righteous | neutral | demonic
  "headquarters": "azure_cloud_peak",
  "description": "...",
  "signature_techniques": ["azure_dragon_palm", "cloud_step"],
  "elders": ["elder_baixu"],
  "rivals": ["scarlet_lotus_pavilion"]
}
```

## quests/  — `Quest`
```jsonc
{
  "id": "missing_disciple",
  "name": "The Missing Disciple",
  "giver": "elder_baixu",
  "description": "Find the disciple lost on Azure Cloud Peak.",
  "steps": [
    { "type": "visit",  "target": "azure_cloud_peak" },
    { "type": "defeat", "target": "frost_wolf" },
    { "type": "talk",   "target": "elder_baixu" }
  ],
  "reward": { "spirit_stones": 100, "items": ["spirit_gathering_pill"], "xp": 50 },

  // Reputation deltas applied on quest completion. Deltas can be negative.
  "rep_change": { "azure_cloud_sect": 2, "scarlet_lotus_pavilion": -1 },

  // Optional rep gate on quest offer. If the player doesn't meet this,
  // the questgiver's `talk` will not auto-offer the quest (they weigh
  // you silently).
  "requires_rep": { "azure_cloud_sect": 1 },

  // Optional prerequisite quest — this quest is not offered until the
  // named quest sits in `Player.completed_quests`. Used to chain an arc:
  // the second errand stays silent until the first is closed.
  "requires_quest": "the_red_path"
}
```

## events/  — `Event`
Random text encounters. Triggered with some probability when entering a location.
```jsonc
{
  "id": "bamboo_flute_song",
  "location": "verdant_bamboo_sea",
  "chance": 0.3,
  "text": "A haunting flute drifts through the bamboo...",
  "effect": { "qi": 5 }            // optional small reward / penalty
}
```

## realms/  — `Realm`
```jsonc
{
  "id": "qi_condensation",
  "order": 1,
  "name": "Qi Condensation",
  "description": "First gathering of qi into the dantian.",
  "qi_required": 100,              // total qi to break through to next realm
  "hp_bonus": 20,
  "atk_bonus": 2,
  "def_bonus": 1
}
```

## recipes/  — `Recipe`
```jsonc
{
  "id": "forge_skybreaker_blade",
  "name": "Skybreaker Blade",
  "type": "forge",                  // forge | brew | craft  (flavor tag, all use `craft`)
  "crafter": "forge_master_bo",     // npc id; player must be at their location to use
  "inputs": { "gale_tiger_fang": 1, "cloudroot_spirit_stone": 2 },  // item_id -> qty
  "stones": 250,                    // spirit stones consumed (default 0)
  "requires_realm": "foundation_establishment",   // optional realm gate
  "output": "skybreaker_blade",     // item id
  "output_qty": 1,                  // default 1
  "flavor": "Bo sets the fang into the fuller..."  // prose on successful craft
}
```

### Crafting (engine)
`craft` with no arg lists recipes available from every crafter NPC at the
current location. `craft <recipe_id>` executes one: it checks that the
crafter is here, that realm gates are met, that the player has every input
(items + spirit stones), then consumes the inputs and adds the output to
inventory. `forge` and `brew` are aliases for `craft`; `recipes` is an
alias for `craft` (with no arg). NPCs automatically advertise their
recipes when the player `talk`s to them.

Rep gate on a recipe is expressed as `requires_rep: {sect_id: min_rep}`
and blocks `craft`; the listing shows the required standing inline.

---

## Reputation system

Every sect defined in `content/sects/` is a potential reputation bucket.
The player's rep is stored in `Player.reputation` as a `sect_id -> int`
dict. Default is 0 (stranger).

Ranks (from `game.state.rep_rank`):
- `+8..`      sect-honoured
- `+5..+7`    honoured
- `+3..+4`    respected
- `+1..+2`    known
- `  0`       stranger
- `-1..-2`    distrusted
- `-3..-5`    enemy
- `-6..`      reviled

Any content object can gate itself with `requires_rep: {sect_id: min}`.
Currently honored on: quests (auto-offer on talk), items (buy, equip),
techniques (learn), recipes (craft), and the **spawn presence** of
NPCs and enemies at their location. All require *every* threshold in
the dict to be met; negative min means "rep must be >= this value".

NPCs and enemies additionally support `requires_rep_at_most: {sect_id: max}`
as a ceiling — the entity disappears when the player's rep exceeds it.
Used for "scouts who retreat once you outrank them" and for defenders
who only attack when the player has insulted the sect. Enemies can
also carry `ambush_text`, a one-line atmospheric tag shown under the
enemy in `look` — pairs naturally with rep-triggered spawns.

Quests also support `rep_change: {sect_id: delta}` — applied on
completion, reported to the player with old->new rank crossings when
the change moves them through a rank boundary.

The `reputation` / `rep` / `standing` command shows rep against every
known sect, with rank names.


## Companions

An NPC with a `companion` block can be `recruit`ed to fight at the
player's side. At most one companion walks with the player at a time;
`dismiss` releases the bond and `companion` / `party` prints a status.
Recruited NPCs remain at their home location (visible, talk-able); only
their combat shape is snapshotted onto the player (`Player.companion`).

During combat, if a companion is active and not downed:
- they take one turn per round after the player, choosing a random
  technique they can afford or a basic attack;
- the enemy splits attention — ~35% of enemy attacks target the
  companion instead of the player;
- status effects apply to whoever was targeted.

A companion reduced to 0 HP is **downed** — they skip the rest of the
fight but are not dead. `cultivate` at any location revives them to full
HP. After any non-defeat outcome, an un-downed companion also heals to
full (the post-battle breather is part of the fiction).

Gates on recruitment are all optional: `requires_realm`, `requires_rep`,
and `requires_quest` (must be in `Player.completed_quests`). The
`recruit_dialogue` / `decline_dialogue` strings let each companion
speak in their own voice at bind-time.

### Affinity (the bond that deepens)

Each companion tracks an **affinity** score with the player in
`Player.companion_affinity: {npc_id -> int}`. Affinity grows with
shared experience and persists across dismiss/recruit cycles — a bond
once earned is not lost by a temporary parting.

Gains:
- **+1** per combat victory while the companion is active and still
  standing at the final blow (downed companions get nothing; the win
  is not yours alone, and not theirs if they fell first);
- **+2** on quest completion while a companion is active (downed does
  not disqualify — they walked the road).

Tiers (and the flat stat bonuses each grants at fight start):
| Affinity | Tier        | Bonus                  |
|----------|-------------|------------------------|
| 0–4      | bonded      | —                      |
| 5–11     | trusted     | +1 ATK                 |
| 12–24    | steadfast   | +1 ATK, +1 DEF         |
| 25+      | soul-sworn  | +2 ATK, +1 DEF, +1 SPD |

Tier crossings (either direction) print a prose beat. The runtime
bonus applies only during combat — base stats stored on
`Player.companion` are never mutated by affinity.

### Location barks

An optional `location_barks: {loc_id: "line"}` on the companion block
lets each ally react to arriving at specific places. The line fires
once per arrival under `look`; re-looking in place does not re-bark.
Walking away and returning re-arms the bark. Used for flavor when a
companion has stakes at a location — a sword of the Azure Cloud at
the Scarlet shrine; a demon-path prodigal at the sect he left.


## lore/  — `Lore`
```jsonc
{
  "id": "legend_of_jade_emperor",
  "title": "The Legend of the Jade Emperor",
  "category": "myth",              // myth | history | poem | sutra
  "text": "Long ago, when the heavens were young..."
}
```
