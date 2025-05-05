import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Final
from dataclasses import dataclass
from colorama import Fore, Style
from modules.utils import clear_screen
from modules.logger import logger
from modules.constants import DATA_DIR

@dataclass
class Trait:
    """Represents a trait in the vault"""
    name: str
    tier: int
    point_value: int
    effects: List[Dict[str, str]]

    def validate(self) -> bool:
        """Validate trait data"""
        return all([
            isinstance(self.name, str),
            isinstance(self.tier, int),
            isinstance(self.point_value, int),
            isinstance(self.effects, list),
            all(isinstance(e, dict) for e in self.effects)
        ])

class VaultManager:
    """Manages the trait vault operations"""
    VAULT_PATH: Final[Path] = DATA_DIR / "vault.json"

    def __init__(self):
        self.vault: List[Dict] = []
        self.initialize()

    def initialize(self) -> None:
        """Initialize the vault system"""
        try:
            self.vault = self.load_vault()
            logger.debug(f"Loaded {len(self.vault)} traits from vault")
        except Exception as e:
            logger.error(f"Failed to initialize vault: {e}")
            self.vault = []

    def load_vault(self) -> List[Dict]:
        """Load the player's trait vault"""
        try:
            if not self.VAULT_PATH.exists():
                return []
            with open(self.VAULT_PATH, "r", encoding='utf-8') as f:
                return [trait for trait in json.load(f) if self._validate_trait(trait)]
        except Exception as e:
            logger.error(f"Failed to load vault: {e}")
            return []

    def save_vault(self) -> bool:
        """Save the current vault state"""
        try:
            self.VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.VAULT_PATH, "w", encoding='utf-8') as f:
                json.dump(self.vault, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save vault: {e}")
            return False

    def _validate_trait(self, trait: Dict) -> bool:
        """Validate trait structure"""
        try:
            Trait(**trait)
            return True
        except Exception:
            return False

    def display_vault(self) -> None:
        """Display the vault contents"""
        clear_screen()
        print(f"{Fore.BLUE}{'=' * 44}")
        print(f"{Fore.WHITE}🔐 UNLOCKED TRAITS VAULT")
        print(f"{Fore.BLUE}{'=' * 44}{Style.RESET_ALL}")

        if not self.vault:
            print(f"{Fore.LIGHTBLACK_EX}Vault is empty. Unlock traits in the shop.")
        else:
            for i, trait in enumerate(self.vault):
                name = trait.get("name", "Unknown Trait")
                tier = trait.get("tier", "Unknown Tier")
                point_value = trait.get("point_value", "N/A")
                effects = [e["text"] for e in trait.get("effects", [])]

                print(f"\n{i + 1}. {Fore.CYAN}{name}{Style.RESET_ALL}")
                print(f"   Tier: {tier} | Value: {point_value} pts")
                print(f"   Effects: {', '.join(effects)}")

        print(f"\n{Fore.BLUE}{'=' * 44}{Style.RESET_ALL}")

    def add_trait(self, trait: Dict) -> bool:
        """Add a new trait to the vault"""
        try:
            trait.setdefault("point_value", 0)
            self.vault.append(trait)
            success = self.save_vault()
            if success:
                logger.info(f"Added trait to vault: {trait['name']}", Fore.GREEN)
            return success
        except Exception as e:
            logger.error(f"Failed to add trait: {e}")
            return False
