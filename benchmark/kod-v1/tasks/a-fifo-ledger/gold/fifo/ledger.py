"""A FIFO inventory ledger with issue returns."""

from fifo.costing import average_cost, total_cost
from fifo.lots import Lot, consume, restore, total_qty


def _check_sku(sku):
    if type(sku) is not str:
        raise TypeError('sku must be a str')
    if not sku:
        raise ValueError('sku must not be empty')


def _check_int(name, value, minimum):
    if type(value) is not int:
        raise TypeError(name + ' must be an int')
    if value < minimum:
        raise ValueError(name + ' must be at least %d' % minimum)


class Ledger:
    def __init__(self):
        self._lots = {}
        self._next_lot_id = 1
        self._issues = {}
        self._next_issue_id = 1

    def receive(self, sku, qty, unit_cost):
        _check_sku(sku)
        _check_int('qty', qty, 1)
        _check_int('unit_cost', unit_cost, 0)
        lot_id = self._next_lot_id
        self._next_lot_id += 1
        self._lots.setdefault(sku, []).append(Lot(lot_id, unit_cost, qty))
        return lot_id

    def issue(self, sku, qty):
        _check_sku(sku)
        _check_int('qty', qty, 1)
        taken = consume(self._lots.get(sku, []), qty)
        cost = total_cost(taken)
        issue_id = self._next_issue_id
        self._next_issue_id += 1
        self._issues[issue_id] = {
            'sku': sku,
            'entries': [[lot_id, count, unit_cost, 0] for lot_id, count, unit_cost in taken],
        }
        return {
            'issue_id': issue_id,
            'cost': cost,
            'unit_cost': average_cost(cost, qty),
            'lots': [(lot_id, count) for lot_id, count, _unit_cost in taken],
        }

    def return_items(self, issue_id, qty):
        _check_int('issue_id', issue_id, 1)
        _check_int('qty', qty, 1)
        record = self._issues.get(issue_id)
        if record is None:
            raise ValueError('unknown issue')
        if qty > sum(entry[1] - entry[3] for entry in record['entries']):
            raise ValueError('more than was issued')
        lots = self._lots[record['sku']]
        remaining = qty
        credit = 0
        restored = []
        for entry in reversed(record['entries']):
            if not remaining:
                break
            put = min(entry[1] - entry[3], remaining)
            if put == 0:
                continue
            restore(lots, entry[0], entry[2], put)
            entry[3] += put
            remaining -= put
            credit += put * entry[2]
            restored.append((entry[0], put))
        return {'credit': credit, 'restored': restored}

    def on_hand(self, sku):
        _check_sku(sku)
        return total_qty(self._lots.get(sku, []))

    def value(self, sku):
        _check_sku(sku)
        return sum(lot.qty * lot.unit_cost for lot in self._lots.get(sku, []))

    def lots(self, sku):
        _check_sku(sku)
        return [(lot.lot_id, lot.qty, lot.unit_cost) for lot in self._lots.get(sku, [])]
