"""Ordered stock movements with strict record validation."""


def apply(moves):
    if type(moves) not in (list, tuple):
        raise TypeError('moves must be a list or tuple')
    for move in moves:
        if type(move) is not dict:
            raise TypeError('movement must be a dictionary')
        if set(move) != {'item', 'direction', 'quantity'}:
            raise ValueError('invalid movement keys')
        item, direction, quantity = move['item'], move['direction'], move['quantity']
        if type(item) is not str:
            raise TypeError('item must be a string')
        if not item:
            raise ValueError('empty item')
        if type(direction) is not str:
            raise TypeError('direction must be a string')
        if direction not in ('in', 'out'):
            raise ValueError('unknown direction')
        if type(quantity) is not int:
            raise TypeError('quantity must be an integer')
        if quantity < 0:
            raise ValueError('negative quantity')

    balances = {}
    for move in moves:
        item = move['item']
        delta = move['quantity'] if move['direction'] == 'in' else -move['quantity']
        updated = balances.get(item, 0) + delta
        if updated < 0:
            raise ValueError('insufficient stock')
        balances[item] = updated
    return balances
