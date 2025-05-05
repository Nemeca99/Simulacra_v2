import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, Any, Optional
import json
from contextlib import asynccontextmanager

from modules.logger import logger

class AsyncIO:
    """Asynchronous I/O operations"""

    @staticmethod
    @asynccontextmanager
    async def atomic_write(path: Path):
        """Atomic file writing context manager"""
        temp_path = path.with_suffix('.tmp')
        try:
            async with aiofiles.open(temp_path, mode='w', encoding='utf-8') as f:
                yield f
            temp_path.replace(path)
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

    @staticmethod
    async def load_json(path: Path) -> Optional[Dict]:
        """Load JSON file asynchronously"""
        try:
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Async load failed: {e}")
            return None

    @staticmethod
    async def save_json(path: Path, data: Dict) -> bool:
        """Save JSON file asynchronously with atomic writes"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            async with AsyncIO.atomic_write(path) as f:
                await f.write(json.dumps(data, indent=2))
            return True
        except Exception as e:
            logger.error(f"Async save failed: {e}")
            return False