import subprocess
import sys
from pathlib import Path


def run_git_command(cmd: list, description: str) -> bool:
    """Run a git command with error handling"""
    print(f"📝 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e.stderr}")
        return False


def setup_git():
    """Complete Git setup process"""
    print("🚀 Starting Git setup...")

    # Verify git is initialized
    if not Path('.git').exists():
        if not run_git_command(['git', 'init'], "Initializing git repository"):
            return False

    # Configure user if needed
    if not run_git_command(['git', 'config', 'user.name'], "Checking git config"):
        name = input("Enter your Git username: ")
        email = input("Enter your Git email: ")
        run_git_command(['git', 'config', '--local', 'user.name', name], "Setting username")
        run_git_command(['git', 'config', '--local', 'user.email', email], "Setting email")

    # Create and switch to main branch
    run_git_command(['git', 'checkout', '-b', 'main'], "Creating main branch")

    # Add files
    run_git_command(['git', 'add', '.'], "Adding files")
    run_git_command(['git', 'commit', '-m', "Initial commit: Simulacra v2.0"], "Creating commit")

    # Create or update remote
    try:
        subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True)
    except:
        pass

    print("Creating GitHub repository...")
    create_result = subprocess.run([
        'gh', 'repo', 'create',
        'Simulacra_v2',
        '--private',
        '--source=.',
        '--remote=origin'
    ], capture_output=True, text=True)

    if create_result.returncode == 0:
        # Push to remote
        if run_git_command(['git', 'push', '-u', 'origin', 'main'], "Pushing to remote"):
            print("✅ Git setup complete!")
            print("\nNext steps:")
            print("1. Wait a few minutes for GitHub to process the push")
            print("2. Press Ctrl+Shift+P")
            print("3. Type: GitHub Copilot: Build remote workspace index")
            return True

    print("❌ Setup failed")
    return False


if __name__ == "__main__":
    sys.exit(0 if setup_git() else 1)
