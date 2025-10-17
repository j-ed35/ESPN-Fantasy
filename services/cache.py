import time
from functools import wraps


def cached(ttl: int = 300):
    store = {}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (fn.__name__, args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in store:
                value, ts = store[key]
                if now - ts < ttl:
                    return value
            value = fn(*args, **kwargs)
            store[key] = (value, now)
            return value

        return wrapper

    return decorator
