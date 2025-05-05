from dataclasses import dataclass
from typing import Tuple, Dict, List, Final, Callable
from pathlib import Path

from modules.logger import logger
from modules.mutation_generator import generate_trait
from modules.vault import VaultManager

@dataclass
class ShopItem:
    """Shop item configuration"""
    name: str
    cost: int
    description: str
    action: str
    handler: Callable

class Shop:
    """Handles shop interface and purchases"""
    def __init__(self, vault_manager: VaultManager):
        self.vault_manager = vault_manager
        self.inventory = self._setup_inventory()

    def _setup_inventory(self) -> List[ShopItem]:
        """Initialize shop inventory"""
        return [
            ShopItem(
                "Random Trait",
                10,
                "Unlock a random trait",
                "trait",
                self._handle_trait_purchase
            ),
            ShopItem(
                "Trait Slot",
                25,
                "Increase max trait slots",
                "slot",
                self._handle_slot_purchase
            )
        ]

    def purchase(self, item: ShopItem, points: int) -> Tuple[bool, str, int]:
        """Process purchase attempt"""
        if points < item.cost:
            return False, "❌ Insufficient points", points

        try:
            success = item.handler()
            if success:
                return True, "✅ Purchase successful", points - item.cost
            return False, "❌ Purchase failed", points
        except Exception as e:
            logger.error(f"Purchase error: {e}")
            return False, "❌ System error", points

    def _handle_trait_purchase(self) -> bool:
        """Handle trait purchase"""
        try:
            trait = generate_trait()
            return self.vault_manager.add_trait(trait)
        except Exception as e:
            logger.error(f"Trait purchase failed: {e}")
            return False

    def display(self, points: int) -> int:
        """Show shop interface"""
        while True:
            print(f"\n🛒 Shop (💠 {points} RP)")
            print("=" * 44)

            for i, item in enumerate(self.inventory, 1):
                print(f"{i}. {item.name} ({item.cost} RP)")
                print(f"   {item.description}")

            print(f"\n0. Exit Shop")

            try:
                choice = input("Choice: ").strip()
                if choice == "0":
                    break

                idx = int(choice) - 1
                if 0 <= idx < len(self.inventory):
                    success, msg, points = self.purchase(
                        self.inventory[idx],
                        points
                    )
                    print(msg)

            except ValueError:
                print("❌ Invalid input")

            input("\nPress Enter to continue...")

        return points
