from pathlib import Path
from typing import Dict, Any, Optional, Final
from dataclasses import dataclass
from datetime import datetime
import json
import os

from modules.logger import logger
from modules.constants import DATA_DIR

@dataclass
class GameConfig:
    """Game configuration data"""
    rp: int = 0
    trait_slots: int = 3
    unlocked_themes: list = None
    unlocked_audio: list = None

    def __post_init__(self):
        """Initialize optional fields"""
        self.unlocked_themes = self.unlocked_themes or []
        self.unlocked_audio = self.unlocked_audio or []

    def validate(self) -> bool:
        """Validate configuration values"""
        return all([
            isinstance(self.rp, int),
            isinstance(self.trait_slots, int),
            isinstance(self.unlocked_themes, list),
            isinstance(self.unlocked_audio, list)
        ])

class FileManager:
    """Handles file operations with error handling"""
    @staticmethod
    def safe_load(path: Path) -> Optional[Dict]:
        try:
            if not path.exists():
                return None
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load file {path}: {e}")
            return None

    @staticmethod
    def safe_save(path: Path, data: Dict) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save file {path}: {e}")
            return False

class ConfigManager:
    """Manages game configuration"""
    CONFIG_PATH = Path(DATA_DIR) / "config.json"

    @classmethod
    def get_config(cls) -> GameConfig:
        """Load configuration or create default"""
        data = FileManager.safe_load(cls.CONFIG_PATH)
        if data is None:
            return GameConfig()
        return GameConfig(**data)

    @classmethod
    def save_config(cls, config: GameConfig) -> bool:
        """Save configuration to file"""
        if not config.validate():
            logger.error("Invalid configuration data")
            return False
        return FileManager.safe_save(cls.CONFIG_PATH, config.__dict__)

def format_time(seconds: int) -> str:
    """Format seconds into readable time"""
    minutes = seconds // 60
    remaining = seconds % 60
    return f"{minutes}m {remaining}s"

def get_entropy_drain(survival_seconds: int) -> float:
    """Calculate current entropy drain rate"""
    base_entropy = 5.0
    time_multiplier = 1 + (survival_seconds // 60) * 0.01
    return round(base_entropy * time_multiplier, 2)

def view_highlights():
    folder = "data/highlights"
    if not os.path.exists(folder):
        print("No highlights found.")
        return

    files = sorted(os.listdir(folder), reverse=True)
    if not files:
        print("No highlights saved yet.")
        return

    print("\n📁 Highlight Log Files:")
    for i, fname in enumerate(files[:10], 1):
        print(f"{i}. {fname}")

    choice = input("Select a highlight to view (or press Enter to cancel): ")
    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(files):
            with open(os.path.join(folder, files[index]), "r") as f:
                print("\n" + f.read())
        else:
            print("Invalid selection.")

def clear_screen() -> None:
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")
