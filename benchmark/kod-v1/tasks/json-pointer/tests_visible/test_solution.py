import copy
import itertools
import unittest

import solution


class ResolveTests(unittest.TestCase):


    def test_empty_tokens_are_keys(self):
        leaf = ['leaf']
        doc = {'': {'': leaf}, 'a': {'': {'b': 42}}}
        self.assertIs(solution.resolve(doc, '/'), doc[''])
        self.assertIs(solution.resolve(doc, '//'), leaf)
        self.assertEqual(solution.resolve(doc, '/a//b'), 42)
        self.assertIs(solution.resolve(doc, '/a/'), doc['a'][''])


    def test_bounded_combinations_of_encoded_keys(self):
        alphabet = ('a', '~', '/', '0', '1')
        for size in range(4):
            for chars in itertools.product(alphabet, repeat=size):
                key = ''.join(chars)
                encoded = ''.join({'~': '~0', '/': '~1'}.get(c, c) for c in key)
                value = [key]
                with self.subTest(key=key):
                    self.assertIs(solution.resolve({key: value}, '/' + encoded), value)




    def test_pointer_type_and_prefix(self):
        for pointer in (None, 0, False, [], {}, b'/x'):
            with self.subTest(pointer=pointer):
                with self.assertRaises(TypeError):
                    solution.resolve({}, pointer)
        for pointer in ('a', '#', '#/a', ' /a', '\n/a'):
            with self.subTest(pointer=pointer):
                with self.assertRaises(ValueError):
                    solution.resolve({}, pointer)

    def test_invalid_escapes_validated_before_traversal(self):
        for token in ('~', '~2', 'a~x', '~~0', '~0~', '~10~9'):
            for prefix in ('/', '/missing/', '/0/'):
                with self.subTest(token=token, prefix=prefix):
                    with self.assertRaises(ValueError):
                        solution.resolve({}, prefix + token)
        with self.assertRaises(ValueError):
            solution.resolve(None, '/absent/~2')
        with self.assertRaises(ValueError):
            solution.resolve([], '/01/~2')


    def test_no_mutation_on_success_or_failure(self):
        doc = {'a': [{'b': [1, 2]}], '': {'x': None}}
        original = copy.deepcopy(doc)
        self.assertIs(solution.resolve(doc, '/a/0/b'), doc['a'][0]['b'])
        self.assertEqual(doc, original)
        for pointer, error in [('/a/3', KeyError), ('/missing', KeyError),
                               ('/a/0/b/-', KeyError), ('/a/0/~2', ValueError)]:
            with self.subTest(pointer=pointer):
                with self.assertRaises(error):
                    solution.resolve(doc, pointer)
                self.assertEqual(doc, original)


if __name__ == '__main__':
    unittest.main()
