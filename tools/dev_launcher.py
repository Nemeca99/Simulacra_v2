import subprocess
import sys
import time
from pathlib import Path


def dev_launch():
    """Launch development environment"""
    # Start test monitor
    test_monitor = subprocess.Popen(
        [sys.executable, 'tools/test_runner.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Start profiler
    profiler = subprocess.Popen(
        [sys.executable, 'tools/profiler.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Launch game
    try:
        subprocess.run([sys.executable, 'launcher.py'])
    finally:
        test_monitor.terminate()
        profiler.terminate()


if __name__ == "__main__":
    dev_launch()
