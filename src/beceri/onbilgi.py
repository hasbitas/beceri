"""SKILL.md ön bilgisi (YAML frontmatter): ayırma ve güvenli ayrıştırma.

Skill'lerin kullandığı YAML alt kümesi bağımlılıksız ayrıştırılır: eşlem (mapping), liste, düz/tırnaklı
skaler, `|` ve `>` blokları (`-`/`+` ekleriyle), tek satırlık `[a, b]` ve `{a: b}`, yorumlar.
Gerçek YAML ayrıştırıcılarının da reddettiği yazımlar reddedilir: düz değerin içinde `: `, kapanmamış
tırnak, sekmeyle girinti, yinelenen anahtar. Böylece burada geçen bir ön bilgi PyYAML'da da geçer.

Çapa, takma ad ve etiket (`&`, `*`, `!`) gibi alt kümenin dışındaki yapılar `Desteklenmiyor` verir; PyYAML
kuruluysa yalnız o durumda ona başvurulur. Kod çalıştırma yoktur (yalnız `safe_load`).
"""
import re

__all__ = ["Desteklenmiyor", "ayir", "oku"]


class Desteklenmiyor(ValueError):
    """Geçerli olabilecek ama bu alt kümede olmayan YAML yapısı."""


_ANAHTAR = re.compile(r"^([^\s#'\"\[\]{},&*!|>%@`-][^:#]*?|-[^\s:#][^:#]*?|\"[^\"]*\"|'[^']*')\s*:(?:\s+(.*)|$)")
_TAM_SAYI = re.compile(r"[-+]?\d+")
_ONDALIK = re.compile(r"[-+]?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?")
_KACIS = {"n": "\n", "t": "\t", "r": "\r", "0": "\0", '"': '"', "\\": "\\", "/": "/", " ": " ", "e": "\x1b"}


def ayir(metin):
    """(ön_bilgi_metni | None, gövde_metni, gövdenin_ilk_satır_no). İlk satır '---' olmalı."""
    metin = metin.removeprefix("﻿").replace("\r\n", "\n")
    satirlar = metin.split("\n")
    if not satirlar or satirlar[0].rstrip() != "---":
        return None, metin, 1
    for i in range(1, len(satirlar)):
        if satirlar[i].rstrip() in ("---", "..."):
            return "\n".join(satirlar[1:i]), "\n".join(satirlar[i + 1:]), i + 2
    return None, metin, 1


def oku(metin):
    """Ön bilgi metnini sözlüğe çevirir. Bozuk metinde ValueError (alt kümenin dışındaysa Desteklenmiyor)."""
    try:
        return _Ayristirici(metin).belge()
    except Desteklenmiyor as destek_yok:
        try:
            import yaml  # isteğe bağlı
        except ImportError:
            raise destek_yok from None
        try:
            d = yaml.safe_load(metin)
        except yaml.YAMLError as e:
            raise ValueError(str(e).splitlines()[0] if str(e) else "YAML hatası") from None
        if d is None:
            return {}
        if not isinstance(d, dict):
            raise ValueError("ön bilgi bir eşlem değil") from None  # noqa: TRY004  # tek hata türü
        return d


def _girinti(satir):
    return len(satir) - len(satir.lstrip(" "))


def _yorum_mu(satir):
    return satir.lstrip(" ").startswith("#")


class _Ayristirici:
    def __init__(self, metin):
        self.s = metin.split("\n")
        for no, satir in enumerate(self.s, 1):
            bas = satir[:len(satir) - len(satir.lstrip(" \t"))]
            if "\t" in bas:
                raise ValueError(f"satır {no}: girintide sekme")

    # --------------------------------------------------------------- gezinme
    def _sonraki(self, i):
        """i'den itibaren ilk anlamlı (boş ya da yorum olmayan) satırın indeksi."""
        while i < len(self.s) and (not self.s[i].strip() or _yorum_mu(self.s[i])):
            i += 1
        return i

    def belge(self):
        i = self._sonraki(0)
        if i >= len(self.s):
            return {}
        if self.s[i].lstrip().startswith("- ") or self.s[i].strip() == "-":
            raise ValueError("ön bilgi bir eşlem değil")
        deger, i = self._eslem(i, _girinti(self.s[i]))
        i = self._sonraki(i)
        if i < len(self.s):
            raise ValueError(f"satır {i + 1}: beklenmeyen girinti")
        return deger

    def _blok(self, i, ust):
        """ust girintisinden derin (ya da aynı girintide liste) bir blok; (değer, yeni_i)."""
        j = self._sonraki(i)
        if j >= len(self.s):
            return None, j
        g = _girinti(self.s[j])
        satir = self.s[j].lstrip(" ")
        liste = satir.startswith("- ") or satir == "-"
        if g < ust or (g == ust and not liste):
            return None, j
        if liste:
            return self._liste(j, g)
        return self._eslem(j, g)

    # --------------------------------------------------------------- eşlem
    def _eslem(self, i, g):
        sonuc = {}
        while True:
            i = self._sonraki(i)
            if i >= len(self.s) or _girinti(self.s[i]) < g:
                return sonuc, i
            if _girinti(self.s[i]) > g:
                raise ValueError(f"satır {i + 1}: beklenmeyen girinti")
            satir = self.s[i][g:]
            if satir.startswith("- ") or satir == "-":
                return sonuc, i
            if satir.startswith(("? ", "<<")):
                raise Desteklenmiyor(f"satır {i + 1}: karmaşık anahtar")
            m = _ANAHTAR.match(satir)
            if not m:
                raise ValueError(f"satır {i + 1}: tanınmayan satır: {satir.strip()[:60]}")
            anahtar = m.group(1).strip()
            if anahtar[:1] in "\"'":
                anahtar = anahtar[1:-1]
            if anahtar in sonuc:
                raise ValueError(f"satır {i + 1}: yinelenen anahtar: {anahtar}")
            deger, i = self._deger(m.group(2) or "", i, g)
            sonuc[anahtar] = deger

    # --------------------------------------------------------------- liste
    def _liste(self, i, g):
        sonuc = []
        while True:
            i = self._sonraki(i)
            if i >= len(self.s) or _girinti(self.s[i]) < g:
                return sonuc, i
            satir = self.s[i][g:]
            if _girinti(self.s[i]) > g or not (satir.startswith("- ") or satir == "-"):
                if _girinti(self.s[i]) == g:
                    return sonuc, i
                raise ValueError(f"satır {i + 1}: beklenmeyen girinti")
            ic = satir[2:] if satir != "-" else ""
            ic_g = g + 2 + _girinti(ic)
            ic = ic.lstrip(" ")
            if not ic or _yorum_mu(ic):
                deger, i = self._blok(i + 1, g + 1)
            elif _ANAHTAR.match(ic):
                # "- anahtar: değer" → girintisi ic_g olan bir eşlem
                self.s[i] = " " * ic_g + ic
                deger, i = self._eslem(i, ic_g)
            elif ic.startswith("- "):
                raise Desteklenmiyor(f"satır {i + 1}: iç içe satır içi liste")
            else:
                deger, i = self._deger(ic, i, g)
            sonuc.append(deger)

    # --------------------------------------------------------------- değer
    def _deger(self, ham, i, g):
        """Anahtar ya da liste ögesinin değeri; ham satırın i'deki kalanıdır. (değer, yeni_i)."""
        ham = ham.strip()
        if ham == "" or ham.startswith("#"):
            return self._blok(i + 1, g)
        bas = ham[0]
        if bas in "|>":
            return self._blok_skaler(ham, i, g)
        if bas in "\"'":
            return self._tirnakli(ham, i, g)
        if bas == "[":
            return _akis_liste(ham, i), i + 1
        if bas == "{":
            return _akis_eslem(ham, i), i + 1
        if bas in "&*!":
            raise Desteklenmiyor(f"satır {i + 1}: çapa/takma ad/etiket")
        if bas in "%@`" or ham.startswith(("- ", "? ", ": ")) or ham in ("-", "?"):
            raise ValueError(f"satır {i + 1}: düz değer '{bas}' ile başlayamaz")
        return self._duz(ham, i, g)

    def _duz(self, ham, i, g):
        parcalar = [_duz_satir(ham, i)]
        j = i + 1
        bosluk = 0
        while j < len(self.s):
            satir = self.s[j]
            if not satir.strip():
                bosluk += 1
                j += 1
                continue
            if _girinti(satir) <= g:
                break
            if _yorum_mu(satir):
                raise ValueError(f"satır {j + 1}: çok satırlı düz değerin içinde yorum")
            parcalar.append("\n" * bosluk if bosluk else " ")
            parcalar.append(_duz_satir(satir.strip(), j))
            bosluk = 0
            j += 1
        metin = "".join(parcalar)
        return (_skaler(metin) if len(parcalar) == 1 else metin), j

    def _tirnakli(self, ham, i, g):
        metin = ham
        j = i
        while True:
            try:
                deger, kalan = _tirnak_coz(metin)
                break
            except _Kapanmadi:
                j += 1
                if j >= len(self.s) or (self.s[j].strip() and _girinti(self.s[j]) <= g):
                    raise ValueError(f"satır {i + 1}: kapanmamış tırnak") from None
                metin += (" " if self.s[j].strip() else "\n") + self.s[j].strip()
        kalan = kalan.strip()
        if kalan and not kalan.startswith("#"):
            raise ValueError(f"satır {j + 1}: tırnaktan sonra beklenmeyen metin: {kalan[:30]}")
        return deger, j + 1

    def _blok_skaler(self, ham, i, g):
        m = re.fullmatch(r"([|>])([-+]?)(\d?)([-+]?)\s*(#.*)?", ham)
        if not m:
            raise ValueError(f"satır {i + 1}: geçersiz blok başlığı: {ham[:20]}")
        stil, kesim = m.group(1), m.group(2) or m.group(4)
        satirlar = []
        j = i + 1
        while j < len(self.s) and (not self.s[j].strip() or _girinti(self.s[j]) > g):
            satirlar.append(self.s[j])
            j += 1
        dolu = [s for s in satirlar if s.strip()]
        if m.group(3):
            ic = g + int(m.group(3))
        else:
            ic = _girinti(dolu[0]) if dolu else g + 1
        govde = []
        for no, s in enumerate(satirlar, i + 2):
            if s.strip() and _girinti(s) < ic:
                raise ValueError(f"satır {no}: blok içinde girinti azaldı")
            govde.append(s[ic:] if s.strip() else "")
        sondaki = 0
        while govde and govde[-1] == "":
            govde.pop()
            sondaki += 1
        metin = "\n".join(govde) if stil == "|" else _katla(govde)
        if kesim == "-" or not govde:
            son = ""
        elif kesim == "+":
            son = "\n" * (1 + sondaki)
        else:
            son = "\n"
        return metin + son, j


def _katla(satirlar):
    """> bloğu: ardışık normal satırlar boşlukla, boş satırlar satır sonuyla birleşir;
    daha girintili satırların satır sonları korunur."""
    cikti = []
    onceki = None
    bos = 0
    for s in satirlar:
        if s == "":
            bos += 1
            continue
        girintili = s[0] in " \t"
        if onceki is None:
            cikti.append("\n" * bos)
        elif onceki == "normal" and not girintili:
            cikti.append("\n" * bos if bos else " ")
        else:
            cikti.append("\n" * (bos + 1))
        cikti.append(s)
        bos = 0
        onceki = "girintili" if girintili else "normal"
    return "".join(cikti)


def _duz_satir(metin, i):
    """Düz değer satırı: ' #' yorumu atılır; ': ' ve sondaki ':' YAML'da geçersizdir."""
    metin = re.sub(r"\s+#.*$", "", metin).rstrip()
    if ": " in metin or metin.endswith(":"):
        raise ValueError(f"satır {i + 1}: düz değerde ': ' var; değeri tırnağa alın ya da '>-' bloğu kullanın")
    if "\t#" in metin:
        raise ValueError(f"satır {i + 1}: düz değerde sekme ve yorum")
    return metin


class _Kapanmadi(Exception):
    pass


def _tirnak_coz(metin):
    """Metnin başındaki tırnaklı değeri çözer: (değer, kalan). Kapanmazsa _Kapanmadi."""
    k = metin[0]
    i = 1
    cikti = []
    while i < len(metin):
        c = metin[i]
        if k == "'" and c == "'":
            if metin[i + 1:i + 2] == "'":
                cikti.append("'")
                i += 2
                continue
            return "".join(cikti), metin[i + 1:]
        if k == '"' and c == '"':
            return "".join(cikti), metin[i + 1:]
        if k == '"' and c == "\\":
            n = metin[i + 1:i + 2]
            if n in _KACIS:
                cikti.append(_KACIS[n])
                i += 2
                continue
            if n in ("x", "u", "U"):
                uz = {"x": 2, "u": 4, "U": 8}[n]
                kod = metin[i + 2:i + 2 + uz]
                if not re.fullmatch(rf"[0-9a-fA-F]{{{uz}}}", kod):
                    raise ValueError("geçersiz kaçış dizisi: \\" + n + kod)
                cikti.append(chr(int(kod, 16)))
                i += 2 + uz
                continue
            if n == "":
                raise _Kapanmadi
            raise ValueError("geçersiz kaçış dizisi: \\" + n)
        cikti.append(c)
        i += 1
    raise _Kapanmadi


def _skaler(v):
    """Düz skalerin türü (YAML 1.2 çekirdek şeması): null, bool, int, float, metin."""
    if v in ("", "~", "null", "Null", "NULL"):
        return None
    if v in ("true", "True", "TRUE"):
        return True
    if v in ("false", "False", "FALSE"):
        return False
    if _TAM_SAYI.fullmatch(v):
        return int(v)
    if _ONDALIK.fullmatch(v):
        return float(v)
    return v


def _akis_bol(ic, i):
    parcalar, tampon, tirnak = [], "", None
    for c in ic:
        if tirnak:
            tampon += c
            if c == tirnak:
                tirnak = None
        elif c in "\"'":
            tirnak = c
            tampon += c
        elif c in "[]{}":
            raise Desteklenmiyor(f"satır {i + 1}: iç içe akış yapısı")
        elif c == ",":
            parcalar.append(tampon.strip())
            tampon = ""
        else:
            tampon += c
    if tirnak:
        raise ValueError(f"satır {i + 1}: kapanmamış tırnak")
    if tampon.strip():
        parcalar.append(tampon.strip())
    return parcalar


def _akis_ogesi(p, i):
    if p[:1] in "\"'":
        deger, kalan = _tirnak_coz(p)
        if kalan.strip():
            raise ValueError(f"satır {i + 1}: tırnaktan sonra beklenmeyen metin")
        return deger
    if p[:1] in "&*!":
        raise Desteklenmiyor(f"satır {i + 1}: çapa/takma ad/etiket")
    return _skaler(p)


def _akis_kapat(ham, ac, kapa, i):
    ham = re.sub(r"\s+#[^\"']*$", "", ham).rstrip()
    if not ham.endswith(kapa):
        raise ValueError(f"satır {i + 1}: '{ac}' aynı satırda kapanmalı")
    return ham[1:-1]


def _akis_liste(ham, i):
    return [_akis_ogesi(p, i) for p in _akis_bol(_akis_kapat(ham, "[", "]", i), i)]


def _akis_eslem(ham, i):
    sonuc = {}
    for p in _akis_bol(_akis_kapat(ham, "{", "}", i), i):
        if ":" not in p:
            raise ValueError(f"satır {i + 1}: akış eşleminde ':' yok")
        a, d = p.split(":", 1)
        a = _akis_ogesi(a.strip(), i)
        if a in sonuc:
            raise ValueError(f"satır {i + 1}: yinelenen anahtar: {a}")
        sonuc[a] = _akis_ogesi(d.strip(), i)
    return sonuc
