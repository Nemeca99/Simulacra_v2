"""
Debug module imports and paths
"""
import sys
import os
from pathlib import Path

# Import path setup
from setup_paths import setup_paths
setup_paths()

def debug_paths():
    """Print Python path information"""
    print("\nPython path:")
    for i, path in enumerate(sys.path):
        print(f"{i}: {path}")

    print("\nCurrent directory:", os.getcwd())

    # Check module files
    module_path = Path("src/simulacra/core/traits.py")
    if module_path.exists():
        print(f"\nTraits module exists at: {module_path.absolute()}")
        with open(module_path, "r") as f:
            content = f.read()
        print("\nFirst 100 characters of traits.py:")
        print(content[:100])
    else:
        print(f"\nTraits module NOT found at: {module_path.absolute()}")

    # Try to import and inspect
    try:
        from simulacra.core.traits import TraitSystem
        print("\nSuccessfully imported TraitSystem")
        print("TraitSystem attributes:", dir(TraitSystem))

        # Create instance
        system = TraitSystem()
        print("Instance attributes:", dir(system))

    except Exception as e:
        print(f"\nError importing TraitSystem: {e}")

if __name__ == "__main__":
    debug_paths()