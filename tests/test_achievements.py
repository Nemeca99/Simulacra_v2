import pytest
from pathlib import Path
import tempfile
import shutil
from io import StringIO
import sys
from modules.achievements import Achievement, AchievementManager, AchievementCategory

class TestAchievements:
    @pytest.fixture
    def temp_dir(self):
        """Provide temporary directory for tests"""
        path = Path(tempfile.mkdtemp())
        yield path
        shutil.rmtree(path)

    @pytest.fixture
    def achievement_manager(self, temp_dir):
        """Provide achievement manager instance"""
        # Override the default save path for testing
        AchievementManager.ACHIEVEMENTS_PATH = temp_dir / "achievements.json"
        return AchievementManager()

    def test_achievement_creation(self):
        """Test achievement creation"""
        achievement = Achievement(
            id="test_achievement",
            name="Test Achievement",
            description="Test description",
            category=AchievementCategory.SURVIVAL
        )
        assert not achievement.is_unlocked()
        assert not achievement.is_hidden()
        assert achievement.validate()

    def test_achievement_unlocking(self, achievement_manager):
        """Test achievement unlocking"""
        # Add test achievement
        test_achievement = Achievement(
            id="test_unlock",
            name="Test Unlock",
            description="Test unlocking",
            category=AchievementCategory.MUTATION
        )
        achievement_manager.achievements["test_unlock"] = test_achievement

        # Test unlocking
        assert achievement_manager.unlock("test_unlock")
        assert test_achievement.is_unlocked()
        assert test_achievement.unlock_date is not None

    def test_hidden_achievement(self, achievement_manager):
        """Test hidden achievement behavior"""
        hidden_achievement = Achievement(
            id="hidden_test",
            name="Hidden Achievement",
            description="Secret achievement",
            category=AchievementCategory.SPECIAL,
            hidden=True
        )
        achievement_manager.achievements["hidden_test"] = hidden_achievement

        assert hidden_achievement.is_hidden()
        achievement_manager.unlock("hidden_test")
        assert not hidden_achievement.is_hidden()

    def test_achievement_persistence(self, achievement_manager, temp_dir):
        """Test achievement saving and loading"""
        # Add and unlock achievement
        achievement_manager.achievements["test_save"] = Achievement(
            id="test_save",
            name="Test Save",
            description="Test saving",
            category=AchievementCategory.SURVIVAL
        )
        achievement_manager.unlock("test_save")

        # Create new manager instance to test loading
        AchievementManager.ACHIEVEMENTS_PATH = temp_dir / "achievements.json"
        new_manager = AchievementManager()

        # Verify achievement persisted
        assert "test_save" in new_manager.achievements
        assert new_manager.achievements["test_save"].is_unlocked()

    def test_achievement_progress(self, achievement_manager):
        """Test achievement progress tracking"""
        achievement = Achievement(
            id="progress_test",
            name="Progress Test",
            description="Test progress tracking",
            category=AchievementCategory.COLLECTION,
            max_progress=5
        )
        achievement_manager.achievements["progress_test"] = achievement

        # Test initial state
        assert achievement.progress == 0
        assert not achievement.is_unlocked()

        # Update progress
        achievement.progress = 3
        assert achievement.validate()

        # Test invalid progress
        achievement.progress = 6
        assert not achievement.validate()

    def test_run_achievements(self, achievement_manager):
        """Test run-based achievement checks"""
        # Test first run achievement
        stats = {"total_runs": 1}
        achievement_manager.check_run_achievements(stats)
        assert achievement_manager.achievements["first_run"].is_unlocked()

        # Test no unlock for subsequent runs
        stats = {"total_runs": 2}
        achievement_manager.check_run_achievements(stats)
        assert len([a for a in achievement_manager.achievements.values() if a.is_unlocked()]) == 1

    def test_achievement_display(self, achievement_manager):
        """Test achievement display functionality"""
        # Add test achievements
        achievement_manager.achievements.update({
            "test1": Achievement(
                id="test1",
                name="Test 1",
                description="Visible achievement",
                category=AchievementCategory.SURVIVAL
            ),
            "test2": Achievement(
                id="test2",
                name="Test 2",
                description="Hidden achievement",
                category=AchievementCategory.SPECIAL,
                hidden=True
            )
        })

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            achievement_manager.display_achievements()
            output = captured_output.getvalue()

            # Verify output contains expected elements
            assert "🏆 Achievements" in output
            assert "Test 1" in output
            assert "???" in output  # Hidden achievement
            assert "Test 2" not in output  # Hidden achievement name shouldn't appear
        finally:
            sys.stdout = sys.__stdout__  # Restore stdout

    def test_achievement_error_handling(self, achievement_manager):
        """Test error handling in achievement operations"""
        # Test unlocking non-existent achievement
        assert not achievement_manager.unlock("non_existent")

        # Test loading from corrupted file
        with open(achievement_manager.ACHIEVEMENTS_PATH, 'w') as f:
            f.write("invalid json{")

        # Create new manager to test loading corrupted file
        new_manager = AchievementManager()
        assert "first_run" in new_manager.achievements  # Should initialize defaults

    def test_achievement_progress_update(self, achievement_manager):
        """Test achievement progress update mechanism"""
        achievement = Achievement(
            id="progress_update",
            name="Progress Update",
            description="Test progress updates",
            category=AchievementCategory.COLLECTION,
            max_progress=3
        )
        achievement_manager.achievements["progress_update"] = achievement

        # Test progress update and auto-unlock
        achievement_manager.update_progress("progress_update", 2)
        assert achievement.progress == 2
        assert not achievement.is_unlocked()

        achievement_manager.update_progress("progress_update", 1)
        assert achievement.progress == 3
        assert achievement.is_unlocked()

        # Test update on non-existent achievement
        achievement_manager.update_progress("non_existent", 1)