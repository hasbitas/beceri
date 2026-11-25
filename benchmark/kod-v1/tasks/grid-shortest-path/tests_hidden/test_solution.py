import unittest
import solution


class ShortestTests(unittest.TestCase):
    def test_move_counts(self):
        for grid, start, goal, expected in [
            (['.'], (0, 0), (0, 0), 0),
            (['..'], (0, 0), (0, 1), 1),
            (['.....'], (0, 4), (0, 0), 4),
            (['.', '.', '.', '.'], (3, 0), (0, 0), 3),
            (['....', '....', '....'], (0, 0), (2, 3), 5),
        ]:
            with self.subTest(grid=grid, start=start):
                self.assertEqual(solution.shortest(grid, start, goal), expected)


    def test_shortest_among_multiple_routes(self):
        grid = ['.....', '.....', '.....', '.....']
        self.assertEqual(solution.shortest(grid, (0, 0), (3, 0)), 3)
        self.assertEqual(solution.shortest(grid, (3, 4), (0, 4)), 3)

    def test_unreachable_and_no_diagonal_or_wrap(self):
        for grid, start, goal in [
            (['.#', '#.'], (0, 0), (1, 1)),
            (['.#.'], (0, 0), (0, 2)),
            (['.', '#', '.'], (0, 0), (2, 0)),
            (['...', '###', '...'], (0, 0), (2, 2)),
        ]:
            with self.subTest(grid=grid):
                self.assertEqual(solution.shortest(grid, start, goal), -1)



    def test_invalid_grids(self):
        grids = [None, 4, '.', {'a': '.'}, [], (), [''], ['', ''],
                 ['..', '.'], ['.', '..'], ['.', None], [1],
                 ['.x'], [' '], ['.\n'], ['.', '#x'], [['.']]]
        for grid in grids:
            with self.subTest(grid=grid):
                with self.assertRaises(ValueError):
                    solution.shortest(grid, (0, 0), (0, 0))


    def test_validation_before_early_returns(self):
        for grid, start, goal in [
            (['#', 'x'], (0, 0), (0, 0)),
            (['.', '..'], (0, 0), (0, 0)),
            (['#'], (0, 0), (0, 1)),
            (['#'], (False, 0), (0, 0)),
        ]:
            with self.subTest(grid=grid, start=start, goal=goal):
                with self.assertRaises(ValueError):
                    solution.shortest(grid, start, goal)


if __name__ == '__main__':
    unittest.main()
