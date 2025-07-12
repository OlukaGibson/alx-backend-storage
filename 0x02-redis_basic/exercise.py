#!/usr/bin/env python3
"""Exercise module for Redis basic project"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count number of calls to method."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store history of inputs and outputs of a function."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"

        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, result)
        return result
    return wrapper


class Cache:
    """Cache class for storing and retrieving data from Redis."""

    def __init__(self):
        """Initialize the Redis client and flush existing data."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis with a random key and return the key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """Retrieve data from Redis and optionally apply a conversion function."""
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> str:
        """Retrieve a string value from Redis."""
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """Retrieve an integer value from Redis."""
        return self.get(key, fn=int)


def replay(method: Callable) -> None:
    """Display the history of calls for a particular method."""
    r = redis.Redis()
    name = method.__qualname__
    inputs = r.lrange(f"{name}:inputs", 0, -1)
    outputs = r.lrange(f"{name}:outputs", 0, -1)

    print(f"{name} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        print(f"{name}(*{inp.decode('utf-8')}) -> {out.decode('utf-8')}")
