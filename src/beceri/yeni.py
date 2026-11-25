"""Yeni skill iskeleti: `<hedef>/<ad>/SKILL.md` profilin şablonundan yazılır.

`esnek` (varsayılan) genel şablonu, `siki` sabit bölüm sıralı şablonu kullanır. Şablondaki `DOLDUR` yer
tutucuları B25 uyarısı verir; iskelet kendi profilinde hatasız doğrulanır, doldurulunca uyarı kalkar.
"""
import textwrap
from importlib import resources
from pathlib import Path

from beceri.dogrula import AD_DESENI
from beceri.kurallar import ESNEK, PROFILLER, SIKI

VARSAYILAN_ACIKLAMA = ("DOLDUR - skill'in yaptığı işi ve onu tetikleyen isteği yaz. Kullan - kullanıcı bu işi "
                       "istediğinde. Kullanma - benzer görünen ama başka bir iş için.")
SABLONLAR = {ESNEK: "sablon/skill-sablonu.md", SIKI: "sablon/skill-sablonu-siki.md"}


def sablon_metni(profil=ESNEK):
    if profil not in PROFILLER:
        raise ValueError(f"bilinmeyen profil: {profil}")
    return resources.files("beceri").joinpath(SABLONLAR[profil]).read_text(encoding="utf-8")


def ad_denetle(ad, ayrilmis=("claude", "anthropic"), azami=64):
    """Geçersiz adda ValueError."""
    if len(ad) > azami or not AD_DESENI.match(ad):
        raise ValueError(f"geçersiz ad (küçük harf, rakam, tek tire; en çok {azami}): {ad}")
    for s in ayrilmis:
        if s in ad:
            raise ValueError(f"ad ayrılmış sözcük içeriyor: {s}")


def olustur_metin(ad, aciklama=None, profil=ESNEK, isaretle=None):
    """Şablonu ad ve açıklamayla doldurulmuş SKILL.md metni olarak döndürür.

    isaretle: ön bilgiye `metadata.profil` yazılsın mı (varsayılan: yalnız siki şablonunda; o şablon zaten
    taşır). Ayarın varsayılanı siki olan bir depoda esnek skill açılırken işaret gerekir.
    """
    aciklama = (aciklama or VARSAYILAN_ACIKLAMA).strip()
    if not aciklama:
        raise ValueError("açıklama boş olamaz")
    if "<" in aciklama or ">" in aciklama:
        raise ValueError("açıklama '<' ya da '>' içeremez")
    if len(aciklama) > 1024:
        raise ValueError("açıklama 1024 karakteri aşamaz")
    satirlar = []
    for paragraf in aciklama.splitlines():
        satirlar += ["  " + s for s in textwrap.wrap(paragraf.strip(), 100)] or [""]
    girintili = "\n".join(satirlar)
    baslik = ad.replace("-", " ")
    baslik = baslik[:1].upper() + baslik[1:]
    metin = (sablon_metni(profil).replace("__AD__", ad).replace("__ACIKLAMA__", girintili)
             .replace("__BASLIK__", baslik))
    if isaretle and profil == ESNEK:
        metin = metin.replace("\nmetadata:\n", f'\nmetadata:\n  profil: "{ESNEK}"\n', 1)
    return metin


def olustur(ad, hedef=".", aciklama=None, ayrilmis=("claude", "anthropic"), azami=64, profil=ESNEK,
            isaretle=None):
    """Skill klasörünü oluşturur ve yolunu döndürür. Klasör varsa FileExistsError."""
    ad_denetle(ad, ayrilmis, azami)
    metin = olustur_metin(ad, aciklama, profil, isaretle)
    klasor = Path(hedef) / ad
    if klasor.exists():
        raise FileExistsError(f"zaten var: {klasor}")
    klasor.mkdir(parents=True)
    (klasor / "SKILL.md").write_bytes(metin.encode("utf-8"))
    return klasor
