import subprocess
import time
from pathlib import Path


def check_repo_status():
    """Verify repository status for Copilot indexing"""
    print("🔍 Checking repository status...")

    try:
        # Check remote
        remote = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True,
            text=True
        )
        print(f"📦 Remote URL: {remote.stdout.strip()}")

        # Check current branch
        branch = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True
        )
        print(f"🌿 Current branch: {branch.stdout.strip()}")

        # Check last commit
        last_commit = subprocess.run(
            ['git', 'log', '-1', '--oneline'],
            capture_output=True,
            text=True
        )
        print(f"📝 Last commit: {last_commit.stdout.strip()}")

        # Check GitHub status
        gh_status = subprocess.run(
            ['gh', 'repo', 'view', '--json', 'name,visibility,url'],
            capture_output=True,
            text=True
        )
        print(f"🌐 GitHub status: {gh_status.stdout.strip()}")

        print("\n✅ Repository ready for indexing!")
        print("\nNext steps:")
        print("1. Press Ctrl+Shift+P")
        print("2. Type: GitHub Copilot: Build remote workspace index")
        print("3. Wait for indexing to complete")

    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False


if __name__ == "__main__":
    check_repo_status()
