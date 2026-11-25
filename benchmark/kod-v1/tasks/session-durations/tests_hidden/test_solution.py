import copy
import itertools
import unittest

import solution


class DurationsTests(unittest.TestCase):
    def test_empty_and_fresh_result(self):
        first = solution.durations([])
        second = solution.durations(())
        self.assertEqual(first, {})
        self.assertIs(type(first), dict)
        self.assertIsNot(first, second)
        first['x'] = 1
        self.assertEqual(second, {})


    def test_repeated_login_keeps_first_start(self):
        self.assertEqual(solution.durations([
            ('u', 'login', 1), ('u', 'login', 4), ('u', 'login', 8),
            ('u', 'logout', 10), ('u', 'logout', 13),
            ('u', 'login', 20), ('u', 'logout', 25)]), {'u': 14})


    def test_ties_preserve_original_order(self):
        prefix = [('u', 'login', 0)]
        self.assertEqual(solution.durations(prefix + [
            ('u', 'logout', 5), ('u', 'login', 5), ('u', 'logout', 9)]), {'u': 9})
        self.assertEqual(solution.durations(prefix + [
            ('u', 'login', 5), ('u', 'logout', 5), ('u', 'logout', 9)]), {'u': 5})
        self.assertEqual(solution.durations([
            ('u', 'logout', 5), ('u', 'login', 5), ('u', 'logout', 8)]), {'u': 3})
        self.assertEqual(solution.durations([
            ('u', 'login', 5), ('u', 'logout', 5), ('u', 'logout', 8)]), {'u': 0})

    def test_zero_negative_and_large_timestamps(self):
        big = 10 ** 100
        result = solution.durations([
            ('zero', 'login', 0), ('zero', 'logout', 0),
            ('huge', 'logout', big), ('huge', 'login', -big),
            ('neg', 'login', -9), ('neg', 'logout', -2)])
        self.assertEqual(result, {'huge': 2 * big, 'neg': 7, 'zero': 0})
        for value in result.values():
            self.assertIs(type(value), int)


    def test_input_unchanged_and_result_not_shared(self):
        events = [['u', 'logout', 10], ['u', 'login', 2]]
        snapshot = copy.deepcopy(events)
        records = list(events)
        result = solution.durations(events)
        self.assertEqual(events, snapshot)
        for original, current in zip(records, events):
            self.assertIs(original, current)
        self.assertEqual(result, {'u': 8})
        result['u'] = -1
        self.assertEqual(solution.durations(events), {'u': 8})
        self.assertEqual(events, snapshot)

    def test_invalid_container_types(self):
        class ListSubclass(list):
            pass
        for events in (None, {}, 'abc', iter([]), ListSubclass()):
            with self.subTest(events=type(events)):
                with self.assertRaises(TypeError):
                    solution.durations(events)
        for record in (None, {}, 'abc', ListSubclass(['u', 'login', 0])):
            with self.subTest(record=type(record)):
                with self.assertRaises(TypeError):
                    solution.durations([record])

    def test_invalid_field_types(self):
        class IntSubclass(int):
            pass
        class StrSubclass(str):
            pass
        records = [(1, 'login', 0), (None, 'login', 0),
                   ('u', None, 0), ('u', 1, 0), ('u', 'login', True),
                   ('u', 'login', 1.0), ('u', 'login', '1'),
                   ('u', 'login', IntSubclass(1)),
                   (StrSubclass('u'), 'login', 0),
                   ('u', StrSubclass('login'), 0)]
        for record in records:
            with self.subTest(record=record):
                with self.assertRaises(TypeError):
                    solution.durations([record])




if __name__ == '__main__':
    unittest.main()
