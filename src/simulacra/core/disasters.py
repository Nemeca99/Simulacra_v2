from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import random


class DisasterType(Enum):
    RADIATION = "radiation"
    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    PHYSICAL = "physical"
    PSYCHIC = "psychic"


@dataclass
class Disaster:
    id: str
    name: str
    description: str
    type: DisasterType
    damage: float
    mutation_chance: float
    duration: int = 1
    cooldown: int = 30  # Minimum seconds between same disaster

    def to_dict(self) -> Dict:
        """Convert disaster to dictionary for display"""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'damage': self.damage,
            'mutation_chance': self.mutation_chance
        }

    def get_scaled_damage(self, time: int, count: int) -> float:
        """Calculate scaled damage based on time and disaster count"""
        early_game_bonus = max(0, 30 - time) * 0.02  # +2% per second under 30s
        time_scaling = 1.0 + (time / 180.0)  # +100% every 3 minutes
        count_scaling = 1.0 + (count * 0.15)  # +15% per disaster

        return self.damage * (1 + early_game_bonus) * time_scaling * count_scaling


class DisasterSystem:

    def __init__(self):
        self.disasters: Dict[str, Disaster] = {}
        self.last_occurrence: Dict[str, int] = {}
        self._initialize_disasters()

    def _initialize_disasters(self) -> None:
        base_disasters = [
            Disaster(
                id="radiation_burst",
                name="Radiation Burst",
                description="Intense radiation damage and high mutation chance",
                type=DisasterType.RADIATION,
                damage=20.0,  # Higher base damage
                mutation_chance=25.0,
                cooldown=35
            ),
            Disaster(
                id="acid_rain",
                name="Acid Rain",
                description="Corrosive damage over time",
                type=DisasterType.CHEMICAL,
                damage=8.0,  # Higher base damage
                mutation_chance=15.0,
                duration=3,
                cooldown=25
            ),
            Disaster(
                id="psychic_wave",
                name="Psychic Wave",
                description="Mental damage and mutation acceleration",
                type=DisasterType.PSYCHIC,
                damage=15.0,  # Higher base damage
                mutation_chance=35.0,
                cooldown=40
            ),
            Disaster(
                id="toxic_cloud",
                name="Toxic Cloud",
                description="Poison damage and resistance weakening",
                type=DisasterType.CHEMICAL,
                damage=12.0,
                mutation_chance=15.0,
                cooldown=40
            )
        ]
        for disaster in base_disasters:
            self.disasters[disaster.id] = disaster

    def trigger_random_disaster(self, current_time: int) -> Optional[Disaster]:
        available_disasters = [
            d for d in self.disasters.values()
            if current_time - self.last_occurrence.get(d.id, -999) >= d.cooldown
        ]

        if not available_disasters:
            return None

        disaster = random.choice(available_disasters)
        self.last_occurrence[disaster.id] = current_time
        return disaster
