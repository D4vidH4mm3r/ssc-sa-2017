import time
import contextlib


class StopWatch():
    def __init__(self):
        self.start_time = time.time()
        self.stop_time = None
    def stop(self):
        self.stop_time = time.time()
    def elapsed(self):
        if self.stop_time is not None:
            return self.stop_time - self.start_time
        else:
            return time.time() - self.start_time
    def __str__(self):
        return "{0:.3f}".format(self.elapsed())
    def __repr__(self):
        return "timer: " + str(self)
@contextlib.contextmanager
def timed():
    t = StopWatch()
    yield t
    t.stop()
