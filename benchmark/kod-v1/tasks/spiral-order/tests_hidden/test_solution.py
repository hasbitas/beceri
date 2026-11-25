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
    def test_known_rectangles(self):
        self.assertEqual(solution.spiral([[1, 2, 3], [4, 5, 6]]),
                         [1, 2, 3, 6, 5, 4])
        self.assertEqual(solution.spiral([[1, 2], [3, 4], [5, 6]]),
                         [1, 2, 4, 6, 5, 3])
        self.assertEqual(solution.spiral([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                         [1, 2, 3, 6, 9, 8, 7, 4, 5])

    def test_single_rows_and_columns(self):
        for size in range(1, 10):
            with self.subTest(size=size):
                self.assertEqual(solution.spiral([list(range(size))]), list(range(size)))
                self.assertEqual(solution.spiral([[i] for i in range(size)]), list(range(size)))




    def test_cells_identity_and_no_mutation(self):
        cells = [[], {}, object(), None, ['nested'], {'x': 1}, False, 'text', (1, 2)]
        matrix = [cells[:3], cells[3:6], cells[6:]]
        rows_before = matrix[:]
        snapshots = [row[:] for row in matrix]
        result = solution.spiral(matrix)
        for actual, index in zip(result, [0, 1, 2, 5, 8, 7, 6, 3, 4]):
            self.assertIs(actual, cells[index])
        self.assertEqual(len(result), 9)
        for row, original, snapshot in zip(matrix, rows_before, snapshots):
            self.assertIs(row, original)
            self.assertEqual(row, snapshot)
        self.assertEqual(cells[0], [])
        self.assertEqual(cells[1], {})
        self.assertEqual(cells[4], ['nested'])
        self.assertEqual(cells[5], {'x': 1})
        shared = []
        self.assertEqual(solution.spiral([[shared] * 3 for _ in range(4)]), [shared] * 12)

    def test_unsupported_outer_types(self):
        for matrix in (None, 42, 'abc', b'abc', {}, {1, 2}, range(3)):
            with self.subTest(matrix=matrix):
                with self.assertRaises(TypeError):
                    solution.spiral(matrix)

    def test_unsupported_rows_and_precedence(self):
        for row in (None, 7, 'ab', b'ab', {}, range(2)):
            matrix = [[1], [2, 3], row]
            before = matrix[:]
            with self.subTest(row=row):
                with self.assertRaises(TypeError):
                    solution.spiral(matrix)
                for actual, original in zip(matrix, before):
                    self.assertIs(actual, original)
                self.assertEqual(matrix[:2], [[1], [2, 3]])



if __name__ == '__main__':
    unittest.main()
