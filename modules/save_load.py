import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from modules.logger import logger
from modules.constants import DATA_DIR, MAX_HIGHLIGHTS

@dataclass
class RunData:
    """Single run data structure"""
    timestamp: str
    traits: List[Dict]
    mutations: List[Dict]
    reflection_points: int
    survival_seconds: int

@dataclass
class HighlightData:
    """Structure for a highlight entry"""
    timestamp: str
    hp_end: float
    mutation_rate_end: float
    reflection_points: int
    time_alive: int
    entropy_drain: float
    mutations: List[Dict]
    traits: List[Dict]
    resistance: Dict[str, float]

class SaveManager:
    """Handles game saving and loading"""
    SAVE_DIR: Path = DATA_DIR / "runs"
    HIGHLIGHT_FILE: Path = DATA_DIR / "highlights.json"

    def __init__(self):
        self.SAVE_DIR.mkdir(parents=True, exist_ok=True)

    def save_run(self, run: RunData) -> bool:
        """Save run data to file"""
        try:
            filename = f"run_{datetime.now():%Y-%m-%d_%H-%M-%S}.json"
            with open(self.SAVE_DIR / filename, "w", encoding='utf-8') as f:
                json.dump(run.__dict__, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save run: {e}")
            return False

    def load_runs(self, limit: int = 10) -> List[RunData]:
        """Load most recent runs"""
        try:
            files = sorted(self.SAVE_DIR.glob("*.json"), reverse=True)
            runs = []
            for file in files[:limit]:
                with open(file, encoding='utf-8') as f:
                    runs.append(RunData(**json.load(f)))
            return runs
        except Exception as e:
            logger.error(f"Failed to load runs: {e}")
            return []

def save_highlight_log(hp: float, mutation_rate: float, rp: int,
                      time_alive: int, entropy_drain: float,
                      mutations: List[Dict], traits: List[Dict],
                      resistance: Dict[str, float]) -> None:
    """Save highlight data to JSON file"""
    try:
        highlight = HighlightData(
            timestamp=datetime.now().isoformat(),
            hp_end=hp,
            mutation_rate_end=mutation_rate,
            reflection_points=rp,
            time_alive=time_alive,
            entropy_drain=entropy_drain,
            mutations=mutations,
            traits=traits,
            resistance=resistance
        )

        highlights = []
        if os.path.exists(SaveManager.HIGHLIGHT_FILE):
            with open(SaveManager.HIGHLIGHT_FILE, "r") as f:
                highlights = json.load(f)

        highlights.append(highlight.__dict__)
        highlights = highlights[-MAX_HIGHLIGHTS:]

        with open(SaveManager.HIGHLIGHT_FILE, "w") as f:
            json.dump(highlights, f, indent=2)

        logger.info("💾 Highlight saved successfully", Fore.GREEN)

    except Exception as e:
        logger.error(f"Failed to save highlight: {e}")
