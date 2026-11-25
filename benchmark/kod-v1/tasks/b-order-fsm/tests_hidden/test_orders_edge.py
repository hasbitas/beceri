import itertools
import math
import unittest

import orders
from orders import (InvalidTransition, Order, RetryTooEarly, ReturnWindowClosed,
                    TransitionError, next_state, retry_delay)
from orders import states

EXPECTED = {
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
ALL_STATES = ("awaiting_payment", "paid", "packed", "shipped", "delivered", "returned",
              "cancelled", "refunded")
ALL_EVENTS = ("pay", "pay_fail", "pack", "ship", "deliver", "cancel", "return", "refund")


def delivered_order(at=100):
    order = Order("x")
    order.apply("pay", at - 3)
    order.apply("pack", at - 2)
    order.apply("ship", at - 1)
    order.apply("deliver", at)
    return order


class HiddenStaticTests(unittest.TestCase):
    def test_transition_table(self):
        for state, event in itertools.product(ALL_STATES, ALL_EVENTS):
            with self.subTest(state=state, event=event):
                self.assertEqual(next_state(state, event), EXPECTED.get((state, event)))
        self.assertIsNone(next_state("nowhere", "pay"))
        self.assertEqual(states.INITIAL, "awaiting_payment")
        self.assertEqual(set(states.TERMINAL), {"cancelled", "refunded"})
        self.assertEqual(states.MAX_ATTEMPTS, 3)
        self.assertEqual(states.RETURN_WINDOW, 20160)

    def test_retry_delay(self):
        self.assertEqual([retry_delay(n) for n in range(1, 8)], [5, 10, 20, 40, 60, 60, 60])
        self.assertEqual(retry_delay(10 ** 6), 60)
        for bad in (0, -1):
            with self.assertRaises(ValueError):
                retry_delay(bad)
        for bad in (True, 1.0, "1", None):
            with self.assertRaises(TypeError):
                retry_delay(bad)

    def test_exports_and_error_hierarchy(self):
        self.assertIs(orders.Order, Order)
        for cls in (InvalidTransition, RetryTooEarly, ReturnWindowClosed):
            self.assertTrue(issubclass(cls, TransitionError))
        order = Order("e")
        with self.assertRaises(InvalidTransition) as caught:
            order.apply("pack", 0)
        self.assertEqual((caught.exception.state, caught.exception.event), ("awaiting_payment", "pack"))


class HiddenOrderTests(unittest.TestCase):
    def test_constructor(self):
        order = Order("abc")
        self.assertEqual((order.order_id, order.state, order.attempts), ("abc", "awaiting_payment", 0))
        self.assertIsNone(order.retry_at)
        self.assertIsNone(order.delivered_at)
        self.assertEqual(order.history, [])
        for bad in (0, -2):
            with self.assertRaises(ValueError):
                Order("a", max_attempts=bad)
        for bad in (True, 2.0, "3", None):
            with self.assertRaises(TypeError):
                Order("a", max_attempts=bad)
        with self.assertRaises(TypeError):
            Order(17)

    def test_exhausted_retries_cancel_the_order(self):
        order = Order("a")
        self.assertEqual(order.apply("pay_fail", 0), "awaiting_payment")
        self.assertEqual(order.apply("pay_fail", 5), "awaiting_payment")
        self.assertEqual(order.retry_at, 15)
        self.assertEqual(order.apply("pay_fail", 15), "cancelled")
        self.assertEqual((order.attempts, order.state, order.retry_at), (3, "cancelled", None))
        self.assertTrue(order.finished)
        self.assertEqual(order.history[-1], (15, "pay_fail", "awaiting_payment", "cancelled"))
        for event in ALL_EVENTS:
            with self.assertRaises(InvalidTransition):
                order.apply(event, 1000)

    def test_backoff_grows_and_is_capped(self):
        order = Order("a", max_attempts=7)
        at = 0
        seen = []
        for _ in range(6):
            order.apply("pay_fail", at)
            seen.append(order.retry_at - at)
            at = order.retry_at
        self.assertEqual(seen, [5, 10, 20, 40, 60, 60])
        self.assertEqual(order.apply("pay_fail", at), "cancelled")
        single = Order("s", max_attempts=1)
        self.assertEqual(single.apply("pay_fail", 3), "cancelled")

    def test_retry_gate(self):
        order = Order("a")
        order.apply("pay_fail", 100)
        for event in ("pay", "pay_fail"):
            with self.assertRaises(RetryTooEarly) as caught:
                order.apply(event, 104.5)
            self.assertEqual(caught.exception.retry_at, 105)
        self.assertEqual((order.attempts, order.retry_at, len(order.history)), (1, 105, 1))
        self.assertEqual(order.apply("pay", 105), "paid")
        self.assertIsNone(order.retry_at)
        self.assertEqual(order.attempts, 1)
        gated = Order("b")
        gated.apply("pay_fail", 0)
        self.assertEqual(gated.apply("cancel", 0), "cancelled")

    def test_rejected_events_do_not_advance_time_or_state(self):
        order = Order("a")
        order.apply("pay_fail", 0)
        with self.assertRaises(InvalidTransition):
            order.apply("ship", 10)
        with self.assertRaises(ValueError):
            order.apply("bogus", 20)
        with self.assertRaises(TypeError):
            order.apply("pay", "30")
        self.assertEqual(order.apply("pay", 6), "paid")
        self.assertEqual([entry[0] for entry in order.history], [0, 6])
        with self.assertRaises(InvalidTransition):
            order.apply("return", 7)
        self.assertEqual(order.apply("pack", 7), "packed")

    def test_time_validation(self):
        order = Order("a")
        self.assertEqual(order.apply("pay", -50), "paid")
        self.assertEqual(order.apply("pack", -50), "packed")
        with self.assertRaises(ValueError):
            order.apply("ship", -50.5)
        for bad in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                order.apply("ship", bad)
        for bad in (True, "5", None, [1]):
            with self.assertRaises(TypeError):
                order.apply("ship", bad)
        for bad in (None, 3, b"pay"):
            with self.assertRaises(TypeError):
                order.apply(bad, 0)
        self.assertEqual(order.apply("ship", 2.5), "shipped")
        self.assertEqual(order.state, "shipped")

    def test_return_window_is_inclusive(self):
        order = delivered_order(100)
        self.assertEqual(order.delivered_at, 100)
        with self.assertRaises(ReturnWindowClosed) as caught:
            order.apply("return", 100 + 20160.5)
        self.assertEqual(caught.exception.deadline, 20260)
        self.assertEqual(order.state, "delivered")
        self.assertEqual(order.apply("return", 20260), "returned")
        self.assertEqual(order.apply("refund", 20261), "refunded")
        self.assertTrue(order.finished)
        late = delivered_order(0)
        with self.assertRaises(ReturnWindowClosed):
            late.apply("return", 20161)
        with self.assertRaises(InvalidTransition):
            late.apply("cancel", 20161)
        self.assertEqual(late.state, "delivered")
        self.assertFalse(late.finished)

    def test_return_before_delivery_and_history_copy(self):
        order = Order("a")
        order.apply("pay", 0)
        with self.assertRaises(InvalidTransition):
            order.apply("return", 1)
        snapshot = order.history
        snapshot.append("junk")
        self.assertEqual(order.history, [(0, "pay", "awaiting_payment", "paid")])
        full = delivered_order(10)
        full.apply("return", 11)
        full.apply("refund", 12)
        self.assertEqual(
            full.history,
            [(7, "pay", "awaiting_payment", "paid"), (8, "pack", "paid", "packed"),
             (9, "ship", "packed", "shipped"), (10, "deliver", "shipped", "delivered"),
             (11, "return", "delivered", "returned"), (12, "refund", "returned", "refunded")],
        )

    def test_apply_returns_new_state_and_orders_are_independent(self):
        first, second = Order("1"), Order("2")
        self.assertEqual(first.apply("pay", 5), "paid")
        self.assertEqual(second.state, "awaiting_payment")
        self.assertEqual(second.history, [])
        second.apply("pay_fail", 1)
        self.assertEqual((first.attempts, second.attempts), (0, 1))


if __name__ == "__main__":
    unittest.main()
