"""Game balance constants"""
from typing import Final

# Base Values
BASE_HP: Final[float] = 100.0
BASE_ENTROPY_DRAIN: Final[float] = 1.2
MAX_ENTROPY_DRAIN: Final[float] = 5.0
ENTROPY_ACCELERATION: Final[float] = 0.008

# Mutation Settings
BASE_REGEN_AMOUNT: Final[float] = 1.5
MAX_MUTATION_RATE: Final[float] = 100.0
RESISTANCE_CAP: Final[float] = 50.0
RESISTANCE_DECAY: Final[float] = 0.2
RESISTANCE_GAIN: Final[float] = 0.4

# Disaster Settings
MAX_RECENT_DISASTERS: Final[int] = 5
DISASTER_BASE_INTERVAL: Final[int] = 25
DISASTER_MIN_INTERVAL: Final[int] = 15
INITIAL_GRACE_PERIOD: Final[int] = 10

# Game Balance
REGEN_INTERVAL: Final[int] = 8
EARLY_GAME_SCALING: Final[float] = 0.02
