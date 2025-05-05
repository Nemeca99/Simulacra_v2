from pathlib import Path
import shutil
import logging
from datetime import datetime
from cleanup_config import CleanupConfig


class ProjectCleaner:

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.config = CleanupConfig()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging with rotation"""
        log_dir = self.root_dir / "logs" / "cleanup"
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            filename=log_dir / f"cleanup_{datetime.now():%Y%m%d_%H%M%S}.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _rotate_log(self, log_file: Path) -> None:
        """Rotate large log files"""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = log_file.parent / "archived"
            backup_dir.mkdir(exist_ok=True)

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
            backup_path = backup_dir / backup_name

            # Move old log to backup
            shutil.move(str(log_file), str(backup_path))
            logging.info(f"Rotated log file: {log_file.name} -> {backup_name}")

            # Clean old backups (keep last 5)
            self._cleanup_old_backups(backup_dir)

        except Exception as e:
            logging.error(f"Failed to rotate log {log_file}: {e}")

    def _cleanup_old_backups(self, backup_dir: Path, keep: int=5) -> None:
        """Remove old backup files, keeping only the most recent ones"""
        try:
            # Get all backup files sorted by modification time
            backups = sorted(
                backup_dir.glob("*.log"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )

            # Remove old backups
            for old_backup in backups[keep:]:
                old_backup.unlink()
                logging.info(f"Removed old backup: {old_backup.name}")

        except Exception as e:
            logging.error(f"Failed to clean old backups: {e}")

    def clean(self) -> None:
        """Run full project cleanup"""
        logging.info("Starting project cleanup...")
        self._clean_dev_files()
        self._clean_oversized_files()
        self._clean_empty_dirs()
        logging.info("Cleanup completed")

    def _clean_dev_files(self) -> None:
        """Clean development artifacts"""
        for pattern in self.config.dev_patterns:
            for file in self.root_dir.rglob(pattern):
                if self._is_protected(file):
                    continue
                try:
                    file.unlink()
                    logging.info(f"Removed dev file: {file}")
                except Exception as e:
                    logging.error(f"Failed to remove {file}: {e}")

    def _clean_oversized_files(self) -> None:
        """Clean files exceeding size limits"""
        for ext, limit in self.config.size_limits.items():
            limit_bytes = limit * 1024 * 1024  # Convert MB to bytes
            for file in self.root_dir.rglob(f"*{ext}"):
                if not file.exists():
                    continue

                if file.stat().st_size > limit_bytes:
                    if ext == ".log":
                        self._rotate_log(file)
                    else:
                        logging.warning(f"Large file found: {file}")

    def _clean_empty_dirs(self) -> None:
        """Remove empty directories"""
        for dir_path in self.root_dir.rglob("**/"):
            if self._is_protected(dir_path):
                continue

            try:
                # Check if directory is empty
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    logging.info(f"Removed empty directory: {dir_path}")
            except Exception as e:
                logging.error(f"Failed to remove directory {dir_path}: {e}")

    def _is_protected(self, path: Path) -> bool:
        """Check if path should be preserved"""
        rel_path = path.relative_to(self.root_dir)
        return (str(rel_path) in self.config.protected_files or
                any(str(rel_path).startswith(d) for d in self.config.protected_dirs))


if __name__ == "__main__":
    cleaner = ProjectCleaner(Path(__file__).parent.parent)
    cleaner.clean()
