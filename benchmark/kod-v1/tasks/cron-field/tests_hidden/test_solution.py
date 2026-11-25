import unittest
import solution


class CronFieldTests(unittest.TestCase):
    def test_basic_items(self):
        for field, lo, hi, expected in [
            ('*/15', 0, 59, [0, 15, 30, 45]),
            ('1-5', 0, 9, [1, 2, 3, 4, 5]),
            ('1,3', 0, 9, [1, 3]),
            ('2-10/3', 0, 12, [2, 5, 8]),
            ('*', 4, 7, [4, 5, 6, 7]),
            ('0003', 0, 9, [3]),
        ]:
            with self.subTest(field=field):
                self.assertEqual(solution.expand(field, lo, hi), expected)

    def test_union_and_order(self):
        for field in ['9,2-8/3,5,2,7-9', '7-9,2,5,2-8/3,9']:
            self.assertEqual(solution.expand(field, 0, 12), [2, 5, 7, 8, 9])
        self.assertEqual(solution.expand('*,2,1-3,*/2', 1, 5), [1, 2, 3, 4, 5])

    def test_boundaries_and_steps(self):
        cases = [('*', 0, 0, [0]), ('*/3', 4, 11, [4, 7, 10]),
                 ('4-4/9', 4, 4, [4]), ('3-8/99', 0, 9, [3]),
                 ('3-9/3', 3, 9, [3, 6, 9]),
                 ('03-09/003', 0, 9, [3, 6, 9]),
                 ('*/99', 4, 8, [4])]
        for field, lo, hi, expected in cases:
            with self.subTest(field=field, low=lo):
                self.assertEqual(solution.expand(field, lo, hi), expected)

    def test_small_intervals_exhaustively(self):
        for low in range(4):
            high = low + 5
            for start in range(low, high + 1):
                for end in range(start, high + 1):
                    for step in range(1, 8):
                        expected = [n for n in range(low, high + 1)
                                    if start <= n <= end and (n - start) % step == 0]
                        with self.subTest(start=start, end=end, step=step, low=low):
                            self.assertEqual(solution.expand(
                                f'{start}-{end}/{step}', low, high), expected)


    def test_invalid_values(self):
        for field in ['2', '10', '2-5', '4-10', '8-4', '4,10',
                      '*,2', '4-10/99', '8-4/2']:
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    solution.expand(field, 3, 9)
        for lo, hi in [(-1, 5), (5, 4), (-5, -1)]:
            with self.subTest(low=lo, high=hi):
                with self.assertRaises(ValueError):
                    solution.expand('*', lo, hi)





if __name__ == '__main__':
    unittest.main()
