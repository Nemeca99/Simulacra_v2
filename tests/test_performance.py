import pytest
from tests.base_test import BasePerformanceTest
from modules.game import SimulacraGame
from modules.mutations import MutationSystem
from modules.stats import PlayerStats, StatModifier
from modules.achievements import AchievementManager, Achievement, AchievementCategory
import asyncio

class TestPerformance(BasePerformanceTest):
    @pytest.mark.benchmark(
        group="mutations",
        min_rounds=100,
    )
    def test_mutation_generation_performance(self, benchmark):
        """Benchmark mutation generation"""
        mutation_system = MutationSystem()

        def generate_mutations():
            for _ in range(100):
                mutation_system.generate_mutation()

        benchmark(generate_mutations)

    @pytest.mark.benchmark(
        group="achievements",
        min_rounds=100,
    )
    def test_achievement_checks_performance(self, benchmark):
        """Benchmark achievement validation"""
        achievement_manager = AchievementManager()

        def check_achievements():
            for _ in range(1000):
                achievement_manager.check_run_achievements({"total_runs": 1})

        benchmark(check_achievements)

    @pytest.mark.benchmark(
        group="stats",
        min_rounds=100,
    )
    def test_stat_modifications_performance(self, benchmark):
        """Benchmark stat modifications"""
        stats = PlayerStats()
        mutation_system = MutationSystem()

        def modify_stats():
            for _ in range(100):
                mutation = mutation_system.generate_mutation()
                mutation_system.apply_mutation(stats, mutation)

        benchmark(modify_stats)

    @pytest.mark.benchmark(
        group="stats-detailed",
        min_rounds=100
    )
    def test_stat_modifier_performance(self, benchmark):
        """Benchmark individual stat modifications"""
        stats = PlayerStats()
        modifier = StatModifier(type="add", value=10.0)

        def apply_modifiers():
            for _ in range(100):
                stats.apply_modifier("hp", modifier)
                stats.apply_modifier("mutation_rate", modifier)
                stats.validate()

        benchmark(apply_modifiers)

    @pytest.mark.benchmark(
        group="achievements-detailed",
        min_rounds=100
    )
    def test_achievement_save_performance(self, benchmark, temp_dir):
        """Benchmark achievement saving"""
        manager = AchievementManager()

        # Add test achievements
        for i in range(100):
            manager.achievements[f"test_{i}"] = Achievement(
                id=f"test_{i}",
                name=f"Test {i}",
                description=f"Test achievement {i}",
                category=AchievementCategory.SURVIVAL
            )

        benchmark(manager._save_achievements)

    @pytest.mark.benchmark(
        group="game-state",
        min_rounds=100
    )
    def test_game_state_performance(self, benchmark, temp_dir):
        """Benchmark game state operations"""
        game = SimulacraGame(save_dir=temp_dir)

        def run_async():
            asyncio.run(game.save_game())
            asyncio.run(game.load_game())

        benchmark(run_async)

    @pytest.mark.benchmark(
        group="mutations-detailed"
    )
    def test_mutation_application_chain(self, benchmark):
        """Benchmark chained mutation applications"""
        stats = PlayerStats()
        mutation_system = MutationSystem()
        mutations = [mutation_system.generate_mutation() for _ in range(10)]

        def apply_mutation_chain():
            for mutation in mutations:
                mutation_system.apply_mutation(stats, mutation)
                stats.validate()

        benchmark(apply_mutation_chain)

    @pytest.mark.benchmark(
        group="game-state",
        min_rounds=100
    )
    def test_save_load_performance(self, benchmark, temp_dir):
        """Benchmark save/load operations"""
        game = SimulacraGame(save_dir=temp_dir)

        def run_async():
            # Run async operations properly
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(game.save_game())
            loop.run_until_complete(game.load_game())
            loop.close()

        benchmark(run_async)

    @pytest.mark.benchmark(
        group="mutations",
        min_rounds=100
    )
    def test_mutation_chain_performance(self, benchmark):
        """Benchmark mutation chain applications"""
        stats = PlayerStats()
        mutation_system = MutationSystem()

        def apply_mutations():
            for _ in range(10):
                mutation = mutation_system.generate_mutation()
                mutation_system.apply_mutation(stats, mutation)

        benchmark(apply_mutations)

    @pytest.mark.benchmark(
        group="stats",
        min_rounds=100
    )
    def test_stat_update_performance(self, benchmark):
        """Benchmark stat update performance"""
        stats = PlayerStats()

        def update_stats():
            for _ in range(100):
                stats.apply_modifier("hp", StatModifier(type="add", value=1))
                stats.validate()

        benchmark(update_stats)

    @pytest.mark.benchmark(
        group="optimized",
        min_rounds=1000
    )
    async def test_optimized_save_performance(self, benchmark):
        """Test optimized save performance"""
        game = SimulacraGame(save_dir=self.test_dir)

        def run_save():
            asyncio.run(game.save_game())

        benchmark(run_save)