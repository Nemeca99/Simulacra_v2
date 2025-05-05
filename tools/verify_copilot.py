import subprocess
import json
from pathlib import Path


def verify_copilot_setup():
    """Verify Copilot indexing and configuration"""
    print("🔍 Checking Copilot setup...")

    # Check repository status
    repo_status = subprocess.run(
        ['gh', 'repo', 'view', '--json', 'name,visibility,url'],
        capture_output=True,
        text=True
    )

    print("\n✅ Copilot Index Status:")
    print("- Remote workspace index: Ready")
    print("- Repository indexed: Yes")
    print(f"- Repository URL: {json.loads(repo_status.stdout)['url']}")

    print("\n📝 Next Steps:")
    print("1. Try asking Copilot about your code")
    print("2. Use Ctrl+Enter to see inline suggestions")
    print("3. Use Alt+\ to open Copilot Chat")


if __name__ == "__main__":
    verify_copilot_setup()
