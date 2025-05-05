import os
import logging
from datetime import datetime
import sys
from pathlib import Path
from typing import Optional, Dict
from colorama import Fore, Style
import gzip
import shutil
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class SimulacraLogger:
    """Enhanced logging system for Simulacra with color support and multi-output"""

    COLORS = {
        'DEBUG': Fore.LIGHTBLACK_EX,
        'INFO': '',
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
        'MUTATION': Fore.GREEN,
        'DISASTER': Fore.RED,
        'ACHIEVEMENT': Fore.YELLOW
    }

    MAX_BYTES = 5 * 1024 * 1024  # 5MB
    BACKUP_COUNT = 5

    LOG_LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self):
        self.log_dir = Path("data/logs")
        self.metrics_dir = self.log_dir / "metrics"
        self.setup_directories()
        self.setup_logging()
        self.metrics: Dict[str, int] = {"errors": 0, "warnings": 0}

        self.main_log = self.log_dir / "simulacra.log"
        self.run_log = self.log_dir / "current_run.log"

        self._clear_run_log()
        self._compress_old_logs()

    def setup_directories(self) -> None:
        """Create required directories"""
        for directory in [self.log_dir, self.metrics_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def setup_logging(self) -> None:
        """Initialize enhanced logging setup"""
        self.logger = logging.getLogger('simulacra')
        self.logger.setLevel(logging.DEBUG)

        # Main rotating log handler
        main_handler = RotatingFileHandler(
            self.log_dir / "simulacra.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )

        # Daily rotating debug log
        debug_handler = TimedRotatingFileHandler(
            self.log_dir / "debug.log",
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )

        # Format handlers
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        main_handler.setFormatter(formatter)
        debug_handler.setFormatter(formatter)

        self.logger.addHandler(main_handler)
        self.logger.addHandler(debug_handler)

    def _clear_run_log(self) -> None:
        """Initialize new run log"""
        with open(self.run_log, "w", encoding="utf-8") as f:
            f.write(f"=== SIMULACRA RUN LOG ===\n{datetime.now()}\n\n")

    def _compress_old_logs(self) -> None:
        """Compress rotated log files"""
        for i in range(1, self.BACKUP_COUNT + 1):
            log_file = self.main_log.with_suffix(f'.log.{i}')
            if log_file.exists():
                gz_file = log_file.with_suffix('.gz')
                with open(log_file, 'rb') as f_in:
                    with gzip.open(gz_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                log_file.unlink()  # Remove original file

    def _log(self, level: str, msg: str, color: Optional[str]=None) -> None:
        """Core logging function with color support"""
        color = color or self.COLORS.get(level, '')
        print(f"{color}{msg}{Style.RESET_ALL}")

        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(msg)

    def debug(self, msg: str) -> None:
        self._log('DEBUG', f"DEBUG: {msg}")

    def info(self, msg: str, color: Optional[str]=None) -> None:
        self._log('INFO', msg, color)

    def warning(self, msg: str) -> None:
        print(f"{Fore.YELLOW}WARNING: {msg}{Style.RESET_ALL}")
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self._log('ERROR', f"ERROR: {msg}")

    def mutation(self, name: str, rarity: str, effect: str, time: int) -> None:
        msg = f"[{time}s] 🌱 {name} [{rarity.upper()}] — {effect}"
        self._log('MUTATION', msg)
        self._append_run_log(msg)

    def disaster(self, name: str, dtype: str, flair: str, dmg: float, time: int) -> None:
        msg = f"[{time}s] ⚠️ {name} [{dtype.upper()}] — {flair} | Damage: -{dmg:.2f} HP"
        self._log('DISASTER', msg)
        self._append_run_log(msg)

    def achievement(self, name: str) -> None:
        msg = f"🏆 Achievement Unlocked: {name}"
        self._log('ACHIEVEMENT', msg)

    def _append_run_log(self, text: str) -> None:
        """Append to current run log"""
        with open(self.run_log, "a", encoding="utf-8") as f:
            f.write(f"{text}\n")


# Global logger instance
logger = SimulacraLogger()


def setup_logging() -> None:
    """Configure logging with rotation"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    handler = RotatingFileHandler(
        log_dir / "simulacra.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )

    logging.basicConfig(
        handlers=[handler],
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
