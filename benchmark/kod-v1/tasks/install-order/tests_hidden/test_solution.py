import unittest
import solution


class InstallOrderTests(unittest.TestCase):
    def assert_error(self, data, message):
        with self.assertRaises(ValueError) as caught:
            solution.install_order(data)
        self.assertEqual(str(caught.exception), message)

    def test_empty_and_single(self):
        self.assertEqual(solution.install_order({}), [])
        self.assertEqual(solution.install_order({'only': ()}), ['only'])


    def test_newly_ready_preempts_old_ready(self):
        data = {'z': [], 'b': ['a'], 'a': []}
        self.assertEqual(solution.install_order(data), ['a', 'b', 'z'])


    def test_diamond_duplicates_and_tuple(self):
        data = {'top': ['left', 'right', 'left'], 'right': ('base', 'base'),
                'left': ['base'], 'base': []}
        self.assertEqual(solution.install_order(data), ['base', 'left', 'right', 'top'])


    def test_all_missing_pairs_sorted_and_deduplicated(self):
        self.assert_error({'z': ['q', 'b', 'q'], 'a': ('q', 'p'), 'ok': []},
                          'missing dependencies: a -> p; a -> q; z -> b; z -> q')


    def test_self_cycle(self):
        self.assert_error({'self': ['self', 'self']}, 'cycle blocks: self')


    def test_invalid_types(self):
        cases = [None, [], (), 'x', {1: []}, {'x': 'abc'}, {'x': {'a'}},
                 {'x': None}, {'x': [1]}, {'x': [None]}, {'x': [['a']]}]
        for data in cases:
            with self.subTest(data=data):
                with self.assertRaises(TypeError):
                    solution.install_order(data)

    def test_empty_names(self):
        for data in ({'': []}, {'x': ['']}, {'x': ('',)}):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    solution.install_order(data)

    def test_validation_precedes_graph_errors(self):
        with self.assertRaises(TypeError):
            solution.install_order({'missing': ['absent'], 'bad': [3]})
        with self.assertRaises(TypeError):
            solution.install_order({'cycle': ['cycle'], 'bad': {}})
        with self.assertRaises(ValueError) as caught:
            solution.install_order({'missing': ['absent'], 'bad': ['']})
        self.assertNotIn('missing dependencies:', str(caught.exception))


    def test_no_mutation_or_retained_state(self):
        deps = ['base', 'base']
        data = {'app': deps, 'base': []}
        for _ in range(2):
            self.assertEqual(solution.install_order(data), ['base', 'app'])
            self.assertEqual(data, {'app': ['base', 'base'], 'base': []})
            self.assertIs(data['app'], deps)
        self.assert_error({'x': ['absent', 'absent']},
                          'missing dependencies: x -> absent')
        cyclic = {'a': ['b'], 'b': ['a']}
        self.assert_error(cyclic, 'cycle blocks: a, b')
        self.assertEqual(cyclic, {'a': ['b'], 'b': ['a']})
        self.assertEqual(solution.install_order({'a': []}), ['a'])
        self.assertEqual(solution.install_order({}), [])


if __name__ == '__main__':
    unittest.main()
