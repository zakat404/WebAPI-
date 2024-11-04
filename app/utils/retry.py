import time
import functools

def retry(times=3, delay=1, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _times = times
            while _times > 0:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    _times -= 1
                    if _times == 0:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator
