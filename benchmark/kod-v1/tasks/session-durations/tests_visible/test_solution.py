import copy
import itertools
import unittest

import solution


class DurationsTests(unittest.TestCase):

    def test_interleaved_sessions_and_unmatched(self):
        events = [('b', 'logout', -5), ('a', 'login', 0),
                  ('b', 'login', 2), ('a', 'logout', 5),
                  ('a', 'login', 7), ('b', 'logout', 8),
                  ('a', 'logout', 11), ('b', 'login', 12),
                  ('c', 'logout', 20), ('d', 'login', 30)]
        self.assertEqual(solution.durations(events), {'a': 9, 'b': 6, 'c': 0, 'd': 0})


    def test_unsorted_independent_of_distinct_time_order(self):
        events = [('z', 'login', -4), ('a', 'login', -2),
                  ('z', 'logout', 3), ('a', 'logout', 6)]
        for permutation in itertools.permutations(events):
            with self.subTest(events=permutation):
                result = solution.durations(permutation)
                self.assertEqual(result, {'a': 8, 'z': 7})
                self.assertEqual(list(result), ['a', 'z'])



    def test_names_and_key_order(self):
        names = ['é', 'a', 'A', ' a ', ' ', 'ß']
        result = solution.durations([(name, 'logout', 1) for name in names])
        self.assertEqual(list(result), [' ', ' a ', 'A', 'a', 'ß', 'é'])
        self.assertEqual(result, dict.fromkeys(names, 0))




    def test_invalid_values_and_full_validation_without_mutation(self):
        invalid = [[], ['u'], ['u', 'login'], ['u', 'login', 0, 1],
                   ['', 'login', 0], ['u', 'LOGIN', 0],
                   ['u', 'logout ', 0], ['u', '', 0]]
        for record in invalid:
            events = [['u', 'logout', 9], ['u', 'login', 2], record]
            snapshot = copy.deepcopy(events)
            with self.subTest(record=record):
                with self.assertRaises(ValueError):
                    solution.durations(events)
                self.assertEqual(events, snapshot)
        events = [['u', 'login', 5], ['u', 'login', False]]
        snapshot = copy.deepcopy(events)
        with self.assertRaises(TypeError):
            solution.durations(events)
        self.assertEqual(events, snapshot)

    def test_bounded_action_sequences_against_run_oracle(self):
        # Each login run followed by a logout run forms one completed session;
        # only the first event in each run matters.
        for length in range(7):
            for actions in itertools.product(('login', 'logout'), repeat=length):
                runs = [(action, next(group)[0]) for action, group in
                        itertools.groupby(enumerate(actions), key=lambda item: item[1])]
                expected = sum(runs[i + 1][1] - start
                               for i, (action, start) in enumerate(runs[:-1])
                               if action == 'login')
                events = [('u', action, index) for index, action in enumerate(actions)]
                with self.subTest(actions=actions):
                    self.assertEqual(solution.durations(events[::-1]),
                                     {'u': expected} if events else {})


if __name__ == '__main__':
    unittest.main()
