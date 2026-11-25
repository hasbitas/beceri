"""A cost-bounded cache with per-entry expiry and least-recently-used eviction."""

from collections import OrderedDict

from .policy import Entry, check_ttl, compute_expiry, is_expired


def _check_whole(value, name):
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an int")
    if value < 1:
        raise ValueError(f"{name} must be at least 1")


class Cache:
    def __init__(self, capacity, clock, default_ttl=None):
        _check_whole(capacity, "capacity")
        if not callable(clock):
            raise TypeError("clock must be callable")
        check_ttl(default_ttl)
        self._capacity = capacity
        self._clock = clock
        self._default_ttl = default_ttl
        self._items = OrderedDict()
        self._total = 0

    def _purge(self, now):
        for key in [k for k, e in self._items.items() if is_expired(e, now)]:
            self._total -= self._items.pop(key).cost

    def _sync(self, *keys):
        now = self._clock()
        for key in keys:
            hash(key)
        self._purge(now)
        return now

    def put(self, key, value, ttl=None, cost=1):
        now = self._clock()
        _check_whole(cost, "cost")
        if cost > self._capacity:
            raise ValueError("cost exceeds the capacity")
        expires_at = compute_expiry(now, ttl, self._default_ttl)
        hash(key)
        self._purge(now)
        old = self._items.pop(key, None)
        if old is not None:
            self._total -= old.cost
        evicted = []
        while self._total + cost > self._capacity:
            victim, entry = self._items.popitem(last=False)
            self._total -= entry.cost
            evicted.append(victim)
        self._items[key] = Entry(value, expires_at, cost)
        self._total += cost
        return evicted

    def get(self, key, default=None):
        self._sync(key)
        if key not in self._items:
            return default
        self._items.move_to_end(key)
        return self._items[key].value

    def peek(self, key, default=None):
        self._sync(key)
        entry = self._items.get(key)
        return default if entry is None else entry.value

    def delete(self, key):
        self._sync(key)
        entry = self._items.pop(key, None)
        if entry is None:
            return False
        self._total -= entry.cost
        return True

    def keys(self):
        self._sync()
        return list(self._items)

    def total_cost(self):
        self._sync()
        return self._total

    def __len__(self):
        self._sync()
        return len(self._items)

    def __contains__(self, key):
        self._sync(key)
        return key in self._items
