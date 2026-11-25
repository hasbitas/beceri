"""Exact integer point location using winding numbers."""


def locate(point, polygon):
    x, y = point
    winding = 0
    for i, (ax, ay) in enumerate(polygon):
        bx, by = polygon[(i + 1) % len(polygon)]
        cross = (bx - ax) * (y - ay) - (by - ay) * (x - ax)
        if (cross == 0 and min(ax, bx) <= x <= max(ax, bx)
                and min(ay, by) <= y <= max(ay, by)):
            return 'boundary'
        if ay <= y < by and cross > 0:
            winding += 1
        elif by <= y < ay and cross < 0:
            winding -= 1
    return 'inside' if winding else 'outside'
