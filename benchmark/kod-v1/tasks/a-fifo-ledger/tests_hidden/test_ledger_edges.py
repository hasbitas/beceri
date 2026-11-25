import unittest

from fifo.costing import average_cost, total_cost
from fifo.ledger import Ledger
from fifo.lots import Lot, consume, restore, total_qty


class HiddenLedgerTests(unittest.TestCase):
    def test_average_cost_rounds_ties_up(self):
        self.assertEqual(average_cost(5, 2), 3)
        self.assertEqual(average_cost(1, 2), 1)
        self.assertEqual(average_cost(0, 3), 0)
        self.assertEqual(average_cost(7, 3), 2)
        self.assertEqual(average_cost(10, 4), 3)
        self.assertEqual(average_cost(9, 4), 2)
        self.assertEqual(total_cost([(1, 2, 5), (2, 3, 7)]), 31)
        ledger = Ledger()
        ledger.receive('A', 1, 2)
        ledger.receive('A', 1, 3)
        self.assertEqual(ledger.issue('A', 2)['unit_cost'], 3)

    def test_returned_exhausted_lot_is_reinserted_in_order(self):
        ledger = Ledger()
        ledger.receive('A', 5, 10)
        ledger.receive('A', 5, 20)
        first = ledger.issue('A', 5)
        ledger.issue('A', 2)
        self.assertEqual(ledger.lots('A'), [(2, 3, 20)])
        result = ledger.return_items(first['issue_id'], 5)
        self.assertEqual(result, {'credit': 50, 'restored': [(1, 5)]})
        self.assertEqual(ledger.lots('A'), [(1, 5, 10), (2, 3, 20)])
        self.assertEqual(ledger.value('A'), 110)

    def test_lots_helpers_directly(self):
        lots = [Lot(2, 20, 3), Lot(5, 30, 1)]
        restore(lots, 3, 25, 4)
        restore(lots, 1, 15, 2)
        restore(lots, 9, 40, 1)
        restore(lots, 5, 99, 2)
        self.assertEqual([(l.lot_id, l.unit_cost, l.qty) for l in lots],
                         [(1, 15, 2), (2, 20, 3), (3, 25, 4), (5, 30, 3), (9, 40, 1)])
        self.assertEqual(total_qty(lots), 13)
        before = [(l.lot_id, l.qty) for l in lots]
        with self.assertRaises(ValueError):
            consume(lots, 14)
        self.assertEqual([(l.lot_id, l.qty) for l in lots], before)
        taken = consume(lots, 6)
        self.assertEqual(taken, [(1, 2, 15), (2, 3, 20), (3, 1, 25)])
        self.assertEqual([(l.lot_id, l.qty) for l in lots], [(3, 3), (5, 3), (9, 1)])

    def test_partial_returns_accumulate_across_calls(self):
        ledger = Ledger()
        ledger.receive('A', 3, 10)
        ledger.receive('A', 3, 20)
        ledger.receive('A', 3, 30)
        issue = ledger.issue('A', 8)
        self.assertEqual(issue['lots'], [(1, 3), (2, 3), (3, 2)])
        self.assertEqual(issue['cost'], 30 + 60 + 60)
        self.assertEqual(issue['unit_cost'], 19)
        one = ledger.return_items(issue['issue_id'], 1)
        self.assertEqual(one, {'credit': 30, 'restored': [(3, 1)]})
        two = ledger.return_items(issue['issue_id'], 3)
        self.assertEqual(two, {'credit': 30 + 40, 'restored': [(3, 1), (2, 2)]})
        self.assertEqual(ledger.lots('A'), [(2, 2, 20), (3, 3, 30)])
        with self.assertRaises(ValueError):
            ledger.return_items(issue['issue_id'], 5)
        three = ledger.return_items(issue['issue_id'], 4)
        self.assertEqual(three['restored'], [(2, 1), (1, 3)])
        self.assertEqual(three['credit'], 20 + 30)
        self.assertEqual(ledger.lots('A'), [(1, 3, 10), (2, 3, 20), (3, 3, 30)])
        with self.assertRaises(ValueError):
            ledger.return_items(issue['issue_id'], 1)

    def test_failed_calls_leave_counters_untouched(self):
        ledger = Ledger()
        with self.assertRaises(ValueError):
            ledger.issue('A', 1)
        with self.assertRaises(ValueError):
            ledger.receive('A', 0, 5)
        with self.assertRaises(ValueError):
            ledger.receive('A', 1, -1)
        self.assertEqual(ledger.receive('A', 2, 5), 1)
        with self.assertRaises(ValueError):
            ledger.issue('A', 3)
        self.assertEqual(ledger.lots('A'), [(1, 2, 5)])
        self.assertEqual(ledger.issue('A', 2)['issue_id'], 1)
        with self.assertRaises(ValueError):
            ledger.return_items(1, 3)
        with self.assertRaises(ValueError):
            ledger.return_items(2, 1)
        self.assertEqual(ledger.lots('A'), [])
        self.assertEqual(ledger.return_items(1, 2), {'credit': 10, 'restored': [(1, 2)]})

    def test_ids_are_global_and_skus_are_independent(self):
        ledger = Ledger()
        self.assertEqual(ledger.receive('A', 1, 10), 1)
        self.assertEqual(ledger.receive('B', 4, 5), 2)
        self.assertEqual(ledger.receive('A', 2, 11), 3)
        self.assertEqual(ledger.receive('a', 1, 1), 4)
        self.assertEqual(ledger.issue('B', 3)['issue_id'], 1)
        self.assertEqual(ledger.issue('A', 3)['issue_id'], 2)
        self.assertEqual(ledger.lots('B'), [(2, 1, 5)])
        self.assertEqual(ledger.lots('A'), [])
        self.assertEqual(ledger.lots('a'), [(4, 1, 1)])
        self.assertEqual(ledger.value('B'), 5)
        self.assertEqual(ledger.on_hand('A'), 0)
        self.assertEqual(ledger.return_items(2, 2), {'credit': 22, 'restored': [(3, 2)]})
        self.assertEqual(ledger.lots('A'), [(3, 2, 11)])

    def test_type_checks_precede_value_and_state_checks(self):
        ledger = Ledger()
        ledger.receive('A', 3, 10)
        issue = ledger.issue('A', 1)['issue_id']
        for call in (
            lambda: ledger.receive(1, 1, 1),
            lambda: ledger.receive('A', 1.0, 1),
            lambda: ledger.receive('A', 1, True),
            lambda: ledger.issue(None, 1),
            lambda: ledger.issue('A', False),
            lambda: ledger.return_items(True, 1),
            lambda: ledger.return_items(issue, 1.5),
            lambda: ledger.return_items(99, '1'),
            lambda: ledger.on_hand(5),
            lambda: ledger.value(b'A'),
            lambda: ledger.lots(None),
        ):
            with self.assertRaises(TypeError):
                call()
        with self.assertRaises(TypeError):
            ledger.receive(7, 0, -1)
        with self.assertRaises(ValueError):
            ledger.receive('', 'x', 1)
        with self.assertRaises(ValueError):
            ledger.receive('A', 0, 1.5)
        with self.assertRaises(TypeError):
            ledger.receive('A', 'x', -1)
        with self.assertRaises(ValueError):
            ledger.return_items(0, 1)
        with self.assertRaises(ValueError):
            ledger.return_items(issue, 0)
        with self.assertRaises(ValueError):
            ledger.on_hand('')

    def test_zero_cost_lots(self):
        ledger = Ledger()
        ledger.receive('F', 3, 0)
        ledger.receive('F', 1, 7)
        result = ledger.issue('F', 4)
        self.assertEqual(result, {'issue_id': 1, 'cost': 7, 'unit_cost': 2, 'lots': [(1, 3), (2, 1)]})
        back = ledger.return_items(1, 4)
        self.assertEqual(back, {'credit': 7, 'restored': [(2, 1), (1, 3)]})
        self.assertEqual(ledger.lots('F'), [(1, 3, 0), (2, 1, 7)])
        self.assertEqual(ledger.value('F'), 7)
