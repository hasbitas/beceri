def rotate(matrix, k):
    """Return a shallow, independently allocated rectangular rotation."""
    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k must be an integer other than bool")
    if not isinstance(matrix, (list, tuple)):
        raise TypeError("matrix must be a list or tuple")
    if any(not isinstance(row, (list, tuple)) for row in matrix):
        raise TypeError("rows must be lists or tuples")
    width = len(matrix[0]) if matrix else 0
    if any(len(row) != width for row in matrix):
        raise ValueError("rows must have equal lengths")
    if not matrix or not width:
        return []
    result = [list(row) for row in matrix]
    for _ in range(k % 4):
        result = [list(column) for column in zip(*result[::-1])]
    return result
