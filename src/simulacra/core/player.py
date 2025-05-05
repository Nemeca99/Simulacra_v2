"""
Player implementation
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set
from .types import PlayerState

@dataclass
class PlayerConfig:
    """Player configuration"""
    base_health: float = 100.0
    base_speed: float = 1.0
    max_health: float = 100.0
    trait_slots: int = 3
    max_resistances: Dict[str, float] = field(default_factory=lambda: {
        'radiation': 75.0,
        'chemical': 75.0,
        'biological': 75.0,
        'physical': 75.0,
        'psychic': 75.0
    })
    mutation_rate: float = 0.0
    immunities: List[str] = field(default_factory=list)

@dataclass
class Player:
    """Player class"""
    id: str
    name: str
    config: PlayerConfig = field(default_factory=PlayerConfig)
    health: float = field(init=False)
    speed: float = field(init=False)
    mutation_rate: float = field(init=False)
    resistances: Dict[str, float] = field(default_factory=dict)
    immunities: List[str] = field(default_factory=list)
    active_traits: Set[str] = field(default_factory=set)

    def __post_init__(self):
        """Initialize with config values"""
        self.health = self.config.base_health
        self.speed = self.config.base_speed
        self.mutation_rate = self.config.mutation_rate

    def modify_mutation_rate(self, amount: float) -> None:
        """Modify the mutation rate"""
        self.mutation_rate = max(0.0, min(100.0, self.mutation_rate + amount))

    def modify_resistance(self, damage_type: str, amount: float) -> None:
        """Modify resistance with proper capping"""
        max_res = self.config.max_resistances.get(damage_type, 75.0)
        current = self.resistances.get(damage_type, 0.0)
        self.resistances[damage_type] = min(max_res, current + amount)

    def modify_health(self, amount: float) -> None:
        """Modify player health with bounds checking"""
        self.health = max(0, min(self.config.max_health, self.health + amount))

    def to_state(self) -> PlayerState:
        """Convert to PlayerState"""
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'health': self.health,
            'experience': self.experience
        }
