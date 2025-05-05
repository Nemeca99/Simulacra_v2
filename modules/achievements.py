# modules/achievements.py

from dataclasses import dataclass, asdict, field
from typing import Dict, Optional, List, Final, Set
from pathlib import Path
import json
import os
from enum import Enum, auto, IntEnum
from datetime import datetime
from functools import lru_cache
from collections import defaultdict
import numpy as np
from numpy.typing import NDArray

from colorama import Fore, Style
from modules.logger import logger
from modules.constants import DATA_DIR


class AchievementCategory(IntEnum):
    """Using IntEnum for faster comparisons"""
    SURVIVAL = 0
    MUTATION = 1
    DISASTER = 2
    COLLECTION = 3
    SPECIAL = 4


@dataclass
class Achievement:
    """Enhanced achievement structure with validation"""
    id: str
    name: str
    description: str
    category: AchievementCategory
    hidden: bool = False
    unlocked: bool = False
    unlock_date: Optional[str] = None
    progress: int = 0
    max_progress: int = 1

    def validate(self) -> bool:
        """Validate achievement data"""
        return all([
            isinstance(self.id, str) and len(self.id) > 0,
            isinstance(self.name, str) and len(self.name) > 0,
            isinstance(self.description, str),
            isinstance(self.category, AchievementCategory),
            isinstance(self.progress, int),
            isinstance(self.max_progress, int),
            self.progress <= self.max_progress
        ])

    def is_unlocked(self) -> bool:
        return self.unlocked

    def is_hidden(self) -> bool:
        return self.hidden and not self.unlocked

    def to_dict(self) -> dict:
        """Convert achievement to JSON-serializable dict"""
        data = asdict(self)
        data['category'] = self.category.name
        return data


class AchievementManager:
    """Manages game achievements"""
    ACHIEVEMENTS_PATH: Final[Path] = DATA_DIR / "achievements.json"

    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        # Array-based storage for vectorized operations
        self._category_array: NDArray[np.int32] = np.array([], dtype=np.int32)
        self._unlocked_array: NDArray[np.bool_] = np.array([], dtype=bool)
        # Cache-based storage for lookups
        self._category_cache: Dict[AchievementCategory, List[str]] = defaultdict(list)
        self._unlocked_cache: Set[str] = set()
        self._load_achievements()

    def _load_achievements(self) -> None:
        """Load achievements from file"""
        try:
            if self.ACHIEVEMENTS_PATH.exists():
                with open(self.ACHIEVEMENTS_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.achievements = {
                        id: Achievement(
                            **{**ach_data,
                               'category': AchievementCategory[ach_data['category']]
                            }
                        )
                        for id, ach_data in data.items()
                    }
            else:
                self._initialize_default_achievements()
        except Exception as e:
            logger.error(f"Failed to load achievements: {e}")
            self._initialize_default_achievements()

        self._update_caches()

    def _save_achievements(self) -> None:
        """Save achievements to file"""
        try:
            self.ACHIEVEMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ACHIEVEMENTS_PATH, 'w', encoding='utf-8') as f:
                data = {
                    id: achievement.to_dict()
                    for id, achievement in self.achievements.items()
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save achievements: {e}")

    def _initialize_default_achievements(self) -> None:
        """Initialize default achievements"""
        self.achievements = {
            "first_run": Achievement(
                id="first_run",
                name="First Steps",
                description="Complete your first run",
                category=AchievementCategory.SPECIAL
            )
        }
        self._save_achievements()

    def unlock(self, achievement_id: str) -> bool:
        """Unlock achievement and update caches"""
        if achievement_id not in self.achievements:
            return False

        achievement = self.achievements[achievement_id]
        if achievement.unlocked:
            return True

        achievement.unlocked = True
        achievement.unlock_date = datetime.now().isoformat()

        # Update both storage types
        self._unlocked_cache.add(achievement_id)
        idx = list(self.achievements.keys()).index(achievement_id)
        self._unlocked_array[idx] = True

        return True

    def _update_caches(self) -> None:
        """Update both caches and arrays"""
        # Update dictionary caches
        self._category_cache.clear()
        self._unlocked_cache.clear()

        for aid, achievement in self.achievements.items():
            self._category_cache[achievement.category].append(aid)
            if achievement.unlocked:
                self._unlocked_cache.add(aid)

        # Update numpy arrays
        achievement_count = len(self.achievements)
        self._category_array = np.zeros(achievement_count, dtype=np.int32)
        self._unlocked_array = np.zeros(achievement_count, dtype=bool)

        for idx, achievement in enumerate(self.achievements.values()):
            self._category_array[idx] = achievement.category
            self._unlocked_array[idx] = achievement.unlocked

    def _batch_check_achievements(self, stats: dict) -> Set[str]:
        """Batch check multiple achievements at once"""
        to_unlock = set()

        # Check all achievements in one pass
        for achievement_id, achievement in self.achievements.items():
            if not achievement.unlocked:
                if (
                    (achievement.category == AchievementCategory.SURVIVAL and stats.get("health", 0) < 10) or
                    (achievement.category == AchievementCategory.MUTATION and stats.get("mutations", 0) >= achievement.max_progress) or
                    (achievement.category == AchievementCategory.COLLECTION and stats.get("items", 0) >= achievement.max_progress)
                ):
                    to_unlock.add(achievement_id)

        return to_unlock

    def check_run_achievements(self, stats: dict) -> None:
        """Vectorized achievement checking"""
        # Update arrays if needed
        if len(self._category_array) != len(self.achievements):
            self._update_arrays()

        # Create condition masks
        survival_mask = (self._category_array == AchievementCategory.SURVIVAL) & ~self._unlocked_array
        mutation_mask = (self._category_array == AchievementCategory.MUTATION) & ~self._unlocked_array
        collection_mask = (self._category_array == AchievementCategory.COLLECTION) & ~self._unlocked_array

        # Check conditions
        if stats.get("health", 100) < 10:
            to_unlock = np.where(survival_mask)[0]
            for idx in to_unlock:
                self.unlock(list(self.achievements.keys())[idx])

        mutations = stats.get("mutations", 0)
        if mutations > 0:
            to_unlock = np.where(mutation_mask)[0]
            for idx in to_unlock:
                achievement = list(self.achievements.values())[idx]
                if mutations >= achievement.max_progress:
                    self.unlock(achievement.id)

    def display_achievements(self) -> None:
        """Display all achievements"""
        print(f"\n{Fore.CYAN}🏆 Achievements{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'='*44}{Style.RESET_ALL}")

        for ach in self.achievements.values():
            if ach.hidden and not ach.unlocked:
                print(f"{'🔒' if not ach.unlocked else '✨'} ???")
                continue

            print(f"{'🔒' if not ach.unlocked else '✨'} {ach.name}")
            print(f"   {ach.description}\n")

        print(f"{Fore.WHITE}{'='*44}{Style.RESET_ALL}")

    def update_progress(self, achievement_id: str, progress: int) -> bool:
        """Update achievement progress and unlock if max progress reached"""
        if achievement_id not in self.achievements:
            logger.error(f"Achievement {achievement_id} not found")
            return False

        achievement = self.achievements[achievement_id]
        achievement.progress += progress

        # Cap progress at max_progress
        achievement.progress = min(achievement.progress, achievement.max_progress)

        # Auto-unlock if max progress reached
        if achievement.progress >= achievement.max_progress:
            achievement.unlocked = True
            achievement.unlock_date = datetime.now().isoformat()
            logger.info(f"Achievement unlocked: {achievement.name}")
            self._save_achievements()
            self._update_caches()

        return True

    @lru_cache(maxsize=128)
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get unlocked achievements with caching"""
        return [ach for ach in self.achievements.values() if ach.unlocked]

    @lru_cache(maxsize=128)
    def _get_achievements_by_category(self, category: AchievementCategory) -> List[Achievement]:
        """Cache achievement lookups by category"""
        return [ach for ach in self.achievements.values() if ach.category == category]

    def _update_arrays(self) -> None:
        """Update numpy arrays for vectorized operations"""
        achievement_count = len(self.achievements)
        self._category_array = np.zeros(achievement_count, dtype=np.int32)
        self._unlocked_array = np.zeros(achievement_count, dtype=bool)

        for idx, achievement in enumerate(self.achievements.values()):
            self._category_array[idx] = achievement.category
            self._unlocked_array[idx] = achievement.unlocked
