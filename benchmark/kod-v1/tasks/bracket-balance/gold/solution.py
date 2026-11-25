def balanced(text):
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    stack = []
    quote = None
    escaped = False
    pairs = {')': '(', ']': '[', '}': '{'}
    for char in text:
        if quote is not None:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char in '([{':
            stack.append(char)
        elif char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False
    return quote is None and not stack
