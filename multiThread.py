from threading import Thread
from typing import Callable


class MultiThread:
    def __init__(self):
        # list of all the functions currently running
        self.functions_running: list[Callable] = []

    def add(self, func: Callable):
        Thread(target=lambda:(
            self.functions_running.append(func),
            func(),
            self.functions_running.remove(func)
        )).start()
        
    def is_alive(self):
        return len(self.functions_running) == 0



# def foo(s):
#     time.sleep(s)
#     print(f"**{s}")


# t = MultiThread()
# t.add(lambda:foo(5))
# t.add(lambda:foo(6))

# while True:
#     time.sleep(0.2)
#     print(t.is_alive())
