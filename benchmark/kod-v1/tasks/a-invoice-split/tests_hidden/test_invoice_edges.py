import copy
import unittest

from billing.invoice import build_invoice
from billing.money import allocate, round_div, round_to
from billing.tax import line_tax, tax_by_rate


def line(sku, qty, unit_price, rate_bp):
    return {'sku': sku, 'qty': qty, 'unit_price': unit_price, 'rate_bp': rate_bp}


class HiddenInvoiceTests(unittest.TestCase):
    def test_round_div_rounds_ties_away_from_zero(self):
        self.assertEqual(round_div(5, 2), 3)
        self.assertEqual(round_div(-5, 2), -3)
        self.assertEqual(round_div(-4, 2), -2)
        self.assertEqual(round_div(-1, 3), 0)
        self.assertEqual(round_div(-2, 3), -1)
        self.assertEqual(round_div(-15, 10), -2)
        self.assertEqual(round_div(15, 10), 2)
        self.assertEqual(round_div(0, 7), 0)
        self.assertEqual(round_to(-15, 10), -20)
        self.assertEqual(round_to(1003, 5), 1005)
        with self.assertRaises(ValueError):
            round_div(1, 0)
        with self.assertRaises(ValueError):
            round_div(1, -2)
        with self.assertRaises(TypeError):
            round_div(1.0, 2)
        with self.assertRaises(TypeError):
            round_div(1, True)

    def test_allocate_ties_go_to_lower_indexes(self):
        self.assertEqual(allocate(100, [1, 1, 1]), [34, 33, 33])
        self.assertEqual(allocate(10, [1, 1, 1, 1, 1, 1]), [2, 2, 2, 2, 1, 1])
        self.assertEqual(allocate(10, (1, 1, 4)), [2, 2, 6])
        self.assertEqual(allocate(1, [1, 1]), [1, 0])
        self.assertEqual(allocate(-100, [1, 1, 1]), [-34, -33, -33])

    def test_allocate_remainders_and_zero_weights(self):
        self.assertEqual(allocate(7, [1, 2, 3]), [1, 2, 4])
        self.assertEqual(allocate(7, [0, 3, 0, 4]), [0, 3, 0, 4])
        self.assertEqual(allocate(5, [2, 3, 0]), [2, 3, 0])
        self.assertEqual(allocate(0, [1, 2]), [0, 0])
        self.assertEqual(allocate(1, [0, 1, 1]), [0, 1, 0])
        self.assertEqual(allocate(10 ** 20, [1, 3]), [25 * 10 ** 18, 75 * 10 ** 18])

    def test_allocate_validation(self):
        for total, weights, error in (
            (5, [], ValueError),
            (5, [0, 0], ValueError),
            (5, [1, -1, 2], ValueError),
            (5.0, [1], TypeError),
            (True, [1], TypeError),
            (5, [True], TypeError),
            (5, [1.5], TypeError),
            (5, 'ab', TypeError),
            (5, {1: 1}, TypeError),
        ):
            with self.assertRaises(error):
                allocate(total, weights)

    def test_credit_note_tax_rounds_away_from_zero(self):
        result = build_invoice([line('R', -1, 5, 5000)])
        self.assertEqual(result['lines'], [{'sku': 'R', 'net': -5, 'discount': 0, 'taxable': -5, 'tax': -3}])
        self.assertEqual(result['subtotal'], -5)
        self.assertEqual(result['tax'], -3)
        self.assertEqual(result['total'], -8)
        self.assertEqual(result['tax_by_rate'], {5000: -3})
        positive = build_invoice([line('R', 1, 5, 5000)])
        self.assertEqual(positive['tax'], 3)

    def test_cash_rounding(self):
        up = build_invoice([line('A', 1, 1003, 0)], cash_step=5)
        self.assertEqual((up['total'], up['rounding'], up['payable']), (1003, 2, 1005))
        down = build_invoice([line('A', 1, 1002, 0)], cash_step=5)
        self.assertEqual((down['total'], down['rounding'], down['payable']), (1002, -2, 1000))
        tie = build_invoice([line('A', 1, 15, 0)], cash_step=10)
        self.assertEqual((tie['rounding'], tie['payable']), (5, 20))
        negative_tie = build_invoice([line('A', -1, 15, 0)], cash_step=10)
        self.assertEqual((negative_tie['total'], negative_tie['rounding'], negative_tie['payable']), (-15, -5, -20))

    def test_discount_ties_and_remainders(self):
        result = build_invoice([line('A', 1, 100, 0), line('B', 1, 100, 0), line('C', 1, 100, 0)],
                               discount_cents=10)
        self.assertEqual([row['discount'] for row in result['lines']], [4, 3, 3])
        self.assertEqual(result['total'], 290)
        free = build_invoice([line('A', 1, 0, 1000), line('B', 2, 50, 1000), line('C', 3, 0, 0)],
                             discount_cents=100)
        self.assertEqual([row['discount'] for row in free['lines']], [0, 100, 0])
        self.assertEqual([row['taxable'] for row in free['lines']], [0, 0, 0])
        self.assertEqual(free['total'], 0)

    def test_tax_is_rounded_per_line_and_grouped_by_rate(self):
        result = build_invoice([line('A', 1, 5, 5000), line('B', 1, 5, 5000), line('C', 4, 7, 0),
                                line('D', 1, 333, 700)])
        self.assertEqual([row['tax'] for row in result['lines']], [3, 3, 0, 23])
        self.assertEqual(result['tax'], 29)
        self.assertEqual(list(result['tax_by_rate'].items()), [(0, 0), (700, 23), (5000, 6)])
        self.assertEqual(result['total'], 5 + 5 + 28 + 333 + 29)
        self.assertEqual(line_tax(333, 700), 23)
        self.assertEqual(line_tax(-333, 700), -23)
        self.assertEqual(list(tax_by_rate([1, 2, 3], [200, 100, 200]).items()), [(100, 2), (200, 4)])
        self.assertEqual(tax_by_rate([], []), {})

    def test_empty_invoice_and_discount_limits(self):
        self.assertEqual(build_invoice([]), {'lines': [], 'subtotal': 0, 'discount': 0, 'tax': 0,
                                             'tax_by_rate': {}, 'total': 0, 'rounding': 0, 'payable': 0})
        self.assertEqual(build_invoice(()), build_invoice([]))
        with self.assertRaises(ValueError):
            build_invoice([], discount_cents=1)
        full = build_invoice([line('A', 2, 50, 1000)], discount_cents=100)
        self.assertEqual((full['total'], full['tax']), (0, 0))
        with self.assertRaises(ValueError):
            build_invoice([line('A', 2, 50, 1000)], discount_cents=101)
        with self.assertRaises(ValueError):
            build_invoice([line('A', 2, 50, 0), line('B', -1, 30, 0)], discount_cents=10)
        mixed = build_invoice([line('A', 2, 50, 0), line('B', -1, 30, 0)])
        self.assertEqual(mixed['subtotal'], 70)

    def test_validation_order_and_types(self):
        good = line('A', 1, 1, 0)
        cases = [
            (TypeError, lambda: build_invoice('abc')),
            (TypeError, lambda: build_invoice([good, 'x'])),
            (TypeError, lambda: build_invoice([good, dict(good, sku=5)])),
            (ValueError, lambda: build_invoice([dict(good, sku='')])),
            (ValueError, lambda: build_invoice([{'sku': 'A'}])),
            (ValueError, lambda: build_invoice([dict(good, extra=1)])),
            (TypeError, lambda: build_invoice([dict(good, qty=1.0)])),
            (ValueError, lambda: build_invoice([dict(good, unit_price=-1)])),
            (TypeError, lambda: build_invoice([dict(good, unit_price=True)])),
            (ValueError, lambda: build_invoice([dict(good, rate_bp=10001)])),
            (ValueError, lambda: build_invoice([dict(good, rate_bp=-1)])),
            (TypeError, lambda: build_invoice([good], discount_cents=1.5)),
            (ValueError, lambda: build_invoice([good], discount_cents=-1)),
            (TypeError, lambda: build_invoice([good], cash_step='5')),
            (ValueError, lambda: build_invoice([good], cash_step=0)),
            (ValueError, lambda: build_invoice([dict(good, qty=0), 'x'])),
            (TypeError, lambda: build_invoice([dict(good, qty=0, sku=3)])),
            (TypeError, lambda: build_invoice([dict(good, qty='1', unit_price=-1)])),
            (ValueError, lambda: build_invoice([good], discount_cents=-1, cash_step='x')),
            (TypeError, lambda: build_invoice([good], discount_cents='x', cash_step=0)),
            (ValueError, lambda: build_invoice([dict(good, rate_bp=20000)], discount_cents='x')),
        ]
        for error, call in cases:
            with self.assertRaises(error):
                call()

    def test_input_is_not_mutated_and_output_is_fresh(self):
        lines = [line('A', 2, 100, 1000), line('B', 1, 50, 1000)]
        before = copy.deepcopy(lines)
        first = build_invoice(lines, discount_cents=7)
        second = build_invoice(lines, discount_cents=7)
        self.assertEqual(lines, before)
        self.assertEqual(first, second)
        self.assertIsNot(first['lines'], second['lines'])
        self.assertIsNot(first['lines'][0], second['lines'][0])
        self.assertEqual(list(first['lines'][0]), ['sku', 'net', 'discount', 'taxable', 'tax'])
        self.assertEqual(sum(row['discount'] for row in first['lines']), 7)
