"""Parser that turns configuration text into nested dictionaries."""

from .errors import ConfigError
from .tokens import tokenize


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.root = {}
        self.current = self.root
        self.defined = set()

    def peek(self):
        return self.tokens[self.pos]

    def take(self, kind=None, what=None):
        token = self.tokens[self.pos]
        if kind is not None and token.kind != kind:
            raise ConfigError(f"expected {what or kind}", token.line, token.column)
        if token.kind != "EOF":
            self.pos += 1
        return token

    def skip_newlines(self):
        while self.peek().kind == "NEWLINE":
            self.pos += 1

    def parse(self):
        while True:
            token = self.peek()
            if token.kind == "EOF":
                return self.root
            if token.kind == "NEWLINE":
                self.pos += 1
                continue
            if token.kind == "LBRACKET":
                self.header()
            elif token.kind == "NAME":
                self.assignment()
            else:
                raise ConfigError("unexpected token", token.line, token.column)
            end = self.peek()
            if end.kind not in ("NEWLINE", "EOF"):
                raise ConfigError("expected end of line", end.line, end.column)

    def header(self):
        opener = self.take("LBRACKET")
        path = [self.take("NAME", "section name").value]
        while self.peek().kind == "DOT":
            self.take()
            path.append(self.take("NAME", "section name").value)
        self.take("RBRACKET", "']'")
        table = self.root
        for name in path:
            if name not in table:
                table[name] = {}
            elif not isinstance(table[name], dict):
                raise ConfigError("section conflicts with a value", opener.line, opener.column)
            table = table[name]
        if tuple(path) in self.defined:
            raise ConfigError("duplicate section", opener.line, opener.column)
        self.defined.add(tuple(path))
        self.current = table

    def assignment(self):
        key = self.take("NAME")
        if key.value in self.current:
            raise ConfigError("duplicate key", key.line, key.column)
        self.take("EQUALS", "'='")
        self.current[key.value] = self.value()

    def value(self):
        token = self.take()
        if token.kind in ("STRING", "INT"):
            return token.value
        if token.kind == "NAME":
            if token.value == "true":
                return True
            if token.value == "false":
                return False
            raise ConfigError("unknown bare word", token.line, token.column)
        if token.kind == "LBRACKET":
            return self.items()
        raise ConfigError("expected a value", token.line, token.column)

    def items(self):
        result = []
        while True:
            self.skip_newlines()
            if self.peek().kind == "RBRACKET":
                self.take()
                return result
            result.append(self.value())
            self.skip_newlines()
            token = self.peek()
            if token.kind == "COMMA":
                self.take()
            elif token.kind == "RBRACKET":
                self.take()
                return result
            else:
                raise ConfigError("expected ',' or ']'", token.line, token.column)


def parse(text):
    return _Parser(tokenize(text)).parse()
