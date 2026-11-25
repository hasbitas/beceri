"""Tokenizer for the configuration language."""

from collections import namedtuple

from .errors import ConfigError

Token = namedtuple("Token", ["kind", "value", "line", "column"])

_PUNCTUATION = {"[": "LBRACKET", "]": "RBRACKET", "=": "EQUALS", ",": "COMMA", ".": "DOT"}
_ESCAPES = {"\\": "\\", '"': '"', "n": "\n", "t": "\t"}
_NAME_START = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
_DIGITS = "0123456789"


def tokenize(text):
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    tokens = []
    i = 0
    line = 1
    column = 1
    size = len(text)
    while i < size:
        ch = text[i]
        if ch in " \t\r":
            i += 1
            column += 1
        elif ch == "\n":
            tokens.append(Token("NEWLINE", "\n", line, column))
            i += 1
            line += 1
            column = 1
        elif ch == "#":
            while i < size and text[i] != "\n":
                i += 1
                column += 1
        elif ch in _PUNCTUATION:
            tokens.append(Token(_PUNCTUATION[ch], ch, line, column))
            i += 1
            column += 1
        elif ch == '"':
            j = i + 1
            chars = []
            while True:
                if j >= size or text[j] == "\n":
                    raise ConfigError("unterminated string", line, column)
                current = text[j]
                if current == '"' and text[j - 1] != "\\":
                    break
                if current == "\\":
                    if j + 1 >= size or text[j + 1] not in _ESCAPES:
                        raise ConfigError("invalid escape", line, column + (j - i))
                    chars.append(_ESCAPES[text[j + 1]])
                    j += 2
                else:
                    chars.append(current)
                    j += 1
            tokens.append(Token("STRING", "".join(chars), line, column))
            column += len(chars) + 2
            i = j + 1
        elif ch in _DIGITS or (ch == "-" and text[i + 1:i + 2] in tuple(_DIGITS)):
            j = i + 1
            while j < size and text[j] in _DIGITS:
                j += 1
            tokens.append(Token("INT", int(text[i:j]), line, column))
            column += j - i
            i = j
        elif ch in _NAME_START:
            j = i + 1
            while j < size and (text[j] in _NAME_START or text[j] in _DIGITS or text[j] == "-"):
                j += 1
            tokens.append(Token("NAME", text[i:j], line, column))
            column += j - i
            i = j
        else:
            raise ConfigError(f"unexpected character {ch!r}", line, column)
    tokens.append(Token("EOF", "", line, column))
    return tokens
