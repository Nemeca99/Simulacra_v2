# modules/log_utils.py
from typing import Optional
from colorama import Fore, Style
from .logger import logger

def log_mutation(name: str, rarity: str, effect: str, time: int = 0) -> None:
    """Log mutation events with consistent formatting"""
    logger.mutation(name, rarity, effect, time)

def log_disaster(name: str, dtype: str, flair: str, dmg: float, time: int = 0) -> None:
    """Log disaster events with consistent formatting"""
    logger.disaster(name, dtype, flair, dmg, time)

def log_achievement(name: str) -> None:
    """Log achievement unlocks with consistent formatting"""
    logger.achievement(name)

def log_event(title: str, message: str, color: Optional[str] = Fore.CYAN) -> None:
    """Log generic game events with custom colors"""
    logger.info(f"{title}: {message}", color)
