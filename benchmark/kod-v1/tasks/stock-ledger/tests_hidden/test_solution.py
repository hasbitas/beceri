import copy
import itertools
import unittest

import solution


def move(item='apple', direction='in', quantity=1):
    return {'item': item, 'direction': direction, 'quantity': quantity}


class LedgerTests(unittest.TestCase):
    def test_interleaved_items_and_order(self):
        records = [move('z', quantity=8), move('a', quantity=4),
                   move('z', 'out', 3), move('m', 'out', 0),
                   move('a', 'out', 4), move('z', quantity=2)]
        result = solution.apply(records)
        self.assertIs(type(result), dict)
        self.assertEqual(result, {'z': 7, 'a': 0, 'm': 0})
        self.assertEqual(list(result), ['z', 'a', 'm'])
        self.assertTrue(all(type(value) is int for value in result.values()))

    def test_empty_and_independent_results(self):
        for records in ([], ()):
            first = solution.apply(records)
            second = solution.apply(records)
            self.assertEqual(first, {})
            self.assertIsNot(first, second)
        records = [move()]
        first = solution.apply(records)
        first['apple'] = 999
        self.assertEqual(solution.apply(records), {'apple': 1})
        with self.assertRaises(ValueError):
            solution.apply([move(direction='out')])


    def test_large_quantities_and_exact_depletion(self):
        huge = 10 ** 100
        self.assertEqual(solution.apply([move(quantity=huge),
                                        move(direction='out', quantity=huge)]),
                         {'apple': 0})




    def test_schema_and_invalid_fields(self):
        class IntSubclass(int):
            pass
        class StringSubclass(str):
            pass
        cases = [({}, ValueError),
                 ({'item': 'a', 'direction': 'in'}, ValueError),
                 (dict(move(), extra=1), ValueError)]
        for field, values, error in [
            ('item', [None, 1, False, StringSubclass('a')], TypeError),
            ('item', [''], ValueError),
            ('direction', [None, 1, StringSubclass('in')], TypeError),
            ('direction', ['', 'IN', 'in ', 'transfer'], ValueError),
            ('quantity', [True, False, 1.0, '1', None, IntSubclass(1)], TypeError),
            ('quantity', [-1, -10 ** 100], ValueError),
        ]:
            for value in values:
                record = move()
                record[field] = value
                cases.append((record, error))
        for record, error in cases:
            with self.subTest(record=record), self.assertRaises(error):
                solution.apply([record])

    def test_validation_precedes_stock_and_field_precedence(self):
        with self.assertRaises(TypeError):
            solution.apply([move(direction='out'), move(quantity=False)])
        with self.assertRaises(TypeError):
            solution.apply([{'item': None, 'direction': 'bad', 'quantity': -1}])
        with self.assertRaises(ValueError):
            solution.apply([{'item': '', 'direction': None, 'quantity': False}])
        with self.assertRaises(ValueError):
            solution.apply([{'item': None}])
        with self.assertRaises(ValueError):
            solution.apply([move(direction='bad', quantity=None)])
        with self.assertRaises(ValueError):
            solution.apply([move(item=''), None])

    def test_bounded_sequences_against_prefix_oracle(self):
        # Each item's prefix sum must stay nonnegative, not just its total.
        alphabet = [('b', 0), ('b', 1), ('b', -1), ('a', 2), ('a', -2)]
        for length in range(5):
            for events in itertools.product(alphabet, repeat=length):
                records = [move(item, 'in' if delta >= 0 else 'out', abs(delta))
                           for item, delta in events]
                names = list(dict.fromkeys(item for item, _ in events))
                valid = all(sum(delta for item, delta in events[:end] if item == name) >= 0
                            for name in names for end in range(1, length + 1))
                with self.subTest(events=events):
                    if not valid:
                        with self.assertRaises(ValueError):
                            solution.apply(records)
                    else:
                        expected = {name: sum(delta for item, delta in events if item == name)
                                    for name in names}
                        result = solution.apply(records)
                        self.assertEqual(result, expected)
                        self.assertEqual(list(result), names)


if __name__ == '__main__':
    unittest.main()
