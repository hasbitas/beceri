"""Point location by a horizontal ray crossing count."""


def locate(point, polygon):
    x, y = point
    inside = False
    for i, (ax, ay) in enumerate(polygon):
        bx, by = polygon[(i + 1) % len(polygon)]
        cross = (bx - ax) * (y - ay) - (by - ay) * (x - ax)
        if (cross == 0 and min(ax, bx) <= x <= max(ax, bx)
                and min(ay, by) <= y <= max(ay, by)):
            return 'boundary'
        if (ay > y) != (by > y):
            intersection_x = ax + (y - ay) * (bx - ax) / (by - ay)
            if x < intersection_x:
                inside = not inside
    return 'inside' if inside else 'outside'
