import copy
import itertools
import unittest

import solution


class ResolveTests(unittest.TestCase):
    def test_empty_pointer_returns_root_by_identity(self):
        for root in ({}, [], {'x': []}, 'text', 0, False, None):
            with self.subTest(root=root):
                self.assertIs(solution.resolve(root, ''), root)

    def test_nested_containers_and_falsy_values(self):
        values = [None, False, 0, '', [], {}]
        doc = {'items': [{'value': value} for value in values]}
        for i, value in enumerate(values):
            self.assertIs(solution.resolve(doc, '/items/' + str(i) + '/value'), value)
        self.assertIs(solution.resolve(doc, '/items'), doc['items'])


    def test_rfc_escapes_and_single_pass(self):
        doc = {'a/b': 1, 'm~n': 2, '~1': 3, '/': 4,
               '~01': 5, '~0/': 6, '~/': 7}
        cases = [('/a~1b', 1), ('/m~0n', 2), ('/~01', 3),
                 ('/~1', 4), ('/~001', 5), ('/~00~1', 6), ('/~0~1', 7)]
        for pointer, expected in cases:
            with self.subTest(pointer=pointer):
                self.assertEqual(solution.resolve(doc, pointer), expected)


    def test_object_keys_are_not_indexes_or_normalized(self):
        keys = ['0', '01', '-1', '-', '+1', ' 1', '1 ', '١', '１',
                '%2F', '#', 'A', 'a', 'é', 'é', '\u0000']
        doc = {key: [key] for key in keys}
        for key in keys:
            with self.subTest(key=key):
                self.assertIs(solution.resolve(doc, '/' + key), doc[key])
        with self.assertRaises(KeyError):
            solution.resolve({'/': 1}, '/%2F')

    def test_array_index_boundaries(self):
        doc = list(range(12))
        for i in (0, 1, 9, 10, 11):
            self.assertEqual(solution.resolve(doc, '/' + str(i)), i)
        for pointer in ('/12', '/99', '/999999999999999999999999', '/' + '9' * 5000):
            with self.subTest(pointer_length=len(pointer)):
                with self.assertRaises(KeyError):
                    solution.resolve(doc, pointer)
        with self.assertRaises(KeyError):
            solution.resolve([], '/0')

    def test_invalid_array_index_spellings(self):
        tokens = ['', '00', '01', '-1', '+1', '-', ' 0', '0 ', '1.0',
                  '1_0', '١', '１', '²', '\n0', '0\n', '0x0', '0' * 5000]
        for token in tokens:
            with self.subTest(token_length=len(token), prefix=token[:10]):
                with self.assertRaises(KeyError):
                    solution.resolve(list(range(12)), '/' + token)



    def test_missing_keys_and_scalar_traversal(self):
        for doc, pointer in [({}, '/missing'), ({'a': {}}, '/a/b'),
                             ({'a': []}, '/a/0')]:
            with self.subTest(pointer=pointer):
                with self.assertRaises(KeyError):
                    solution.resolve(doc, pointer)
        for scalar in (None, False, True, 0, 1.5, '', 'abc'):
            for pointer in ('/0', '/'):
                with self.subTest(scalar=scalar, pointer=pointer):
                    with self.assertRaises(KeyError):
                        solution.resolve(scalar, pointer)



if __name__ == '__main__':
    unittest.main()
