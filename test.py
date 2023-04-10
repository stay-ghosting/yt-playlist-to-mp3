import concurrent.futures
import time

def foo():
    time.sleep(1)
    return 2

with concurrent.futures.ProcessPoolExecutor() as ex:
    t = ex.submit(foo)
    # v = ex.submit(foo)
    # print(t.result())
    # print(v.result())