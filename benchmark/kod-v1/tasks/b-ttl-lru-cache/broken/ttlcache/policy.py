"""Expiry rules for cache entries."""

import math


class Entry:
    __slots__ = ("value", "expires_at", "cost")

    def __init__(self, value, expires_at, cost):
        self.value = value
        self.expires_at = expires_at
        self.cost = cost


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_ttl(ttl):
    """Validate a time to live; None means that no limit applies."""
    if ttl is None:
        return
    if not is_number(ttl):
        raise TypeError("ttl must be a number or None")
    if not math.isfinite(ttl) or ttl <= 0:
        raise ValueError("ttl must be a positive finite number")


def compute_expiry(now, ttl, default_ttl):
    """Return the absolute expiry time, or None when the entry never expires."""
    chosen = ttl or default_ttl
    check_ttl(chosen)
    if chosen is None:
        return None
    return now + chosen


def is_expired(entry, now):
    return entry.expires_at is not None and now > entry.expires_at
