import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
from typing import AsyncGenerator
import pytest_asyncio
from modules.game import SimulacraGame
from modules.stats import PlayerStats
from modules.mutations import MutationSystem

class TestSimulacra:
    """Test suite for Simulacra game components"""

    @pytest_asyncio.fixture
    async def temp_dir(self) -> Path:
        """Fixture providing temporary directory"""
        test_dir = Path(tempfile.mkdtemp())
        yield test_dir  # Not AsyncGenerator, just Path
        shutil.rmtree(test_dir)

    @pytest_asyncio.fixture
    async def game(self, temp_dir: Path) -> SimulacraGame:
        """Provide game instance"""
        game = SimulacraGame(save_dir=temp_dir)
        await game.initialize()
        return game

    @pytest.mark.asyncio
    async def test_async_save_load(self, temp_dir: Path) -> None:
        """Test async file operations"""
        from modules.async_io import AsyncIO

        test_data = {"test": "data", "nested": {"key": "value"}}
        test_file = temp_dir / "test.json"

        assert await AsyncIO.save_json(test_file, test_data)
        assert test_file.exists()

        loaded_data = await AsyncIO.load_json(test_file)
        assert loaded_data == test_data

    @pytest.mark.asyncio
    async def test_config_operations(self, temp_dir: Path) -> None:
        """Test configuration operations"""
        from modules.config_manager import ConfigurationManager, GameConfig

        config_path = temp_dir / "config.json"
        manager = ConfigurationManager(config_path)

        # Test save and load with various configs
        configs = [
            GameConfig(trait_slots=5, reflection_points=100),
            GameConfig(trait_slots=3, unlocked_themes=["dark", "light"]),
            GameConfig(unlocked_audio=["pack1", "pack2"])
        ]

        for test_config in configs:
            assert await manager.async_save(test_config)
            loaded = await manager.async_load()
            assert loaded.__dict__ == test_config.__dict__

    @pytest.mark.asyncio
    async def test_game_initialization(self, game: SimulacraGame):
        """Test game initialization"""
        assert game.stats is not None
        assert game.mutation_system is not None
        assert game.achievement_manager is not None

    @pytest.mark.asyncio
    async def test_game_save_load(self, game: SimulacraGame, temp_dir: Path):
        """Test game state persistence"""
        # Modify game state
        game.stats.reflection_points += 100
        await game.save_game()

        # Create new game instance
        new_game = SimulacraGame(save_dir=temp_dir)
        await new_game.load_game()

        assert new_game.stats.reflection_points == 100