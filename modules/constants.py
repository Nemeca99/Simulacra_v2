from pathlib import Path
from typing import Dict, Final
from colorama import Fore, Style

# Color Constants (as Final to prevent modification)
CYAN: Final[str] = Fore.CYAN
BLUE: Final[str] = Fore.BLUE
PURPLE: Final[str] = Fore.MAGENTA
WHITE: Final[str] = Fore.WHITE
RED: Final[str] = Fore.RED
RESET: Final[str] = Style.RESET_ALL

# File Structure (using Path objects)
ROOT_DIR: Final[Path] = Path(__file__).parent.parent
DATA_DIR: Final[Path] = ROOT_DIR / "data"
CONFIG_DIR: Final[Path] = DATA_DIR / "config"
SAVE_DIR: Final[Path] = DATA_DIR / "runs"
LOGS_DIR: Final[Path] = DATA_DIR / "logs"
MUTATION_PARTS_DIR: Final[Path] = DATA_DIR / "mutation_parts"
DISASTER_PARTS_DIR: Final[Path] = DATA_DIR / "disaster_parts"

# Game Constants
BASE_HP: Final[float] = 100.0
BASE_ENTROPY_DRAIN: Final[float] = 5.0
DISASTER_INTERVAL: Final[int] = 15
MAX_RECENT_DISASTERS: Final[int] = 3
MAX_TRAIT_SLOTS: Final[int] = 9
MAX_MUTATIONS: Final[int] = 10
MAX_HIGHLIGHTS: Final[int] = 100

# Rarity Configuration
RARITY_WEIGHTS: Final[Dict[str, int]] = {
    "common": 70,
    "uncommon": 20,
    "rare": 8,
    "legendary": 2
}

RARITY_COLORS: Final[Dict[str, str]] = {
    "common": Fore.WHITE,
    "uncommon": Fore.GREEN,
    "rare": Fore.BLUE,
    "legendary": Fore.YELLOW
}

# Ensure directories exist
def ensure_directories() -> None:
    """Create required game directories if they don't exist"""
    for directory in [DATA_DIR, CONFIG_DIR, SAVE_DIR, LOGS_DIR,
                     MUTATION_PARTS_DIR, DISASTER_PARTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)