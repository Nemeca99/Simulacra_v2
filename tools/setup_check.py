import subprocess
import os


def check_git_setup():
    """Verify git and GitHub setup"""
    checks = {
        "Git Repository": False,
        "Remote Config": False,
        "Files Tracked": 0,
        "GitHub Connected": False
    }

    try:
        # Check git init
        if os.path.exists('.git'):
            checks["Git Repository"] = True

            # Check remote
            remote = subprocess.run(['git', 'remote', '-v'],
                                 capture_output=True,
                                 text=True)
            checks["Remote Config"] = "origin" in remote.stdout

            # Count tracked files
            files = subprocess.run(['git', 'ls-files'],
                                capture_output=True,
                                text=True)
            checks["Files Tracked"] = len(files.stdout.splitlines())

            # Check GitHub CLI
            gh = subprocess.run(['gh', 'auth', 'status'],
                             capture_output=True,
                             text=True)
            checks["GitHub Connected"] = gh.returncode == 0

    except Exception as e:
        print(f"Error during checks: {e}")

    # Print results
    print("\n=== Setup Status ===")
    for key, value in checks.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}: {value}")


if __name__ == "__main__":
    check_git_setup()
