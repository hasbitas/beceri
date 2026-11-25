"""Static description of the order life cycle."""

INITIAL = "awaiting_payment"
EVENTS = ("pay", "pay_fail", "pack", "ship", "deliver", "cancel", "return", "refund")
TERMINAL = frozenset({"cancelled", "refunded"})

TRANSITIONS = {
    ("awaiting_payment", "pay"): "paid",
    ("awaiting_payment", "pay_fail"): "awaiting_payment",
    ("awaiting_payment", "cancel"): "cancelled",
    ("paid", "pack"): "packed",
    ("paid", "cancel"): "refunded",
    ("packed", "ship"): "shipped",
    ("packed", "cancel"): "refunded",
    ("shipped", "deliver"): "delivered",
    ("delivered", "return"): "returned",
    ("returned", "refund"): "refunded",
}

MAX_ATTEMPTS = 3
RETRY_BASE = 5
RETRY_CAP = 60
RETURN_WINDOW = 14 * 24 * 60


def next_state(state, event):
    """Return the state reached from state by event, or None if not allowed."""
    return TRANSITIONS.get((state, event))


def retry_delay(attempts):
    """Minutes to wait after the given number of failed payments."""
    if not isinstance(attempts, int) or isinstance(attempts, bool):
        raise TypeError("attempts must be an int")
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    return min(RETRY_BASE * 2 ** (attempts - 1), RETRY_CAP)
