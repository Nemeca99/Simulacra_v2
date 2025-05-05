import pytest
from pathlib import Path
import tempfile
import shutil
from modules.config_manager import ConfigurationManager, GameConfig

class TestConfigManager:
    @pytest.fixture
    def config_dir(self) -> Path:
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def config_manager(self, config_dir: Path) -> ConfigurationManager:
        return ConfigurationManager(config_dir / "config.json")

    def test_load_config(self, config_manager: ConfigurationManager):
        """Test default config loading"""
        config = config_manager.load_config()
        assert isinstance(config, GameConfig)
        assert config.trait_slots == 3
        assert config.reflection_points == 0
        assert isinstance(config.unlocked_themes, list)

    def test_save_config(self, config_manager: ConfigurationManager):
        """Test config saving and reloading"""
        test_config = GameConfig(trait_slots=5, reflection_points=100)
        assert config_manager.save(test_config)

        loaded_config = config_manager.load_config()
        assert loaded_config.trait_slots == 5
        assert loaded_config.reflection_points == 100

    def test_invalid_config(self, config_manager: ConfigurationManager):
        """Test handling of invalid config file"""
        with open(config_manager.config_path, 'w') as f:
            f.write("invalid json")

        config = config_manager.load_config()
        assert isinstance(config, GameConfig)
        assert config.trait_slots == 3  # Should return default config

    @pytest.mark.asyncio
    async def test_async_operations(self, config_manager: ConfigurationManager):
        """Test async config operations"""
        test_config = GameConfig(trait_slots=7)
        assert await config_manager.async_save(test_config)

        loaded_config = await config_manager.async_load()
        assert loaded_config.trait_slots == 7