import unittest
from copy import deepcopy

import solution


def container_ids(value):
    if not isinstance(value, (dict, list)):
        return set()
    found = {id(value)}
    children = value.values() if isinstance(value, dict) else value
    for child in children:
        found.update(container_ids(child))
    return found


class DeepMergeTests(unittest.TestCase):
    def checked_merge(self, base, override, expected):
        before_base, before_override = deepcopy(base), deepcopy(override)
        result = solution.deep_merge(base, override)
        self.assertIs(type(result), dict)
        self.assertEqual(result, expected)
        self.assertEqual(base, before_base)
        self.assertEqual(override, before_override)
        self.assertFalse(container_ids(result) &
                         (container_ids(base) | container_ids(override)))
        return result

    def test_empty_and_disjoint(self):
        self.checked_merge({}, {}, {})
        self.checked_merge({'a': {'b': [1]}}, {}, {'a': {'b': [1]}})
        self.checked_merge({}, {'a': {'b': [1]}}, {'a': {'b': [1]}})
        self.checked_merge({'a': 1}, {'b': 2}, {'a': 1, 'b': 2})

    def test_recursive_merge(self):
        self.checked_merge(
            {'cfg': {'db': {'host': 'old', 'port': 12}, 'keep': True}, 'x': 1},
            {'cfg': {'db': {'host': 'new', 'tls': True}, 'extra': None}},
            {'cfg': {'db': {'host': 'new', 'port': 12, 'tls': True},
                     'keep': True, 'extra': None}, 'x': 1})

    def test_lists_are_atomic(self):
        self.checked_merge(
            {'a': [{'old': 1}, 2], 'b': [1, 2]},
            {'a': [{'new': [3]}], 'b': []},
            {'a': [{'new': [3]}], 'b': []})

    def test_type_changes(self):
        self.checked_merge(
            {'a': {'old': 1}, 'b': [1], 'c': None, 'd': {'x': 2}, 'e': 4},
            {'a': [2], 'b': {'new': [3]}, 'c': {'z': {}}, 'd': 0, 'e': {}},
            {'a': [2], 'b': {'new': [3]}, 'c': {'z': {}}, 'd': 0, 'e': {}})



    def test_base_only_nested_containers(self):
        base = {'a': [{'b': [[1]]}], 'cfg': {'keep': {'x': []}}}
        result = self.checked_merge(base, {'cfg': {'new': 2}},
                                    {'a': [{'b': [[1]]}],
                                     'cfg': {'keep': {'x': []}, 'new': 2}})
        result['a'][0]['b'][0].append(2)
        self.assertEqual(base['a'][0]['b'], [[1]])
        base['cfg']['keep']['x'].append(9)
        self.assertEqual(result['cfg']['keep']['x'], [])

    def test_override_mutation_does_not_leak(self):
        base = {'x': [0]}
        override = {'x': [{'inside': [1]}], 'new': {'nested': []}}
        expected = deepcopy(override)
        result = solution.deep_merge(base, override)
        override['x'][0]['inside'].append(2)
        override['new']['nested'].append(3)
        self.assertEqual(result, expected)
        self.assertEqual(base, {'x': [0]})

    def test_result_mutation_does_not_leak(self):
        override = {'x': [{'inside': [1]}], 'new': {'nested': []}}
        snapshot = deepcopy(override)
        result = solution.deep_merge({'x': None}, override)
        result['x'][0]['inside'].append(2)
        result['new']['nested'].append(3)
        self.assertEqual(override, snapshot)




if __name__ == '__main__':
    unittest.main()
