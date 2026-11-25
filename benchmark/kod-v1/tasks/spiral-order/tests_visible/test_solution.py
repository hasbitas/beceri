import unittest

import solution


def walking_order(rows, cols):
    """Independent oracle: walk cells, turning when blocked."""
    if not rows or not cols:
        return []
    directions = ((0, 1), (1, 0), (0, -1), (-1, 0))
    seen = set()
    result = []
    row = col = direction = 0
    for _ in range(rows * cols):
        result.append(row * cols + col)
        seen.add((row, col))
        dr, dc = directions[direction]
        nr, nc = row + dr, col + dc
        if not (0 <= nr < rows and 0 <= nc < cols) or (nr, nc) in seen:
            direction = (direction + 1) % 4
            dr, dc = directions[direction]
        row, col = row + dr, col + dc
    return result


class SpiralTests(unittest.TestCase):


    def test_all_small_shapes(self):
        for rows in range(10):
            for cols in range(10):
                with self.subTest(rows=rows, cols=cols):
                    matrix = [[r * cols + c for c in range(cols)] for r in range(rows)]
                    self.assertEqual(solution.spiral(matrix), walking_order(rows, cols))

    def test_empty_and_fresh_results(self):
        for matrix in ([], (), [[]], [[], []], ((), [], ())):
            with self.subTest(matrix=matrix):
                first = solution.spiral(matrix)
                second = solution.spiral(matrix)
                self.assertIs(type(first), list)
                self.assertEqual(first, [])
                self.assertIsNot(first, second)
                self.assertIsNot(first, matrix)
        row = [1, 2]
        first = solution.spiral([row])
        second = solution.spiral([row])
        self.assertIsNot(first, row)
        self.assertIsNot(first, second)

    def test_container_combinations(self):
        for outer in (list, tuple):
            for row_type in (list, tuple):
                matrix = outer(row_type((r * 4 + c for c in range(4))) for r in range(5))
                self.assertEqual(solution.spiral(matrix), walking_order(5, 4))
        self.assertEqual(solution.spiral(([0, 1], (2, 3), [4, 5])), [0, 1, 3, 5, 4, 2])




    def test_ragged_inputs_unchanged(self):
        for matrix in ([[], [1]], [[1], []], [[1, 2], [3]], ((1,), (2, 3))):
            with self.subTest(matrix=matrix):
                before = [list(row) for row in matrix]
                with self.assertRaises(ValueError):
                    solution.spiral(matrix)
                self.assertEqual([list(row) for row in matrix], before)


if __name__ == '__main__':
    unittest.main()
