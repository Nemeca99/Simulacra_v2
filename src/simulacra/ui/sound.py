import winsound
from typing import Dict, Optional
from pathlib import Path


class SoundManager:
    """Manages game sound effects"""

    SOUNDS: Dict[str, str] = {
        'damage': 'damage.wav',
        'heal': 'heal.wav',
        'disaster': 'disaster.wav',
        'game_over': 'game_over.wav',
        'mutation': 'mutation.wav'
    }

    @classmethod
    def play(cls, sound_id: str) -> None:
        """Play a sound effect if available"""
        sound_path = Path(__file__).parent / 'sounds' / cls.SOUNDS.get(sound_id, '')
        if sound_path.exists():
            winsound.PlaySound(str(sound_path), winsound.SND_ASYNC)
