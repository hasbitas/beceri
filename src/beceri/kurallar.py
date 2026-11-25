"""Doğrulama kuralları: kalıcı kimlik, önem, profil ve tek satırlık açıklama.

Kimlikler kalıcıdır: bir kural kaldırılırsa kimliği yeniden kullanılmaz. Önem `hata` ya da `uyari`dır;
ayar dosyasında `[onem]` ile değiştirilebilir, `kapali` ile kural kapatılır.

Profil: B kuralları iki profilde de (`ortak`) denetlenir; tek istisna B19'dur, `siki` profilde aynı sınırı
S04 hata olarak sahiplenir. S kuralları yalnız `siki` profilde denetlenir.
"""
from dataclasses import dataclass

HATA = "hata"
UYARI = "uyari"
ONEMLER = (HATA, UYARI)
ESNEK = "esnek"
SIKI = "siki"
PROFILLER = (ESNEK, SIKI)
ORTAK = "ortak"


@dataclass(frozen=True)
class Kural:
    kimlik: str
    onem: str
    aciklama: str
    profil: str = ORTAK  # ortak: her profilde; esnek ya da siki: yalnız o profilde


KURALLAR = (
    Kural("B01", HATA, "Skill klasöründe SKILL.md yok."),
    Kural("B02", HATA, "Ön bilgi (YAML frontmatter) yok, kapanmıyor ya da ayrıştırılamıyor."),
    Kural("B03", HATA, "name yok ya da biçimi geçersiz (küçük harf, rakam, tek tire; en çok 64 karakter)."),
    Kural("B04", HATA, "name skill klasörünün (ya da ona giden bağlantının) adıyla aynı değil."),
    Kural("B05", HATA, "name ayrılmış bir sözcük içeriyor (varsayılan: claude, anthropic)."),
    Kural("B06", HATA, "description yok, boş, metin değil ya da azami uzunluğu (1024) aşıyor."),
    Kural("B07", HATA, "description '<' ya da '>' içeriyor (etiket gibi yorumlanabilir)."),
    Kural("B08", HATA, "Bilinmeyen ön bilgi alanı (ek alanlara ayarda izin verilebilir)."),
    Kural("B09", HATA, "compatibility metin değil ya da çok uzun; metadata metin→metin eşlemi değil."),
    Kural("B10", HATA, "SKILL.md gövdesi azami satır sayısını (500) aşıyor."),
    Kural("B11", HATA, "SKILL.md'de anılan references/, scripts/ ya da assets/ yolu yok."),
    Kural("B12", HATA, "references/ dosyası başka bir referansa ya da SKILL.md'ye zincirleniyor (tek seviye kalmalı)."),
    Kural("B13", HATA, "Skill ağacında yedek ya da artık dosya var (*.bak, *.orig, *~, SKILL.v*.md)."),
    Kural("B14", HATA, "Makineye özgü ev dizini yolu var (/home/<ad>, /Users/<ad>, C:\\Users\\<ad>, /root)."),
    Kural("B15", HATA, "Sır görünümlü değer var (bilinen anahtar biçimi, özel anahtar ya da atanmış uzun token)."),
    Kural("B16", HATA, "Modelden bağımsız ilan edilen skill'in gövdesinde model adı geçiyor."),
    Kural("B17", UYARI, "description ne zaman kullanılmayacağını söylemiyor (Kullanma / Do not / Not for)."),
    Kural("B18", UYARI, "description tetikleyicisi ilk 200 karakterde yok ya da description 500 karakteri aşıyor."),
    Kural("B19", UYARI, "SKILL.md gövdesi önerilen boyutu (150 satır ya da 12 KB) aşıyor.", ESNEK),
    Kural("B20", UYARI, "Gövdede tarih var; skill metni zamana bağlı bilgi taşımamalı."),
    Kural("B21", UYARI, "100 satırı aşan references/ dosyasında içindekiler bölümü yok."),
    Kural("B22", UYARI, "Aynı name taranan başka bir skill klasöründe de var."),
    Kural("B23", UYARI, "Gövde satırlarının %20'den fazlası 120 karakteri aşıyor."),
    Kural("B24", UYARI, "Platforma özgü ön bilgi alanı var ama compatibility yazılmamış."),
    Kural("B25", UYARI, "Şablondan kalan doldurulmamış yer tutucu (DOLDUR) var."),
    Kural("B26", HATA, "metadata.profil bilinmeyen bir değer taşıyor (esnek ya da siki olmalı)."),
    Kural("S01", HATA, "Başlık (# ...) yok, ilk başlık değil ya da zorunlu ## bölümlerinden biri eksik.", SIKI),
    Kural("S02", HATA, "## bölümleri sabit sırada değil, tanımsız ya da tekrarlanan ## bölüm var.", SIKI),
    Kural("S03", HATA, "## Amaç bölümü boş ya da azami satır sayısını (2) aşıyor.", SIKI),
    Kural("S04", HATA, "SKILL.md gövdesi 150 satırı ya da 12 KB'ı aşıyor (siki profilde sert sınır).", SIKI),
    Kural("S05", HATA, "## Adımlar'da adım yok ya da bir adım satırı nesne, eylem, yetki ve kanıt taşımıyor.", SIKI),
    Kural("S06", UYARI, "Gövdede ölçüm sonucu ya da ISO dışı tarih var; tarihçe references/ altına gider.", SIKI),
    Kural("S07", HATA, "references/ altında alt klasör var; referanslar tek seviye kalmalı.", SIKI),
)

KURAL = {k.kimlik: k for k in KURALLAR}
