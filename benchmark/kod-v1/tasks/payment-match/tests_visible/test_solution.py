import copy
from datetime import date
from itertools import permutations, product
import unittest

import solution


def record(day, amount=100):
    return {'date': day, 'amount': amount}


def expected(pairs=(), bank=(), ledger=()):
    return {'pairs': list(pairs), 'unmatched_bank': list(bank), 'unmatched_ledger': list(ledger)}


class MatchTests(unittest.TestCase):
    def test_empty_and_signed_amounts(self):
        self.assertEqual(solution.match([], [], 0), expected())
        b = [record('2024-01-01', x) for x in (0, -50, 50, 10**100)]
        l = [record('2024-01-01', x) for x in (50, 0, 10**100, -50)]
        self.assertEqual(solution.match(b, l, 0), expected([(0, 1), (1, 3), (2, 0), (3, 2)]))
        self.assertEqual(solution.match(b, [], 0), expected(bank=range(4)))
        self.assertEqual(solution.match([], l, 0), expected(ledger=range(4)))




    def test_inclusive_leap_and_year_boundaries(self):
        for a, b, gap in [('2024-02-28', '2024-03-01', 2),
                          ('1900-02-28', '1900-03-01', 1),
                          ('2000-02-28', '2000-03-01', 2),
                          ('2023-12-31', '2024-01-01', 1)]:
            for left, right in [(a, b), (b, a)]:
                with self.subTest(left=left, right=right):
                    self.assertEqual(solution.match([record(left)], [record(right)], gap), expected([(0, 0)]))
                    self.assertEqual(solution.match([record(left)], [record(right)], gap - 1), expected(bank=[0], ledger=[0]))
        self.assertEqual(solution.match([record('0001-01-01')], [record('9999-12-31')], 10**100), expected([(0, 0)]))




    def test_value_validation_and_late_records(self):
        invalid = [{}, {'amount': 100}, {'date': '2024-01-01'}]
        invalid += [record(d) for d in ('2024-1-01', '20240101', '2024-01-01\n',
                    ' 2024-01-01', '２０２４-01-01', '0000-01-01', '10000-01-01',
                    '2023-02-29', '1900-02-29', '2024-04-31', '2024-00-01', '2024-01-00')]
        for bad in invalid:
            for b, l in (([record('2024-01-01'), bad], []),
                         ([], [record('2024-01-01'), bad]),
                         ([record('2024-01-01')], [record('2024-01-01'), bad])):
                before = copy.deepcopy((b, l))
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    solution.match(b, l, 0)
                self.assertEqual((b, l), before)
        with self.assertRaises(ValueError):
            solution.match([], [], -1)

    def test_no_mutation_freshness_and_exact_output_types(self):
        b = [record('2024-01-03'), record('2024-01-01')]
        l = [record('2024-01-02')]
        b[0]['extra'] = {'opaque': [1, 2]}
        before = copy.deepcopy((b, l))
        a = solution.match(b, l, 1)
        c = solution.match(b, l, 1)
        self.assertEqual((b, l), before)
        self.assertIs(type(a), dict)
        self.assertEqual(set(a), {'pairs', 'unmatched_bank', 'unmatched_ledger'})
        self.assertIsNot(a, c)
        for key in a:
            self.assertIs(type(a[key]), list)
            self.assertIsNot(a[key], c[key])
        for pair in a['pairs']:
            self.assertIs(type(pair), tuple)
            self.assertEqual(len(pair), 2)
            for index in pair:
                self.assertIs(type(index), int)
        for key in ('unmatched_bank', 'unmatched_ledger'):
            for index in a[key]:
                self.assertIs(type(index), int)
        a['pairs'].clear()
        self.assertEqual(c, expected([(1, 0)], [0]))


if __name__ == '__main__':
    unittest.main()
