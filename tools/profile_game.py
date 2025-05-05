import cProfile
import pstats
from pathlib import Path
import sys


def profile_game():
    """Profile game performance"""
    # Add src to path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))

    profiler = cProfile.Profile()
    profiler.enable()

    # Run game for profiling
    from simulacra.core import game

    game.run(duration=60)  # Profile 60 seconds of gameplay

    profiler.disable()

    # Save stats
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.dump_stats("profile_results.prof")

    # Print top 10 time-consuming functions
    stats.print_stats(10)


if __name__ == "__main__":
    profile_game()
