import aiofiles
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import json

class AsyncFileManager:
    """Asynchronous file operations manager"""

    @staticmethod
    async def load_json(path: Path) -> Optional[Dict]:
        """Load JSON file asynchronously"""
        try:
            async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Async load failed: {e}")
            return None

    @staticmethod
    async def save_json(path: Path, data: Dict) -> bool:
        """Save JSON file asynchronously"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2))
            return True
        except Exception as e:
            logger.error(f"Async save failed: {e}")
            return False