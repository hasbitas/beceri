import re
import unicodedata


_TURKISH = str.maketrans({
    'ç': 'c', 'Ç': 'c', 'ğ': 'g', 'Ğ': 'g',
    'ı': 'i', 'I': 'i', 'i': 'i', 'İ': 'i',
    'ö': 'o', 'Ö': 'o', 'ş': 's', 'Ş': 's', 'ü': 'u', 'Ü': 'u',
})
_ASCII_LOWER = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                             'abcdefghijklmnopqrstuvwxyz')


def slugify(text):
    if not isinstance(text, str):
        raise TypeError('text must be a str')
    text = unicodedata.normalize('NFC', text)
    text = text.translate(_TURKISH).translate(_ASCII_LOWER)
    return re.sub('[^a-z0-9]+', '-', text).strip('-')
