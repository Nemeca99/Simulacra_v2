import subprocess
import sys
from pathlib import Path


def fix_remote():
    """Fix GitHub remote configuration"""
    print("🔧 Checking repository configuration...")

    # Check if git is initialized
    if not Path('.git').exists():
        print("❌ Git not initialized")
        return False

    try:
        # Check current remote
        result = subprocess.run(['git', 'remote', '-v'],
                              capture_output=True,
                              text=True)

        if 'origin' not in result.stdout:
            print("Creating GitHub repository...")
            # Create new repository
            create_result = subprocess.run([
                'gh', 'repo', 'create',
                'Simulacra_v2',
                '--private',
                '--source=.',
                '--remote=origin',
                '--push'
            ], capture_output=True, text=True)

            if create_result.returncode != 0:
                print(f"❌ Failed to create repository: {create_result.stderr}")
                return False

        # Force push to remote
        print("Pushing to remote...")
        push_result = subprocess.run([
            'git', 'push', '-u', 'origin', 'main'
        ], capture_output=True, text=True)

        if push_result.returncode == 0:
            print("✅ Repository configured successfully!")
            print("\nNext steps:")
            print("1. Wait a few minutes for GitHub to process the push")
            print("2. Press Ctrl+Shift+P")
            print("3. Type: GitHub Copilot: Build remote workspace index")
            return True
        else:
            print(f"❌ Push failed: {push_result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    sys.exit(0 if fix_remote() else 1)
