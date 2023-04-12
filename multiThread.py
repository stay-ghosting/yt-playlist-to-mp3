from threading import Thread
from typing import Callable


class MultiThread:
    """allows you to run multiple threads with add method.
    is alive method allows you to check if all threads are complete"""
    
    def __init__(self):
        # list of all the functions currently running
        self._functions_running: list[Callable] = []

    def add(self, func: Callable):
        """runs on a new thread"""
        Thread(target=lambda:(
            # add it to list
            self._functions_running.append(func),
            # do task
            func(),
            # remove it from list
            self._functions_running.remove(func)
        )).start()
        
    def is_alive(self):
        """True if 1 or more thread is still running"""
        return len(self._functions_running) == 0



# def foo(s):
#     time.sleep(s)
#     print(f"**{s}")


# t = MultiThread()
# t.add(lambda:foo(5))
# t.add(lambda:foo(6))

# while True:
#     time.sleep(0.2)
#     print(t.is_alive())
