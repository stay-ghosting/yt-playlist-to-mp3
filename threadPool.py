from queue import Queue, Empty
from threading import Thread, Event
import time
from typing import Callable, List, Tuple

class ThreadPool:
    """Allows you to run multiple threads with add method.
    is_alive method allows you to check if all threads are complete."""

    def __init__(self, max_threads=3):
        self.MAX_THREADS = max_threads
        self._functions_waiting: Queue[Tuple[Callable, Tuple, dict]] = Queue()
        self._threads: List[Thread] = []
        self._stop_event = Event()
        
        # Start worker threads
        for _ in range(self.MAX_THREADS):
            thread = Thread(target=self._worker)
            thread.start()
            self._threads.append(thread)

    def _worker(self):
        """Thread worker function to process tasks."""
        while not self._stop_event.is_set():
            try:
                func, args, kwargs = self._functions_waiting.get(timeout=0.1)
                func(*args, **kwargs)
                self._functions_waiting.task_done()
            except Empty:
                continue

    def add(self, func: Callable, *args, **kwargs):
        """Add a task to the queue."""
        self._functions_waiting.put((func, args, kwargs))

    def is_alive(self) -> bool:
        """Check if any threads are still running or there are pending tasks."""
        return any(thread.is_alive() for thread in self._threads) or not self._functions_waiting.empty()

    def shutdown(self):
        """Stop all threads and wait for them to finish."""
        self._stop_event.set()
        for thread in self._threads:
            thread.join()

if __name__ == "__main__":
    def foo(s):
        time.sleep(s)
        print(f"**{s}")

    def bar():
        time.sleep(3)
        print("**bar")

    t = ThreadPool()
    t.add(bar)
    t.add(bar)
    t.add(bar) 

    t.add(bar)
    t.add(bar)
    t.add(bar)

    t.add(bar)
    t.add(bar)
    t.add(bar)

    t.add(foo, 1)
    t.add(foo, 2)
    t.add(foo, 3)



    # Wait for tasks to complete
    while t.is_alive():
        time.sleep(0.1)

    # Shutdown the thread pool
    t.shutdown()
