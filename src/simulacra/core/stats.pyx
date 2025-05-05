from dataclasses import dataclass, field
from typing import Dict, List, Optional, Final, ClassVar, Literal, Tuple
from modules.logger import logger
from enum import Enum
from copy import deepcopy
import numpy as np
from .shared_types import StatModifierData, ModifierType, MutationData


@dataclass
class StatModifier:
    """Represents a modification to a stat"""
    type: Literal["add", "multiply", "set"] = "add"
    value: float = 0.0
    duration: Optional[int] = None  # None means permanent


@dataclass
class PlayerStats:
    """Player statistics manager"""
    hp: float = 100.0
    max_hp: float = 100.0
    mutation_rate: float = 0.0
    resistances: Dict[str, float] = field(default_factory=dict)
    immunities: List[str] = field(default_factory=list)
    reflection_points: int = 0

    # Class variable for constants, not a dataclass field
    STAT_CAPS: ClassVar[Dict[str, float]] = {
        "hp": 1000.0,
        "mutation_rate": 100.0,
        "resistance": 100.0
    }

    def validate(self) -> bool:
        """Validate stat values"""
        self.hp = min(self.hp, self.max_hp)
        self.hp = max(0, self.hp)
        return True

    def apply_effect(self, effect: Dict) -> None:
        """Apply a single effect to player stats"""
        try:
            effect_obj = Effect(**effect)
            if not effect_obj.validate():
                raise ValueError("Invalid effect data")

            match effect_obj.type:
                case "hp_modifier":
                    self._modify_hp(effect_obj.value)
                case "mutation_rate_modifier":
                    self._modify_mutation_rate(effect_obj.value)
                case "resistance_modifier":
                    self._modify_resistance(effect_obj.target, effect_obj.value)
                case "disaster_immunity":
                    self._add_immunity(effect_obj.target)
                case _:
                    logger.warning(f"Unknown effect type: {effect_obj.type}")

        except Exception as e:
            logger.error(f"Failed to apply effect: {e}")
            raise

    def apply_modifier(self, mod: StatModifierData) -> bool:
        """Apply a stat modifier"""
        if not hasattr(self, mod.stat_name):
            return False

        current = getattr(self, mod.stat_name)
        match mod.mod_type:
            case ModifierType.ADD:
                setattr(self, mod.stat_name, current + mod.value)
            case ModifierType.MULTIPLY:
                setattr(self, mod.stat_name, current * mod.value)
            case ModifierType.SET:
                setattr(self, mod.stat_name, mod.value)

        return True

    def apply_modifiers_bulk(self, modifiers: List[Tuple[str, StatModifier]]) -> None:
        """Apply multiple stat modifiers in one pass"""
        for stat, modifier in modifiers:
            if hasattr(self, stat):
                current = getattr(self, stat)

                if modifier.type == "add":
                    new_value = current + modifier.value
                elif modifier.type == "multiply":
                    new_value = current * modifier.value
                else:  # set
                    new_value = modifier.value

                setattr(self, stat, min(new_value, self.STAT_CAPS.get(stat, new_value)))

    def apply_modifiers_vectorized(self, modifiers: List[Tuple[str, StatModifier]]) -> None:
        """Apply multiple modifiers using numpy for speed"""
        # Group modifiers by stat
        stat_groups = {}
        for stat, mod in modifiers:
            if stat not in stat_groups:
                stat_groups[stat] = []
            stat_groups[stat].append(mod)

        # Apply in batches
        for stat, mods in stat_groups.items():
            if hasattr(self, stat):
                current = getattr(self, stat)
                values = np.array([mod.value for mod in mods])
                types = np.array([mod.type for mod in mods])

                # Vectorized calculation
                new_value = current
                new_value += np.sum(values[types == "add"])
                new_value *= np.prod(values[types == "multiply"])

                # Apply cap
                setattr(self, stat, min(new_value, self.STAT_CAPS.get(stat, new_value)))

    def apply_modifiers_batch(self, modifiers: List[Tuple[str, StatModifier]]) -> None:
        """Apply multiple stat modifiers efficiently using numpy"""
        # Group by stat type for vectorized operations
        stat_groups: Dict[str, List[StatModifier]] = {}
        for stat, mod in modifiers:
            if stat not in stat_groups:
                stat_groups[stat] = []
            stat_groups[stat].append(mod)

        # Process each stat group
        for stat, mods in stat_groups.items():
            if not hasattr(self, stat):
                continue

            current = float(getattr(self, stat))
            values = np.array([mod.value for mod in mods])
            types = np.array([mod.type for mod in mods])

            # Vectorized operations
            additions = np.sum(values[types == "add"])
            multipliers = np.prod(values[types == "multiply"])

            # Apply changes
            new_value = (current + additions) * multipliers
            cap = self.STAT_CAPS.get(stat, float('inf'))
            setattr(self, stat, min(new_value, cap))

    def to_dict(self) -> dict:
        """Convert stats to dictionary for saving"""
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mutation_rate": self.mutation_rate,
            "resistances": self.resistances.copy(),
            "immunities": self.immunities.copy(),
            "reflection_points": self.reflection_points
        }

    def copy(self) -> 'PlayerStats':
        """Create a deep copy of stats"""
        return PlayerStats(
            hp=self.hp,
            max_hp=self.max_hp,
            mutation_rate=self.mutation_rate,
            resistances=deepcopy(self.resistances),
            immunities=self.immunities.copy(),
            reflection_points=self.reflection_points
        )

    def _modify_hp(self, percent: float) -> None:
        """Modify HP with percentage change"""
        delta = self.hp * (percent / 100)
        self.hp = min(self.max_hp, max(0, self.hp + delta))
        logger.debug(f"HP modified by {percent}% -> New HP: {self.hp:.1f}")

    def _modify_mutation_rate(self, value: float) -> None:
        """Modify mutation rate with bounds checking"""
        self.mutation_rate = max(0, min(
            self.STAT_CAPS["mutation_rate"],
            self.mutation_rate + value
        ))
        logger.debug(f"Mutation rate: {self.mutation_rate:.1f}%")

    def _modify_resistance(self, target: str, value: float) -> None:
        """Modify resistance with bounds checking"""
        if not target:
            return
        current = self.resistances.get(target, 0)
        self.resistances[target] = max(0, min(
            self.STAT_CAPS["resistance"],
            current + value
        ))
        logger.debug(f"{target} resistance: {self.resistances[target]}%")

    def _add_immunity(self, target: str) -> None:
        """Add new immunity if valid"""
        if target and target not in self.immunities:
            self.immunities.append(target)
            logger.debug(f"Added immunity to {target}")

    def apply_mutation(self, mutation: MutationData) -> None:
        """Apply mutation effects to stats"""
        for effect in mutation.effects:
            self.apply_modifier(StatModifierData(
                stat=effect.stat,
                type=effect.type,
                value=effect.value
            ))
