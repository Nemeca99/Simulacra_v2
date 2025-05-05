import json
from pathlib import Path
import time
import os
import shutil


def reset_copilot_index():
    """Reset Copilot indexing state"""
    print("🔄 Resetting Copilot index...")

    # Locate Copilot cache directories
    appdata = Path(os.getenv('APPDATA'))
    vscode = Path(os.getenv('USERPROFILE')) / '.vscode'

    cache_dirs = [
        appdata / 'Code/User/workspaceStorage',
        vscode / 'copilot',
        Path.home() / '.cache/copilot'
    ]

    for cache_dir in cache_dirs:
        if cache_dir.exists():
            print(f"Cleaning {cache_dir}")
            try:
                # Remove index files only
                for file in cache_dir.glob('**/index*'):
                    file.unlink()
                print(f"✅ Cleared {cache_dir}")
            except Exception as e:
                print(f"⚠️ Error clearing {cache_dir}: {e}")

    print("""
✅ Index reset complete!

Next steps:
1. Close VS Code completely
2. Reopen VS Code
3. Press Ctrl+Shift+P
4. Type: GitHub Copilot: Build remote workspace index
5. Wait for indexing to complete
""")


if __name__ == "__main__":
    reset_copilot_index()
