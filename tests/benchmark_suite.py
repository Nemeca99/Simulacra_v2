import pytest
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from tests.base_test import BasePerformanceTest
from modules.game import SimulacraGame
from modules.mutations import MutationSystem
from modules.stats import PlayerStats, StatModifier
from modules.traits import TraitManager, Trait, TraitCategory
from modules.achievements import AchievementManager, Achievement, AchievementCategory


class GameBenchmarkSuite(BasePerformanceTest):
    """Comprehensive benchmark suite for Simulacra"""

    @pytest.fixture(scope="class")
    def game_instance(self, tmp_path_factory):
        """Provide configured game instance"""
        test_dir = tmp_path_factory.mktemp("benchmark_data")
        return SimulacraGame(save_dir=test_dir)

    @pytest.fixture
    def large_save_data(self) -> Dict[str, Any]:
        """Generate large test save data"""
        return {
            "stats": {
                "hp": 100.0,
                "max_hp": 100.0,
                "mutation_rate": 5.0,
                "reflection_points": 1000,
                "resistances": {str(i): float(i) for i in range(100)},
                "immunities": [f"immunity_{i}" for i in range(50)]
            },
            "mutations": [
                {
                    "id": f"mutation_{i}",
                    "name": f"Test Mutation {i}",
                    "effects": [{"type": "add", "stat": "hp", "value": i}]
                }
                for i in range(1000)
            ],
            "achievements": [
                {
                    "id": f"achievement_{i}",
                    "name": f"Test Achievement {i}",
                    "description": "Test description",
                    "category": AchievementCategory.SURVIVAL.name,
                    "unlocked": i % 2 == 0
                }
                for i in range(500)
            ],
            "traits": [
                {
                    "id": f"trait_{i}",
                    "name": f"Test Trait {i}",
                    "category": TraitCategory.PHYSICAL.name,
                    "power": float(i % 10),
                    "is_active": True
                }
                for i in range(200)
            ]
        }

    @pytest.mark.benchmark(
        group="game-state",
        min_rounds=100
    )
    async def test_game_state_operations(self, benchmark, game_instance, large_save_data):
        """Benchmark game state operations"""

        async def run_state_ops():
            await game_instance.save_game()
            await game_instance.load_game()
            game_instance.stats.validate()

        benchmark(run_state_ops)

    @pytest.mark.benchmark(group="mutations")
    def test_mutation_generation(self, benchmark, game_instance):
        """Benchmark mutation generation"""
        mutation_system = MutationSystem()

        def generate_mutations():
            for _ in range(100):
                mutation = mutation_system.generate_mutation()
                game_instance.stats.apply_mutation(mutation)

        benchmark(generate_mutations)

    @pytest.mark.benchmark(
        group="mutations",
        min_rounds=1000
    )
    def test_mutation_chain_effects(self, benchmark, game_instance):
        """Benchmark mutation chain applications"""
        mutation_system = MutationSystem()
        mutations = [mutation_system.generate_mutation() for _ in range(100)]

        def apply_mutations():
            for mutation in mutations:
                mutation_system.apply_mutation(game_instance.stats, mutation)
                game_instance.stats.validate()

        benchmark(apply_mutations)

    @pytest.mark.benchmark(group="stats")
    def test_stat_calculations(self, benchmark, game_instance):
        """Benchmark stat calculations"""
        modifiers = [
            StatModifier(type="add", value=i)
            for i in range(100)
        ]

        def modify_stats():
            for mod in modifiers:
                game_instance.stats.apply_modifier("hp", mod)
                game_instance.stats.validate()

        benchmark(modify_stats)

    @pytest.mark.benchmark(
        group="stats",
        min_rounds=1000
    )
    def test_vectorized_stat_operations(self, benchmark):
        """Benchmark vectorized stat operations"""
        stats = PlayerStats()
        modifiers = np.array([
            StatModifier(type="add", value=i)
            for i in range(1000)
        ])

        def batch_modify():
            stats.apply_modifiers_bulk([
                ("hp", mod) for mod in modifiers
            ])
            stats.validate()

        benchmark(batch_modify)

    @pytest.mark.benchmark(group="achievements")
    def test_achievement_processing(self, benchmark, game_instance):
        """Benchmark achievement processing"""
        achievements = [
            Achievement(
                id=f"ach_{i}",
                name=f"Achievement {i}",
                description="Test achievement",
                category=AchievementCategory.SURVIVAL
            )
            for i in range(100)
        ]

        def process_achievements():
            for ach in achievements:
                game_instance.achievement_manager.check_achievement(ach)

        benchmark(process_achievements)

    @pytest.mark.benchmark(
        group="achievements",
        min_rounds=100
    )
    def test_achievement_processing(self, benchmark, temp_dir):
        """Benchmark achievement system"""
        manager = AchievementManager()

        # Add test achievements
        for i in range(1000):
            achievement = Achievement(
                id=f"achievement_{i}",
                name=f"Test Achievement {i}",
                description="Test description",
                category=AchievementCategory.SURVIVAL,
                max_progress=100
            )
            manager.achievements[achievement.id] = achievement

        def process_achievements():
            manager.check_run_achievements({
                "health": 5,
                "mutations": 50,
                "items": 100
            })

        benchmark(process_achievements)

    @pytest.mark.benchmark(
        group="combat",
        min_rounds=1000
    )
    def test_combat_simulation(self, benchmark, game_instance):
        """Benchmark combat system performance"""

        def simulate_combat():
            # Simulate 100 combat rounds
            for _ in range(100):
                # Apply damage
                game_instance.stats.hp -= 5
                # Check resistances
                for resistance in game_instance.stats.resistances.values():
                    damage_reduced = 5 * resistance
                # Heal
                game_instance.stats.hp = min(
                    game_instance.stats.hp + 2,
                    game_instance.stats.max_hp
                )
                # Validate state
                game_instance.stats.validate()

        benchmark(simulate_combat)

    @pytest.mark.benchmark(
        group="memory",
        min_rounds=10
    )
    def test_memory_usage(self, benchmark, game_instance, large_save_data):
        """Benchmark memory usage during operations"""

        def memory_test():
            # Load large dataset
            game_instance.stats.from_dict(large_save_data["stats"])
            # Perform memory-intensive operations
            for _ in range(100):
                game_instance.stats.validate()
                game_instance.stats.resistances.update({
                    str(i): float(i) for i in range(1000)
                })

        benchmark(memory_test)


@pytest.mark.benchmark
class BenchmarkSuite:
    @pytest.fixture
    def game(self, tmp_path):
        """Setup game instance"""
        from modules.game import SimulacraGame
        return SimulacraGame(save_dir=tmp_path)

    @pytest.mark.benchmark(group="core")
    def test_game_initialization(self, benchmark, game):
        """Benchmark game initialization"""
        def run_init():
            game.initialize()
            game.stats.validate()
        benchmark(run_init)

    @pytest.mark.benchmark(group="stats")
    def test_stat_system(self, benchmark, game):
        """Benchmark stat system operations"""
        from modules.stats import StatModifier
        def modify_stats():
            for i in range(100):
                game.stats.apply_modifier("hp", StatModifier("add", 1))
        benchmark(modify_stats)

    @pytest.mark.benchmark(group="mutations")
    def test_mutation_system(self, benchmark, game):
        """Benchmark mutation operations"""
        from modules.mutations import MutationSystem
        system = MutationSystem()
        def generate_mutations():
            for _ in range(50):
                mutation = system.generate_mutation()
                game.stats.apply_mutation(mutation)
        benchmark(generate_mutations)
