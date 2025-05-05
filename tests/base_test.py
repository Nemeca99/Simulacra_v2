import pytest
from pathlib import Path
from typing import Optional

class BaseGameTest:
    """Base class for game tests"""

    @pytest.fixture(autouse=True)
    def setup_base(self, temp_dir: Path):
        """Setup base test environment"""
        self.test_dir = temp_dir
        self.save_dir = temp_dir / "saves"
        self.save_dir.mkdir(exist_ok=True)

class BasePerformanceTest(BaseGameTest):
    """Base class for performance tests"""

    @pytest.fixture(autouse=True)
    def setup_performance(self):
        """Setup performance monitoring"""
        self.iterations = 1000
        self.sample_size = 100