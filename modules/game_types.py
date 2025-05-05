"""
Game types module for Simulacra
Contains type definitions, data classes, and protocols used throughout the game
"""
from typing import TypeVar, Dict, List, Union, Literal, Protocol, TypedDict, Optional
from dataclasses import dataclass, field
from enum import Enum

# ======== Type Variables ========
GameID = TypeVar('GameID', str, int)
PlayerID = TypeVar('PlayerID', str, int)


# ======== Game State Types ========
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


# ======== Effect Types ========
class EffectType(Enum):
    ADD = "add"
    MULTIPLY = "multiply"
    SET = "set"


GameEffect = TypedDict('GameEffect', {
    'type': Literal['hp', 'mutation', 'resistance', 'immunity'],
    'value': float,
    'text': str,
    'duration': Optional[int]
})


# ======== Mutation System ========
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


# ======== Trait System ========
TraitData = TypedDict('TraitData', {
    'id': str,
    'name': str,
    'tier': int,
    'effects': List[GameEffect]
})


# ======== Data Protocols ========
class Saveable(Protocol):
    """Protocol for objects that can be saved to disk"""

    def to_dict(self) -> Dict: ...


class Loadable(Protocol):
    """Protocol for objects that can be loaded from disk"""

    @classmethod
    def from_dict(cls, data: Dict) -> 'Loadable': ...
