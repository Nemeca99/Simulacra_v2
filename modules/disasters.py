# modules/disasters.py

from pathlib import Path
import json
import random
from typing import Dict, List, Final
from dataclasses import dataclass

from colorama import Fore
from modules.logger import logger
from modules.constants import DISASTER_PARTS_DIR

@dataclass
class DisasterType:
    """Disaster type configuration"""
    name: str
    base_damage: float
    color: str = Fore.WHITE

# Base damage and color configurations
DISASTER_TYPES: Final[Dict[str, DisasterType]] = {
    "void": DisasterType("Void", 20.0, Fore.MAGENTA),
    "quantum": DisasterType("Quantum", 18.0, Fore.CYAN),
    "temporal": DisasterType("Temporal", 16.0, Fore.BLUE),
    "fire": DisasterType("Fire", 15.0, Fore.RED),
    "frost": DisasterType("Frost", 12.0, Fore.WHITE),
    "system": DisasterType("System", 14.0, Fore.YELLOW),
    "data": DisasterType("Data", 13.0, Fore.GREEN),
    "entropy": DisasterType("Entropy", 17.0, Fore.MAGENTA),
    "neural": DisasterType("Neural", 15.0, Fore.CYAN),
    "memory": DisasterType("Memory", 14.0, Fore.BLUE)
}

class DisasterSystem:
    """Handles disaster generation and effects"""
    def __init__(self):
        self.parts = self._load_disaster_parts()

    def _load_disaster_parts(self) -> Dict[str, List[str]]:
        """Load disaster components from JSON files"""
        parts = {}
        try:
            for part_file in ["names.json", "types.json", "effects.json"]:
                file_path = DISASTER_PARTS_DIR / part_file
                with open(file_path, "r", encoding='utf-8') as f:
                    parts[part_file.split(".")[0]] = json.load(f)
            return parts
        except Exception as e:
            logger.error(f"Failed to load disaster parts: {e}")
            return self._get_default_parts()

    def _get_default_parts(self) -> Dict[str, List[str]]:
        """Provide default disaster parts if files are missing"""
        return {
            "names": ["System Error", "Data Corruption", "Entropy Surge"],
            "types": ["system", "data", "entropy"],
            "effects": ["corrupts your systems", "destabilizes your core", "accelerates decay"]
        }

    def generate_disaster(self) -> Dict:
        """Generate a random disaster event"""
        try:
            disaster_type = random.choice(self.parts["types"])
            return {
                "name": random.choice(self.parts["names"]),
                "type": disaster_type,
                "effect": random.choice(self.parts["effects"]),
                "damage": DISASTER_TYPES[disaster_type].base_damage
            }
        except Exception as e:
            logger.error(f"Failed to generate disaster: {e}")
            return self._get_fallback_disaster()

    def calculate_damage(self, disaster: Dict, stats: Dict) -> float:
        """Calculate final damage after applying resistances"""
        base = DISASTER_TYPES[disaster["type"]].base_damage
        if resistances := stats.get("resistances", {}):
            if reduction := resistances.get(disaster["type"], 0):
                base *= (1 - reduction / 100)
        return round(base, 2)

    def _get_fallback_disaster(self) -> Dict:
        """Provide a fallback disaster event"""
        return {
            "name": "System Error",
            "type": "error",
            "effect": "System malfunction",
            "damage": 5.0
        }

