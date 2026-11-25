def spiral(matrix):
    if not isinstance(matrix, (list, tuple)):
        raise TypeError('matrix must be a list or tuple')
    if any(not isinstance(row, (list, tuple)) for row in matrix):
        raise TypeError('rows must be lists or tuples')
    width = len(matrix[0]) if matrix else 0
    if any(len(row) != width for row in matrix):
        raise ValueError('matrix must be rectangular')

    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, width - 1
    while top <= bottom and left <= right:
        for col in range(left, right + 1):
            result.append(matrix[top][col])
        top += 1
        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1
        if top <= bottom:
            for col in range(right, left - 1, -1):
                result.append(matrix[bottom][col])
            bottom -= 1
        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1
    return result
