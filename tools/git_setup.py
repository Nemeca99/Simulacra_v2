import subprocess
import sys
from pathlib import Path


def run_git_command(cmd: list, description: str, check: bool=True) -> tuple[bool, str]:
    """Run a git command with error handling"""
    print(f"📝 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        if not check:
            return False, e.stderr
        print(f"❌ Failed: {e.stderr}")
        return False, e.stderr


def setup_git():
    """Complete Git setup process"""
    print("🚀 Starting Git setup...")

    # Check current branch
    success, current_branch = run_git_command(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        "Checking current branch",
        check=False
    )

    if success:
        current_branch = current_branch.strip()
        if current_branch != 'main':
            run_git_command(
                ['git', 'checkout', '-b', 'main'],
                "Switching to main branch"
            )

    # Check if there are changes to commit
    success, status = run_git_command(
        ['git', 'status', '--porcelain'],
        "Checking git status",
        check=False
    )

    if status.strip():
        run_git_command(['git', 'add', '.'], "Adding files")
        run_git_command(
            ['git', 'commit', '-m', "Update: Simulacra v2.0 files"],
            "Creating commit"
        )

    # Check if repo exists on GitHub
    success, _ = run_git_command(
        ['gh', 'repo', 'view', 'Simulacra_v2'],
        "Checking if repository exists",
        check=False
    )

    if not success:
        print("Creating new GitHub repository...")
        create_result = subprocess.run([
            'gh', 'repo', 'create',
            'Simulacra_v2',
            '--private',
            '--source=.',
            '--remote=origin'
        ], capture_output=True, text=True)

        if create_result.returncode != 0:
            print(f"❌ Failed to create repository: {create_result.stderr}")
            return False

    # Push to remote
    success, push_output = run_git_command(
        ['git', 'push', '-u', 'origin', 'main'],
        "Pushing to remote",
        check=False
    )

    if success:
        print("✅ Git setup complete!")
        print("\nNext steps:")
        print("1. Wait a few minutes for GitHub to process the push")
        print("2. Press Ctrl+Shift+P")
        print("3. Type: GitHub Copilot: Build remote workspace index")
        return True
    else:
        print(f"❌ Push failed: {push_output}")
        return False


if __name__ == "__main__":
    sys.exit(0 if setup_git() else 1)
