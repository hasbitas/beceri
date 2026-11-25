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



    def test_crossing_matches_and_duplicate_alignment(self):
        self.assertEqual(solution.diff(['a', 'b'], ['b', 'a']),
                         [('-', 'a'), ('=', 'b'), ('+', 'a')])
        self.assertEqual(solution.diff(['a', 'a', 'b'], ['a', 'b', 'a']),
                         [('=', 'a'), ('-', 'a'), ('=', 'b'), ('+', 'a')])
        self.assertEqual(solution.diff(['x', 'a', 'b'], ['a', 'b', 'x']),
                         [('-', 'x'), ('=', 'a'), ('=', 'b'), ('+', 'x')])
        self.assertEqual(solution.diff(['a', 'b', 'x'], ['x', 'a', 'b']),
                         [('+', 'x'), ('=', 'a'), ('=', 'b'), ('-', 'x')])

    def test_lines_are_opaque(self):
        cases = [(['a\n'], ['a']), ([' a'], ['a ']),
                 (['é'], ['e\u0301']), (['A'], ['a']),
                 (['one\ntwo', '\r\n', '\x00'], ['one', 'two', '\n', '\x00'])]
        for old, new in cases:
            with self.subTest(old=old, new=new):
                self.assertEqual(solution.diff(old, new), exhaustive_script(old, new))

    def test_invalid_containers(self):
        for bad in (None, 'abc', b'abc', 12, {'a': 1}, {'a'}, iter(['a'])):
            for old, new in ((bad, []), ([], bad)):
                with self.subTest(old=old, new=new):
                    with self.assertRaises(TypeError):
                        solution.diff(old, new)

    def test_invalid_elements_even_with_empty_peer(self):
        for bad in (None, 1, False, b'a', [], ('x',)):
            for old, new in ((['valid', bad], []), ([], ('valid', bad)),
                             (['a'], ['a', bad]), (['a', bad], ['a'])):
                with self.subTest(old=old, new=new):
                    before_old, before_new = list(old), list(new)
                    with self.assertRaises(TypeError):
                        solution.diff(old, new)
                    self.assertEqual(list(old), before_old)
                    self.assertEqual(list(new), before_new)


    def test_exhaustive_small_sequences(self):
        sequences = [seq for length in range(4)
                     for seq in itertools.product(('a', 'b'), repeat=length)]
        for old in sequences:
            for new in sequences:
                with self.subTest(old=old, new=new):
                    actual = solution.diff(old, list(new))
                    self.assertEqual(actual, exhaustive_script(old, new))
                    self.assertEqual([line for op, line in actual if op != '+'], list(old))
                    self.assertEqual([line for op, line in actual if op != '-'], list(new))


if __name__ == '__main__':
    unittest.main()
