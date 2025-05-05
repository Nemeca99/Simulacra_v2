import pstats
from pstats import SortKey

def analyze_profile(stats_file: str) -> None:
    """Analyze CPU profile stats"""
    stats = pstats.Stats(stats_file)

    print("\n=== Top 10 Time Consuming Functions ===")
    stats.sort_stats(SortKey.TIME).print_stats(10)

    print("\n=== Top 10 Cumulative Time Functions ===")
    stats.sort_stats(SortKey.CUMULATIVE).print_stats(10)

    print("\n=== Call Hierarchy ===")
    stats.print_callers(10)

if __name__ == '__main__':
    analyze_profile('game_profile.stats')