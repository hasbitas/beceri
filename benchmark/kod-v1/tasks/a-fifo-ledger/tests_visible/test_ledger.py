import unittest

from fifo.ledger import Ledger


class VisibleLedgerTests(unittest.TestCase):
    def test_issue_consumes_oldest_lots_first(self):
        ledger = Ledger()
        self.assertEqual(ledger.receive('A', 5, 10), 1)
        self.assertEqual(ledger.receive('A', 5, 20), 2)
        result = ledger.issue('A', 7)
        self.assertEqual(result, {'issue_id': 1, 'cost': 90, 'unit_cost': 13, 'lots': [(1, 5), (2, 2)]})
        self.assertEqual(ledger.lots('A'), [(2, 3, 20)])
        self.assertEqual(ledger.on_hand('A'), 3)
        self.assertEqual(ledger.value('A'), 60)

    def test_return_walks_lots_from_last_consumed(self):
        ledger = Ledger()
        ledger.receive('A', 5, 10)
        ledger.receive('A', 5, 20)
        issue = ledger.issue('A', 8)
        result = ledger.return_items(issue['issue_id'], 2)
        self.assertEqual(result, {'credit': 40, 'restored': [(2, 2)]})
        self.assertEqual(ledger.lots('A'), [(2, 4, 20)])

    def test_validation_and_unknowns(self):
        ledger = Ledger()
        ledger.receive('A', 2, 10)
        with self.assertRaises(TypeError):
            ledger.receive('A', True, 10)
        with self.assertRaises(ValueError):
            ledger.receive('', 1, 10)
        with self.assertRaises(ValueError):
            ledger.issue('A', 3)
        with self.assertRaises(ValueError):
            ledger.issue('B', 1)
        with self.assertRaises(ValueError):
            ledger.return_items(7, 1)
        self.assertEqual(ledger.on_hand('B'), 0)
        self.assertEqual(ledger.lots('B'), [])
