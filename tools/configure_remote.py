import subprocess
import sys
from pathlib import Path


def configure_remote():
    """Configure GitHub remote for Copilot indexing"""
    print("🔧 Configuring GitHub remote...")

    try:
        # Get GitHub username
        user_result = subprocess.run(
            ['gh', 'api', 'user', '--jq', '.login'],
            capture_output=True,
            text=True,
            check=True
        )
        username = user_result.stdout.strip()

        # Set the remote URL
        remote_url = f"https://github.com/{username}/Simulacra_v2.git"

        # Remove existing remote if any
        subprocess.run(['git', 'remote', 'remove', 'origin'],
                     capture_output=True)

        # Add new remote
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url],
                     check=True)

        # Push to remote
        print(f"📤 Pushing to {remote_url}")
        push_result = subprocess.run(
            ['git', 'push', '-u', 'origin', 'main'],
            capture_output=True,
            text=True
        )

        if push_result.returncode == 0:
            print("✅ Remote configuration successful!")
            print("\nNext steps:")
            print("1. Wait 2-3 minutes for GitHub to process")
            print("2. Press Ctrl+Shift+P")
            print("3. Type: GitHub Copilot: Build remote workspace index")
            return True
        else:
            print(f"❌ Push failed: {push_result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Configuration failed: {e.stderr}")
        return False


if __name__ == "__main__":
    sys.exit(0 if configure_remote() else 1)
