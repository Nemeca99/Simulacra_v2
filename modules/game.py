from pathlib import Path
from typing import Optional
from datetime import datetime
from functools import lru_cache
import orjson  # Much faster than standard json
import aiofiles
import asyncio
import lz4.frame

from modules.stats import PlayerStats
from modules.mutations import MutationSystem
from modules.achievements import AchievementManager
from modules.logger import logger
from modules.performance import PerformanceMonitor
from .game_types import GameState, PlayerState, GameID, PlayerID

class SimulacraGame:
    """Main game class managing state and systems"""

    def __init__(self, save_dir: Optional[Path] = None):
        self.save_dir = save_dir or Path("saves")
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.stats = PlayerStats()
        self.mutation_system = MutationSystem()
        self.achievement_manager = AchievementManager()

    async def initialize(self) -> None:
        """Initialize game systems"""
        await self.load_game()

    @lru_cache(maxsize=32)
    async def _read_state_cache(self, file_path: str) -> dict:
        """Cached state reading"""
        async with aiofiles.open(file_path, 'r') as f:
            return json.loads(await f.read())

    @lru_cache(maxsize=32)
    def _serialize_state(self) -> bytes:
        """Cache state serialization"""
        return orjson.dumps({
            "stats": self.stats.to_dict(),
            "timestamp": datetime.now().isoformat()
        })

    @lru_cache(maxsize=32)
    def _compress_state(self) -> bytes:
        """Compress game state for faster saving"""
        state_data = orjson.dumps({
            "stats": self.stats.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
        return lz4.frame.compress(state_data)

    @PerformanceMonitor.track
    async def save_game(self) -> bool:
        """Save compressed game state"""
        try:
            save_path = self.save_dir / "save.lz4"
            async with aiofiles.open(save_path, mode='wb') as f:
                await f.write(self._compress_state())
            return True
        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False

    async def load_game(self) -> bool:
        """Load compressed game state"""
        try:
            save_path = self.save_dir / "save.lz4"
            if not save_path.exists():
                return False

            async with aiofiles.open(save_path, mode='rb') as f:
                compressed_data = await f.read()
                data = orjson.loads(lz4.frame.decompress(compressed_data))
                self.stats = PlayerStats(**data["stats"])
            return True
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            return False