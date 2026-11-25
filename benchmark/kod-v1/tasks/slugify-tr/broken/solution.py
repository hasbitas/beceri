import re
import unicodedata


_TURKISH = str.maketrans({
    'ç': 'c', 'ğ': 'g', 'ı': 'i', 'i': 'i',
    'ö': 'o', 'ş': 's', 'ü': 'u',
})


def slugify(text):
    if not isinstance(text, str):
        raise TypeError('text must be a str')
    text = unicodedata.normalize('NFC', text).lower()
    text = text.translate(_TURKISH)
    return re.sub('[^a-z0-9]+', '-', text).strip('-')
