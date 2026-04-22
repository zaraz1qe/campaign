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
  "disposition": "friendly"        // friendly | neutral | hostile
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
  "reward": { "spirit_stones": 100, "items": ["spirit_gathering_pill"], "xp": 50 }
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

## lore/  — `Lore`
```jsonc
{
  "id": "legend_of_jade_emperor",
  "title": "The Legend of the Jade Emperor",
  "category": "myth",              // myth | history | poem | sutra
  "text": "Long ago, when the heavens were young..."
}
```
