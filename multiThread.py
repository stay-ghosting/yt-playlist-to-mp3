from queue import Queue
from threading import Thread
import time
from typing import Callable


class MultiThread:
    """allows you to run multiple threads with add method.
    is alive method allows you to check if all threads are complete"""
    

    def __init__(self, max_theads=2):
        # list of all the functions currently running
        self.MAX_THREADS = max_theads
        self._functions_running: list[Callable] = []
        self._functions_waiting: Queue[Callable] = Queue()

    def add(self, func: Callable):
        """runs on a new thread"""
        # if at max threads ...
        if len(self._functions_running) >= self.MAX_THREADS:
            # put in queue
            self._functions_waiting.put(func)
        # if at NOT max threads ...
        else:
            # add it to list
            self._functions_running.append(func),
            Thread(target=lambda:self._do_function(func)).start()

    def _do_function(self, func: Callable):
        # do task
        func(),
        # remove it from list
        self._functions_running.remove(func)
        # get function from the queue and try run it
        self.add(self._functions_waiting.get())
        
    def is_alive(self):
        """True if 1 or more thread is still running"""
        return len(self._functions_running) != 0



# def foo(s):
#     time.sleep(s)
#     print(f"**{s}")


# t = MultiThread()
# t.add(lambda:foo(3))
# t.add(lambda:foo(3))
# t.add(lambda:foo(3))

# t.add(lambda:foo(3))
# t.add(lambda:foo(3))
# t.add(lambda:foo(3))

# t.add(lambda:foo(3))
# time.sleep(11)
# t.add(lambda:foo(3))

# while True:
#     pass
    # print(len(t._functions_running))
    
# 1 1 1
# 1
