import copy
import itertools
import unittest

import solution


def move(item='apple', direction='in', quantity=1):
    return {'item': item, 'direction': direction, 'quantity': quantity}


class LedgerTests(unittest.TestCase):


    def test_zero_and_literal_names(self):
        names = [' A ', 'A', 'a', ' ', 'é', 'e\u0301']
        result = solution.apply(tuple(move(name, 'out', 0) for name in names))
        self.assertEqual(list(result.items()), [(name, 0) for name in names])


    def test_shortages_are_not_net_aggregation(self):
        cases = [
            [move(direction='out'), move()],
            [move(quantity=2), move(direction='out', quantity=3), move(quantity=5)],
            [move('a', quantity=100), move('b', 'out', 1)],
            [move(quantity=1), move(direction='out', quantity=2)],
        ]
        for records in cases:
            with self.subTest(records=records), self.assertRaises(ValueError):
                solution.apply(records)

    def test_input_preservation(self):
        for records, fails in [([move(quantity=2), move(direction='out')], False),
                               ([move(), move(direction='out', quantity=3)], True),
                               ([move(), move(quantity=False)], True)]:
            before = copy.deepcopy(records)
            identities = [id(record) for record in records]
            if fails:
                with self.assertRaises((TypeError, ValueError)):
                    solution.apply(records)
            else:
                solution.apply(records)
            self.assertEqual(records, before)
            self.assertEqual([id(record) for record in records], identities)

    def test_container_and_record_types(self):
        class ListSubclass(list):
            pass
        class DictSubclass(dict):
            pass
        for records in (None, {}, 'abc', 7, iter([]), ListSubclass()):
            with self.subTest(records=repr(records)), self.assertRaises(TypeError):
                solution.apply(records)
        for record in (None, [], ('apple', 'in', 1), DictSubclass(move())):
            with self.subTest(record=record), self.assertRaises(TypeError):
                solution.apply([record])





if __name__ == '__main__':
    unittest.main()
