import subprocess
import os
from pathlib import Path


def run_command(cmd: list) -> bool:
    """Run a command and return success status"""
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {' '.join(cmd)}: {e.stderr}")
        return False


def setup_repository():
    """Setup GitHub repository for Simulacra"""
    print("🚀 Setting up Simulacra repository...")

    # Initialize if needed
    if not Path('.git').exists():
        if not run_command(['git', 'init']):
            return False

    # Create .gitignore if it doesn't exist
    gitignore = Path('.gitignore')
    if not gitignore.exists():
        gitignore.write_text("""
__pycache__/
*.py[cod]
*$py.class
.vscode/
.env
logs/
*.log
dist/
build/
venv/
.pytest_cache/
""")

    # Add and commit files
    run_command(['git', 'add', '.'])
    run_command(['git', 'commit', '-m', "Initial commit: Simulacra v2.0"])

    # Create and push to GitHub repository
    run_command([
        'gh', 'repo', 'create',
        'Simulacra_v2',
        '--private',
        '--source=.',
        '--remote=origin',
        '--push'
    ])

    print("✅ Repository setup complete!")
    print("📝 Next steps:")
    print("1. Open Command Palette (Ctrl+Shift+P)")
    print("2. Type: GitHub Copilot: Build remote workspace index")
    print("3. Press Enter to start indexing")


if __name__ == "__main__":
    setup_repository()
