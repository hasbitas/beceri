import unittest

from ttlcache import Cache


class Clock:
    def __init__(self, now=0):
        self.now = now

    def __call__(self):
        return self.now


class VisibleCacheTests(unittest.TestCase):
    def test_entry_expires_exactly_at_its_deadline(self):
        clock = Clock()
        cache = Cache(4, clock)
        cache.put("a", 1, ttl=5)
        clock.now = 4
        self.assertEqual(cache.get("a"), 1)
        clock.now = 5
        self.assertIsNone(cache.get("a"))
        self.assertEqual(len(cache), 0)

    def test_least_recently_used_goes_first(self):
        cache = Cache(3, Clock())
        for key in "abc":
            self.assertEqual(cache.put(key, key.upper()), [])
        self.assertEqual(cache.get("a"), "A")
        self.assertEqual(cache.put("d", "D"), ["b"])
        self.assertEqual(cache.keys(), ["c", "a", "d"])

    def test_default_ttl_and_override(self):
        clock = Clock(100)
        cache = Cache(4, clock, default_ttl=10)
        cache.put("a", 1)
        cache.put("b", 2, ttl=30)
        clock.now = 110
        self.assertNotIn("a", cache)
        self.assertEqual(cache.peek("b"), 2)
        clock.now = 130
        self.assertEqual(cache.keys(), [])

    def test_costs_and_delete(self):
        cache = Cache(5, Clock())
        cache.put("big", "x", cost=4)
        self.assertEqual(cache.total_cost(), 4)
        self.assertEqual(cache.put("small", "y", cost=2), ["big"])
        self.assertTrue(cache.delete("small"))
        self.assertFalse(cache.delete("small"))
        self.assertEqual(cache.total_cost(), 0)

    def test_invalid_arguments(self):
        cache = Cache(2, Clock())
        with self.assertRaises(ValueError):
            cache.put("a", 1, cost=3)
        with self.assertRaises(TypeError):
            cache.put("a", 1, ttl="5")
        with self.assertRaises(ValueError):
            Cache(0, Clock())


if __name__ == "__main__":
    unittest.main()
