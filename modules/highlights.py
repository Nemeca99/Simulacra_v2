from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime
import os
import json
from pathlib import Path

from modules.logger import logger
from modules.error_handler import handle_errors
from modules.constants import MAX_HIGHLIGHTS, DATA_DIR

@dataclass
class Highlight:
    """Structured highlight data"""
    timestamp: str
    survival_time: int
    hp_end: float
    max_hp: float
    mutation_rate: float
    entropy_drain: float
    reflection_points: int
    traits: List[Dict]
    mutations: List[Dict]
    resistances: Dict[str, float]
    immunities: List[str]

    @classmethod
    def from_stats(cls, stats: Dict, time: int,
                  mutations: List, traits: List) -> 'Highlight':
        """Create highlight from game stats"""
        return cls(
            timestamp=datetime.now().isoformat(),
            survival_time=time,
            hp_end=stats['current_hp'],
            max_hp=stats['max_hp'],
            mutation_rate=stats['mutation_rate'],
            entropy_drain=stats.get('entropy_drain', 5.0),
            reflection_points=stats.get('reflection_points', 0),
            traits=traits,
            mutations=mutations,
            resistances=stats.get('resistances', {}),
            immunities=stats.get('immunities', [])
        )

class HighlightManager:
    """Manages game highlights and saving"""
    def __init__(self):
        self.highlights_dir = Path(DATA_DIR) / "highlights"
        self.highlights_json = self.highlights_dir / "highlights.json"
        self.highlights_dir.mkdir(parents=True, exist_ok=True)

    @handle_errors()
    def save_highlight(self, stats: Dict, time: int,
                      mutations: List, traits: List) -> None:
        """Save both JSON and text format highlights"""
        highlight = Highlight.from_stats(stats, time, mutations, traits)
        self._save_json_highlight(highlight)
        self._save_text_highlight(highlight)
        logger.info("💾 Highlight saved successfully")

    def _save_json_highlight(self, highlight: Highlight) -> None:
        """Save highlight in JSON format"""
        highlights = []
        if os.path.exists(self.highlights_json):
            with open(self.highlights_json, 'r') as f:
                highlights = json.load(f)

        highlights.append(vars(highlight))
        highlights = highlights[-MAX_HIGHLIGHTS:]  # Keep only most recent

        with open(self.highlights_json, 'w') as f:
            json.dump(highlights, f, indent=2)

    def _save_text_highlight(self, highlight: Highlight) -> None:
        """Save highlight in readable text format"""
        filename = f"{self.highlights_dir}/highlight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(filename, 'w') as f:
            f.write("=== SIMULACRA RUN HIGHLIGHT ===\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Survival Time: {highlight.survival_time//60}m {highlight.survival_time%60}s\n")
            f.write(f"Final HP: {highlight.hp_end:.1f}/{highlight.max_hp}\n")
            f.write(f"Mutation Rate: {highlight.mutation_rate:.2f}%\n")
            f.write(f"Entropy Drain: {highlight.entropy_drain:.2f} HP/s\n")
            f.write(f"Reflection Points: {highlight.reflection_points}\n\n")

            f.write("Traits:\n")
            for trait in highlight.traits:
                effects = [e['text'] for e in trait.get('effects', [])]
                f.write(f"  - {trait['name']} ({', '.join(effects)})\n")

            f.write("\nResistances:\n")
            for k, v in highlight.resistances.items():
                f.write(f"  - {k}: {v}%\n")

            f.write("\nMutations:\n")
            for mut in highlight.mutations:
                f.write(f"  - {mut['name']} ({mut['effect']})\n")
