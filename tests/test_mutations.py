import pytest
from modules.mutations import MutationType, MutationSystem
from modules.stats import PlayerStats

class TestMutations:
    @pytest.fixture
    def mutation_system(self) -> MutationSystem:
        return MutationSystem()

    def test_mutation_generation(self, mutation_system: MutationSystem):
        """Test mutation generation"""
        mutation = mutation_system.generate_mutation()
        assert mutation.name is not None
        assert len(mutation.effects) > 0

    def test_mutation_application(self, mutation_system: MutationSystem):
        """Test applying mutations to stats"""
        stats = PlayerStats()
        mutation = mutation_system.generate_mutation()

        old_stats = stats.copy()
        mutation_system.apply_mutation(stats, mutation)

        # Verify stats changed
        assert stats != old_stats

    def test_mutation_validation(self, mutation_system: MutationSystem):
        """Test mutation validation"""
        mutation = mutation_system.generate_mutation()
        assert mutation_system.validate_mutation(mutation)