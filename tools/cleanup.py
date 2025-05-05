from pathlib import Path
import shutil
import os
from typing import Set, List
import logging
from datetime import datetime

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_dir / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_protected_paths() -> Set[Path]:
    """Get paths that should not be cleaned"""
    return {
        Path(".venv"),  # Virtual environment
        Path("data/default_config.json"),
        Path("data/saves"),
        Path("logs/game.log")
    }


def cleanup_project() -> None:
    """Clean up temporary and cached files with permission handling"""
    project_root = Path(__file__).parent.parent
    protected = get_protected_paths()

    # Patterns to clean
    cleanup_patterns: List[str] = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/.pytest_cache",
        "**/temp",
        "logs/*.log",
        "data/saves/*.bak"
    ]

    bytes_cleaned = 0
    files_removed = 0
    errors = 0

    print("Starting cleanup process...")

    for pattern in cleanup_patterns:
        for item in project_root.glob(pattern):
            # Skip protected paths
            if any(protect in item.parents or protect == item for protect in protected):
                logging.info(f"Skipping protected path: {item}")
                continue

            try:
                if item.is_file():
                    size = item.stat().st_size
                    try:
                        item.unlink(missing_ok=True)
                        bytes_cleaned += size
                        files_removed += 1
                        print(f"Removed: {item.relative_to(project_root)}")
                    except PermissionError:
                        logging.warning(f"Permission denied: {item}")
                        errors += 1
                elif item.is_dir():
                    try:
                        size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                        shutil.rmtree(item, ignore_errors=True)
                        bytes_cleaned += size
                        print(f"Removed directory: {item.relative_to(project_root)}")
                    except PermissionError:
                        logging.warning(f"Permission denied on directory: {item}")
                        errors += 1

            except Exception as e:
                logging.error(f"Error processing {item}: {e}")
                errors += 1
                continue

    mb_cleaned = bytes_cleaned / (1024 * 1024)

    # Print summary
    print("\nCleanup Summary:")
    print(f"Files removed: {files_removed}")
    print(f"Space cleaned: {mb_cleaned:.2f} MB")
    if errors > 0:
        print(f"Errors encountered: {errors} (see logs for details)")

    logging.info(f"Cleanup completed - Removed {files_removed} files ({mb_cleaned:.2f} MB)")
    if errors > 0:
        logging.warning(f"Encountered {errors} errors during cleanup")


if __name__ == "__main__":
    try:
        cleanup_project()
    except Exception as e:
        logging.critical(f"Critical error during cleanup: {e}")
        print(f"Critical error occurred. Check logs for details.")
