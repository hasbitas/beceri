import unittest

import solution


class RotationTests(unittest.TestCase):

    def test_bounded_coordinate_oracle(self):
        for h in range(1, 5):
            for w in range(1, 6):
                matrix = [[(r, c) for c in range(w)] for r in range(h)]
                for k in range(-9, 10):
                    t = k % 4
                    oh, ow = (h, w) if t % 2 == 0 else (w, h)
                    expected = [[None] * ow for _ in range(oh)]
                    for r in range(h):
                        for c in range(w):
                            rr, cc = ((r, c), (c, h - 1 - r),
                                      (h - 1 - r, w - 1 - c),
                                      (w - 1 - c, r))[t]
                            expected[rr][cc] = matrix[r][c]
                    with self.subTest(h=h, w=w, k=k):
                        self.assertEqual(solution.rotate(matrix, k), expected)

    def test_large_counts(self):
        n = 10 ** 120
        matrix = [[1, 2], [3, 4], [5, 6]]
        for k, expected in (
            (n, matrix), (-n, matrix),
            (n + 1, [[5, 3, 1], [6, 4, 2]]),
            (-n - 1, [[2, 4, 6], [1, 3, 5]]),
        ):
            with self.subTest(k=k):
                self.assertEqual(solution.rotate(matrix, k), expected)




    def test_invalid_counts(self):
        for k in (True, False, 1.0, "1", None, [], complex(1, 0)):
            for matrix in ([], [[1]], None, [[1], []]):
                with self.subTest(k=k, matrix=matrix):
                    with self.assertRaises(TypeError):
                        solution.rotate(matrix, k)


    def test_ragged_and_failure_preserves_input(self):
        for matrix in ([[], [1]], [[1], []], [[1, 2], [3]],
                       ((), (1,)), [[1], [2], [3, 4]]):
            before = [list(row) for row in matrix]
            row_ids = [id(row) for row in matrix]
            for k in (0, 1, -1, 4):
                with self.subTest(matrix=matrix, k=k):
                    with self.assertRaises(ValueError):
                        solution.rotate(matrix, k)
                    self.assertEqual([list(row) for row in matrix], before)
                    self.assertEqual([id(row) for row in matrix], row_ids)


if __name__ == "__main__":
    unittest.main()
