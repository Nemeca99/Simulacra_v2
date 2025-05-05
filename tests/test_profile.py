import cProfile
import pytest
from modules.game import SimulacraGame
from modules.mutations import MutationSystem

def test_game_profile(temp_dir):
    """Profile game operations"""
    profiler = cProfile.Profile()
    game = SimulacraGame(save_dir=temp_dir)

    profiler.enable()
    game.initialize()
    mutation_system = MutationSystem()

    for _ in range(1000):
        mutation = mutation_system.generate_mutation()
        mutation_system.apply_mutation(game.stats, mutation)

    profiler.disable()
    profiler.dump_stats('game_profile.stats')