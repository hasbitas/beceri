import unittest

import solution


class RotationTests(unittest.TestCase):
    def test_explicit_rectangle_turns(self):
        matrix = [[1, 2, 3], [4, 5, 6]]
        cases = {
            0: [[1, 2, 3], [4, 5, 6]],
            1: [[4, 1], [5, 2], [6, 3]],
            2: [[6, 5, 4], [3, 2, 1]],
            3: [[3, 6], [2, 5], [1, 4]],
            -1: [[3, 6], [2, 5], [1, 4]],
            -2: [[6, 5, 4], [3, 2, 1]],
            -3: [[4, 1], [5, 2], [6, 3]],
        }
        for k, expected in cases.items():
            with self.subTest(k=k):
                self.assertEqual(solution.rotate(matrix, k), expected)
                self.assertEqual(matrix, [[1, 2, 3], [4, 5, 6]])



    def test_empty_matrices(self):
        for matrix in ([], (), [[]], ((),), [[], (), []]):
            for k in (0, 1, -1, 2, 10 ** 80):
                with self.subTest(matrix=matrix, k=k):
                    first = solution.rotate(matrix, k)
                    second = solution.rotate(matrix, k)
                    self.assertEqual(first, [])
                    self.assertIs(type(first), list)
                    self.assertIsNot(first, matrix)
                    self.assertIsNot(first, second)

    def test_tuple_inputs_and_integer_subclass(self):
        class Count(int):
            pass
        matrix = ((1, 2), [3, 4], (5, 6))
        result = solution.rotate(matrix, Count(1))
        self.assertEqual(result, [[5, 3, 1], [6, 4, 2]])
        self.assertIs(type(result), list)
        for row in result:
            self.assertIs(type(row), list)
        self.assertEqual(matrix, ((1, 2), [3, 4], (5, 6)))

    def test_identity_and_fresh_structure(self):
        a, b = object(), {"mutable": []}
        shared = [a, b]
        matrix = [shared, shared]
        for k in (0, 1, 2, 3, 4, -1):
            with self.subTest(k=k):
                first = solution.rotate(matrix, k)
                second = solution.rotate(matrix, k)
                self.assertIsNot(first, matrix)
                self.assertIsNot(first, second)
                rows = first + second
                self.assertEqual(len({id(row) for row in rows}), len(rows))
                for row in rows:
                    self.assertIs(type(row), list)
                    self.assertIsNot(row, shared)
                    self.assertIsNot(row, matrix)
                    for cell in row:
                        self.assertTrue(cell is a or cell is b)
                self.assertEqual(sum(cell is a for row in first for cell in row), 2)
                first[0].append("new")
                self.assertEqual(len(shared), 2)
                self.assertEqual(len(first[1]), 2)
                self.assertIs(matrix[0], shared)
                self.assertIs(matrix[1], shared)
                self.assertIs(shared[0], a)
                self.assertIs(shared[1], b)


    def test_invalid_containers(self):
        for matrix in (None, 42, "12", {0: [1]}, {1, 2},
                       ["12"], [[1], None], [[1], {2}], [[], [], 3]):
            for k in (0, 1, -4):
                with self.subTest(matrix=matrix, k=k):
                    with self.assertRaises(TypeError):
                        solution.rotate(matrix, k)
        with self.assertRaises(TypeError):
            solution.rotate(iter([[1]]), 1)
        # Row types take precedence even after a ragged prefix.
        with self.assertRaises(TypeError):
            solution.rotate([[1], [], "bad"], 0)



if __name__ == "__main__":
    unittest.main()
