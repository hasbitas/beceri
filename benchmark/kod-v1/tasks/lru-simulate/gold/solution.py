"""Request-by-request LRU simulation."""
from collections import OrderedDict


def simulate(capacity, keys):
    if type(capacity) is not int:
        raise TypeError('capacity must be a built-in int')
    if capacity < 0:
        raise ValueError('capacity must be nonnegative')
    resident = OrderedDict()
    result = []
    for key in keys:
        hash(key)
        hit = key in resident
        result.append(hit)
        if capacity:
            resident[key] = None
            resident.move_to_end(key)
            if len(resident) > capacity:
                resident.popitem(last=False)
    return result
