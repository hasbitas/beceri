"""Deterministic topological sorting."""
import heapq


def topo_sort(graph):
    if type(graph) is not dict:
        raise TypeError('graph must be a dict')
    for node, neighbors in graph.items():
        if type(node) is not str:
            raise TypeError('vertices must be strings')
        if type(neighbors) not in (list, tuple, set):
            raise TypeError('neighbors must be a list, tuple, or set')
        if any(type(v) is not str for v in neighbors):
            raise TypeError('vertices must be strings')

    adjacency = {node: set(neighbors) for node, neighbors in graph.items()}
    vertices = set(adjacency)
    for neighbors in adjacency.values():
        vertices.update(neighbors)
    indegree = dict.fromkeys(vertices, 0)
    for neighbors in adjacency.values():
        for target in neighbors:
            indegree[target] += 1
    ready = [v for v in vertices if indegree[v] == 0]
    heapq.heapify(ready)
    result = []
    while ready:
        node = heapq.heappop(ready)
        result.append(node)
        for target in adjacency.get(node, ()):
            indegree[target] -= 1
            if indegree[target] == 0:
                heapq.heappush(ready, target)
    if len(result) != len(vertices):
        raise ValueError('graph contains a cycle')
    return result
