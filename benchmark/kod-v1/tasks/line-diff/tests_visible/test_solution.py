import itertools
import unittest

import solution


def exhaustive_script(old, new):
    """Enumerate scripts, then rank by matches and operation precedence."""
    def scripts(i, j):
        if i == len(old) and j == len(new):
            yield ()
            return
        if i < len(old) and j < len(new) and old[i] == new[j]:
            for rest in scripts(i + 1, j + 1):
                yield (('=', old[i]),) + rest
        if i < len(old):
            for rest in scripts(i + 1, j):
                yield (('-', old[i]),) + rest
        if j < len(new):
            for rest in scripts(i, j + 1):
                yield (('+', new[j]),) + rest
    ranks = {'=': 0, '-': 1, '+': 2}
    return list(min(scripts(0, 0), key=lambda s: (
        -sum(op == '=' for op, line in s),
        tuple(ranks[op] for op, line in s),
    )))


class DiffTests(unittest.TestCase):
    def test_empty_and_one_sided(self):
        self.assertEqual(solution.diff([], ()), [])
        self.assertEqual(solution.diff([], ['x', '', 'x']),
                         [('+', 'x'), ('+', ''), ('+', 'x')])
        self.assertEqual(solution.diff(('a', 'b'), []),
                         [('-', 'a'), ('-', 'b')])

    def test_unchanged_and_output_shape(self):
        lines = ['same', '', 'same', 'last\n']
        result = solution.diff(lines, tuple(lines))
        self.assertIs(type(result), list)
        self.assertEqual(result, [('=', line) for line in lines])
        for entry in result:
            self.assertIs(type(entry), tuple)
            self.assertEqual(len(entry), 2)

    def test_disjoint_and_replacement_order(self):
        self.assertEqual(solution.diff(['a', 'b'], ['x', 'y']),
                         [('-', 'a'), ('-', 'b'), ('+', 'x'), ('+', 'y')])
        self.assertEqual(solution.diff(['start', 'old', 'end'],
                                       ['start', 'new', 'end']),
                         [('=', 'start'), ('-', 'old'), ('+', 'new'), ('=', 'end')])





    def test_inputs_and_results_are_independent(self):
        old, new = ['b', 'a', 'a'], ['a', 'a', 'c']
        before_old, before_new = old[:], new[:]
        first = solution.diff(old, new)
        second = solution.diff(old, new)
        self.assertEqual(old, before_old)
        self.assertEqual(new, before_new)
        self.assertIsNot(first, second)
        saved = second[:]
        first.append(('+', 'extra'))
        self.assertEqual(second, saved)
        old.append('later')
        new.clear()
        self.assertEqual(second, saved)
        empty_a = solution.diff([], [])
        empty_b = solution.diff([], [])
        self.assertIsNot(empty_a, empty_b)



if __name__ == '__main__':
    unittest.main()
