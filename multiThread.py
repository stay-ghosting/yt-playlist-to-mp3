from queue import Queue
from threading import Thread, current_thread
import time
from typing import Callable, List


class MultiThread:
    """Allows you to run multiple threads with add method.
    is_alive method allows you to check if all threads are complete."""

    def __init__(self, max_threads=3):
        self.MAX_THREADS = max_threads
        self._threads_running: List[Thread] = []
        self._functions_waiting: Queue[tuple[Callable, tuple, dict]] = Queue()

    def add(self, func: Callable, *args, **kwargs):
        if len(self._threads_running) >= self.MAX_THREADS:
            self._functions_waiting.put((func, args, kwargs))
        else:
            thread = Thread(target=self._do_function, args=(func, args, kwargs))
            self._threads_running.append(thread)
            thread.start()

    def _do_function(self, func: Callable, args: tuple, kwargs: dict):
        func(*args, **kwargs)
        self._threads_running.remove(current_thread())
        self._process_next()

    def _process_next(self):
        if not self._functions_waiting.empty():
            next_func, next_args, next_kwargs = self._functions_waiting.get()
            self.add(next_func, *next_args, **next_kwargs)

    def is_alive(self):
        """True if 1 or more thread is still running"""
        return any(thread.is_alive() for thread in self._threads_running)


if __name__ == "__main__":

    def foo(s):
        time.sleep(s)
        print(f"**{s}")

    def bar():
        time.sleep(3)
        print("**bar")


    t = MultiThread()
    t.add(foo, 1)
    t.add(foo, 2)
    t.add(foo, 3)

    t.add(bar)
    t.add(bar)
    t.add(bar)

    time.sleep(11)
    t.add(foo, 1)

    while t.is_alive():
        time.sleep(0.1)
