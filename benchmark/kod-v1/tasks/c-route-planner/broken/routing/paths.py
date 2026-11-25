"""Route queries over a Network."""

import heapq


def _search(network, source, limit=None):
    best = {}
    heap = [(0, 1, (source,))]
    while heap:
        cost, _, path = heapq.heappop(heap)
        place = path[-1]
        if place in best:
            continue
        if limit is not None and cost > limit:
            break
        best[place] = (cost, list(path))
        for neighbor, length in network.neighbors(place):
            if neighbor not in best:
                heapq.heappush(heap, (cost + length, len(path) + 1, path + (neighbor,)))
    return best


def shortest_path(network, source, target):
    for place in (source, target):
        if place not in network.places():
            raise KeyError(place)
    found = _search(network, source).get(target)
    if found is None:
        return None
    return found[0], found[1]


def reachable_within(network, source, budget):
    if source not in network.places():
        raise KeyError(source)
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise TypeError("budget must be an int")
    if budget < 0:
        raise ValueError("budget must not be negative")
    found = _search(network, source, budget)
    ordered = sorted((cost, place) for place, (cost, _) in found.items() if cost < budget or place == source)
    return {place: cost for cost, place in ordered}
