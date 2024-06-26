from threading import Thread
import time
from typing import Callable

class OneFunctionThread:
	"""runs one function at a time
	only one function can be queued at a time"""
	def __init__(self):
		self._next: Callable = None
		self._thread = None
		self.is_alive = False

	def set_function(self, func: Callable):
		"""sets the "next" function to be called
		will be overwiten if there is already a "next" function"""
		self._next = func
		if self.is_alive == False:
			self.is_alive = True
			Thread(target=lambda:self._do_function(func)).start()

	def _do_function(self, func:Callable):
		func()
		if self._next is not None:
			self._next()
			self._next = None
		self.is_alive = False


# def foo(s):
#     time.sleep(s)
#     print(f"**{s}")
    
# t = OneFunctionThread()
# t.set_function(lambda:foo(2))
# t.set_function(lambda:foo(0.5))
# t.set_function(lambda:foo(0.7))
# t.set_function(lambda:foo(0.3))
# t.set_function(lambda:foo(0.1))

# time.sleep(2.2)

# t.set_function(lambda:foo(2))
# t.set_function(lambda:foo(0.5))
# t.set_function(lambda:foo(0.7))
# t.set_function(lambda:foo(0.3))
# t.set_function(lambda:foo(0.1))


# 2 
# 0.1