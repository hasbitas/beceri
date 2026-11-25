import unittest

import solution


class CompareTests(unittest.TestCase):
    def assert_order(self, lower, higher):
        self.assertIs(type(solution.compare(lower, higher)), int)
        self.assertEqual(solution.compare(lower, higher), -1)
        self.assertEqual(solution.compare(higher, lower), 1)
        self.assertEqual(solution.compare(lower, lower), 0)
        self.assertEqual(solution.compare(higher, higher), 0)

    def test_core_components(self):
        for a, b in [
            ('0.0.0', '0.0.1'), ('1.2.9', '1.2.10'),
            ('1.9.99', '1.10.0'), ('9.99.99', '10.0.0'),
            ('1.99.99', '2.0.0-alpha'), ('0.0.0', '1.0.0'),
        ]:
            with self.subTest(a=a, b=b):
                self.assert_order(a, b)

    def test_standard_prerelease_chain(self):
        chain = ['alpha', 'alpha.1', 'alpha.beta', 'beta', 'beta.2',
                 'beta.11', 'rc.1']
        versions = ['1.0.0-' + item for item in chain] + ['1.0.0']
        for i, a in enumerate(versions):
            for b in versions[i + 1:]:
                with self.subTest(a=a, b=b):
                    self.assert_order(a, b)

    def test_numeric_prerelease_comparison(self):
        for a, b in [('2', '10'), ('9', '100'), ('99', '101'),
                     ('alpha.9', 'alpha.10'), ('0', '1')]:
            with self.subTest(a=a, b=b):
                self.assert_order('3.2.1-' + a, '3.2.1-' + b)


    def test_ascii_lexical_order(self):
        for a, b in [('-', 'A'), ('A', 'Z'), ('Z', 'a'),
                     ('a', 'a-'), ('a-10', 'a-2'), ('01a', '1a')]:
            with self.subTest(a=a, b=b):
                self.assert_order('1.0.0-' + a, '1.0.0-' + b)

    def test_prefix_and_release(self):
        self.assert_order('1.0.0-a', '1.0.0-a.0')
        self.assert_order('1.0.0-a.0', '1.0.0-a.0.0')
        self.assert_order('1.0.0-0', '1.0.0')
        self.assert_order('1.0.0-z.z.z+build', '1.0.0+000')




    def test_invalid_optional_identifiers(self):
        self.assert_invalid_versions([
            '1.2.3-', '1.2.3+', '1.2.3-a+', '1.2.3-.a',
            '1.2.3-a.', '1.2.3-a..b', '1.2.3+.a', '1.2.3+a.',
            '1.2.3+a..b', '1.2.3-a+b+c', '1.2.3-00',
            '1.2.3-a.01', '1.2.3-01+valid', '1.2.3-a_b',
            '1.2.3+a_b', '1.2.3-é', '1.2.3+é', '1.2.3-١',
            '1.2.3+１', '1.2.3-a b', '1.2.3+a\nb',
        ])

    def assert_invalid_versions(self, versions):
        for bad in versions:
            for a, b in [(bad, '999.0.0'), ('0.0.0', bad), (bad, bad)]:
                with self.subTest(a=a, b=b):
                    with self.assertRaises(ValueError):
                        solution.compare(a, b)

    def test_argument_types_and_error_priority(self):
        for value in [None, 1, 1.2, b'1.2.3', [], {}, True]:
            for a, b in [(value, '1.2.3'), ('1.2.3', value),
                         (value, 'invalid'), ('invalid', value)]:
                with self.subTest(a=a, b=b):
                    with self.assertRaises(TypeError):
                        solution.compare(a, b)



if __name__ == '__main__':
    unittest.main()
