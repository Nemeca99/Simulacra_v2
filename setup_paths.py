"""
Setup Python paths for the Simulacra project.
Run this before importing any project modules.
"""
import sys
import os
from pathlib import Path


def setup_paths():
    """Add project directories to Python path"""
    # Get project root directory
    root_dir = Path(__file__).parent.absolute()

    # Paths to add
    paths = [
        str(root_dir),
        str(root_dir / "src"),
        str(root_dir / "modules")
    ]

    # Add to sys.path if not already present
    for path in paths:
        if path not in sys.path:
            sys.path.insert(0, path)

    # Set environment variable for child processes
    os.environ["PYTHONPATH"] = os.pathsep.join([
        *paths,
        os.environ.get("PYTHONPATH", "")
    ])

    return paths


if __name__ == "__main__":
    paths = setup_paths()
    print("Python paths set up successfully:")
    for path in paths:
        print(f"  - {path}")
