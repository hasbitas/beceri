"""Doğrulama ayarı: `.beceri.toml` ya da `pyproject.toml` içindeki `[tool.beceri]`.

Arama: `--ayar DOSYA` verilmişse yalnız o. Yoksa çalışma klasöründen köke doğru ilk `.beceri.toml` ya da
`[tool.beceri]` tablosu olan `pyproject.toml`; `.git` içeren klasörde arama durur. Bilinmeyen anahtar ve
bilinmeyen kural kimliği ValueError'dur (komut 2 ile çıkar).

    kapali = ["B20"]                  # kapatılan kurallar
    kati = false                      # uyarılar da çıkışı 1 yapar
    ek_alanlar = ["x-ekip"]           # izin verilen ek ön bilgi alanları
    ayrilmis_adlar = ["claude", "anthropic"]
    model_adlari = ["ozel-model"]     # B16 için ek model adları (sözcük olarak aranır)
    atla = [".*", "node_modules"]     # taramada atlanan klasör adları (glob)

    [sinirlar]
    govde_uyari_satir = 200

    [onem]
    B16 = "uyari"

    [[muaf]]
    skill = "eski-skill"
    kural = "B23"
    gerekce = "tablo satırları"
"""
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path

from beceri.kurallar import KURAL, ONEMLER

SINIRLAR = {
    "ad_azami": 64,
    "aciklama_azami": 1024,
    "aciklama_uyari": 500,
    "tetik_karakter": 200,
    "uyumluluk_azami": 500,
    "govde_azami_satir": 500,
    "govde_uyari_satir": 150,
    "govde_uyari_kb": 12,
    "uzun_satir": 120,
    "uzun_satir_oran": 0.20,
    "referans_icindekiler_satir": 100,
}
_ANAHTARLAR = {"kapali", "kati", "ek_alanlar", "ayrilmis_adlar", "model_adlari", "atla", "sinirlar", "onem", "muaf"}
_MUAF_ANAHTAR = {"skill", "kural", "gerekce"}


@dataclass(frozen=True)
class Ayar:
    kapali: frozenset = frozenset()
    kati: bool = False
    ek_alanlar: frozenset = frozenset()
    ayrilmis_adlar: tuple = ("claude", "anthropic")
    model_adlari: tuple = ()
    atla: tuple = (".*", "__pycache__", "node_modules")
    sinirlar: dict = field(default_factory=lambda: dict(SINIRLAR))
    onem: dict = field(default_factory=dict)
    muaf: dict = field(default_factory=dict)  # (skill, kural) -> gerekçe
    kaynak: str = ""

    def onemi(self, kimlik):
        return self.onem.get(kimlik, KURAL[kimlik].onem)

    def acik(self, kimlik):
        return kimlik not in self.kapali

    def kapat(self, kimlikler):
        kimlikler = {k.strip().upper() for k in kimlikler if k.strip()}
        _kimlikleri_denetle(kimlikler, "--kapat")
        return replace(self, kapali=self.kapali | kimlikler)


def _kimlikleri_denetle(kimlikler, alan):
    bilinmeyen = sorted(k for k in kimlikler if k not in KURAL)
    if bilinmeyen:
        raise ValueError(f"{alan}: bilinmeyen kural: {', '.join(bilinmeyen)}")


def _metin_listesi(deger, alan):
    if not isinstance(deger, list) or not all(isinstance(x, str) and x.strip() for x in deger):
        raise ValueError(f"{alan} metin listesi olmalı")
    return [x.strip() for x in deger]


def ayar_kur(ham, kaynak=""):
    """Ham sözlükten Ayar; hatalı içerikte ValueError."""
    if not isinstance(ham, dict):
        raise ValueError("ayar bir tablo olmalı")  # noqa: TRY004  # ayar hataları tek türdür
    bilinmeyen = sorted(set(ham) - _ANAHTARLAR)
    if bilinmeyen:
        raise ValueError(f"bilinmeyen ayar anahtarı: {', '.join(bilinmeyen)}")
    a = Ayar(kaynak=kaynak)
    if "kapali" in ham:
        kapali = {x.upper() for x in _metin_listesi(ham["kapali"], "kapali")}
        _kimlikleri_denetle(kapali, "kapali")
        a = replace(a, kapali=frozenset(kapali))
    if "kati" in ham:
        if not isinstance(ham["kati"], bool):
            raise ValueError("kati true/false olmalı")
        a = replace(a, kati=ham["kati"])
    if "ek_alanlar" in ham:
        a = replace(a, ek_alanlar=frozenset(_metin_listesi(ham["ek_alanlar"], "ek_alanlar")))
    if "ayrilmis_adlar" in ham:
        a = replace(a, ayrilmis_adlar=tuple(x.lower() for x in _metin_listesi(ham["ayrilmis_adlar"], "ayrilmis_adlar")))
    if "model_adlari" in ham:
        a = replace(a, model_adlari=tuple(_metin_listesi(ham["model_adlari"], "model_adlari")))
    if "atla" in ham:
        a = replace(a, atla=tuple(_metin_listesi(ham["atla"], "atla")))
    if "sinirlar" in ham:
        s = ham["sinirlar"]
        if not isinstance(s, dict):
            raise ValueError("sinirlar bir tablo olmalı")
        sinirlar = dict(SINIRLAR)
        for k, v in s.items():
            if k not in SINIRLAR:
                raise ValueError(f"bilinmeyen sınır: {k}")
            tur = float if isinstance(SINIRLAR[k], float) else int
            if isinstance(v, bool) or not isinstance(v, (int, float)) or (tur is int and not isinstance(v, int)):
                raise ValueError(f"sinirlar.{k} sayı olmalı")
            if v <= 0:
                raise ValueError(f"sinirlar.{k} pozitif olmalı")
            sinirlar[k] = tur(v)
        a = replace(a, sinirlar=sinirlar)
    if "onem" in ham:
        o = ham["onem"]
        if not isinstance(o, dict):
            raise ValueError("onem bir tablo olmalı")
        onem = {}
        for k, v in o.items():
            _kimlikleri_denetle({k.upper()}, "onem")
            if v not in ONEMLER:
                raise ValueError(f"onem.{k}: 'hata' ya da 'uyari' olmalı")
            onem[k.upper()] = v
        a = replace(a, onem=onem)
    if "muaf" in ham:
        if not isinstance(ham["muaf"], list):
            raise ValueError("muaf bir tablo dizisi olmalı ([[muaf]])")
        muaf = {}
        for m in ham["muaf"]:
            if not isinstance(m, dict) or set(m) != _MUAF_ANAHTAR:
                raise ValueError("her [[muaf]] yalnız skill, kural ve gerekce taşır")
            if not all(isinstance(m[x], str) and m[x].strip() for x in _MUAF_ANAHTAR):
                raise ValueError("muaf: skill, kural ve gerekce boş olmayan metin olmalı")
            _kimlikleri_denetle({m["kural"].upper()}, "muaf")
            muaf[(m["skill"].strip(), m["kural"].upper())] = m["gerekce"].strip()
        a = replace(a, muaf=muaf)
    return a


def dosyadan(yol):
    """Ayar dosyasını okur. pyproject.toml ise [tool.beceri] tablosu alınır (yoksa varsayılan)."""
    yol = Path(yol)
    try:
        veri = tomllib.loads(yol.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
        raise ValueError(f"ayar okunamadı: {yol}: {e}") from None
    if yol.name == "pyproject.toml":
        veri = veri.get("tool", {}).get("beceri", {})
    try:
        return ayar_kur(veri, str(yol))
    except ValueError as e:
        raise ValueError(f"{yol}: {e}") from None


def bul(baslangic):
    """baslangic'tan köke doğru ilk ayar dosyası; yoksa None."""
    d = Path(baslangic).resolve()
    for klasor in (d, *d.parents):
        aday = klasor / ".beceri.toml"
        if aday.is_file():
            return aday
        py = klasor / "pyproject.toml"
        if py.is_file():
            try:
                veri = tomllib.loads(py.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
                veri = {}
            if "beceri" in veri.get("tool", {}):
                return py
        if (klasor / ".git").exists():
            return None
    return None


def yukle(acik_yol=None, baslangic="."):
    """--ayar verilmişse onu, yoksa bulunan dosyayı; hiçbiri yoksa varsayılan Ayar."""
    if acik_yol:
        return dosyadan(acik_yol)
    bulunan = bul(baslangic)
    return dosyadan(bulunan) if bulunan else Ayar()
