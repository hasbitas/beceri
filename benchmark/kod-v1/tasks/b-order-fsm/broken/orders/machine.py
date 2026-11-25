"""The order state machine with payment retries and a return window."""

import math

from .errors import InvalidTransition, RetryTooEarly, ReturnWindowClosed
from .states import (EVENTS, INITIAL, MAX_ATTEMPTS, RETURN_WINDOW, TERMINAL,
                     next_state, retry_delay)

_PAYMENT_EVENTS = ("pay", "pay_fail")


def _check_time(at):
    if not isinstance(at, (int, float)) or isinstance(at, bool):
        raise TypeError("at must be a number")
    if not math.isfinite(at):
        raise ValueError("at must be finite")


class Order:
    def __init__(self, order_id, max_attempts=MAX_ATTEMPTS):
        if not isinstance(order_id, str):
            raise TypeError("order_id must be a string")
        if not isinstance(max_attempts, int) or isinstance(max_attempts, bool):
            raise TypeError("max_attempts must be an int")
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.order_id = order_id
        self.state = INITIAL
        self.attempts = 0
        self.retry_at = None
        self.delivered_at = None
        self._max_attempts = max_attempts
        self._last_at = None
        self._history = []

    @property
    def history(self):
        return list(self._history)

    @property
    def finished(self):
        return self.state in TERMINAL

    def apply(self, event, at):
        if not isinstance(event, str):
            raise TypeError("event must be a string")
        if event not in EVENTS:
            raise ValueError(f"unknown event {event!r}")
        _check_time(at)
        if self._last_at is not None and at < self._last_at:
            raise ValueError("events must not go back in time")
        self._last_at = at
        target = next_state(self.state, event)
        if target is None:
            raise InvalidTransition(self.state, event)
        if event in _PAYMENT_EVENTS and self.retry_at is not None and at < self.retry_at:
            raise RetryTooEarly(self.retry_at)
        if event == "return":
            deadline = self.delivered_at + RETURN_WINDOW
            if at >= deadline:
                raise ReturnWindowClosed(deadline)
        if event == "pay_fail":
            self.attempts += 1
            if self.attempts >= self._max_attempts:
                target = "cancelled"
                self.retry_at = None
            else:
                self.retry_at = at + retry_delay(self.attempts)
        elif event == "pay":
            self.retry_at = None
        elif event == "deliver":
            self.delivered_at = at
        self._history.append((at, event, self.state, target))
        self.state = target
        return target
