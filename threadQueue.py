from queue import Queue, Empty
from threading import Thread, Semaphore
import time

class ThreadQueue:
    """Runs functions on many threads asynchronously."""
    
    def __init__(self, max_threads=4):
        self._queue = Queue()
        self._max_threads = max_threads
        self._semaphore = Semaphore(max_threads)
        self.is_alive = False

    def add(self, func, *args):
        """Adds a process to the queue."""
        job = {"func": func, "args": args}
        self._queue.put(job)
        if not self.is_alive:
            self.is_alive = True
            self._do_function()

    def _do_function(self):
        """ recursivley calls function on a new thread"""
        try:
            job = self._queue.get_nowait()
        except Empty:
            self.is_alive = False
        else:
            self._semaphore.acquire()
            Thread(target=self._execute_job, args=(job,)).start()
            self._do_function()

    def _execute_job(self, job):
        """executes a job and releases semaphore when done."""
        try:
            job["func"](*job["args"])
        finally:
            self._semaphore.release()

# def foo(x, s):
#     time.sleep(s)
#     print(x)

# t1 = ThreadQueue()
# t1.add(lambda: foo("***1", 1))
# t1.add(lambda: foo("***2", 1))
# t1.add(lambda: foo("***3", 1))
# t1.add(lambda: foo("***4", 1))

# t1.add(lambda: foo("***1", 1))
# t1.add(lambda: foo("***2", 1))
# t1.add(lambda: foo("***3", 1))
# t1.add(lambda: foo("***4", 1))

# time.sleep(7)
# t1.add(lambda: foo("***5", 1))
