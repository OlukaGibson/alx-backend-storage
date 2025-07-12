#!/usr/bin/env python3
"""Main test file"""

from exercise import Cache, replay

cache = Cache()

# Store some values
s1 = cache.store("foo")
s2 = cache.store("bar")
s3 = cache.store(42)

# Show input/output logs
replay(cache.store)
