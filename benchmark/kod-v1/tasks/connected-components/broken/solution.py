def components(n, edges):
    if type(n) is not int:
        raise TypeError('n must be an int')
    if n < 0:
        raise ValueError('negative vertex count')
    parent = list(range(n))

    def find(vertex):
        while vertex != parent[vertex]:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for edge in edges:
        if not isinstance(edge, (list, tuple)):
            raise TypeError('edge must be a list or tuple')
        if len(edge) != 2:
            raise ValueError('edge must have two endpoints')
        u, v = edge
        if type(u) is not int or type(v) is not int:
            raise TypeError('endpoints must be ints')
        if not (0 <= u < n and 0 <= v < n):
            raise ValueError('endpoint out of range')
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[u] = rv

    groups = {}
    for vertex in range(n):
        groups.setdefault(find(vertex), []).append(vertex)
    return sorted(groups.values(), key=lambda group: (-len(group), group[0]))
