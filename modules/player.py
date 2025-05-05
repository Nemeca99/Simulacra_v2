from pathlib import Path
from typing import Dict, List, Optional, Final
from dataclasses import dataclass, field
import json

from modules.logger import logger
from modules.constants import DATA_DIR
from modules.error_handler import GameError, ValidationError

@dataclass
class PlayerConfig:
    """Player configuration with validation"""
    trait_slots: int = field(
        default=3,
        metadata={"min": 1, "max": 10}
    )
    reflection_points: int = field(
        default=0,
        metadata={"min": 0}
    )
    unlocked_themes: List[str] = field(default_factory=list)
    unlocked_audio: List[str] = field(default_factory=list)
    hud_upgrades: List[str] = field(default_factory=list)
    dev_flags: Dict[str, bool] = field(
        default_factory=lambda: {
            "debug_mode": False,
            "mutation_log_visible": True
        }
    )

    def __post_init__(self):
        """Validate configuration after initialization"""
        try:
            self._validate_trait_slots()
            self._validate_reflection_points()
            self._validate_lists()
            self._validate_dev_flags()
        except ValueError as e:
            raise ValidationError(f"Configuration validation failed: {e}")

    def _validate_trait_slots(self) -> None:
        min_slots = self.__dataclass_fields__["trait_slots"].metadata["min"]
        max_slots = self.__dataclass_fields__["trait_slots"].metadata["max"]
        if not min_slots <= self.trait_slots <= max_slots:
            raise ValueError(f"Trait slots must be between {min_slots} and {max_slots}")

    def _validate_reflection_points(self) -> None:
        min_points = self.__dataclass_fields__["reflection_points"].metadata["min"]
        if self.reflection_points < min_points:
            raise ValueError(f"Reflection points cannot be negative")

    def _validate_lists(self) -> None:
        if not isinstance(self.unlocked_themes, list):
            self.unlocked_themes = list(self.unlocked_themes)
        if not isinstance(self.unlocked_audio, list):
            self.unlocked_audio = list(self.unlocked_audio)
        if not isinstance(self.hud_upgrades, list):
            self.hud_upgrades = list(self.hud_upgrades)

    def _validate_dev_flags(self) -> None:
        required_flags = {"debug_mode", "mutation_log_visible"}
        if not all(flag in self.dev_flags for flag in required_flags):
            self.dev_flags.update({
                flag: False for flag in required_flags
                if flag not in self.dev_flags
            })

class PlayerManager:
    """Manages player configuration and state"""
    CONFIG_FILE: Final[Path] = Path("data/player_config.json")

    def __init__(self):
        self.config = PlayerConfig()

    CONFIG_PATH: Final[Path] = DATA_DIR / "player_config.json"
    MAX_TRAIT_SLOTS: Final[int] = 9

    @classmethod
    def load_config(cls) -> PlayerConfig:
        """Load or create player configuration"""
        try:
            if cls.CONFIG_PATH.exists():
                with open(cls.CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return PlayerConfig(**data)
            return cls._create_default_config()
        except Exception as e:
            logger.error(f"Failed to load player config: {e}")
            return cls._create_default_config()

    @classmethod
    def save_config(cls, config: PlayerConfig) -> bool:
        """Save player configuration"""
        try:
            cls.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(cls.CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(vars(config), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save player config: {e}")
            return False

    @staticmethod
    def _create_default_config() -> PlayerConfig:
        """Create default player configuration"""
        return PlayerConfig()

    @staticmethod
    def increase_trait_slots(config: PlayerConfig) -> bool:
        """Attempt to increase trait slots"""
        if config.trait_slots < PlayerManager.MAX_TRAIT_SLOTS:
            config.trait_slots += 1
            return True
        return False

    @staticmethod
    def unlock_theme(config: PlayerConfig, theme_name: str) -> None:
        """Unlock a new theme"""
        if theme_name not in config.unlocked_themes:
            config.unlocked_themes.append(theme_name)

    @staticmethod
    def has_theme(config: PlayerConfig, theme_name: str) -> bool:
        """Check if theme is unlocked"""
        return theme_name in config.unlocked_themes

    @staticmethod
    def toggle_debug_mode(config: PlayerConfig) -> None:
        """Toggle debug mode"""
        config.dev_flags["debug_mode"] = not config.dev_flags["debug_mode"]

    @staticmethod
    def is_debug_enabled(config: PlayerConfig) -> bool:
        """Check if debug mode is enabled"""
        return config.dev_flags.get("debug_mode", False)
