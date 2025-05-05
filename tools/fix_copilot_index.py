import subprocess
import json
from pathlib import Path
import time


def check_and_fix_index():
    """Validate and fix repository for Copilot indexing"""
    print("🔍 Checking repository configuration...")

    # 1. Verify repository structure
    required_files = [
        "README.md",
        "requirements.txt",
        "setup.py",
        ".gitignore"
    ]

    # Create missing files
    for file in required_files:
        if not Path(file).exists():
            if file == "README.md":
                Path(file).write_text("""# Simulacra v2.0

A survival game where players manage traits, mutations, and disasters.

## Features
- Trait system with merging and upgrades
- Mutation and disaster events
- Reflection Points (RP) economy

## Development
- Python 3.10+
- VSCode with Copilot
- Git version control
""")
            elif file == "requirements.txt":
                Path(file).write_text("""colorama
pyyaml
pytest
""")
            elif file == "setup.py":
                Path(file).write_text("""from setuptools import setup, find_packages

setup(
    name="simulacra",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "colorama",
        "pyyaml",
        "pytest",
    ],
)
""")
            elif file == ".gitignore":
                Path(file).write_text("""__pycache__/
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

    # 2. Push changes
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', "chore: Add required repository files"],
                      capture_output=True)
        subprocess.run(['git', 'push'], check=True)
        print("✅ Repository files updated")

        # 3. Wait for GitHub to process
        print("⏳ Waiting for GitHub to process changes...")
        time.sleep(30)  # Give GitHub time to process

        print("""
✅ Repository should now be ready for indexing!

Next steps:
1. Close and reopen VS Code
2. Press Ctrl+Shift+P
3. Type: GitHub Copilot: Build remote workspace index
4. Wait for indexing to complete

If indexing still fails:
- Check GitHub repository visibility (should be public or properly licensed)
- Verify GitHub account has active Copilot subscription
- Try signing out and back in to GitHub in VS Code
""")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error updating repository: {e}")
        return False


if __name__ == "__main__":
    check_and_fix_index()
