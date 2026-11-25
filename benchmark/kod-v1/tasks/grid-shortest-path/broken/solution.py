"""Find a route through a rectangular maze."""
from collections import deque


def shortest(grid, start, goal):
    if not isinstance(grid, (list, tuple)) or not grid:
        raise ValueError('invalid grid')
    if any(not isinstance(row, str) or not row for row in grid):
        raise ValueError('invalid row')
    width = len(grid[0])
    if any(len(row) != width or any(c not in '.#' for c in row) for row in grid):
        raise ValueError('invalid grid')
    height = len(grid)
    for point in (start, goal):
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise ValueError('invalid coordinate')
        if any(not isinstance(v, int) or isinstance(v, bool) for v in point):
            raise ValueError('invalid coordinate')
        if not (0 <= point[0] < height and 0 <= point[1] < width):
            raise ValueError('coordinate out of bounds')
    start, goal = tuple(start), tuple(goal)
    if start == goal:
        return 0
    if grid[start[0]][start[1]] == '#' or grid[goal[0]][goal[1]] == '#':
        return -1
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        (r, c), distance = queue.pop()
        if (r, c) == goal:
            return distance
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if (0 <= nr < height and 0 <= nc < width
                    and grid[nr][nc] == '.' and (nr, nc) not in seen):
                seen.add((nr, nc))
                queue.append(((nr, nc), distance + 1))
    return -1
