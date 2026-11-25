import itertools
import unittest

import solution


class JustifyTests(unittest.TestCase):
    def check_case(self, words, width, expected):
        original = words[:]
        actual = solution.justify(words, width)
        self.assertIsInstance(actual, list)
        self.assertEqual(actual, expected)
        self.assertEqual(words, original)
        for line in actual:
            self.assertEqual(len(line), width)



    def test_last_line_is_left_aligned(self):
        self.check_case(['a', 'bb', 'c'], 10, ['a bb c    '])
        self.check_case(['a', 'bb', 'c'], 6, ['a bb c'])

    def test_standard_paragraph(self):
        self.check_case(
            ['This', 'is', 'an', 'example', 'of', 'text', 'justification.'],
            16,
            ['This    is    an', 'example  of text', 'justification.  '],
        )



    def test_single_word_nonfinal_lines(self):
        self.check_case(['abcde', 'x', 'yyyyy', 'z'], 5,
                        ['abcde', 'x    ', 'yyyyy', 'z    '])
        self.check_case(['a', 'b', 'c'], 1, ['a', 'b', 'c'])



    def test_exhaustive_small_valid_inputs(self):
        # Independently verify the greedy grouping and the spacing constraints.
        for count in range(6):
            for sequence in itertools.product(('a', 'bb', '猫'), repeat=count):
                for width in range(2, 8):
                    with self.subTest(words=sequence, width=width):
                        words = list(sequence)
                        actual = solution.justify(words, width)
                        self.assertIsInstance(actual, list)
                        self.assertEqual(words, list(sequence))
                        self.assertEqual(bool(actual), bool(words))
                        consumed = 0
                        for line_number, line in enumerate(actual):
                            self.assertIsInstance(line, str)
                            self.assertEqual(len(line), width)
                            self.assertFalse(line.startswith(' '))
                            tokens = line.split(' ')
                            tokens = [token for token in tokens if token]
                            self.assertTrue(tokens)
                            self.assertEqual(tokens, words[consumed:consumed + len(tokens)])
                            consumed += len(tokens)
                            minimal = sum(map(len, tokens)) + len(tokens) - 1
                            if consumed < len(words):
                                self.assertGreater(minimal + 1 + len(words[consumed]), width)
                            if line_number == len(actual) - 1 or len(tokens) == 1:
                                self.assertEqual(line, ' '.join(tokens).ljust(width))
                            else:
                                self.assertFalse(line.endswith(' '))
                                gaps = []
                                cursor = len(tokens[0])
                                for token in tokens[1:]:
                                    start = cursor
                                    while line[cursor] == ' ':
                                        cursor += 1
                                    gaps.append(cursor - start)
                                    cursor += len(token)
                                self.assertGreaterEqual(min(gaps), 1)
                                self.assertLessEqual(max(gaps) - min(gaps), 1)
                                self.assertEqual(gaps, sorted(gaps, reverse=True))
                        self.assertEqual(consumed, len(words))


if __name__ == '__main__':
    unittest.main()
