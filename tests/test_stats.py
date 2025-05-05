import pytest
from tests.base_test import BaseGameTest
from modules.stats import PlayerStats, StatModifier

class TestStats(BaseGameTest):
    @pytest.fixture
    def stats(self) -> PlayerStats:
        return PlayerStats()

    def test_stat_initialization(self, stats: PlayerStats):
        """Test stat initialization"""
        assert stats.hp == 100.0
        assert stats.max_hp == 100.0
        assert stats.mutation_rate == 0.0
        assert isinstance(stats.resistances, dict)
        assert isinstance(stats.immunities, list)

    def test_stat_validation(self, stats: PlayerStats):
        """Test stat validation"""
        stats.hp = 1000  # Try to exceed cap
        assert stats.validate() is False

        stats.hp = 100
        assert stats.validate() is True

    def test_stat_modifiers(self, stats: PlayerStats):
        """Test stat modification system"""
        modifier = StatModifier(type="add", value=10)
        assert stats.apply_modifier("hp", modifier)
        assert stats.hp == 110.0

    def test_bulk_modifications(self, stats: PlayerStats):
        """Test bulk stat modifications"""
        modifiers = [
            ("hp", StatModifier(type="add", value=10)),
            ("mutation_rate", StatModifier(type="add", value=5))
        ]
        stats.apply_modifiers_bulk(modifiers)
        assert stats.hp == 110.0
        assert stats.mutation_rate == 5.0