def balanced(text):
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    stack = []
    quote = None
    pairs = {')': '(', ']': '[', '}': '{'}
    for index, char in enumerate(text):
        if quote is not None:
            # A quote preceded by a backslash is escaped.
            if char == quote and text[index - 1] != '\\':
                quote = None
        elif char in "\"'":
            quote = char
        elif char in '([{':
            stack.append(char)
        elif char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False
    return quote is None and not stack
