import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, check_output: bool=False) -> tuple[int, str]:
    """Run a command and return status and output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if check_output:
            return result.returncode, result.stdout
        return result.returncode, ""
    except Exception as e:
        return 1, str(e)


def setup_branch():
    """Setup git branch and push to remote"""
    print("🔧 Setting up git branch...")

    # Get current branch name
    _, branch = run_command(['git', 'branch', '--show-current'], True)
    branch = branch.strip()

    if not branch:
        # Create and switch to main branch
        print("Creating main branch...")
        run_command(['git', 'checkout', '-b', 'main'])

    # Stage all files
    print("Staging files...")
    run_command(['git', 'add', '.'])

    # Commit if needed
    _, status = run_command(['git', 'status', '--porcelain'], True)
    if status:
        print("Creating commit...")
        run_command(['git', 'commit', '-m', "Initial commit: Simulacra v2.0"])

    # Push to remote
    print("Pushing to remote...")
    code, output = run_command([
        'git', 'push', '-u', 'origin', 'main'
    ], True)

    if code == 0:
        print("✅ Branch setup complete!")
        print("\nNext steps:")
        print("1. Wait a few minutes for GitHub to process the push")
        print("2. Press Ctrl+Shift+P")
        print("3. Type: GitHub Copilot: Build remote workspace index")
        return True
    else:
        print(f"❌ Push failed: {output}")
        return False


if __name__ == "__main__":
    sys.exit(0 if setup_branch() else 1)
