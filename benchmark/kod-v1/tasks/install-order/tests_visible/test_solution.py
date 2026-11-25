import unittest
import solution


class InstallOrderTests(unittest.TestCase):
    def assert_error(self, data, message):
        with self.assertRaises(ValueError) as caught:
            solution.install_order(data)
        self.assertEqual(str(caught.exception), message)


    def test_chain(self):
        data = {'app': ['lib'], 'lib': ['base'], 'base': []}
        self.assertEqual(solution.install_order(data), ['base', 'lib', 'app'])


    def test_reconsider_after_every_installation(self):
        data = {'z': [], 'd': ['a'], 'a': [], 'b': ['a'], 'c': ['b']}
        self.assertEqual(solution.install_order(data), ['a', 'b', 'c', 'd', 'z'])


    def test_case_whitespace_and_insertion_order(self):
        data = {'a': [], 'Z': [], ' a': [], 'A': [], 'a ': []}
        expected = [' a', 'A', 'Z', 'a', 'a ']
        self.assertEqual(solution.install_order(data), expected)
        self.assertEqual(solution.install_order(dict(reversed(list(data.items())))), expected)
        self.assert_error({' x': ['x']}, 'missing dependencies:  x -> x')


    def test_missing_takes_precedence_over_cycle(self):
        self.assert_error({'a': ['a'], 'b': ['unknown']},
                          'missing dependencies: b -> unknown')


    def test_cycles_and_blocked_descendants(self):
        data = {'free': [], 'a': ['b'], 'b': ['a'], 'c': ['b', 'free'],
                'd': ['c'], 'e': ['e'], 'ok': ['free']}
        self.assert_error(data, 'cycle blocks: a, b, c, d, e')




    def test_subclasses_accepted(self):
        class Packages(dict):
            pass

        class Dependencies(list):
            pass

        class Names(str):
            pass

        class TupleDependencies(tuple):
            pass

        data = Packages({Names('app'): Dependencies(['base']),
                         'base': TupleDependencies()})
        self.assertEqual(solution.install_order(data), ['base', 'app'])



if __name__ == '__main__':
    unittest.main()
