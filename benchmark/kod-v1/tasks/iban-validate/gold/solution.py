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
        if '0' <= c <= '9':
            remainder = (remainder * 10 + int(c)) % 97
        else:
            remainder = (remainder * 100 + ord(c) - ord('A') + 10) % 97
    return remainder == 1
