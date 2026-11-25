import unittest

import solution


class FreeSlotsTests(unittest.TestCase):
    def test_empty_busy_and_inclusive_threshold(self):
        self.assertEqual(solution.free_slots([], 5, 15, 10), [(5, 15)])
        self.assertEqual(solution.free_slots([], 5, 15, 11), [])
        self.assertEqual(solution.free_slots([], 5, 5, 1), [])


    def test_nested_busy_does_not_move_coverage_backwards(self):
        self.assertEqual(
            solution.free_slots([(3, 18), (5, 7), (10, 12), (20, 22)], 0, 25, 2),
            [(0, 3), (18, 20), (22, 25)],
        )


    def test_touching_and_overlap_chain(self):
        self.assertEqual(
            solution.free_slots([(8, 12), (2, 5), (5, 9), (11, 16)], 0, 20, 1),
            [(0, 2), (16, 20)],
        )


    def test_empty_reversed_and_boundary_intervals(self):
        self.assertEqual(
            solution.free_slots([(3, 3), (8, 2), (-5, 0), (10, 15)], 0, 10, 1),
            [(0, 10)],
        )





if __name__ == '__main__':
    unittest.main()
