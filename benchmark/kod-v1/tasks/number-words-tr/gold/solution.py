"""Turkish cardinal numbers in the supported six-digit range."""

_UNITS = ('', 'bir', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi', 'sekiz', 'dokuz')
_TENS = ('', 'on', 'yirmi', 'otuz', 'kırk', 'elli', 'altmış', 'yetmiş', 'seksen', 'doksan')


def _small(n):
    words = []
    hundreds, rest = divmod(n, 100)
    if hundreds:
        if hundreds != 1:
            words.append(_UNITS[hundreds])
        words.append('yüz')
    tens, units = divmod(rest, 10)
    if tens:
        words.append(_TENS[tens])
    if units:
        words.append(_UNITS[units])
    return ' '.join(words)


def to_words(n):
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError('n must be an integer other than bool')
    if not 0 <= n <= 999999:
        raise ValueError('n must be between 0 and 999999')
    if n == 0:
        return 'sıfır'
    thousands, remainder = divmod(n, 1000)
    parts = []
    if thousands:
        parts.append('bin' if thousands == 1 else _small(thousands) + ' bin')
    if remainder:
        parts.append(_small(remainder))
    return ' '.join(parts)
