"""IBAN structure and streaming mod-97 validation."""


def iban_valid(text):
    if not isinstance(text, str):
        return False
    text = text.replace(' ', '')
    if not 15 <= len(text) <= 34:
        return False
    if any(not ('A' <= c <= 'Z' or 'a' <= c <= 'z' or '0' <= c <= '9')
           for c in text):
        return False
    text = text.upper()
    if not all('A' <= c <= 'Z' for c in text[:2]):
        return False
    if not all('0' <= c <= '9' for c in text[2:4]):
        return False
    if not 2 <= int(text[2:4]) <= 98:
        return False
    remainder = 0
    for c in text[4:] + text[:4]:
        value = int(c) if '0' <= c <= '9' else ord(c) - ord('A') + 10
        remainder = (remainder * 10 + value) % 97
    return remainder == 1
