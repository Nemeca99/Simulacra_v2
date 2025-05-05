from typing import Dict, Callable, Optional, Final
from dataclasses import dataclass
import random

from modules.logger import logger

@dataclass
class GameState:
    """Current game state"""
    hp: float
    rp: int
    mutation_rate: float
    traits: list
    mutations: list
    handle_mutation: Callable
    apply_stats: Callable

    def modify_hp(self, amount: float) -> None:
        self.hp = max(0, min(100, self.hp + amount))

    def add_rp(self, amount: int) -> None:
        self.rp = max(0, self.rp + amount)

class ProcSystem:
    """Handles procedural effects"""
    EFFECTS: Final[Dict[str, Callable]] = {
        "heal": lambda state: state.modify_hp(5),
        "regen": lambda state: state.modify_hp(2),
        "explode": lambda state: state.modify_hp(-10),
        "gain_rp": lambda state: state.add_rp(1),
        "burst_rp": lambda state: state.add_rp(3)
    }

    @staticmethod
    def trigger(effect: str, chance: int, state: GameState) -> Optional[str]:
        """Try to trigger a proc effect"""
        try:
            if random.randint(1, 100) <= chance:
                ProcSystem.EFFECTS[effect](state)
                return effect
            return None
        except Exception as e:
            logger.error(f"Proc effect failed: {e}")
            return None

def roll_proc_effect(effect_string: str, state: Dict[str, Any]) -> Optional[str]:
    """
    Parses and triggers procedural mutation effects.

    Args:
        effect_string: Format like '12% chance to gain rp'
        state: Current game state dictionary

    Returns:
        str: Name of triggered effect, or None if no trigger

    Raises:
        ValueError: If effect string is malformed
    """
    try:
        parts = effect_string.lower().split(" chance to ")
        if len(parts) != 2:
            raise ValueError(f"Invalid effect format: {effect_string}")

        percent_str, action_str = parts
        chance = int(percent_str.replace("%", "").strip())

        if chance < 0 or chance > 100:
            raise ValueError(f"Invalid chance percentage: {chance}")

        if action_str not in ProcSystem.EFFECTS:
            logger.warning(f"Unknown proc action: {action_str}")
            return None

        if random.randint(1, 100) <= chance:
            print(f"🧪 PROC TRIGGERED: {action_str.upper()}!")
            game_state = GameState(**state)
            ProcSystem.EFFECTS[action_str](game_state)

            # Update original state dict
            state.update({
                'hp': game_state.hp,
                'rp': game_state.rp,
                'mutation_rate': game_state.mutation_rate,
                'mutations': game_state.mutations
            })
            return action_str

        return None

    except Exception as e:
        logger.error(f"Failed to process effect: {effect_string} - {str(e)}")
        return None

def multi_mutate(state: GameState, count: int) -> None:
    """Apply multiple mutations"""
    for _ in range(count):
        result = state.handle_mutation(
            state.traits,
            state.mutations,
            state.mutation_rate
        )

        if result:
            state.mutations.append({
                "name": result["mutation"].split(" — ")[0],
                "effect": result["generated"]
            })

            new_hp, new_rate = state.apply_stats(
                state.hp,
                state.mutation_rate,
                result["effects"]
            )
            state.hp = new_hp
            state.mutation_rate = new_rate
            state.rp += result.get("rp_reward", 0)
