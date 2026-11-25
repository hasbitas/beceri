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

    def test_chronology_and_output_order(self):
        b = [record('2024-01-03'), record('2024-01-01')]
        l = [record('2024-01-02'), record('2024-01-04')]
        self.assertEqual(solution.match(b, l, 1), expected([(0, 1), (1, 0)]))
        self.assertEqual(solution.match(b, l[:1], 1), expected([(1, 0)], [0]))

    def test_nearest_then_earlier_then_index(self):
        b = [record('2024-01-10')]
        l = [record('2024-01-12'), record('2024-01-08'), record('2024-01-08')]
        self.assertEqual(solution.match(b, l, 3), expected([(0, 1)], ledger=[0, 2]))
        l.append(record('2024-01-10'))
        self.assertEqual(solution.match(b, l, 3), expected([(0, 3)], ledger=[0, 1, 2]))

    def test_equal_bank_dates_and_duplicate_identity(self):
        r = record('2024-01-10')
        self.assertEqual(solution.match([r, r, r], [r, r], 0), expected([(0, 0), (1, 1)], [2]))


    def test_greedy_is_not_global_optimization(self):
        b = [record('2024-01-02'), record('2024-01-03')]
        l = [record('2024-01-02'), record('2024-01-01')]
        self.assertEqual(solution.match(b, l, 1), expected([(0, 0)], [1], [1]))

    def test_small_permutation_oracle(self):
        # Construct eligibility using ordinal sets; choose a winner by successive filters.
        originals_b = [record('2024-01-03'), record('2024-01-01'), record('2024-01-02', -100)]
        originals_l = [record('2024-01-02'), record('2024-01-04'), record('2024-01-01', -100)]
        for b, l, days in product(permutations(originals_b), permutations(originals_l), range(3)):
            b, l = list(b), list(l)
            available = list(range(len(l)))
            pairs = []
            for i in sorted(range(len(b)), key=lambda k: (b[k]['date'], k)):
                center = date.fromisoformat(b[i]['date']).toordinal()
                eligible_days = set(range(center - days, center + days + 1))
                eligible = [j for j in available if l[j]['amount'] == b[i]['amount']
                            and date.fromisoformat(l[j]['date']).toordinal() in eligible_days]
                if not eligible:
                    continue
                distances = {j: abs(date.fromisoformat(l[j]['date']).toordinal() - center) for j in eligible}
                closest = [j for j in eligible if distances[j] == min(distances.values())]
                earliest = min(l[j]['date'] for j in closest)
                j = min(j for j in closest if l[j]['date'] == earliest)
                pairs.append((i, j))
                available.remove(j)
            want = expected(sorted(pairs), [i for i in range(len(b)) if i not in {p[0] for p in pairs}], available)
            self.assertEqual(solution.match(b, l, days), want)

    def test_type_validation(self):
        class IntSubclass(int):
            pass
        class ListSubclass(list):
            pass
        class DictSubclass(dict):
            pass
        class StrSubclass(str):
            pass
        for days in (True, 1.0, '1', None, IntSubclass(1)):
            with self.subTest(days=days), self.assertRaises(TypeError):
                solution.match([], [], days)
        for bad in (None, (), {}, iter([]), ListSubclass()):
            for bank, ledger in ((bad, []), ([], bad)):
                with self.assertRaises(TypeError):
                    solution.match(bank, ledger, 0)
        bad_records = [None, [], DictSubclass(amount=1, date='2024-01-01')]
        bad_records += [record('2024-01-01', x) for x in (True, 1.0, '1', None, IntSubclass(1))]
        bad_records += [record(x) for x in (None, date(2024, 1, 1), 20240101, StrSubclass('2024-01-01'))]
        for bad in bad_records:
            for b, l in (([bad], []), ([], [bad])):
                with self.subTest(bad=bad), self.assertRaises(TypeError):
                    solution.match(b, l, 0)




if __name__ == '__main__':
    unittest.main()
