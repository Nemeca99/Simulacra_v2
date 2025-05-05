import subprocess
import os
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


def setup_github():
    """Setup GitHub repository and connection"""
    print("🚀 Setting up GitHub repository...")

    # Check if gh is installed
    status, _ = run_command(['gh', '--version'])
    if status != 0:
        print("❌ GitHub CLI not found. Please install it first.")
        return False

    # Check auth status
    status, _ = run_command(['gh', 'auth', 'status'])
    if status != 0:
        print("⚠️ Not logged in to GitHub. Please run 'gh auth login' first.")
        return False

    # Create repository if needed
    if not Path('.git').exists():
        print("Initializing git repository...")
        run_command(['git', 'init'])
        run_command(['git', 'add', '.'])
        run_command(['git', 'commit', '-m', "Initial commit: Simulacra v2.0"])

    # Check if remote exists
    status, output = run_command(['git', 'remote', '-v'], True)
    if 'origin' not in output:
        print("Creating GitHub repository...")
        status, _ = run_command([
            'gh', 'repo', 'create',
            'Simulacra_v2',
            '--private',
            '--source=.',
            '--remote=origin',
            '--push'
        ])
        if status != 0:
            print("❌ Failed to create repository")
            return False

    print("✅ GitHub setup complete!")
    return True


if __name__ == "__main__":
    setup_github()
