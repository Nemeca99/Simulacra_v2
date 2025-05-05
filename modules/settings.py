# modules/settings.py

from dataclasses import dataclass
from typing import Dict, Final
import os
from colorama import Fore, Style

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

@dataclass
class Settings:
    """Game settings configuration"""
    sound_volume: int = 70
    music_volume: int = 50
    visual_glitches: bool = True
    hud_theme: str = "default"
    crt_filter: bool = True

    def validate(self) -> None:
        """Validate settings values"""
        self.sound_volume = max(0, min(100, self.sound_volume))
        self.music_volume = max(0, min(100, self.music_volume))

class SettingsManager:
    """Manages game settings"""
    THEMES: Final[Dict[str, str]] = {
        "default": "Classic terminal",
        "neon": "Neon cyberpunk",
        "retro": "Retro console",
        "minimal": "Minimal display"
    }

    def __init__(self):
        self.settings = Settings()

    def display(self) -> None:
        """Display settings interface"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n⚙️ Settings")
        print("=" * 44)
        print(f"1. Sound Volume: {self.settings.sound_volume}%")
        print(f"2. Music Volume: {self.settings.music_volume}%")
        print(f"3. Visual Glitches: {'On' if self.settings.visual_glitches else 'Off'}")
        print(f"4. HUD Theme: {self.THEMES[self.settings.hud_theme]}")
        print(f"5. CRT Filter: {'On' if self.settings.crt_filter else 'Off'}")
        print("0. Back")
