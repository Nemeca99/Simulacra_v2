from pathlib import Path
from typing import Dict, List
import yaml
import json


class TodoTracker:
    """Track development progress"""

    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.roadmap_file = self.root / "docs" / "ROADMAP.md"
        self.progress_file = self.root / "docs" / "progress.yaml"

    def update_progress(self, phase: int, task: str, status: str) -> None:
        """Update task progress"""
        if not self.progress_file.exists():
            self._init_progress()

        with open(self.progress_file) as f:
            progress = yaml.safe_load(f)

        if str(phase) not in progress:
            progress[str(phase)] = {}

        progress[str(phase)][task] = status

        with open(self.progress_file, 'w') as f:
            yaml.safe_dump(progress, f)

    def get_phase_status(self, phase: int) -> Dict:
        """Get status of specific phase"""
        if not self.progress_file.exists():
            return {}

        with open(self.progress_file) as f:
            progress = yaml.safe_load(f)

        return progress.get(str(phase), {})

    def _init_progress(self) -> None:
        """Initialize progress tracking"""
        progress = {
            "1": {
                "PlayerSystems": "IN_PROGRESS",
                "CoreMechanics": "NOT_STARTED",
                "DisasterSystem": "IN_PROGRESS"
            }
        }
        with open(self.progress_file, 'w') as f:
            yaml.safe_dump(progress, f)
