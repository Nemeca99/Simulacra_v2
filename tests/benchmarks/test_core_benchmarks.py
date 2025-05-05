import pytest
from pathlib import Path
from modules.game import SimulacraGame
from modules.shared_types import StatModifierData, ModifierType
from modules.mutations import MutationSystem


@pytest.mark.usefixtures("tmp_path")
class TestCoreBenchmarks:

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.game = SimulacraGame(save_dir=tmp_path)
        self.game.initialize()  # Initialize game before tests
        self.mutation_system = MutationSystem()

    @pytest.mark.benchmark(group="core")
    def test_game_initialization(self, benchmark):
        """Benchmark game initialization"""

        def run_init():
            self.game.initialize()
            self.game.stats.validate()

        benchmark(run_init)

    @pytest.mark.benchmark(group="stats")
    def test_stat_operations(self, benchmark):
        """Benchmark stat operations"""

        def run_stats():
            for i in range(100):
                modifier = StatModifierData(
                    stat_name="hp",
                    mod_type=ModifierType.ADD,
                    value=1.0
                )
                self.game.stats.apply_modifier(modifier)

        benchmark(run_stats)

    @pytest.mark.benchmark(group="mutations")
    def test_mutation_generation(self, benchmark):
        """Benchmark mutation generation and application"""

        def run_mutations():
            for _ in range(50):
                effects = self.mutation_system.generate_mutation()
                for effect in effects:
                    self.game.stats.apply_modifier(StatModifierData(
                        stat_name=effect.target_stat,
                        mod_type=effect.effect_type,
                        value=effect.magnitude
                    ))

        benchmark(run_mutations)
