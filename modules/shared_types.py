from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class ModifierType(str, Enum):
    ADD = "add"
    MULTIPLY = "multiply"
    SET = "set"


@dataclass
class StatModifierData:
    """Base data structure for stat modifications"""
    stat_name: str
    mod_type: ModifierType
    value: float
    duration: Optional[int] = None


@dataclass
class MutationEffectData:
    """Base structure for mutation effects"""
    target_stat: str
    effect_type: ModifierType
    magnitude: float


@dataclass
class MutationData:
    """Data structure for mutations"""
    id: str
    name: str
    effects: List[MutationEffectData] = field(default_factory=list)
