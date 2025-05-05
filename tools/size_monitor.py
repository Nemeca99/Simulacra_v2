from pathlib import Path
from collections import defaultdict
import json


def analyze_project_size():
    """Analyze project size and composition"""
    project_root = Path(__file__).parent.parent

    statistics = defaultdict(lambda: {"files": 0, "size": 0})

    for item in project_root.rglob("*"):
        if item.is_file():
            ext = item.suffix or "no_extension"
            size = item.stat().st_size
            statistics[ext]["files"] += 1
            statistics[ext]["size"] += size

    # Generate report
    report = {
        "extension_stats": dict(statistics),
        "total_size": sum(s["size"] for s in statistics.values()),
        "total_files": sum(s["files"] for s in statistics.values())
    }

    with open(project_root / "project_stats.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\nProject Size Analysis:")
    print("-" * 50)
    for ext, stats in sorted(statistics.items(),
                           key=lambda x: x[1]["size"],
                           reverse=True):
        mb_size = stats["size"] / (1024 * 1024)
        print(f"{ext:12} {stats['files']:6} files {mb_size:8.2f} MB")


if __name__ == "__main__":
    analyze_project_size()
