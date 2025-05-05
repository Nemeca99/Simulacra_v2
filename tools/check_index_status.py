import json
import time
from pathlib import Path
import subprocess


def check_copilot_status():
    """Monitor Copilot indexing status"""
    print("🔍 Checking Copilot index status...")

    # VS Code settings path
    vscode_dir = Path.home() / 'AppData' / 'Roaming' / 'Code' / 'User'
    copilot_state = vscode_dir / 'globalStorage' / 'github.copilot' / 'state.json'

    if not copilot_state.exists():
        print("❌ Copilot state file not found")
        return False

    try:
        # Read current state
        with open(copilot_state) as f:
            state = json.load(f)

        indexing_status = state.get('indexingStatus', {})
        print(f"\n📊 Current Status:")
        print(f"Active: {indexing_status.get('isIndexing', False)}")
        print(f"Progress: {indexing_status.get('progress', 0)}%")

        # Check repository status
        repo_result = subprocess.run(
            ['gh', 'repo', 'view', '--json', 'id,visibility,isPrivate'],
            capture_output=True,
            text=True
        )

        if repo_result.returncode == 0:
            repo_info = json.loads(repo_result.stdout)
            print(f"\n📦 Repository Info:")
            print(f"Visibility: {repo_info.get('visibility', 'unknown')}")
            print(f"Private: {repo_info.get('isPrivate', True)}")

        print("\n🔧 Troubleshooting Steps:")
        print("1. If stuck, try:")
        print("   - Close VS Code")
        print("   - Delete .vscode/copilot folder")
        print("   - Reopen VS Code")
        print("2. Verify GitHub authentication:")
        print("   - Ctrl+Shift+P")
        print("   - Type: GitHub: Sign in")

        return True

    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False


if __name__ == "__main__":
    check_copilot_status()
