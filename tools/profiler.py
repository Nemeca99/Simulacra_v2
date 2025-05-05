import cProfile
import pstats
import time
from pathlib import Path
from datetime import datetime


class GameProfiler:

    def __init__(self):
        self.profiler = cProfile.Profile()
        self.start_time = None
        self.stats = {}

    def start(self):
        self.start_time = time.time()
        self.profiler.enable()

    def stop(self):
        self.profiler.disable()
        duration = time.time() - self.start_time

        # Save profile results
        stats_dir = Path("profiling")
        stats_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_file = stats_dir / f"profile_{timestamp}.prof"

        # Generate report
        stats = pstats.Stats(self.profiler)
        stats.sort_stats('cumulative')
        stats.dump_stats(stats_file)

        print(f"\n📊 Profile saved to {stats_file}")
