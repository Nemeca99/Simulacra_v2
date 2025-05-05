import subprocess
import time
from pathlib import Path
import sys
import threading
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class TestRunner(FileSystemEventHandler):

    def __init__(self):
        self.last_run = 0
        self.cooldown = 2  # seconds between runs
        self.test_paths = [
            Path("tests"),
            Path("src")
        ]
        self._stop_event = threading.Event()

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            if event.src_path.endswith('.py'):
                current_time = time.time()
                if current_time - self.last_run > self.cooldown:
                    self.run_tests()
                    self.last_run = current_time

    def run_tests(self):
        """Run pytest with verbose output"""
        print("\n" + "="*50)
        print("🧪 Running tests...")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '-v'],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.returncode == 0:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed!")
        except Exception as e:
            print(f"❌ Error running tests: {e}")


def main():
    """Main entry point"""
    print("🔍 Starting test monitor...")

    # Create observer
    path = Path.cwd()
    event_handler = TestRunner()

    # Use PollingObserver instead of Observer
    observer = PollingObserver()

    # Schedule watching
    observer.schedule(event_handler, str(path), recursive=True)

    try:
        observer.start()
        print(f"👀 Watching for changes in: {path}")
        print("Press Ctrl+C to stop")

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping test monitor...")
        observer.stop()

    observer.join()
    print("✨ Test monitor stopped")


if __name__ == "__main__":
    main()
