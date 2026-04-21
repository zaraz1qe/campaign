"""Mutable player state. Pure data — methods only mutate self."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Any
import json


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
        return cls(**d)
