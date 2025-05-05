"""
Setup Python paths for Simulacra project
"""
import sys
import os
from pathlib import Path


def setup_paths():
    """Add project paths to Python path"""
    # Get project root directory
    root_dir = Path(__file__).parent.parent.absolute()
    src_dir = root_dir / "src"

    # Add src directory to path
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Set PYTHONPATH environment variable
    os.environ["PYTHONPATH"] = os.pathsep.join([
        str(src_dir),
        os.environ.get("PYTHONPATH", "")
    ])


if __name__ == "__main__":
    setup_paths()
    print("Python paths configured:")
    for path in sys.path[:5]:
        print(f"  - {path}")
