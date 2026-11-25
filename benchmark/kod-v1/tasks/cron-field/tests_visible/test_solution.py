import unittest
import solution


class CronFieldTests(unittest.TestCase):




    def test_invalid_syntax(self):
        bad = ['', ',', ',1', '1,', '1,,2', ' ', ' 1', '1 ', '1\n',
               '1\t', '\u00a01', '1 -2', '1- 2', '* /2', '1/2',
               '*/', '/2', '**', '1--2', '-1', '+1', '1.0', '1e0',
               '1_0', '1-2-3', '*/2/3', '1-3/', '1-3/+2', '*/0',
               '1-3/000', '*/-2', '?', 'MON', 'L', '1#2', '١', '１',
               '*/٢', '1-３', '*,bad']
        for field in bad:
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    solution.expand(field, 0, 10)


    def test_invalid_types(self):
        for field in [None, 1, b'*', ['*'], True]:
            with self.subTest(field=field):
                with self.assertRaises(TypeError):
                    solution.expand(field, 0, 9)
        for bad in [None, '3', 3.0, True, False, [], complex(3)]:
            for lo, hi in [(bad, 9), (0, bad)]:
                with self.subTest(low=lo, high=hi):
                    with self.assertRaises(TypeError):
                        solution.expand('*', lo, hi)

    def test_long_numerals(self):
        zeros = '0' * 5000
        self.assertEqual(solution.expand(zeros + '3', 0, 9), [3])
        self.assertEqual(solution.expand('2-8/' + zeros + '3', 0, 9), [2, 5, 8])
        self.assertEqual(solution.expand('*/1' + zeros, 2, 8), [2])
        with self.assertRaises(ValueError):
            solution.expand('1' + zeros, 0, 9)

    def test_fresh_integer_list(self):
        first = solution.expand('3,1,3', 0, 9)
        second = solution.expand('3,1,3', 0, 9)
        self.assertIs(type(first), list)
        self.assertTrue(all(type(n) is int for n in first))
        self.assertIsNot(first, second)
        first.append(99)
        self.assertEqual(second, [1, 3])
        self.assertEqual(solution.expand('3,1,3', 0, 9), [1, 3])


if __name__ == '__main__':
    unittest.main()
