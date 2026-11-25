import unicodedata


def group_anagrams(words):
    groups = {}
    for word in words:
        text = unicodedata.normalize("NFC", word.casefold())
        letters = {char for char in text if char.isalpha()}
        signature = "".join(sorted(letters))
        groups.setdefault(signature, []).append((text, word))
    signatures = sorted(groups, key=lambda signature: (-len(groups[signature]), signature))
    return [[word for text, word in sorted(groups[signature])] for signature in signatures]
