from typing import Dict, List, Optional
from dataclasses import dataclass
from modules.soft_prestige_merge import merge_traits_by_index
from modules.vault import load_vault, save_vault
from modules.logger import logger

@dataclass
class TraitTheme:
    """Theme configuration for trait naming"""
    keywords: List[str]
    weight: int = 0

    def matches(self, text: str) -> bool:
        """Check if text contains any theme keywords"""
        return any(kw.lower() in text.lower() for kw in self.keywords)

class MergeStation:
    """Handles trait merging operations"""
    THEMES = {
        "HP": TraitTheme(["HP", "health", "vitality"]),
        "Resilience": TraitTheme(["resilience", "resist", "defense"]),
        "Mutation": TraitTheme(["mutation", "entropy", "chaos"]),
        "Fire": TraitTheme(["fire", "burn", "ash"]),
        "Synergy": TraitTheme(["synergy", "fusion", "hybrid"])
    }

    @classmethod
    def generate_trait_name(cls, effects: List[Dict], merge_count: int) -> str:
        """Generate dynamic name for merged trait"""
        themes = cls.THEMES.copy()

        # Count theme occurrences
        for effect in effects:
            for theme in themes.values():
                if theme.matches(effect['text']):
                    theme.weight += 1

        # Find dominant theme
        dominant = max(themes.items(), key=lambda x: x[1].weight)
        base_name = f"Core of {dominant[0]}" if dominant[1].weight > 0 else "Hybrid Core"

        return f"{base_name} +{merge_count}"

    @staticmethod
    def merge_station() -> None:
        """Interactive trait merging interface"""
        vault = load_vault()

        if len(vault) < 2:
            logger.error("Not enough traits in vault to merge")
            input("Press Enter to return...")
            return

        print("\n🔄 Merge Station")
        for i, trait in enumerate(vault):
            print(f"{i + 1}. {trait['name']} (Tier {trait['tier']}, {trait['point_value']} pts)")

        try:
            choice1 = int(input("First trait: ")) - 1
            choice2 = int(input("Second trait: ")) - 1

            if not (0 <= choice1 < len(vault) and 0 <= choice2 < len(vault)):
                raise ValueError("Invalid selection")

            if choice1 == choice2:
                raise ValueError("Must select different traits")

            result = merge_traits_by_index(choice1, choice2)
            if result:
                logger.info(f"Created new trait: {result['name']}")

        except ValueError as e:
            logger.error(f"Merge failed: {str(e)}")

        input("Press Enter to return...")