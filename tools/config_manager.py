import yaml
import json
from pathlib import Path
from typing import Any, Dict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ConfigManager(FileSystemEventHandler):

    def __init__(self, config_dir: str="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config: Dict[str, Any] = {}
        self._load_all()

        # Watch for changes
        self.observer = Observer()
        self.observer.schedule(self, str(self.config_dir), recursive=False)
        self.observer.start()

    def _load_all(self):
        """Load all config files"""
        for file in self.config_dir.glob("*.yml"):
            with open(file) as f:
                self.config[file.stem] = yaml.safe_load(f)

    def on_modified(self, event):
        """Hot reload when configs change"""
        if event.src_path.endswith('.yml'):
            self._load_all()
            print(f"🔄 Reloaded config: {Path(event.src_path).name}")
