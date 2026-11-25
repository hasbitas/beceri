"""Cost arithmetic in integer cents."""


def total_cost(taken):
    return sum(count * unit_cost for _lot_id, count, unit_cost in taken)


def average_cost(total, qty):
    return (2 * total + qty) // (2 * qty)
