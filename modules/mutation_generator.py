from dataclasses import dataclass
from typing import Dict, List, Optional, Final
from pathlib import Path
import random
import uuid
import json

from modules.logger import logger
from modules.constants import DATA_DIR

@dataclass
class MutationComponents:
    """Mutation component pools"""
    percent: List[str]
    effect: List[str]
    ability: List[str]
    flavor: List[str]

class MutationGenerator:
    """Handles generation of mutations and traits"""
    MUTATION_PARTS_DIR: Final[Path] = DATA_DIR / "mutation_parts"

    BASE_NAMES: Final[List[str]] = [
        "Iron Heart", "Stone Skin", "Blood Bloom", "Mindroot",
        "Ashborn", "Nullcore", "Titan Coil", "Quantum Shroud"
    ]

    def __init__(self):
        self.components = self._load_components()

    def _load_components(self) -> MutationComponents:
        """Load mutation components from files"""
        try:
            return MutationComponents(
                percent=self._load_json_file("percent.json"),
                effect=self._load_json_file("effect.json"),
                ability=self._load_json_file("ability.json"),
                flavor=self._load_json_file("flavor.json")
            )
        except Exception as e:
            logger.error(f"Failed to load mutation components: {e}")
            return MutationComponents([], [], [], [])

    def _load_json_file(self, filename: str) -> List[str]:
        """Load JSON file from mutation parts directory"""
        file_path = self.MUTATION_PARTS_DIR / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_mutation_effect(self) -> str:
        """Generate random mutation effect string"""
        return (f"{random.choice(self.components.percent)} "
                f"{random.choice(self.components.effect)} "
                f"{random.choice(self.components.ability)} "
                f"{random.choice(self.components.flavor)}")

    def generate_trait(self, tier: int) -> Dict:
        """Generate trait with random effects based on tier"""
        trait = {
            "id": str(uuid.uuid4()),
            "name": random.choice(self.BASE_NAMES),
            "tier": tier,
            "effects": []
        }

        # Add effects based on tier
        base_bonus = 10 * tier
        negative_penalty = 5 * tier

        stats = ["HP", "Resilience", "Mutation Rate"]
        positive_stat = random.choice(stats)
        negative_stats = [s for s in stats if s != positive_stat]

        trait["effects"] = [
            {"rarity": "Common", "text": self.generate_mutation_effect()},
            {"rarity": "Common", "text": f"+{base_bonus}% {positive_stat}"},
            *[{"rarity": "Common", "text": f"-{negative_penalty}% {stat}"}
              for stat in negative_stats]
        ]

        return trait
