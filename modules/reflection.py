from typing import Dict, Literal, Final
from dataclasses import dataclass

@dataclass(frozen=True)
class ReflectionConfig:
    """Configuration for reflection point rewards"""
    passive: Final[int] = 1
    mutation_bonus: Final[int] = 2
    disaster_minor: Final[int] = 1
    disaster_major: Final[int] = 3
    collapse_bonus: Final[int] = 10
    milestone: Final[int] = 5

EventType = Literal[
    "passive", "mutation_bonus", "disaster_minor",
    "disaster_major", "collapse_bonus", "milestone"
]

class ReflectionSystem:
    """Handles reflection point calculations and rewards"""
    def __init__(self):
        self.config = ReflectionConfig()
        self._milestones = {60, 180, 300, 600}  # Time-based milestones

    def grant_points(self, event_type: EventType) -> int:
        """Grant reflection points for an event"""
        return getattr(self.config, event_type)

    def check_milestone(self, time: int) -> bool:
        """Check if current time hits a milestone"""
        return time in self._milestones
