from typing import List, Dict, Optional
import time
import random
from colorama import Fore, Style

# Core imports
from simulacra.core.traits import TraitSystem
from simulacra.core.player import Player, PlayerConfig
from simulacra.core.mutations import MutationSystem, Mutation, MutationType
from simulacra.core.disasters import DisasterSystem, Disaster
from simulacra.core.constants import (
    BASE_HP,
    BASE_ENTROPY_DRAIN,
    MAX_ENTROPY_DRAIN,
    ENTROPY_ACCELERATION,
    BASE_REGEN_AMOUNT,
    RESISTANCE_CAP,
    MAX_MUTATION_RATE,
    MAX_RECENT_DISASTERS,
    RESISTANCE_GAIN
)

# UI imports
from simulacra.ui.hud import HUDManager
from simulacra.ui.sound import SoundManager
from simulacra.ui.start_screen import StartScreen

# Logging
from modules.logger import logger


def normalize_trait(trait: Dict) -> Dict:
    """Ensure trait has required structure"""
    if not isinstance(trait, dict):
        return {
            'name': str(trait),
            'description': '',
            'effects': {},
            'tier': 1,
            'rarity': 'common'
        }

    # Ensure all required fields exist
    default_trait = {
        'name': trait.get('name', 'Unknown'),
        'description': trait.get('description', ''),
        'effects': trait.get('effects', {}),
        'tier': trait.get('tier', 1),
        'rarity': trait.get('rarity', 'common')
    }

    return default_trait


class SimulacraGame:

    def __init__(self, trait_system: TraitSystem, mutation_system: MutationSystem):
        self.trait_system = trait_system
        self.mutation_system = mutation_system
        self.disaster_system = DisasterSystem()  # Add disaster system
        self.player = Player(
            id="player1",
            name="Player",
            config=PlayerConfig()
        )
        self.entropy_drain = 0
        self.survival_seconds = 0
        self.recent_disasters = []
        self.grace_period = 3
        self.regen_tick = 0
        self.REGEN_INTERVAL = 8
        self.disaster_count = 0  # Add disaster counter
        self.is_running = False
        self.game_over = False
        self._initialize_game()

        # Ensure player starts with full health
        self.player.health = BASE_HP

    def _initialize_game(self) -> None:
        """Initialize game state"""
        self._add_test_mutations()
        logger.info("Game initialized")

    def _add_test_mutations(self) -> None:
        """Add initial mutations"""
        initial_mutations = [
            Mutation(
                id="regen",
                name="Regeneration",
                description="Slowly heal over time",
                type=MutationType.PHYSICAL
            ),
            Mutation(
                id="thick_skin",
                name="Thick Skin",
                description="Reduces entropy damage",
                type=MutationType.PHYSICAL
            ),
            Mutation(
                id="adaptive",
                name="Adaptive Tissue",
                description="Gain resistance to recent damage types",
                type=MutationType.ADAPTIVE
            ),
            Mutation(
                id="unstable",
                name="Unstable DNA",
                description="Higher mutation chance but increased entropy",
                type=MutationType.UNSTABLE
            )
        ]
        for mutation in initial_mutations:
            self.mutation_system.add_mutation(mutation)

    def _update_display(self) -> None:
        """Update game display"""
        HUDManager.update_hud(
            self.player,
            self.trait_system,
            self.mutation_system,
            self.survival_seconds,
            self.entropy_drain,
            self.recent_disasters
        )

    def run(self) -> None:
        """Run the game loop"""
        StartScreen.show_title()
        logger.info("Starting new game")
        self.is_running = True

        while self.is_running:
            try:
                # Check for game over condition first
                if self.player.health <= 0:
                    self.game_over = True
                    break

                self.survival_seconds += 1

                # Handle grace period
                if self.survival_seconds > self.grace_period:
                    # Calculate entropy after grace period
                    current_entropy = BASE_ENTROPY_DRAIN + (
                        (self.survival_seconds - self.grace_period) *
                        ENTROPY_ACCELERATION
                    )
                    self.entropy_drain = min(MAX_ENTROPY_DRAIN, current_entropy)
                    self.player.health = max(0, self.player.health - self.entropy_drain)

                # Process mutations and update display
                self._handle_mutations()
                self._update_display()

                time.sleep(1)

            except KeyboardInterrupt:
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Game loop error: {e}")
                self.is_running = False
                break

        # Show game over screen if health reached 0
        if self.game_over:
            self._show_game_over()
            logger.info(f"Game Over! Survived for {self.survival_seconds} seconds")

    def _handle_mutations(self) -> None:
        """Process mutation effects"""
        self.regen_tick += 1

        if self.regen_tick >= self.REGEN_INTERVAL:
            for mutation in self.mutation_system.get_mutation_list():
                if mutation.id == "regen":
                    heal_amount = mutation.power * BASE_REGEN_AMOUNT
                    self.player.modify_health(heal_amount)
            self.regen_tick = 0

    def _trigger_disaster(self) -> None:
        """Handle disaster events"""
        disaster = self.disaster_system.trigger_random_disaster(self.survival_seconds)
        if disaster:
            HUDManager.display_disaster_warning(disaster.name)
            SoundManager.play('disaster')

            # Calculate scaled damage
            scaled_damage = disaster.get_scaled_damage(self.survival_seconds, self.disaster_count)
            final_damage = self._calculate_disaster_damage(disaster, scaled_damage)

            self._handle_damage(final_damage)
            self._update_disaster_history(disaster, final_damage)
            self._handle_mutation_chance(disaster)

            self.disaster_count += 1

    def _calculate_disaster_damage(self, disaster: Disaster, base_damage: float) -> float:
        """Calculate final disaster damage with resistances"""
        if disaster.type.value in self.player.resistances:
            resistance = min(RESISTANCE_CAP, self.player.resistances[disaster.type.value])
            base_damage *= (1.0 - (resistance / 100.0))
        return max(base_damage * 0.2, base_damage)

    def _update_disaster_history(self, disaster: Disaster, damage: float) -> None:
        """Update recent disasters list"""
        disaster_info = disaster.to_dict()
        disaster_info.update({
            'damage': round(damage, 1),
            'time': self.survival_seconds
        })

        self.recent_disasters.append(disaster_info)
        while len(self.recent_disasters) > MAX_RECENT_DISASTERS:
            self.recent_disasters.pop(0)

    def _handle_mutation_chance(self, disaster: Disaster) -> None:
        """Handle mutation chance from disasters"""
        if random.random() * 100 < disaster.mutation_chance:
            mutation_gain = random.uniform(1.0, 3.0)
            self.player.mutation_rate = min(MAX_MUTATION_RATE,
                                          self.player.mutation_rate + mutation_gain)

    def _handle_damage(self, amount: float) -> None:
        """Handle damage with effects"""
        old_health = self.player.health
        self.player.health = max(0, self.player.health - amount)
        damage_dealt = old_health - self.player.health

        if damage_dealt > 0:
            HUDManager.flash_damage(damage_dealt)
            SoundManager.play('damage')

    def _handle_healing(self, amount: float) -> None:
        """Handle healing with effects"""
        old_health = self.player.health
        self.player.health = min(100, self.player.health + amount)
        healing_done = self.player.health - old_health

        if healing_done > 0:
            HUDManager.flash_heal(healing_done)
            SoundManager.play('heal')

    def _show_game_over(self) -> None:
        """Display game over screen"""
        HUDManager.show_game_over(
            self.survival_seconds,
            list(self.mutation_system.active_mutations),
            BASE_HP,
            self.entropy_drain
        )

    def game_over(self) -> None:
        """Handle game over with effects"""
        SoundManager.play('game_over')
        HUDManager.show_game_over(
            self.survival_seconds,
            list(self.mutation_system.active_mutations),
            self.player.health,
            self.entropy_drain
        )


def run_simulacra(loadout: List[Dict]) -> None:
    """Run main game simulation"""
    if not loadout:
        logger.error("No loadout provided!")
        return

    logger.info("Starting new run...", Fore.CYAN)

    # Process traits and calculate initial stats
    processed_loadout = [normalize_trait(trait) for trait in loadout]
    stats = calculate_initial_stats(processed_loadout)

    survival_seconds = 0
    entropy_drain = BASE_ENTROPY_DRAIN
    mutations = []
    recent_disasters = []
    mutation_system = MutationSystem()

    try:
        while stats['current_hp'] > 0:
            survival_seconds += 1

            # Check for mutations
            if mutation := mutation_system.check_mutation(stats['mutation_rate']):
                mutations.append(mutation)
                logger.info(f"🧬 New mutation: {mutation['name']} - {mutation['effect']}", Fore.GREEN)

                # Apply mutation effects
                effect = mutation['mechanical_effect']
                if effect['type'] == 'entropy_reduction':
                    stats['entropy_reduction'] = stats.get('entropy_reduction', 0) + effect['value']
                elif effect['type'] == 'max_hp':
                    hp_increase = stats['max_hp'] * (effect['value'] / 100)
                    stats['max_hp'] += hp_increase
                    stats['current_hp'] += hp_increase
                elif effect['type'] == 'mutation_rate':
                    stats['mutation_rate'] += effect['value']
                elif effect['type'] == 'resistance_all':
                    for key in stats['resistances'].keys():
                        stats['resistances'][key] = min(100, stats['resistances'].get(key, 0) + effect['value'])

            # Apply entropy drain with reduction
            entropy_reduction = stats.get('entropy_reduction', 0) / 100
            actual_drain = entropy_drain * (1 - entropy_reduction)
            stats['current_hp'] = max(0, stats['current_hp'] - actual_drain)

            # Handle disasters with proper resistance
            if survival_seconds % DISASTER_INTERVAL == 0:
                disaster = DisasterSystem().generate_disaster()
                if disaster["type"].lower() in stats["immunities"]:
                    logger.info(f"🛡️ Immune to {disaster['type']} disasters!", Fore.GREEN)
                else:
                    base_damage = DisasterSystem().calculate_base_damage(disaster)
                    resistance = stats['resistances'].get(disaster['type'].lower(), 0) / 100
                    actual_damage = base_damage * (1 - resistance)

                    if actual_damage > 0:
                        stats['current_hp'] = max(0, stats['current_hp'] - actual_damage)
                        recent_disasters.append(disaster)
                        recent_disasters = recent_disasters[-MAX_RECENT_DISASTERS:]
                        logger.debug(f"Disaster damage after resistance: {actual_damage:.1f}")

            update_hud(stats, processed_loadout, mutations, survival_seconds, entropy_drain, recent_disasters)
            time.sleep(1)

    except Exception as e:
        logger.error(f"Main loop error: {str(e)}")

    finally:
        show_collapse_summary(
            hp_end=stats['current_hp'],
            mutation_rate_end=stats['mutation_rate'],
            entropy_drain=entropy_drain,
            survival_seconds=survival_seconds,
            mutations=mutations,
            traits=processed_loadout,
            resistance=stats.get('resistances', {})
        )


def select_trait_loadout(vault_manager) -> Optional[List[Dict]]:
    """Allow player to select trait loadout"""
    if not vault_manager.vault:
        logger.error("No traits in vault!")
        print(f"\n{Fore.RED}You need to unlock traits in the RP Shop first!{Style.RESET_ALL}")
        return None

    config = ConfigurationManager().load_config()
    slot_count = config.trait_slots

    choice = input("\nChoose a loadout:\n"
                  "1. Pick traits manually\n"
                  "2. Use favorite loadout\n"
                  "3. Random loadout\n"
                  "0. Cancel\n"
                  "Enter choice: ")

    if choice == "3":
        # Random loadout
        if len(vault_manager.vault) < slot_count:
            print(f"\n{Fore.YELLOW}Warning: Not enough traits for a full loadout!{Style.RESET_ALL}")
            slot_count = len(vault_manager.vault)
        selected = random.sample(vault_manager.vault, slot_count)
        return [trait for trait in selected]

    return None
