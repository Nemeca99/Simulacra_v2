# hud.py

from typing import List, Dict, Final, Optional
from dataclasses import dataclass, field
import os
import datetime
from colorama import Fore, Style, Back, init
import time
import sys

from simulacra.core.traits import TraitSystem
from simulacra.core.player import Player
from simulacra.core.mutations import MutationSystem, Mutation, MutationType
from simulacra.core.constants import (
    BASE_HP,
    MAX_RECENT_DISASTERS
)
from modules.utils import format_time
from modules.error_handler import handle_errors, GameError, handle_error
from modules.logger import logger
from modules.constants import (
    BASE_HP,
    BASE_ENTROPY_DRAIN,
    MAX_RECENT_DISASTERS,
    DATA_DIR
)

init(autoreset=True)


@dataclass
class HUDAnimation:
    """Animation configuration"""
    DAMAGE_FLASH_DURATION: float = 0.1
    HEAL_FLASH_DURATION: float = 0.1
    GAME_OVER_DELAY: float = 0.05
    DISASTER_WARNING_BLINK: int = 3


@dataclass
class HUDColors:
    """Enhanced color configuration"""
    HEALTH_CRITICAL: str = Fore.RED + Style.BRIGHT
    HEALTH_LOW: str = Fore.YELLOW + Style.BRIGHT
    HEALTH_GOOD: str = Fore.GREEN + Style.BRIGHT
    MUTATION: str = Fore.MAGENTA + Style.BRIGHT
    ENTROPY: str = Fore.RED
    INFO: str = Fore.CYAN
    WARNING: str = Fore.YELLOW + Style.BRIGHT
    RESET: str = Style.RESET_ALL
    HEADER_BG: str = Back.BLUE
    DISASTER_BG: str = Back.RED
    HEAL_FLASH: str = Back.GREEN + Fore.WHITE + Style.BRIGHT
    DAMAGE_FLASH: str = Back.RED + Fore.WHITE + Style.BRIGHT


@dataclass
class HUDConfig:
    """Enhanced HUD configuration"""
    MUTATION_TYPES: Dict[str, str] = field(default_factory=lambda: {
        'physical': '💪',
        'mental': '🧠',
        'special': '✨',
        'adaptive': '🧬',
        'unstable': '☢️'
    })
    HEALTH_THRESHOLDS: Dict[str, float] = field(default_factory=lambda: {
        'critical': 25.0,
        'low': 50.0
    })
    DISASTER_TYPES: Dict[str, str] = field(default_factory=lambda: {
        'radiation': '☢️',
        'chemical': '⚗️',
        'biological': '🦠',
        'physical': '💥',
        'psychic': '🧠'
    })
    UPDATE_INTERVAL: float = 1.0
    SHOW_DECIMALS: bool = True
    MAX_DISASTERS: int = 5


class HUDManager:
    """Manages HUD display and updates"""
    colors = HUDColors()
    config = HUDConfig()
    anim = HUDAnimation()

    @staticmethod
    @handle_errors()
    def clear_screen() -> None:
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def format_hp(current: float, maximum: float) -> str:
        """Format HP display with proper rounding"""
        return f"{max(0, round(current, 1))}/{round(maximum, 1)}"

    @classmethod
    def update_hud(cls,
                  player: Player,
                  trait_system: TraitSystem,
                  mutation_system: MutationSystem,
                  survival_seconds: int,
                  entropy_drain: float,
                  recent_disasters: List[Dict]) -> None:
        """Update the HUD display with enhanced visuals"""
        cls.clear_screen()

        # Header with background
        print(f"{cls.colors.HEADER_BG}{cls.colors.INFO}╔{'═' * 38}╗{cls.colors.RESET}")
        print(f"{cls.colors.HEADER_BG}{cls.colors.INFO}║ {'[ INHALE ]':^36} ║{cls.colors.RESET}")
        print(f"{cls.colors.HEADER_BG}{cls.colors.INFO}╚{'═' * 38}╝{cls.colors.RESET}")

        # Stats section with dynamic coloring
        health_color = cls._get_health_color(player.health)
        print(f"\n{health_color}🫀 HP: {cls._format_stat(player.health)}{cls.colors.RESET}")
        print(f"{cls.colors.MUTATION}🌀 Mutation: {cls._format_stat(player.mutation_rate)}%{cls.colors.RESET}")
        print(f"{cls.colors.ENTROPY}💀 Entropy: {entropy_drain:.2f} HP/s{cls.colors.RESET}")
        print(f"{cls.colors.INFO}⏳ Time: {survival_seconds//60}m {survival_seconds%60}s{cls.colors.RESET}")

        # Separators
        print(f"\n{cls.colors.INFO}{'─' * 40}{cls.colors.RESET}")

        # Active effects
        cls._display_traits(player, trait_system)
        cls._display_mutations(mutation_system)
        cls._display_disasters(recent_disasters)
        cls._display_stats(player)

    @classmethod
    def _get_health_color(cls, health: float) -> str:
        """Get appropriate color for health display"""
        if health <= cls.config.HEALTH_THRESHOLDS['critical']:
            return cls.colors.HEALTH_CRITICAL
        elif health <= cls.config.HEALTH_THRESHOLDS['low']:
            return cls.colors.HEALTH_LOW
        return cls.colors.HEALTH_GOOD

    @classmethod
    def _display_header(cls, player: Player, entropy_drain: float,
                       survival_seconds: int) -> None:
        """Display header section with player stats"""
        print(f"{cls.colors.INFO}[ inhale ]{cls.colors.RESET}")
        print("=" * 40)
        print(f"🫀 HP: {cls._format_stat(player.health)}")  # TODO: Add max_health
        print(f"🌀 Mutation Rate: {cls._format_stat(player.mutation_rate)}%")
        print(f"💀 Entropy Drain: {entropy_drain:.2f} HP/s")
        print(f"⏳ Survival Time: {survival_seconds//60}m {survival_seconds%60}s")
        print("=" * 40)

    @classmethod
    def _display_traits(cls, player: Player, trait_system: TraitSystem) -> None:
        """Display active traits"""
        print("\n🔹 Active Traits:")
        active_traits = [trait_system.get_trait(tid) for tid in player.active_traits]
        if active_traits:
            for trait in active_traits:
                if trait:  # Check if trait exists
                    print(f"  - {trait['name']}")
                    for effect in trait.get('effects', []):
                        duration = f" ({effect['remaining']}s)" if effect.get('remaining') else ""
                        print(f"    • {effect['text']}{duration}")
        else:
            print("  (none)")

    @classmethod
    def _display_mutations(cls, mutation_system: MutationSystem) -> None:
        """Display mutations section with colors based on type"""
        print("\n🔸 Mutations:")
        mutations = mutation_system.get_mutation_list()
        if mutations:
            for mutation in mutations:
                icon = cls.config.MUTATION_TYPES.get(mutation.type.value, '❓')
                print(f"  {icon} {mutation.name} — {mutation.description}")
        else:
            print("  (none)")

    @classmethod
    def _display_disasters(cls, recent_disasters: List[Dict]) -> None:
        """Display recent disasters with enhanced formatting"""
        print(f"\n{cls.colors.WARNING}⚠️ Recent Disasters:{cls.colors.RESET}")
        if recent_disasters:
            for disaster in recent_disasters:
                print(f"{cls.colors.DISASTER_BG} {disaster['name']} {cls.colors.RESET}")
                print(f"  💀 Damage: {disaster['damage']:.1f}")
                print(f"  ⌛ {disaster['time']}s ago")
                print()
        else:
            print("  (none)\n")

    @classmethod
    def _display_stats(cls, player: Player) -> None:
        """Display current player stats"""
        print("\n📊 Current Stats:")
        print(f"  - Speed: {cls._format_stat(player.speed)}x")

        # Format resistances
        resistances = [
            f"{k}: {cls._format_resistance(v)}"
            for k, v in player.resistances.items()
        ]
        print(f"  - Resistances: {', '.join(resistances) if resistances else 'None'}")
        print(f"  - Immunities: {', '.join(player.immunities) if player.immunities else 'None'}")

    @staticmethod
    def _format_stat(value: float) -> str:
        """Format a stat value"""
        return f"{max(0, round(value, 1))}"

    @staticmethod
    def _format_resistance(value: float) -> str:
        """Format resistance values"""
        return f"{round(value, 1)}%"

    @classmethod
    def flash_damage(cls, amount: float) -> None:
        """Flash screen on damage"""
        if amount > 0:
            sys.stdout.write(cls.colors.DAMAGE_FLASH)
            print(f"\n💥 DAMAGE: -{amount:.1f}")
            sys.stdout.write(cls.colors.RESET)
            sys.stdout.flush()
            time.sleep(cls.anim.DAMAGE_FLASH_DURATION)

    @classmethod
    def flash_heal(cls, amount: float) -> None:
        """Flash screen on healing"""
        if amount > 0:
            sys.stdout.write(cls.colors.HEAL_FLASH)
            print(f"\n💚 HEAL: +{amount:.1f}")
            sys.stdout.write(cls.colors.RESET)
            sys.stdout.flush()
            time.sleep(cls.anim.HEAL_FLASH_DURATION)

    @classmethod
    def show_game_over(cls, survival_time: int, mutations: List[Mutation],
                      max_health: float, final_entropy: float) -> None:
        """Display animated game over screen"""
        cls.clear_screen()
        text = """
╔══════════════════════════════════════╗
║             GAME OVER                ║
╚══════════════════════════════════════╝
"""
        for char in text:
            sys.stdout.write(cls.colors.WARNING + char + cls.colors.RESET)
            sys.stdout.flush()
            time.sleep(cls.anim.GAME_OVER_DELAY)

        print(f"\n{cls.colors.INFO}Final Statistics:{cls.colors.RESET}")
        print(f"⌛ Survival Time: {survival_time//60}m {survival_time%60}s")
        print(f"🧬 Mutations: {len(mutations)}")
        print(f"💀 Final Entropy: {final_entropy:.2f} HP/s")

    @classmethod
    def display_disaster_warning(cls, disaster_name: str) -> None:
        """Show blinking disaster warning"""
        for _ in range(cls.anim.DISASTER_WARNING_BLINK):
            sys.stdout.write(cls.colors.DISASTER_BG + cls.colors.WARNING)
            print(f"\n⚠️ INCOMING: {disaster_name} ⚠️")
            sys.stdout.write(cls.colors.RESET)
            sys.stdout.flush()
            time.sleep(0.2)
            cls.clear_screen()
            time.sleep(0.2)


# Update collapse summary for new systems
def show_collapse_summary(
    player: Player,
    trait_system: TraitSystem,
    mutation_system: MutationSystem,
    entropy_drain: float,
    survival_seconds: int
) -> None:
    """Display end of run summary with new system data"""
    print("\n[ exhale ]")
    print("=" * 40)
    print(f"💀 Run Collapsed")
    print(f"⌛ Survival Time: {survival_seconds//60}m {survival_seconds%60}s")
    print(f"🫀 Final HP: {player.health:.1f}")
    print(f"🌀 Final Mutation Rate: {player.mutation_rate:.2f}%")
    print(f"♨️ Final Entropy Drain: {entropy_drain:.2f} HP/s")

    # Display final traits
    active_traits = [
        trait_system.get_trait(tid)
        for tid in player.active_traits
    ]
    print("\n🔹 Final Traits:")
    if active_traits:
        for trait in active_traits:
            print(f"  - {trait['name']}")
            for effect in trait['effects']:
                print(f"    • {effect['text']}")
    else:
        print("  (none)")

    # Display mutations
    mutations = [
        mutation_system.get_mutation(mid)
        for mid in mutation_system.active_mutations
    ]
    print("\n🔸 Acquired Mutations:")
    if mutations:
        for mutation in mutations:
            print(f"  - {mutation.name} — {mutation.description}")
    else:
        print("  (none)")

    # Display resistances
    print("\n🛡️ Final Resistances:")
    if player.resistances:
        for dtype, value in player.resistances.items():
            print(f"  - {dtype.capitalize()}: {value}%")
    else:
        print("  (none)")

    print("=" * 40)
