from threading import Thread
import time
from typing import Callable

class OneFunctionThread:
	"""runs one function at a time
	only one function can be queued at a time"""
	def __init__(self):
		# the next function to be called
		self._next: Callable = None
		# the thread 
		self._thread = None
		# true if thead is running
		self.is_alive = False

	def set_function(self, func: Callable):
		"""sets the "next" function to be called
		will be overwiten if there is already a "next" function"""
		# set nect function
		self._next = func
		# if thread NOT running ...
		if self.is_alive == False:
			# set thead to running
			self.is_alive = True
			# creates a thread that recursivley calls functions in the queue
			Thread(target=lambda:self._do_function(func)).start()

	def _do_function(self, func:Callable):
		# call function
		func()
		# if there is a next function ...
		if self._next is not None:
			# call function
			self._next()
			# remove it from next
			self._next = None
		# set is alive variable
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