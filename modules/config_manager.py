from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
from functools import wraps
import aiofiles

from modules.logger import logger
from modules.constants import CONFIG_DIR

def validate_config(func):
    """Decorator to validate config operations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, GameConfig):
                if not (0 <= result.trait_slots <= 9):
                    raise ValueError("Invalid trait slots value")
                if result.reflection_points < 0:
                    raise ValueError("Negative reflection points")
            return result
        except Exception as e:
            logger.error(f"Config validation failed: {e}")
            raise ConfigError(f"Configuration error: {e}")
    return wrapper

class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass

@dataclass
class GameConfig:
    """Game configuration data structure"""
    trait_slots: int = field(default=3, metadata={"min": 0, "max": 9})
    reflection_points: int = field(default=0, metadata={"min": 0})
    unlocked_themes: List[str] = field(default_factory=list)
    unlocked_audio: List[str] = field(default_factory=list)
    debug_mode: bool = False
    sound_enabled: bool = True
    mutation_log_visible: bool = True

    def __post_init__(self):
        """Validate configuration after initialization"""
        self.validate()

    def validate(self) -> None:
        """Validate configuration values"""
        if not isinstance(self.trait_slots, int):
            raise ConfigError("trait_slots must be an integer")
        if not isinstance(self.reflection_points, int):
            raise ConfigError("reflection_points must be an integer")
        if not isinstance(self.unlocked_themes, list):
            raise ConfigError("unlocked_themes must be a list")
        if not isinstance(self.unlocked_audio, list):
            raise ConfigError("unlocked_audio must be a list")

    @classmethod
    def from_dict(cls, data: Dict) -> 'GameConfig':
        """Create config from dictionary, handling legacy fields"""
        # Handle legacy field names
        if 'rp' in data:
            data['reflection_points'] = data.pop('rp')
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

class ConfigurationManager:
    """Handles game configuration loading and saving"""
    DEFAULT_CONFIG_PATH = CONFIG_DIR / "game_config.json"

    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH):
        self.config_path = Path(config_path)
        self._ensure_config_dir()
        self.backup_path = self.config_path.with_suffix('.backup')

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    @validate_config
    def load_config(self) -> GameConfig:
        """Load configuration with validation and backup support"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return GameConfig(**data)
            return self._create_default_config()
        except json.JSONDecodeError:
            logger.warning("Corrupt config file, attempting to restore backup")
            return self._restore_backup()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> GameConfig:
        """Create and save default configuration"""
        config = GameConfig()
        self.save(config)
        return config

    def _backup_config(self, config: GameConfig) -> None:
        """Create backup of current configuration"""
        try:
            with open(self.backup_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to create config backup: {e}")

    def _restore_backup(self) -> GameConfig:
        """Restore configuration from backup"""
        try:
            if self.backup_path.exists():
                with open(self.backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return GameConfig(**data)
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
        return self._create_default_config()

    @validate_config
    def save(self, config: GameConfig) -> bool:
        """Save configuration with validation and backup"""
        try:
            # Create backup before saving
            self._backup_config(config)

            # Save new configuration
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    async def async_load(self) -> GameConfig:
        """Load configuration asynchronously"""
        try:
            if self.config_path.exists():
                async with aiofiles.open(self.config_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
                    return GameConfig(**data)
            return GameConfig()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return GameConfig()

    async def async_save(self, config: GameConfig) -> bool:
        """Save configuration asynchronously"""
        try:
            async with aiofiles.open(self.config_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(asdict(config), indent=2))
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False