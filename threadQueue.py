from queue import Queue, Empty
from threading import Thread, current_thread
import time
from typing import Callable

class ThreadQueue:
    """Allows you to run multiple threads with add method.
    is_alive method allows you to check if all threads are complete"""

    def __init__(self, max_threads=4):
        self.MAX_THREADS = max_threads
        self._threads_running = []
        self._tasks_waiting = Queue()

    def add(self, func, *args, **kwargs):
        """Runs a function on a new thread."""
        if len(self._threads_running) >= self.MAX_THREADS:
            self._tasks_waiting.put((func, args, kwargs))
        else:
            thread = Thread(target=self._run_task, args=(func, args, kwargs))
            self._threads_running.append(thread)
            thread.start()

    def _run_task(self, func, args, kwargs):
        """Executes the function and manages running/waiting tasks."""
        func(*args, **kwargs)
        self._threads_running.remove(current_thread())
        self._process_next_task()

    def _process_next_task(self):
        """Processes the next task in the waiting queue."""
        try:
            next_func, next_args, next_kwargs = self._tasks_waiting.get_nowait()
        except Empty:
            pass
        else:
            self.add(next_func, *next_args, **next_kwargs)

    def is_alive(self):
        """Returns True if 1 or more thread is still running."""
        return any(thread.is_alive() for thread in self._threads_running)

def foo(x, s):
    import time
    time.sleep(s)
    print(x)

# Example usage
if __name__ == "__main__":
    t1 = ThreadQueue()
    t1.add(foo, "***1", 1)
    t1.add(foo, "***2", 1)
    t1.add(foo, "***3", 1)
    t1.add(foo, "***4", 1)

    t1.add(foo, "***1", 1)
    t1.add(foo, "***2", 1)
    t1.add(foo, "***3", 1)
    t1.add(foo, "***4", 1)

    time.sleep(7)
    t1.add(foo, "***5", 1)
