import unittest

import solution


class FreeSlotsTests(unittest.TestCase):

    def test_unsorted_and_maximal_gaps(self):
        self.assertEqual(
            solution.free_slots([(25, 30), (10, 15), (20, 22)], 0, 40, 5),
            [(0, 10), (15, 20), (30, 40)],
        )


    def test_same_start_and_duplicates(self):
        self.assertEqual(
            solution.free_slots([(2, 16), (2, 8), (2, 16), (4, 6)], 0, 20, 1),
            [(0, 2), (16, 20)],
        )


    def test_clipping_and_outside_intervals(self):
        self.assertEqual(
            solution.free_slots([(-20, -2), (-5, 3), (7, 12), (15, 20)], 0, 10, 1),
            [(3, 7)],
        )
        self.assertEqual(solution.free_slots([(-50, 50), (2, 4)], 0, 10, 1), [])
        self.assertEqual(solution.free_slots([(0, 3)], 2, 2, 1), [])


    def test_negative_times_and_iterator(self):
        busy = ((a, b) for a, b in [(-8, -5), (-15, -12), (-4, -2)])
        self.assertEqual(
            solution.free_slots(busy, -20, 0, 2),
            [(-20, -15), (-12, -8), (-2, 0)],
        )

    def test_short_busy_still_separates_free_intervals(self):
        self.assertEqual(solution.free_slots([(4, 5)], 0, 9, 5), [])
        self.assertEqual(solution.free_slots([(4, 5)], 0, 9, 4), [(0, 4), (5, 9)])

    def test_input_not_mutated_and_calls_independent(self):
        busy = [[8, 10], [2, 4], [3, 3]]
        original = [pair[:] for pair in busy]
        self.assertEqual(solution.free_slots(busy, 0, 12, 2), [(0, 2), (4, 8), (10, 12)])
        self.assertEqual(busy, original)
        self.assertEqual(solution.free_slots([], 0, 3, 1), [(0, 3)])
        self.assertEqual(solution.free_slots(busy, 0, 12, 2), [(0, 2), (4, 8), (10, 12)])


if __name__ == '__main__':
    unittest.main()
