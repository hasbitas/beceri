"""Storage for a weighted road network with string-named places."""


def _check_place(place):
    if not isinstance(place, str):
        raise TypeError("place must be a str")
    if place == "":
        raise ValueError("place must not be empty")


class Network:
    def __init__(self, directed=False):
        self.directed = bool(directed)
        self._adj = {}

    def add_place(self, place):
        _check_place(place)
        self._adj.setdefault(place, {})

    def add_road(self, start, end, length):
        _check_place(start)
        _check_place(end)
        if isinstance(length, bool) or not isinstance(length, int):
            raise TypeError("length must be an int")
        if length < 0:
            raise ValueError("length must not be negative")
        self.add_place(start)
        self.add_place(end)
        self._relax(start, end, length)
        if not self.directed:
            self._relax(end, start, length)

    def _relax(self, start, end, length):
        self._adj[start][end] = length

    def places(self):
        return sorted(self._adj)

    def neighbors(self, place):
        if place not in self._adj:
            raise KeyError(place)
        return sorted(self._adj[place].items())

    def length(self, start, end):
        return self._adj.get(start, {}).get(end)

    def roads(self):
        found = []
        for start in sorted(self._adj):
            for end, length in sorted(self._adj[start].items()):
                if self.directed or start <= end:
                    found.append((start, end, length))
        return found
