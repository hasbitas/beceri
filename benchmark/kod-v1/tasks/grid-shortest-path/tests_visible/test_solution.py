import unittest
import solution


class ShortestTests(unittest.TestCase):

    def test_detour(self):
        grid = ['.#...', '.#.#.', '...#.']
        self.assertEqual(solution.shortest(grid, (0, 0), (2, 4)), 10)
        self.assertEqual(solution.shortest(grid, (2, 4), (0, 0)), 10)



    def test_wall_endpoints(self):
        for start, goal in [((0, 0), (0, 0)), ((0, 0), (0, 1)),
                            ((0, 1), (0, 0))]:
            with self.subTest(start=start, goal=goal):
                self.assertEqual(solution.shortest(['#.'], start, goal), -1)

    def test_container_types_and_no_mutation(self):
        grid, start, goal = ['...', '.#.', '...'], [0, 0], [2, 2]
        before = (grid[:], start[:], goal[:])
        self.assertEqual(solution.shortest(grid, start, goal), 4)
        self.assertEqual((grid, start, goal), before)
        self.assertEqual(solution.shortest(tuple(grid), (0, 0), goal), 4)
        self.assertEqual(solution.shortest(grid, start, goal), 4)


    def test_invalid_coordinates(self):
        points = [None, 0, '00', {0: 0, 1: 0}, (), (0,), (0, 0, 0),
                  (False, 0), (0, True), (0.0, 0), (0, 0.0),
                  ('0', 0), (None, 0), (-1, 0), (0, -1), (2, 0), (0, 3)]
        for point in points:
            for invalid_start in (True, False):
                with self.subTest(point=point, invalid_start=invalid_start):
                    start, goal = (point, (0, 0)) if invalid_start else ((0, 0), point)
                    with self.assertRaises(ValueError):
                        solution.shortest(['#..', '...'], start, goal)



if __name__ == '__main__':
    unittest.main()
