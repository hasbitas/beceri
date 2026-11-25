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




    def test_same_object_both_arguments(self):
        vector = {0: -3, 2: 0, 9: 5}
        self.check_pair(vector, vector, {0: -6, 9: 10}, 34)
        empty = {}
        self.check_pair(empty, empty, {}, 0)


    def test_all_small_vectors(self):
        # Dense tuples supply an independent coordinate-based oracle.
        vectors = list(itertools.product((-1, 0, 1), repeat=3))
        for left in vectors:
            for right in vectors:
                a = dict(enumerate(left))
                b = dict(reversed(list(enumerate(right))))
                expected = {i: left[i] + right[i] for i in range(3)
                            if left[i] + right[i] != 0}
                product = sum(left[i] * right[i] for i in range(3))
                with self.subTest(left=left, right=right):
                    self.check_pair(a, b, expected, product)

    def test_invalid_argument_types(self):
        for invalid in (None, [], (), 3, 'vector', DictChild({0: 1})):
            for function in (solution.add, solution.dot):
                for args in ((invalid, {}), ({}, invalid)):
                    with self.subTest(function=function.__name__, args=args):
                        with self.assertRaises(TypeError):
                            function(*args)



if __name__ == '__main__':
    unittest.main()
