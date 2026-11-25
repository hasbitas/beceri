"""Deterministic reconciliation of signed minor-unit transactions."""
from datetime import date
import re


def _records(records):
    if type(records) is not list:
        raise TypeError('records must be a list')
    result = []
    for record in records:
        if type(record) is not dict:
            raise TypeError('record must be a dictionary')
        if 'amount' not in record or 'date' not in record:
            raise ValueError('missing amount or date')
        amount, text = record['amount'], record['date']
        if type(amount) is not int or type(text) is not str:
            raise TypeError('invalid amount or date type')
        if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', text) is None:
            raise ValueError('invalid date syntax')
        ordinal = date(int(text[:4]), int(text[5:7]), int(text[8:])).toordinal()
        result.append((amount, ordinal))
    return result


def match(bank, ledger, days):
    if type(days) is not int:
        raise TypeError('days must be an integer')
    if days < 0:
        raise ValueError('days must be nonnegative')
    banks = _records(bank)
    ledgers = _records(ledger)
    used = set()
    pairs = []
    for i in range(len(banks)):
        amount, when = banks[i]
        candidates = [
            (abs(when - other_date), other_date, j)
            for j, (other_amount, other_date) in enumerate(ledgers)
            if j not in used and amount == other_amount
            and abs(when - other_date) <= days
        ]
        if candidates:
            j = min(candidates)[2]
            used.add(j)
            pairs.append((i, j))
    pairs.sort()
    paired_bank = {i for i, _ in pairs}
    return {
        'pairs': pairs,
        'unmatched_bank': [i for i in range(len(banks)) if i not in paired_bank],
        'unmatched_ledger': [j for j in range(len(ledgers)) if j not in used],
    }
