"""Strongly connected components and derived queries."""


def components(graph):
    index = {}
    low = {}
    on_stack = set()
    stack = []
    found = []
    counter = 0
    for start in graph.nodes():
        if start in index:
            continue
        index[start] = low[start] = counter
        counter += 1
        stack.append(start)
        on_stack.add(start)
        work = [(start, iter(graph.successors(start)))]
        while work:
            node, children = work[-1]
            descended = False
            for child in children:
                if child not in index:
                    index[child] = low[child] = counter
                    counter += 1
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(graph.successors(child))))
                    descended = True
                    break
                else:
                    low[node] = min(low[node], index[child])
            if descended:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                members = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    members.append(member)
                    if member == node:
                        break
                found.append(sorted(members))
    found.sort(key=lambda members: members[0])
    return found


def cyclic_components(graph):
    return [members for members in components(graph)
            if len(members) > 1 or graph.has_edge(members[0], members[0])]


def is_acyclic(graph):
    return not cyclic_components(graph)


def condensation_edges(graph):
    owner = {}
    for position, members in enumerate(components(graph)):
        for member in members:
            owner[member] = position
    pairs = []
    for node in graph.nodes():
        for child in graph.successors(node):
            if owner[node] != owner[child]:
                pairs.append((owner[node], owner[child]))
    return sorted(pairs)
