from pathlib import Path
import sys
import subprocess


def setup_dev_environment():
    """Setup development environment"""
    print("🔧 Setting up development environment...")

    # Create required directories
    directories = ['tools', 'profiling', 'config', 'logs']
    for dir_name in directories:
        path = Path(dir_name)
        path.mkdir(exist_ok=True)
        print(f"📁 Created directory: {path}")

    # Create default config
    config_file = Path('config/game_config.yml')
    if not config_file.exists():
        config_file.write_text("""
debug_mode: true
profile_enabled: true
log_level: DEBUG
        """.strip())
        print(f"📝 Created default config: {config_file}")

    # Install/update dependencies
    print("📦 Installing dependencies...")
    subprocess.run([
        sys.executable,
        '-m', 'pip',
        'install',
        '-r',
        'requirements.txt'
    ])

    print("\n✅ Development environment setup complete!")
    print("\nNext steps:")
    print("1. Press Ctrl+Shift+P")
    print("2. Type 'Run Task'")
    print("3. Select 'Monitor Tests'")


if __name__ == "__main__":
    setup_dev_environment()
