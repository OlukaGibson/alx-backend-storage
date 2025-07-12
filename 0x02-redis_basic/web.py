#!/usr/bin/env python3
"""Web cache and URL tracker using Redis"""

import requests
import redis
from functools import wraps
from typing import Callable

r = redis.Redis()


def count_access(fn: Callable) -> Callable:
    """Track number of accesses to a URL in Redis."""
    @wraps(fn)
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")
        cached = r.get(f"cached:{url}")
        if cached:
            return cached.decode('utf-8')

        result = fn(url)
        r.setex(f"cached:{url}", 10, result)
        return result
    return wrapper


@count_access
def get_page(url: str) -> str:
    """Fetch and cache page content with expiration."""
    res = requests.get(url)
    return res.text
