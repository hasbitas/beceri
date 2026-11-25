import itertools
import unittest

import solution


class TopKTests(unittest.TestCase):

    def test_ascii_ties_and_cutoff(self):
        data = ["b", "a", "B", "A"]
        for k, expected in [(1, ["A"]), (3, ["A", "a", "B"]),
                            (4, ["A", "a", "B", "b"])]:
            with self.subTest(k=k):
                self.assertEqual(solution.top_k(data, k), expected)




    def test_empty_zero_and_oversized(self):
        self.assertEqual(solution.top_k([], 8), [])
        self.assertEqual(solution.top_k(["x", "x"], 0), [])
        self.assertEqual(solution.top_k(["x", "", "x"], 10**80), ["x", ""])


    def test_one_shot_iterable(self):
        class Once:
            def __init__(self):
                self.calls = 0
                self.seen = []

            def __iter__(self):
                self.calls += 1
                if self.calls > 1:
                    raise AssertionError("restarted iterable")
                for value in ["b", "a", "b"]:
                    self.seen.append(value)
                    yield value

        for k, expected in [(0, []), (1, ["b"]), (8, ["b", "a"])]:
            source = Once()
            self.assertEqual(solution.top_k(source, k), expected)
            self.assertEqual(source.calls, 1)
            self.assertEqual(source.seen, ["b", "a", "b"])
        self.assertEqual(solution.top_k(iter(["b", "a", "b"]), 2), ["b", "a"])


    def test_invalid_items_even_for_zero(self):
        for k in [0, 1, 10]:
            for data in [None, 42, ["ok", 1], ["ok", None],
                         ["ok", []], ["ok", b"bytes"], ["ok", True]]:
                with self.subTest(k=k, data=data), self.assertRaises(TypeError):
                    solution.top_k(data, k)
            with self.assertRaises(TypeError):
                solution.top_k((x for x in ["a", "a", 5]), k)


    def test_bounded_frequency_combinations(self):
        # This list explicitly gives the tie precedence, independently of sorting.
        precedence = ["", "A", "a", "SS", "ß", "st"]
        for counts in itertools.product(range(3), repeat=len(precedence)):
            data = []
            for value, count in zip(reversed(precedence), reversed(counts)):
                data.extend([value] * count)
            expected = []
            for frequency in [2, 1]:
                expected.extend(value for value, count in zip(precedence, counts)
                                if count == frequency)
            for k in [0, 1, 3, 9]:
                with self.subTest(counts=counts, k=k):
                    self.assertEqual(solution.top_k(data, k), expected[:k])


if __name__ == "__main__":
    unittest.main()
