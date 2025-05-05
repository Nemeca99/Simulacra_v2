import pytest
from tests.base_test import BasePerformanceTest
from modules.traits import (
    TraitManager, Trait, TraitCategory,
    CompressionType, TraitValidation, TraitValidationError
)


class TestTraits(BasePerformanceTest):

    @pytest.fixture
    def trait_manager(self, temp_dir):
        """Provide test trait manager"""
        manager = TraitManager()
        manager.TRAIT_FILE = temp_dir / "traits.json"
        return manager

    @pytest.mark.benchmark(
        group="traits",
        min_rounds=1000
    )
    def test_trait_activation_performance(self, benchmark, trait_manager):
        """Benchmark trait activation performance"""
        # Add test traits
        for i in range(100):
            trait = Trait(
                id=f"trait_{i}",
                name=f"Test Trait {i}",
                description="Test trait",
                category=TraitCategory(i % 4),
                power=1.0
            )
            trait_manager.add_trait(trait)

        def activate_traits():
            for i in range(10):
                trait_manager.activate_trait(f"trait_{i}")

        benchmark(activate_traits)

    @pytest.mark.benchmark(
        group="traits",
        min_rounds=1000
    )
    def test_stat_calculation_performance(self, benchmark):
        """Benchmark stat calculation performance"""
        manager = TraitManager()

        # Add and activate test traits
        for i in range(100):
            trait = Trait(
                id=f"trait_{i}",
                name=f"Test Trait {i}",
                description="Test trait",
                category=TraitCategory(i % 4),
                power=1.0
            )
            manager.add_trait(trait)
            manager.activate_trait(f"trait_{i}")

        benchmark(manager.calculate_stat_modifiers)

    @pytest.mark.benchmark(
        group="traits-io",
        min_rounds=100
    )
    def test_trait_loading_performance(self, benchmark, trait_manager):
        """Benchmark trait loading performance"""
        # Generate large trait dataset
        traits = [
            {
                'id': f'trait_{i}',
                'name': f'Test Trait {i}',
                'description': 'Test trait description',
                'category': TraitCategory(i % 4).name,
                'power': 1.0,
                'is_active': True,
                'requirements': {}
            }
            for i in range(1000)
        ]

        # Save traits
        trait_manager._save_binary({'traits': traits})

        # Benchmark loading
        benchmark(trait_manager._load_binary)

    @pytest.mark.benchmark(
        group="traits-compression",
        min_rounds=100
    )
    def test_compression_performance(self, benchmark, trait_manager):
        """Benchmark different compression methods"""
        # Generate test data
        traits = [
            {
                'id': f'trait_{i}',
                'name': f'Test Trait {i}',
                'description': 'Test trait description',
                'category': TraitCategory(i % 4).name,
                'power': 1.0,
                'is_active': True,
                'requirements': {}
            }
            for i in range(1000)
        ]

        def test_compression():
            # Test ZSTD compression
            manager_zstd = TraitManager(compression=CompressionType.ZSTD)
            manager_zstd._save_binary({'traits': traits})

            # Test LZ4 compression
            manager_lz4 = TraitManager(compression=CompressionType.LZ4)
            manager_lz4._save_binary({'traits': traits})

        benchmark(test_compression)

    @pytest.mark.benchmark(
        group="traits-validation",
        min_rounds=100
    )
    def test_trait_validation_performance(self, benchmark, trait_manager):
        """Benchmark trait validation performance"""
        # Generate test traits with some invalid ones
        traits = []
        for i in range(1000):
            trait = {
                'id': f'trait_{i}',
                'name': 'T' * (50 if i % 10 == 0 else 10),  # Some invalid names
                'description': 'Test trait description',
                'category': TraitCategory(i % 4).name,
                'power': float(i if i < 100 else 1000),  # Some invalid powers
                'is_active': True,
                'requirements': {str(j): 1.0 for j in range(i % 7)}  # Some invalid requirement counts
            }
            traits.append(trait)

        def validate_traits():
            trait_manager._process_trait_data({'traits': traits})

        benchmark(validate_traits)
