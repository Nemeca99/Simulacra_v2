from dataclasses import dataclass, field
from typing import Dict, List, Set
from pathlib import Path


@dataclass
class CleanupConfig:
    """Configuration for project cleanup"""
    # Development files to clean
    dev_patterns: Set[str] = field(default_factory=lambda: {
        "*.pdb",  # Debug symbols
        "*.dll",  # Non-essential DLLs
        "*.exe",  # Compiled executables
        "*.pyc",  # Python bytecode
        "*.pyd",  # Python DLLs
        "*.prof"  # Profile data
    })

    # Directories to preserve
    protected_dirs: Set[str] = field(default_factory=lambda: {
        ".venv/Scripts",
        "data/saves",
        "logs/current"
    })

    # Files to always keep
    protected_files: Set[str] = field(default_factory=lambda: {
        ".venv/Scripts/python.exe",
        ".venv/Scripts/pip.exe",
        "data/config.json",
        "logs/current/game.log"
    })

    # Size limits for different file types (in MB)
    size_limits: Dict[str, float] = field(default_factory=lambda: {
        ".log": 5.0,  # Max log file size
        ".json": 1.0,  # Max JSON file size
        ".html": 0.5  # Max HTML file size
    })
