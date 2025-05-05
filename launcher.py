from dataclasses import asdict
import os
import sys
import time
import random
from typing import Optional, List, Dict, NoReturn, Any
from pathlib import Path
import logging
from colorama import Fore, Style

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import core systems
try:
    from simulacra.core.traits import TraitSystem
    from simulacra.core.player import Player
    from simulacra.core.mutations import MutationSystem
    USING_NEW_SYSTEMS = True
    logger.info("Using new game systems")
except ImportError as e:
    logger.error(f"Failed to import core systems: {e}")
    USING_NEW_SYSTEMS = False
    logger.info("Using legacy systems")

from main import run_simulacra, select_trait_loadout, SimulacraGame
from modules.config_manager import ConfigurationManager, GameConfig
from modules.highlights import HighlightManager
from modules.logger import logger, setup_logging
from modules.vault import VaultManager
from modules.credits import display_credits
from modules.achievements import AchievementManager
from modules.constants import *
from modules.error_handler import GameError, handle_error
from simulacra.core.player import Player, PlayerConfig  # Use this instead
from simulacra.ui.menu import MenuScreen


class SimulacraLauncher:

    def __init__(self) -> None:
        """Initialize the launcher with type-safe attributes"""
        self.config_manager: Optional[ConfigurationManager] = None
        self.vault_manager: Optional[VaultManager] = None
        self.achievement_manager: Optional[AchievementManager] = None
        self.highlight_manager: Optional[HighlightManager] = None
        self.game_config: Optional[GameConfig] = None
        self.trait_system = TraitSystem() if USING_NEW_SYSTEMS else None
        self.mutation_system = MutationSystem() if USING_NEW_SYSTEMS else None
        self.player = None
        self.initialize()

    def initialize(self) -> None:
        """Initialize all required managers and configurations with proper error handling"""
        try:
            # Set up logging first
            setup_logging()
            logger.info("Starting Simulacra initialization...")

            # Create required directories
            self._create_directories()

            # Initialize managers with validation
            self.config_manager = ConfigurationManager()
            if not self.config_manager:
                raise RuntimeError("Failed to initialize ConfigurationManager")

            # Changed from load() to load_config()
            self.game_config = self.config_manager.load_config()
            if not self.game_config:
                raise RuntimeError("Failed to load game configuration")

            self.vault_manager = VaultManager()
            if not self.vault_manager:
                raise RuntimeError("Failed to initialize VaultManager")

            self.achievement_manager = AchievementManager()
            if not self.achievement_manager:
                raise RuntimeError("Failed to initialize AchievementManager")

            self.highlight_manager = HighlightManager()
            if not self.highlight_manager:
                raise RuntimeError("Failed to initialize HighlightManager")

            # Initialize trait system
            if USING_NEW_SYSTEMS:
                self._load_test_data()

            logger.info("Game initialization complete")
        except Exception as e:
            logger.critical(f"Initialization failed: {e}")
            raise SystemExit(f"Failed to initialize game systems: {e}")

    def _create_directories(self) -> None:
        """Create required game directories"""
        directories = [DATA_DIR, CONFIG_DIR, SAVE_DIR, LOGS_DIR]
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Directory ensured: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise

    def breathing_intro(self) -> None:
        """Display breathing interface initialization"""
        try:
            phrases = [
                (CYAN, "...breath detected..."),
                (BLUE, "...breath strengthening..."),
                (PURPLE, "...breath accepted..."),
            ]
            for color, phrase in phrases:
                print(f"{color}{phrase}{RESET}")
                time.sleep(random.uniform(0.25, 1))

            stages = ["S", "SI", "SIM", "SIMU", "SIMUL", "SIMULA",
                     "SIMULAC", "SIMULACR", "SIMULACRA"]
            for stage in stages:
                sys.stdout.write(f"\r{CYAN}{stage}{RESET}")
                sys.stdout.flush()
                time.sleep(random.uniform(0.1, 0.3))
            print(f"\r{WHITE}SIMULACRA AWAKENS{RESET}")

        except Exception as e:
            logger.error(f"Breathing intro failed: {e}")

    def _show_shop(self) -> None:
        """Display and handle the RP shop interface"""
        if not self._ensure_initialized():
            logger.error("Cannot show shop - managers not initialized")
            return

        try:
            from modules.shop import show_shop
            new_rp = show_shop(self.game_config.reflection_points)
            if new_rp != self.game_config.reflection_points:
                self.game_config.reflection_points = new_rp
                self.config_manager.save(self.game_config)
        except Exception as e:
            logger.error(f"Shop interface failed: {e}")
            print(f"\n{RED}Error accessing shop: {e}{RESET}")

    def _display_profile(self) -> None:
        """Display player profile information"""
        if not self._ensure_initialized():
            logger.error("Cannot display profile - managers not initialized")
            return

        try:
            print(f"\n{CYAN}🧬 Player Profile{RESET}")
            print(f"{WHITE}{'='*44}{RESET}")
            print(f"Trait Slots: {self.game_config.trait_slots}")
            print(f"Reflection Points: {self.game_config.reflection_points}")
            print(f"Unlocked Themes: {', '.join(self.game_config.unlocked_themes) or 'None'}")
            print(f"Audio Packs: {', '.join(self.game_config.unlocked_audio) or 'None'}")

            # Display achievements summary with null check
            if self.achievement_manager and self.achievement_manager.achievements:
                total = len(self.achievement_manager.achievements)
                unlocked = sum(1 for a in self.achievement_manager.achievements.values()
                             if a and a.unlocked)
                print(f"\nAchievements: {unlocked}/{total}")
            else:
                print("\nAchievements: Not available")

            print(f"{WHITE}{'='*44}{RESET}")
        except Exception as e:
            logger.error(f"Profile display failed: {e}")
            print(f"\n{RED}Error displaying profile: {e}{RESET}")

    def _display_settings(self) -> None:
        """Display game settings interface"""
        try:
            from modules.settings import display_settings
            if changes := display_settings(self.game_config):
                self.game_config = changes
                self.config_manager.save(self.game_config)
        except Exception as e:
            logger.error(f"Settings display failed: {e}")

    def _display_menu(self) -> None:
        """Display main menu"""
        print(f"{BLUE}{'='*44}")
        print(f"{WHITE}          WELCOME TO SIMULACRA SURVIVAL")
        print(f"{CYAN}             Breathing Interface Online")
        print(f"{WHITE}{'='*44}")

        options = [
            "Start New Survival Run",
            "View Trait Vault",
            "View Saved Highlights",
            "Merge Traits",
            "RP Shop",
            "View Player Profile",
            "Achievements",
            "Settings",
            "Credits",
            "Exit"
        ]

        for i, option in enumerate(options[:-1], 1):
            print(f"{PURPLE}[{i}] {option}{RESET}")
        print(f"{PURPLE}[0] {options[-1]}{RESET}")
        print(f"{BLUE}{'='*44}{RESET}")

    def _ensure_initialized(self) -> bool:
        """Verify all required managers are initialized"""
        if not all([self.config_manager, self.game_config,
                    self.vault_manager, self.achievement_manager,
                    self.highlight_manager]):
            logger.error("One or more required managers not initialized")
            return False
        return True

    def run(self) -> None:
        """Main launcher loop"""
        if not self._ensure_initialized():
            raise SystemExit("Cannot start - initialization incomplete")

        while True:
            try:
                os.system("cls" if os.name == "nt" else "clear")
                self._display_menu()
                choice = input(f"{WHITE}Please enter your choice: {RESET}").strip()

                match choice:
                    case "1":  # Start Run
                        if not self.vault_manager:
                            raise RuntimeError("Vault manager not initialized")
                        self.breathing_intro()
                        if loadout := select_trait_loadout(self.vault_manager):
                            run_simulacra(loadout)
                        input("\nPress Enter to continue...")

                    case "2":  # View Vault
                        if not self.vault_manager:
                            raise RuntimeError("Vault manager not initialized")
                        self.vault_manager.display_vault()
                        input("\nPress Enter to return...")

                    case "3":  # View Highlights
                        if not self.highlight_manager:
                            raise RuntimeError("Highlight manager not initialized")
                        self.highlight_manager.display_highlights()
                        input("\nPress Enter to return...")

                    case "4":  # Merge Traits
                        if not self.vault_manager:
                            raise RuntimeError("Vault manager not initialized")
                        self.vault_manager.merge_traits()
                        input("\nPress Enter to return...")

                    case "5":  # RP Shop
                        if not self.vault_manager:
                            raise RuntimeError("Vault manager not initialized")
                        self._show_shop()
                        input("\nPress Enter to return...")

                    case "6":  # Profile
                        if not self.vault_manager:
                            raise RuntimeError("Vault manager not initialized")
                        self._display_profile()
                        input("\nPress Enter to return...")

                    case "7":  # Achievements
                        if not self.achievement_manager:
                            raise RuntimeError("Achievement manager not initialized")
                        self.achievement_manager.display_achievements()
                        input("\nPress Enter to return...")

                    case "8":  # Settings
                        if not self.config_manager:
                            raise RuntimeError("Config manager not initialized")
                        self._display_settings()
                        input("\nPress Enter to return...")

                    case "9":  # Credits
                        display_credits()
                        input("\nPress Enter to return...")

                    case "0":  # Exit
                        print(f"\n{RED}Breathing terminated. See you next cycle.{RESET}")
                        break

                    case _:
                        print(f"{RED}Invalid input. Try again.{RESET}")
                        input("Press Enter to continue...")

            except Exception as e:
                logger.error(f"Main loop error: {e}")
                print(f"\n{RED}Error: {e}{RESET}")
                input("\nPress Enter to continue...")

    def _load_test_data(self):
        """Load test data for systems"""
        # Load test traits
        test_traits = [
            {
                'id': 'tough',
                'name': 'Tough',
                'tier': 1,
                'effects': [
                    {'type': 'hp', 'value': 10.0, 'text': 'Increases health', 'duration': None}
                ]
            }
        ]
        for trait in test_traits:
            self.trait_system.add_trait(trait['id'], trait)

        # Load test mutations
        test_mutations = [
            Mutation(
                id="rapid_healing",
                name="Rapid Healing",
                description="Heal faster over time",
                power=1.5
            )
        ]
        for mutation in test_mutations:
            self.mutation_system.add_mutation(mutation)


def main() -> None:
    """Main entry point"""
    try:
        # Initialize core systems
        trait_system = TraitSystem()
        mutation_system = MutationSystem()
        mutation_system._initialize_mutations()
        logger.info("Game initialized successfully")

        while True:
            choice = MenuScreen.show()

            if choice == 1:
                os.system('cls' if os.name == 'nt' else 'clear')
                game = SimulacraGame(trait_system, mutation_system)
                game.run()
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == 2:
                pass  # TODO: Add credits
            elif choice == 3:
                print(f"\n{Fore.RED}Exiting simulation...{Style.RESET_ALL}")
                time.sleep(1)
                break

    except Exception as e:
        logger.error(f"Game crashed: {e}")
        raise


if __name__ == "__main__":
    main()
