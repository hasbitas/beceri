"""Lot bookkeeping for FIFO costing."""


class Lot:
    __slots__ = ('lot_id', 'unit_cost', 'qty')

    def __init__(self, lot_id, unit_cost, qty):
        self.lot_id = lot_id
        self.unit_cost = unit_cost
        self.qty = qty

    def __repr__(self):
        return 'Lot(%r, %r, %r)' % (self.lot_id, self.unit_cost, self.qty)


def total_qty(lots):
    return sum(lot.qty for lot in lots)


def consume(lots, qty):
    if total_qty(lots) < qty:
        raise ValueError('insufficient stock')
    taken = []
    remaining = qty
    while remaining:
        lot = lots[0]
        used = min(lot.qty, remaining)
        lot.qty -= used
        remaining -= used
        taken.append((lot.lot_id, used, lot.unit_cost))
        if lot.qty == 0:
            lots.pop(0)
    return taken


def restore(lots, lot_id, unit_cost, qty):
    for index, lot in enumerate(lots):
        if lot.lot_id == lot_id:
            lot.qty += qty
            return
        if lot.lot_id > lot_id:
            lots.insert(index, Lot(lot_id, unit_cost, qty))
            return
    lots.append(Lot(lot_id, unit_cost, qty))
