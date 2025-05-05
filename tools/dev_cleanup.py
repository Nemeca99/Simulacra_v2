from pathlib import Path
import shutil
from typing import Set


def get_dev_patterns() -> Set[str]:
    """Patterns for development artifacts"""
    return {
        "*.pdb",  # Debug symbols
        "*.dll",  # Non-essential DLLs
        "*.exe",  # Compiled executables
        "*.prof",  # Profile data
        "*.pyd",  # Python DLLs
        "*.chm"  # Help files
    }


def cleanup_dev_files() -> None:
    """Remove development artifacts"""
    project_root = Path(__file__).parent.parent

    # Essential files to keep
    keep_files = {
        project_root / ".venv" / "Scripts" / "python.exe",
        project_root / ".venv" / "Scripts" / "pip.exe"
    }

    total_cleaned = 0

    for pattern in get_dev_patterns():
        for file in project_root.rglob(pattern):
            if file in keep_files:
                continue

            if file.is_file():
                size = file.stat().st_size
                file.unlink()
                total_cleaned += size

    print(f"Cleaned {total_cleaned / (1024*1024):.2f} MB of development files")
