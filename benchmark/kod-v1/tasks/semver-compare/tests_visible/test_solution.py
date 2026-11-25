import unittest

import solution


class CompareTests(unittest.TestCase):
    def assert_order(self, lower, higher):
        self.assertIs(type(solution.compare(lower, higher)), int)
        self.assertEqual(solution.compare(lower, higher), -1)
        self.assertEqual(solution.compare(higher, lower), 1)
        self.assertEqual(solution.compare(lower, lower), 0)
        self.assertEqual(solution.compare(higher, higher), 0)




    def test_numeric_before_nonnumeric(self):
        for a, b in [('999', '-'), ('0', '0a'), ('10', '2a'),
                     ('alpha.9', 'alpha.-1')]:
            with self.subTest(a=a, b=b):
                self.assert_order('1.0.0-' + a, '1.0.0-' + b)



    def test_build_metadata_is_ignored(self):
        for base in ['0.0.0', '1.2.3-alpha.0', '10.20.30--']:
            variants = [base, base + '+001', base + '+x.Y.000.-',
                        base + '+different-build']
            for a in variants:
                for b in variants:
                    with self.subTest(a=a, b=b):
                        self.assertEqual(solution.compare(a, b), 0)
        self.assert_order('1.2.3-a+z', '1.2.3-b+a')
        self.assert_order('1.2.3+z', '1.2.4+a')

    def test_unbounded_numeric_values(self):
        large = '9' * 5000
        larger = '1' + '0' * 5000
        self.assert_order(large + '.0.0', larger + '.0.0')
        self.assert_order('0.' + large + '.0', '0.' + larger + '.0')
        self.assert_order('0.0.' + large, '0.0.' + larger)
        self.assert_order('1.0.0-' + large, '1.0.0-' + larger)
        self.assertEqual(solution.compare('1.0.0+' + large,
                                          '1.0.0+' + larger), 0)

    def test_invalid_core(self):
        invalid = ['', '1', '1.2', '1.2.3.4', '.1.2', '1..2',
                   '01.2.3', '1.02.3', '1.2.03', '-1.2.3',
                   '+1.2.3', 'v1.2.3', '1.2.a', ' 1.2.3',
                   '1.2.3 ', '1.2.3\n', '1.2.3\x00',
                   '١.2.3', '1.２.3']
        self.assert_invalid_versions(invalid)


    def assert_invalid_versions(self, versions):
        for bad in versions:
            for a, b in [(bad, '999.0.0'), ('0.0.0', bad), (bad, bad)]:
                with self.subTest(a=a, b=b):
                    with self.assertRaises(ValueError):
                        solution.compare(a, b)


    def test_repeated_calls(self):
        for _ in range(3):
            self.assertEqual(solution.compare('1.2.3', '1.2.3+0'), 0)
            self.assert_order('1.2.3-a', '1.2.3-b')
            with self.assertRaises(ValueError):
                solution.compare('1.2.3-01', '1.2.3')
            self.assert_order('2.0.0', '3.0.0')


if __name__ == '__main__':
    unittest.main()
