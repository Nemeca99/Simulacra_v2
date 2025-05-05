from functools import wraps
import time
from typing import Callable, Any, Dict
import statistics

class PerformanceMonitor:
    """Monitor and track function performance"""
    _timings: Dict[str, list] = {}

    @classmethod
    def track(cls, func: Callable) -> Callable:
        """Decorator to track function execution time"""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start

            name = func.__qualname__
            if name not in cls._timings:
                cls._timings[name] = []
            cls._timings[name].append(duration)

            return result
        return wrapper

    @classmethod
    def get_stats(cls) -> Dict[str, Dict[str, float]]:
        """Get performance statistics"""
        stats = {}
        for name, timings in cls._timings.items():
            if not timings:
                continue
            stats[name] = {
                'mean': statistics.mean(timings),
                'median': statistics.median(timings),
                'min': min(timings),
                'max': max(timings),
                'count': len(timings)
            }
        return stats