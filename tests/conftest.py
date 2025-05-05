"""
Test configuration for Simulacra.
"""
import pytest
import tempfile
import shutil
import sys
import os
from pathlib import Path
from typing import Generator, Dict, Any

# Import path setup
sys.path.insert(0, str(Path(__file__).parent.parent))
from setup_paths import setup_paths

# Set up paths
setup_paths()

# Get project root directory
ROOT_DIR = Path(__file__).parent.parent.absolute()

# Add paths to Python's import system
for path in [str(ROOT_DIR), str(ROOT_DIR / "modules")]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Force import priority
os.environ["PYTHONPATH"] = os.pathsep.join([
    str(ROOT_DIR),
    str(ROOT_DIR / "modules"),
    os.environ.get("PYTHONPATH", "")
])


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide temporary directory for tests"""
    test_dir = Path(tempfile.mkdtemp())
    yield test_dir
    shutil.rmtree(test_dir)


@pytest.fixture
def game_state() -> Dict[str, Any]:
    """Provide test game state"""
    return {
        "runs": 0,
        "health": 100,
        "mutations": [],
        "achievements": [],
        "reflection_points": 0,
        "stats": {
            "mutations_collected": 0,
            "disasters_survived": 0,
            "total_reflection": 0
        }
    }
