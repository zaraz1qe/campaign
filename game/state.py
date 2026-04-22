"""Mutable player state. Pure data — methods only mutate self."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Any, Optional
import json


EQUIP_SLOTS = ("weapon", "robe", "accessory")


# Reputation ranks — thresholds are inclusive floors. Walk from highest down.
# Anyone below -5 is reviled; anyone at 0 is a stranger; +3 earns respect; +8
# approaches sect-elder status. Keep the table short — ranks are flavor, the
# number is the mechanic.
REP_RANKS = (
    (8,  "sect-honoured"),
    (5,  "honoured"),
    (3,  "respected"),
    (1,  "known"),
    (0,  "stranger"),
    (-2, "distrusted"),
    (-5, "enemy"),
    (-99, "reviled"),
)


def rep_rank(value: int) -> str:
    """Return the rank title for a reputation value."""
    for floor, name in REP_RANKS:
        if value >= floor:
            return name
    return "reviled"


# Companion affinity tiers. A companion's affinity grows with shared combat
# victories and completed quests. The tier both names the bond and grants
# flat stat bonuses at fight-start.
AFFINITY_TIERS = (
    (25, "soul-sworn"),
    (12, "steadfast"),
    (5,  "trusted"),
    (0,  "bonded"),
    (-99, "strained"),
)


def affinity_tier(value: int) -> str:
    for floor, name in AFFINITY_TIERS:
        if value >= floor:
            return name
    return "strained"


def affinity_bonus(value: int) -> Dict[str, int]:
    """Flat stat bonuses granted to a companion by their affinity with the
    player. Applied once at fight start when snapshotting the companion into
    combat-runtime state."""
    if value >= 25:
        return {"atk": 2, "def": 1, "spd": 1}
    if value >= 12:
        return {"atk": 1, "def": 1, "spd": 0}
    if value >= 5:
        return {"atk": 1, "def": 0, "spd": 0}
    return {"atk": 0, "def": 0, "spd": 0}


@dataclass
class Player:
    name: str = "Wanderer"
    location: str = "verdant_bamboo_sea"

    # Cultivation
    realm_id: str = "mortal"
    qi: int = 0           # progress within current realm
    max_qi: int = 50

    # Combat stats (base; realms add bonuses)
    hp: int = 30
    max_hp: int = 30
    atk: int = 5
    defense: int = 2
    spd: int = 5

    # Resources
    spirit_stones: int = 20
    xp: int = 0

    # Knowledge
    techniques: List[str] = field(default_factory=list)
    inventory: Dict[str, int] = field(default_factory=dict)   # item_id -> count
    visited: Set[str] = field(default_factory=set)
    known_lore: Set[str] = field(default_factory=set)

    # Quests
    active_quests: Dict[str, int] = field(default_factory=dict)  # quest_id -> step index
    completed_quests: Set[str] = field(default_factory=set)
    defeated: Dict[str, int] = field(default_factory=dict)      # enemy_id -> count
    talked_to: Set[str] = field(default_factory=set)

    # Reputation per sect
    reputation: Dict[str, int] = field(default_factory=dict)

    # Equipment — slot -> item_id (empty string = nothing equipped)
    equipped: Dict[str, str] = field(
        default_factory=lambda: {s: "" for s in EQUIP_SLOTS}
    )

    # Companion (optional). A dict shaped by the recruited NPC's `companion`
    # block plus live fields:
    #   { "id": npc_id, "hp": int, "max_hp": int, "atk": int, "def": int,
    #     "spd": int, "qi": int, "max_qi": int, "techniques": [tid, ...],
    #     "downed": bool, "last_bark_loc": str|None }
    # None means no companion. At most one is active at a time.
    companion: Optional[Dict[str, Any]] = None

    # Per-companion affinity — bond with each NPC the player has ever
    # recruited. Persists across dismiss/recruit cycles so that trust earned
    # is not lost by a temporary parting. npc_id -> int.
    companion_affinity: Dict[str, int] = field(default_factory=dict)

    # ------------------------------------------------------------------
    def add_item(self, item_id: str, count: int = 1) -> None:
        self.inventory[item_id] = self.inventory.get(item_id, 0) + count

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        have = self.inventory.get(item_id, 0)
        if have < count:
            return False
        if have == count:
            del self.inventory[item_id]
        else:
            self.inventory[item_id] = have - count
        return True

    def has_item(self, item_id: str, count: int = 1) -> bool:
        return self.inventory.get(item_id, 0) >= count

    def adjust_rep(self, sect_id: str, delta: int) -> None:
        self.reputation[sect_id] = self.reputation.get(sect_id, 0) + delta

    def rep(self, sect_id: str) -> int:
        return int(self.reputation.get(sect_id, 0))

    def affinity(self, npc_id: str) -> int:
        return int(self.companion_affinity.get(npc_id, 0))

    def adjust_affinity(self, npc_id: str, delta: int) -> int:
        new_val = self.affinity(npc_id) + int(delta)
        self.companion_affinity[npc_id] = new_val
        return new_val

    def meets_rep(self, requires: Dict[str, int]) -> bool:
        """True iff the player's rep meets every sect threshold in `requires`."""
        if not requires:
            return True
        for sid, minv in requires.items():
            if self.rep(sid) < int(minv):
                return False
        return True

    def rep_shortfalls(self, requires: Dict[str, int]) -> Dict[str, int]:
        """Return {sect_id: shortfall_value} for each failing rep requirement."""
        out: Dict[str, int] = {}
        if not requires:
            return out
        for sid, minv in requires.items():
            if self.rep(sid) < int(minv):
                out[sid] = int(minv) - self.rep(sid)
        return out

    # ------------------------------------------------------------------
    # Equipment helpers. Bonuses are always computed from `world` so the
    # player's stored stats stay as their *base* values.
    def gear_bonuses(self, world: Dict[str, Any]) -> Dict[str, int]:
        out = {"atk": 0, "def": 0, "spd": 0, "hp": 0}
        for iid in self.equipped.values():
            if not iid:
                continue
            it = world.get("items", {}).get(iid, {})
            for k in out:
                out[k] += int(it.get(f"{k}_bonus", 0) or 0)
        return out

    def eff_max_hp(self, world: Dict[str, Any]) -> int:
        return self.max_hp + self.gear_bonuses(world)["hp"]

    def eff_atk(self, world: Dict[str, Any]) -> int:
        return self.atk + self.gear_bonuses(world)["atk"]

    def eff_def(self, world: Dict[str, Any]) -> int:
        return self.defense + self.gear_bonuses(world)["def"]

    def eff_spd(self, world: Dict[str, Any]) -> int:
        return self.spd + self.gear_bonuses(world)["spd"]

    def weapon(self, world: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        wid = self.equipped.get("weapon", "")
        if not wid:
            return None
        return world.get("items", {}).get(wid)

    # ------------------------------------------------------------------
    def to_json(self) -> str:
        d = asdict(self)
        d["visited"] = sorted(self.visited)
        d["known_lore"] = sorted(self.known_lore)
        d["completed_quests"] = sorted(self.completed_quests)
        d["talked_to"] = sorted(self.talked_to)
        return json.dumps(d, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, blob: str) -> "Player":
        d = json.loads(blob)
        d["visited"] = set(d.get("visited", []))
        d["known_lore"] = set(d.get("known_lore", []))
        d["completed_quests"] = set(d.get("completed_quests", []))
        d["talked_to"] = set(d.get("talked_to", []))
        # Backfill equipment for pre-session-3 saves.
        eq = d.get("equipped") or {}
        d["equipped"] = {s: eq.get(s, "") for s in EQUIP_SLOTS}
        # Backfill companion for pre-session-8 saves (default: none).
        d.setdefault("companion", None)
        # Backfill companion_affinity for pre-session-9 saves (default: empty).
        d.setdefault("companion_affinity", {})
        if not isinstance(d["companion_affinity"], dict):
            d["companion_affinity"] = {}
        return cls(**d)
