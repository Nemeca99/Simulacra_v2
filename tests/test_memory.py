from memory_profiler import profile
import pytest
from modules.game import SimulacraGame
from modules.mutations import MutationSystem
from modules.achievements import AchievementManager

class TestMemoryUsage:
    @profile
    def test_game_memory(self, temp_dir):
        """Profile game memory usage"""
        game = SimulacraGame(save_dir=temp_dir)
        game.initialize()

        # Generate mutations
        mutation_system = MutationSystem()
        for _ in range(1000):
            mutation = mutation_system.generate_mutation()
            mutation_system.apply_mutation(game.stats, mutation)

    @profile
    def test_achievement_memory(self):
        """Profile achievement system memory"""
        manager = AchievementManager()
        for i in range(1000):
            manager.check_run_achievements({"total_runs": i})