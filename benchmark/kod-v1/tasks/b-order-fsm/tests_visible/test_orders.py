import unittest

from orders import InvalidTransition, Order, RetryTooEarly, next_state, retry_delay


class VisibleOrderTests(unittest.TestCase):
    def test_happy_path_and_history(self):
        order = Order("o-1")
        self.assertEqual(order.state, "awaiting_payment")
        for at, event in ((1, "pay"), (2, "pack"), (5, "ship"), (9, "deliver")):
            order.apply(event, at)
        self.assertEqual(order.state, "delivered")
        self.assertEqual(order.history[0], (1, "pay", "awaiting_payment", "paid"))
        self.assertEqual(order.history[-1], (9, "deliver", "shipped", "delivered"))
        self.assertFalse(order.finished)

    def test_cancelling_at_each_stage(self):
        early = Order("a")
        self.assertEqual(early.apply("cancel", 0), "cancelled")
        self.assertTrue(early.finished)
        paid = Order("b")
        paid.apply("pay", 0)
        self.assertEqual(paid.apply("cancel", 1), "refunded")
        packed = Order("c")
        packed.apply("pay", 0)
        packed.apply("pack", 1)
        self.assertEqual(packed.apply("cancel", 2), "refunded")
        self.assertTrue(packed.finished)

    def test_payment_retry_with_backoff(self):
        order = Order("d")
        order.apply("pay_fail", 10)
        self.assertEqual((order.attempts, order.retry_at), (1, 15))
        with self.assertRaises(RetryTooEarly) as caught:
            order.apply("pay", 14)
        self.assertEqual(caught.exception.retry_at, 15)
        self.assertEqual(order.state, "awaiting_payment")
        self.assertEqual(order.apply("pay", 15), "paid")

    def test_invalid_and_unknown_events(self):
        order = Order("e")
        with self.assertRaises(InvalidTransition):
            order.apply("ship", 0)
        with self.assertRaises(ValueError):
            order.apply("explode", 0)
        self.assertEqual(order.history, [])
        self.assertEqual(next_state("paid", "pack"), "packed")
        self.assertIsNone(next_state("paid", "ship"))
        self.assertEqual(retry_delay(2), 10)


if __name__ == "__main__":
    unittest.main()
