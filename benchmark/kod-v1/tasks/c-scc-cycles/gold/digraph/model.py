"""Storage for a directed graph whose nodes are non-empty strings."""


def _check_node(node):
    if not isinstance(node, str):
        raise TypeError("node must be a str")
    if node == "":
        raise ValueError("node must not be empty")


class DiGraph:
    def __init__(self):
        self._succ = {}

    def add_node(self, node):
        _check_node(node)
        self._succ.setdefault(node, set())

    def add_edge(self, source, target):
        _check_node(source)
        _check_node(target)
        self._succ.setdefault(source, set()).add(target)
        self._succ.setdefault(target, set())

    def nodes(self):
        return sorted(self._succ)

    def successors(self, node):
        if node not in self._succ:
            raise KeyError(node)
        return sorted(self._succ[node])

    def has_edge(self, source, target):
        return target in self._succ.get(source, ())

    def edge_count(self):
        return sum(len(targets) for targets in self._succ.values())
