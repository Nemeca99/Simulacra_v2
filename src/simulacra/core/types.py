"""Core game types"""
from typing import TypeVar, Dict, List, Union, Literal, Protocol, TypedDict, Optional
from dataclasses import dataclass, field
from enum import Enum

# Type variables
GameID = TypeVar('GameID', str, int)
PlayerID = TypeVar('PlayerID', str, int)


# Game state types
class GameState(TypedDict):
    id: GameID
    players: Dict[PlayerID, 'PlayerState']
    active: bool
    turn: int


class PlayerState(TypedDict):
    id: PlayerID
    name: str
    level: int
    health: float
    experience: int


# Effect types
class EffectType(Enum):
    HP = "hp"
    IMMUNITY = "immunity"
    RESISTANCE = "resistance"
    DAMAGE = "damage"
    SPEED = "speed"
    TEMPORARY = "temporary"


# Game effects with duration support
GameEffect = TypedDict('GameEffect', {
    'type': str,
    'value': float,
    'text': str,
    'duration': Optional[int],
    'remaining': Optional[int]
})

# Requirements for traits
TraitRequirement = TypedDict('TraitRequirement', {
    'trait_id': str,
    'level': int,
    'stat': Optional[str],
    'value': Optional[float]
})

# Enhanced trait data
TraitData = TypedDict('TraitData', {
    'id': str,
    'name': str,
    'tier': int,
    'effects': List[GameEffect],
    'requirements': List[TraitRequirement]
})


# Mutation system
@dataclass
class StatModifier:
    type: str
    value: float


@dataclass
class MutationEffect:
    stat: str
    type: str
    value: float


@dataclass
class Mutation:
    id: str
    name: str
    effects: List[MutationEffect] = field(default_factory=list)


# Protocol definitions
class Saveable(Protocol):
    """Protocol for objects that can be saved to disk"""

    def to_dict(self) -> Dict: ...


class Loadable(Protocol):
    """Protocol for objects that can be loaded from disk"""

    @classmethod
    def from_dict(cls, data: Dict) -> 'Loadable': ...
