import math
import unittest

import ttlcache
from ttlcache import Cache, Entry, compute_expiry, is_expired
from ttlcache.policy import check_ttl


class Clock:
    def __init__(self, now=0):
        self.now = now
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.now


class HiddenPolicyTests(unittest.TestCase):
    def test_exports(self):
        self.assertEqual(sorted(ttlcache.__all__), ["Cache", "Entry", "compute_expiry", "is_expired"])
        entry = Entry("v", 3, 2)
        self.assertEqual((entry.value, entry.expires_at, entry.cost), ("v", 3, 2))

    def test_check_ttl(self):
        for good in (None, 1, 0.001, 10 ** 9, 2.5):
            with self.subTest(good=good):
                check_ttl(good)
        for bad in (0, 0.0, -1, -0.5, math.inf, -math.inf, math.nan):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    check_ttl(bad)
        for bad in (True, False, "5", [5], 1 + 0j, b"1"):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    check_ttl(bad)

    def test_compute_expiry(self):
        self.assertEqual(compute_expiry(100, 5, None), 105)
        self.assertEqual(compute_expiry(100, None, 10), 110)
        self.assertEqual(compute_expiry(100, 5, 10), 105)
        self.assertIsNone(compute_expiry(100, None, None))
        self.assertEqual(compute_expiry(0.5, 0.25, None), 0.75)
        for ttl, default in ((0, None), (0, 10), (0.0, 10), (-3, 10), (None, 0), (None, -1)):
            with self.subTest(ttl=ttl, default=default):
                with self.assertRaises(ValueError):
                    compute_expiry(100, ttl, default)
        with self.assertRaises(TypeError):
            compute_expiry(100, True, 10)

    def test_is_expired(self):
        self.assertFalse(is_expired(Entry("v", None, 1), 10 ** 12))
        self.assertFalse(is_expired(Entry("v", 10, 1), 9.99))
        self.assertTrue(is_expired(Entry("v", 10, 1), 10))
        self.assertTrue(is_expired(Entry("v", 10, 1), 10.5))


class HiddenCacheTests(unittest.TestCase):
    def test_constructor_validation(self):
        clock = Clock()
        for capacity in (0, -1):
            with self.assertRaises(ValueError):
                Cache(capacity, clock)
        for capacity in (True, 2.0, "3", None):
            with self.assertRaises(TypeError):
                Cache(capacity, clock)
        with self.assertRaises(TypeError):
            Cache(2, 5)
        with self.assertRaises(ValueError):
            Cache(2, clock, default_ttl=0)
        with self.assertRaises(TypeError):
            Cache(2, clock, default_ttl="1")
        self.assertEqual(clock.calls, 0)

    def test_clock_is_read_once_per_call(self):
        clock = Clock()
        cache = Cache(3, clock)
        calls = [
            lambda: cache.put("a", 1),
            lambda: cache.get("a"),
            lambda: cache.peek("a"),
            lambda: cache.keys(),
            lambda: cache.total_cost(),
            lambda: len(cache),
            lambda: "a" in cache,
            lambda: cache.delete("zz"),
        ]
        for call in calls:
            before = clock.calls
            call()
            self.assertEqual(clock.calls - before, 1)
        for bad in (lambda: cache.put("c", 1, cost=0), lambda: cache.put("c", 1, ttl=0)):
            before = clock.calls
            with self.assertRaises(ValueError):
                bad()
            self.assertEqual(clock.calls - before, 1)

    def test_replacing_a_key_releases_its_own_cost_first(self):
        cache = Cache(5, Clock())
        cache.put("a", 1, cost=3)
        cache.put("b", 2, cost=2)
        self.assertEqual(cache.put("a", 10, cost=3), [])
        self.assertEqual(cache.keys(), ["b", "a"])
        self.assertEqual(cache.put("b", 20, cost=2), [])
        self.assertEqual(cache.keys(), ["a", "b"])
        self.assertEqual(cache.total_cost(), 5)
        self.assertEqual(cache.put("a", 30, cost=2), [])
        self.assertEqual(cache.keys(), ["b", "a"])
        self.assertEqual(cache.total_cost(), 4)
        self.assertEqual(cache.put("a", 40, cost=5), ["b"])
        self.assertEqual(cache.keys(), ["a"])
        self.assertEqual(cache.get("a"), 40)

    def test_eviction_order_with_costs(self):
        cache = Cache(10, Clock())
        cache.put("x", 1, cost=4)
        cache.put("y", 2, cost=4)
        cache.put("z", 3, cost=2)
        self.assertEqual(cache.get("x"), 1)
        self.assertEqual(cache.put("w", 4, cost=5), ["y", "z"])
        self.assertEqual(cache.keys(), ["x", "w"])
        self.assertEqual(cache.total_cost(), 9)
        self.assertEqual(cache.put("big", 5, cost=10), ["x", "w"])
        self.assertEqual(cache.keys(), ["big"])
        self.assertEqual(cache.put("exact", 6, cost=10), ["big"])

    def test_expired_entries_are_purged_before_making_room(self):
        clock = Clock()
        cache = Cache(2, clock)
        cache.put("a", 1, ttl=5)
        cache.put("b", 2)
        clock.now = 5
        self.assertEqual(cache.put("c", 3), [])
        self.assertEqual(cache.keys(), ["b", "c"])
        clock.now = 6
        self.assertEqual(cache.put("d", 4, ttl=1), ["b"])
        self.assertEqual(cache.keys(), ["c", "d"])
        clock.now = 7
        self.assertEqual(len(cache), 1)
        self.assertEqual(cache.total_cost(), 1)

    def test_expiry_frees_cost_and_updates_everything(self):
        clock = Clock()
        cache = Cache(6, clock)
        cache.put("a", 1, ttl=3, cost=4)
        cache.put("b", 2, cost=2)
        self.assertEqual(cache.total_cost(), 6)
        clock.now = 2.999
        self.assertEqual(cache.total_cost(), 6)
        clock.now = 3
        self.assertEqual(cache.total_cost(), 2)
        self.assertNotIn("a", cache)
        self.assertEqual(cache.peek("a", "gone"), "gone")
        self.assertFalse(cache.delete("a"))
        self.assertEqual(cache.put("c", 3, cost=4), [])

    def test_ttl_rules(self):
        clock = Clock(50)
        cache = Cache(3, clock, default_ttl=10)
        for bad_ttl in (0, 0.0, -1, math.inf, math.nan):
            with self.subTest(ttl=bad_ttl):
                with self.assertRaises(ValueError):
                    cache.put("a", 1, ttl=bad_ttl)
        with self.assertRaises(TypeError):
            cache.put("a", 1, ttl=True)
        self.assertEqual(len(cache), 0)
        cache.put("a", 1, ttl=100)
        cache.put("a", 2)
        clock.now = 60
        self.assertEqual(cache.get("a", "gone"), "gone")
        plain = Cache(3, clock)
        plain.put("a", 1, ttl=5)
        plain.put("a", 2)
        clock.now = 10 ** 9
        self.assertEqual(plain.get("a"), 2)
        plain.put("f", 1, ttl=0.5)
        clock.now += 0.5
        self.assertNotIn("f", plain)

    def test_a_call_that_raises_does_not_touch_expired_entries(self):
        clock = Clock()
        cache = Cache(3, clock)
        cache.put("a", 1, ttl=5)
        cache.put("b", 2)
        clock.now = 5
        failing = (
            (lambda: cache.put("c", 3, cost=0), ValueError),
            (lambda: cache.put("c", 3, cost=4), ValueError),
            (lambda: cache.put("c", 3, cost=True), TypeError),
            (lambda: cache.put("c", 3, ttl=0), ValueError),
            (lambda: cache.put("c", 3, ttl="x"), TypeError),
            (lambda: cache.put(["k"], 3), TypeError),
            (lambda: cache.put(["k"], 3, ttl=0), ValueError),
            (lambda: cache.put(["k"], 3, cost=4), ValueError),
            (lambda: cache.get(["k"]), TypeError),
            (lambda: cache.peek(["k"]), TypeError),
            (lambda: cache.delete(["k"]), TypeError),
            (lambda: ["k"] in cache, TypeError),
        )
        for call, error in failing:
            with self.assertRaises(error):
                call()
        clock.now = 0
        self.assertEqual(cache.keys(), ["a", "b"])
        self.assertEqual(cache.total_cost(), 2)

    def test_successful_calls_hide_expired_entries(self):
        clock = Clock()
        cache = Cache(3, clock)
        cache.put("a", 1, ttl=5, cost=2)
        cache.put("b", 2)
        clock.now = 5
        self.assertEqual(cache.put("c", 3, cost=2), [])
        self.assertEqual(cache.keys(), ["b", "c"])
        self.assertEqual(cache.total_cost(), 3)
        self.assertIsNone(cache.peek("a"))

    def test_failed_put_changes_nothing(self):
        cache = Cache(4, Clock())
        cache.put("a", 1, cost=2)
        cache.put("b", 2, cost=2)
        for kwargs, error in (({"cost": 5}, ValueError), ({"cost": 0}, ValueError),
                              ({"cost": True}, TypeError), ({"cost": 1.0}, TypeError),
                              ({"ttl": 0}, ValueError), ({"ttl": "x"}, TypeError),
                              ({"cost": 5, "ttl": "x"}, ValueError)):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(error):
                    cache.put("a", 99, **kwargs)
                self.assertEqual(cache.keys(), ["a", "b"])
                self.assertEqual(cache.peek("a"), 1)
                self.assertEqual(cache.total_cost(), 4)
        with self.assertRaises(TypeError):
            cache.put(["unhashable"], 1)
        with self.assertRaises(TypeError):
            cache.get(["unhashable"])
        self.assertEqual(cache.keys(), ["a", "b"])

    def test_peek_contains_and_len_keep_recency(self):
        cache = Cache(3, Clock())
        for key in "abc":
            cache.put(key, key)
        self.assertEqual(cache.peek("a"), "a")
        self.assertIn("a", cache)
        self.assertEqual(len(cache), 3)
        self.assertEqual(cache.put("d", "d"), ["a"])
        self.assertEqual(cache.get("zz", "dflt"), "dflt")
        self.assertEqual(cache.get("b"), "b")
        self.assertEqual(cache.keys(), ["c", "d", "b"])
        self.assertTrue(cache.delete("d"))
        self.assertEqual(cache.keys(), ["c", "b"])
        self.assertIsNone(cache.peek("nothing"))
        cache.put("e", None)
        self.assertEqual(cache.get("e", "dflt"), None)
        self.assertIn("e", cache)


if __name__ == "__main__":
    unittest.main()
