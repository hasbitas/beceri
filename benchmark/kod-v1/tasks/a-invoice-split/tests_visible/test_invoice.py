import unittest

from billing.invoice import build_invoice


def line(sku, qty, unit_price, rate_bp):
    return {'sku': sku, 'qty': qty, 'unit_price': unit_price, 'rate_bp': rate_bp}


class VisibleInvoiceTests(unittest.TestCase):
    def test_plain_invoice(self):
        result = build_invoice([line('A', 3, 1000, 2000), line('B', 1, 500, 1000)])
        self.assertEqual(result['subtotal'], 3500)
        self.assertEqual([row['tax'] for row in result['lines']], [600, 50])
        self.assertEqual(result['tax'], 650)
        self.assertEqual(result['total'], 4150)
        self.assertEqual(result['rounding'], 0)
        self.assertEqual(result['payable'], 4150)
        self.assertEqual(list(result['tax_by_rate'].items()), [(1000, 50), (2000, 600)])

    def test_discount_reduces_the_taxable_amount(self):
        result = build_invoice([line('A', 2, 1500, 1000), line('B', 1, 1000, 1000)], discount_cents=400)
        self.assertEqual([row['discount'] for row in result['lines']], [300, 100])
        self.assertEqual([row['taxable'] for row in result['lines']], [2700, 900])
        self.assertEqual([row['tax'] for row in result['lines']], [270, 90])
        self.assertEqual(result['discount'], 400)
        self.assertEqual(result['total'], 3960)

    def test_rejects_bad_input(self):
        with self.assertRaises(TypeError):
            build_invoice([line('A', True, 100, 0)])
        with self.assertRaises(ValueError):
            build_invoice([line('A', 0, 100, 0)])
        with self.assertRaises(ValueError):
            build_invoice([line('A', 1, 100, 0)], discount_cents=101)
