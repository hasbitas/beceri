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





    def test_falsey_overrides(self):
        for replacement in (None, False, 0, 0.0, '', [], {}):
            with self.subTest(replacement=replacement):
                self.checked_merge({'x': 'old'}, {'x': replacement},
                                   {'x': replacement})
        self.checked_merge({'x': {'keep': 1}}, {'x': {}}, {'x': {'keep': 1}})
        self.checked_merge({'x': 4}, {'x': True}, {'x': True})
        self.checked_merge({'x': 4}, {'x': 2.5}, {'x': 2.5})

    def test_insertion_order(self):
        result = self.checked_merge(
            {'z': 0, 'a': {'q': 1, 'b': 2}, 'm': 3},
            {'m': 4, 'a': {'b': 5, 'c': 6, 'aa': 7}, 'y': 8,
             'b': {'z': 1, 'a': 2}},
            {'z': 0, 'a': {'q': 1, 'b': 5, 'c': 6, 'aa': 7},
             'm': 4, 'y': 8, 'b': {'z': 1, 'a': 2}})
        self.assertEqual(list(result), ['z', 'a', 'm', 'y', 'b'])
        self.assertEqual(list(result['a']), ['q', 'b', 'c', 'aa'])
        self.assertEqual(list(result['b']), ['z', 'a'])




    def test_shared_objects_and_same_argument(self):
        shared = {'items': [{'n': []}]}
        base = {'a': shared, 'b': shared}
        override = {'a': {'extra': 1}, 'c': shared}
        self.checked_merge(base, override,
                           {'a': {'items': [{'n': []}], 'extra': 1},
                            'b': {'items': [{'n': []}]},
                            'c': {'items': [{'n': []}]}})
        self.checked_merge(base, base, base)

    def test_empty_string_keys_and_deep_nesting(self):
        self.checked_merge(
            {'': {'': {'keep': [[], {'': None}], 'change': 1}}},
            {'': {'': {'change': False, 'added': {'': []}}}},
            {'': {'': {'keep': [[], {'': None}], 'change': False,
                       'added': {'': []}}}})


if __name__ == '__main__':
    unittest.main()
