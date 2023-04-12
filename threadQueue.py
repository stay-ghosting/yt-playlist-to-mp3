from queue import Queue, Empty
from threading import Thread
import time

class ThreadQueue:
    def __init__(self):
        # queue of all functions to be called
        self._queue = Queue()
        # the thread 
        self._thread = None
        # true if thead is running
        self.is_alive = False

    def add(self, func):
      # add function to the queue
      self._queue.put(func)
      # if thread NOT running ...
      if self.is_alive == False:
        # set thead to running
        self.is_alive = True
        # creates a thread that recursivley calls functions in the queue
        self._thread = Thread(target=lambda:self._do_function()).start()

    def _do_function(self):
      # check if there is a function in the queue
      try:
        first = self._queue.get()
      except Empty:
        # if queue is empty ... set thread to NOT running
          self.is_alive = False
      else:
        # run the first item of the queue
        first()
        # try do the next function
        self._do_function()

# queue = Queue()

# def z():
#     while True:
#         time.sleep(0.1)
#         print("x")

# def foo(x, s):
#     time.sleep(s)
#     print(x)


# Thread(target=z).start()

# t1 = ThreadQueue()
# t1.add(lambda:foo("***1", 1))
# t1.add(lambda:foo("***2", 3))
# t1.add(lambda:foo("***3", 1))
# t1.add(lambda:foo("***4", 1))
# time.sleep(7)
# t1.add(lambda:foo("***5", 1))
