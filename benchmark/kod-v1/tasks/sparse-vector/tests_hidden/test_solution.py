import itertools
import unittest

import solution


class IntChild(int):
    pass


class DictChild(dict):
    pass


class SparseVectorTests(unittest.TestCase):
    def check_pair(self, a, b, expected_add, expected_dot):
        before_a, before_b = a.copy(), b.copy()
        result = solution.add(a, b)
        self.assertIs(type(result), dict)
        self.assertEqual(result, expected_add)
        self.assertIsNot(result, a)
        self.assertIsNot(result, b)
        self.assertTrue(all(type(v) is int and v != 0 for v in result.values()))
        product = solution.dot(a, b)
        self.assertIs(type(product), int)
        self.assertEqual(product, expected_dot)
        self.assertEqual(a, before_a)
        self.assertEqual(b, before_b)
        result.clear()
        result[91] = 22
        self.assertEqual(a, before_a)
        self.assertEqual(b, before_b)

    def test_overlap_and_disjoint(self):
        self.check_pair({7: 3, 2: -4}, {2: 6, 9: -2},
                        {7: 3, 2: 2, 9: -2}, -24)
        self.check_pair({3: -8}, {5: 7}, {3: -8, 5: 7}, 0)

    def test_empty_and_explicit_zeros(self):
        for a, b, expected in [({}, {}, {}), ({4: 0}, {}, {}),
                               ({}, {6: 0, 1: -3}, {1: -3}),
                               ({2: 5}, {2: 0, 8: 0}, {2: 5})]:
            with self.subTest(a=a, b=b):
                self.check_pair(a, b, expected, 0)
                self.check_pair(b, a, expected, 0)

    def test_cancellation_removes_coordinates(self):
        self.check_pair({1: 4, 8: -3, 10: 0}, {1: -4, 8: 3}, {}, -25)
        self.check_pair({1: 4, 2: 7}, {1: -4, 3: -6}, {2: 7, 3: -6}, -16)


    def test_arbitrary_integer_magnitudes(self):
        index = 10 ** 100
        value = 10 ** 150
        self.check_pair({index: value, 0: -value},
                        {index: -value, index + 1: 7},
                        {0: -value, index + 1: 7}, -(value ** 2))
        self.check_pair({0: value, index: value}, {0: value, index: -value},
                        {0: 2 * value}, 0)



    def test_invalid_entries_fully_validated_and_preserved(self):
        cases = [({True: 1}, TypeError), ({IntChild(2): 1}, TypeError),
                 ({'2': 1}, TypeError), ({2.5: 1}, TypeError),
                 ({-1: 0}, ValueError), ({2: True}, TypeError),
                 ({2: IntChild(3)}, TypeError), ({2: 1.0}, TypeError),
                 ({2: None}, TypeError), ({2: '3'}, TypeError)]
        for invalid, error in cases:
            bad = {5: 9}
            bad.update(invalid)
            for good in ({}, {5: -9, 99: 0}, {100: 3}):
                for function in (solution.add, solution.dot):
                    for a, b in ((bad, good), (good, bad)):
                        with self.subTest(function=function.__name__, a=a, b=b):
                            before_a, before_b = a.copy(), b.copy()
                            with self.assertRaises(error):
                                function(a, b)
                            self.assertEqual(a, before_a)
                            self.assertEqual(b, before_b)


if __name__ == '__main__':
    unittest.main()
