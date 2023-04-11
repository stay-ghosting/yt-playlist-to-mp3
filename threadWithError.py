from threading import Thread

class ThreadWithError(Thread): 
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._error = None
        self._return = None

    def run(self):
        if self._target is not None:
            try:
                self._return = self._target(*self._args, **self._kwargs)
            except Exception as e:
                self._error = e

    def join(self, *args):
        Thread.join(self, *args)
        if self._error != None:
            raise self._error
        return self._return