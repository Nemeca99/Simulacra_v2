from dataclasses import dataclass
from typing import Dict, List, Optional, Final
from pathlib import Path
import json
import random
from collections import Counter

from modules.logger import logger
from modules.mutation_generator import generate_mutation_effect
from modules.constants import DATA_DIR

@dataclass
class MergeResult:
    """Result of a trait merge operation"""
    success: bool
    message: str
    trait: Optional[Dict] = None

class TraitMerger:
    """Handles trait merging operations"""
    VAULT_PATH: Final[Path] = DATA_DIR / "player_vault.json"

    RARITY_POINTS: Final[Dict[str, int]] = {
        "common": 1,
        "uncommon": 2,
        "rare": 3,
        "legendary": 4
    }

    @classmethod
    def load_vault(cls) -> List[Dict]:
        """Load trait vault from file"""
        try:
            if not cls.VAULT_PATH.exists():
                return []
            with open(cls.VAULT_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load vault: {e}")
            return []

    @classmethod
    def save_vault(cls, vault: List[Dict]) -> bool:
        """Save trait vault to file"""
        try:
            cls.VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(cls.VAULT_PATH, 'w', encoding='utf-8') as f:
                json.dump(vault, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save vault: {e}")
            return False

    @staticmethod
    def trait_signature(trait: Dict) -> Counter:
        """Generate unique signature for trait effects"""
        return Counter(effect["text"] for effect in trait["effects"])

    @classmethod
    def merge_traits(cls, index1: int, index2: int) -> MergeResult:
        """Merge two traits by index"""
        vault = cls.load_vault()

        if not cls._validate_indices(vault, index1, index2):
            return MergeResult(False, "❌ Invalid trait indices", None)

        trait1, trait2 = vault[index1], vault[index2]

        if not cls._validate_merge(trait1, trait2):
            return MergeResult(False, "❌ Traits incompatible", None)

        new_trait = cls._create_merged_trait(trait1, trait2)
        if not new_trait:
            return MergeResult(False, "❌ Merge failed", None)

        # Update vault
        for idx in sorted([index1, index2], reverse=True):
            vault.pop(idx)
        vault.append(new_trait)

        if not cls.save_vault(vault):
            return MergeResult(False, "❌ Failed to save", None)

        return MergeResult(
            True,
            f"✅ Created {new_trait['name']}",
            new_trait
        )
