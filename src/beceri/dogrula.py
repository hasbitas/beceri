"""Skill klasörü doğrulama: tek skill ya da skill ağacı.

Kurallar `beceri.kurallar` içinde; sınırlar ve kapatılan kurallar `beceri.ayar` ile gelir. Model ya da ağ
çağrısı yoktur; dosyalar yalnız okunur. Sır görünümlü değerin kendisi asla rapora yazılmaz, yalnız yeri.
"""
import fnmatch
import os
import posixpath
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from beceri import onbilgi
from beceri.ayar import Ayar
from beceri.kurallar import HATA

SKILL_DOSYASI = "SKILL.md"
AD_DESENI = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TEMEL_ALANLAR = frozenset({"name", "description", "license", "compatibility", "metadata", "allowed-tools"})
# Bir platformun (Claude Code) tanıdığı ama açık skill biçiminde olmayan alanlar: compatibility ile anılmalı.
PLATFORM_ALANLARI = frozenset({"disable-model-invocation", "user-invocable", "when_to_use", "paths", "model",
                               "effort", "context", "hooks", "argument-hint", "disallowed-tools"})
KIRLI_KALIPLAR = ("*.bak", "*.bak.*", "*.orig", "*~", "SKILL.v*.md")
MODEL_BAGIMSIZ_ANAHTAR = ("model-agnostic", "model-bagimsiz")
EVET = ("true", "evet", "yes", "1")
TARIH = re.compile(r"(?<!\d)(?:19|20)\d\d-[01]\d-[0-3]\d(?!\d)")
YER_TUTUCU = re.compile(r"\bDOLDUR\b")
OLUMSUZ = ("kullanma", "do not", "don't", "not for", "not when", "never use", "avoid when")
TETIK = re.compile(r"(?i)\b(use|used|using|kullan\w*|tetik\w*|trigger\w*|when)\b")
ICINDEKILER = re.compile(r"(?i)[iİI]̇?çindekiler|\bcontents\b")
# Model kimlikleri ve aile adları; ürün adları (ör. bir CLI) sayılmaz. Ayarda model_adlari ile genişler.
MODEL_KALIPLARI = (r"gpt-\w[\w.-]*", r"claude-[\w.-]+", r"gemini-[\w.-]+", r"llama-?\d[\w.-]*", r"mistral-[\w.-]+",
                   r"mixtral-[\w.-]+", r"deepseek-[\w.-]+", r"qwen[\d.]*-[\w.-]+", "sonnet", "opus", "haiku")
EV_YOLU = re.compile(
    r"(?<![\w.~-])(?:/(?:ho" r"me|Us" r"ers)/(?!<)[A-Za-z0-9._-]+|/root(?![\w.-])"
    r"|[A-Za-z]:[\\/]+Us" r"ers[\\/]+(?!<)[^\\/\s<>\"'`]+)")
SIR_KALIPLARI = (
    ("özel anahtar", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS erişim anahtarı", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})\b")),
    ("GitLab token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b")),
    ("Google API anahtarı", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("API anahtarı (sk-)", re.compile(r"\bsk-(?:[a-z]+-)?[A-Za-z0-9_-]{20,}\b")),
)
SIR_ATAMA = re.compile(
    r"(?i)\b(?:api[_-]?key|secret|token|passw(?:or)?d|access[_-]?key|auth[_-]?token)\w*[\"']?\s*[:=]\s*"
    r"[\"']([^\"'\s]{16,})[\"']")
YER_TUTUCU_SIR = re.compile(r"(?i)[<>{}$]|x{4,}|\.\.\.|your|example|ornek|örnek|changeme|placeholder|dummy|fake")
METIN_AZAMI = 1024 * 1024


@dataclass
class Bulgu:
    kural: str
    mesaj: str
    dosya: str | None = None
    satir: int | None = None
    gerekce: str | None = None

    def yer(self):
        if not self.dosya:
            return ""
        return f"{self.dosya}:{self.satir}" if self.satir else self.dosya


@dataclass
class Sonuc:
    yol: str
    ad: str | None = None
    hatalar: list = field(default_factory=list)
    uyarilar: list = field(default_factory=list)
    muaflar: list = field(default_factory=list)
    olcum: dict = field(default_factory=dict)

    def sozluk(self):
        return {"yol": self.yol, "ad": self.ad,
                "hatalar": [asdict(b) for b in self.hatalar],
                "uyarilar": [asdict(b) for b in self.uyarilar],
                "muaflar": [asdict(b) for b in self.muaflar],
                "olcum": self.olcum}


class _Kayit:
    """Bir skill'in bulgularını ayara göre (kapalı, önem, muafiyet) toplar."""

    def __init__(self, sonuc, giris_adi, ayar):
        self.sonuc = sonuc
        self.giris_adi = giris_adi
        self.ayar = ayar

    def __call__(self, kural, mesaj, dosya=None, satir=None):
        if not self.ayar.acik(kural):
            return
        b = Bulgu(kural, mesaj, dosya, satir)
        gerekce = self.ayar.muaf.get((self.giris_adi, kural))
        if gerekce is None and self.sonuc.ad:
            gerekce = self.ayar.muaf.get((self.sonuc.ad, kural))
        if gerekce is not None:
            b.gerekce = gerekce
            self.sonuc.muaflar.append(b)
        elif self.ayar.onemi(kural) == HATA:
            self.sonuc.hatalar.append(b)
        else:
            self.sonuc.uyarilar.append(b)


# ------------------------------------------------------------------ yardımcılar
def metin_oku(yol):
    return Path(yol).read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n")


def kod_bloklarini_at(metin):
    """Çitli kod bloklarını, satır sayısı korunacak biçimde boşaltır."""
    return re.sub(r"^(```|~~~).*?^\1[^\n]*$", lambda m: "\n" * m.group(0).count("\n"), metin,
                  flags=re.DOTALL | re.MULTILINE)


def goreli_yollar(metin):
    """SKILL.md içinde backtick ya da bağlantıyla anılan references/ scripts/ assets/ yolları."""
    duz = kod_bloklarini_at(metin)
    parcalar = re.findall(r"`([^`\n]+)`", duz) + re.findall(r"\]\(([^)\s]+)\)", duz)
    bulunan = []
    for p in parcalar:
        p = re.sub(r"(?<![\w.~/\-])\./", "", p)
        for m in re.finditer(r"(?<![\w/.~\-])((?:references|scripts|assets)/[^\s`)\]>\"'*<{}|;,]+)", p):
            y = m.group(1).split("#")[0].rstrip(".,:;")
            if y and not y.endswith("/") and y not in bulunan:
                bulunan.append(y)
    return bulunan


def _skill_icinde_md(t, kok, ref_dizin):
    """t, referans klasörüne ya da skill köküne göre skill içinde var olan bir .md dosyası mı?"""
    t = t.split("#")[0]
    if not t.lower().endswith(".md") or t.startswith(("~", "/", "$")):
        return False
    kok_gercek = os.path.realpath(kok)
    for taban in (ref_dizin, kok):
        p = os.path.realpath(os.path.join(taban, *t.split("/")))
        if os.path.isfile(p) and os.path.commonpath([kok_gercek, p]) == kok_gercek:
            return True
    return False


def zincir_baglantilari(duz, kok, ref_dizin):
    """references/*.md içindeki zincir bağlantılar: [(yol, neden)]. assets/ ve scripts/ serbesttir."""
    adaylar = list(re.findall(r"\]\(([^)\s]+)\)", duz))
    for sp in re.findall(r"`([^`\n]+)`", duz):
        for t in sp.split():
            if "/" not in t and not t.lower().endswith(".md"):
                continue
            ham = t.strip("\"'").rstrip(".,;:")
            if ham.startswith(("references/", "./", "../")) or _skill_icinde_md(ham, kok, ref_dizin):
                adaylar.append(t)
    bulunan = []
    for t in adaylar:
        t = t.split("#")[0].split("?")[0].strip("\"'").rstrip(".,;:")
        if not t or re.match(r"^[a-z][a-z0-9+.-]*:", t, re.IGNORECASE) or t.startswith(("~", "/", "$")) \
                or any(c in t for c in "<>*{}|"):
            continue
        n = posixpath.normpath(t)
        if n.startswith("../"):
            n = n[3:]
        elif n.split("/")[0] == "..":
            continue
        ilk = n.split("/")[0]
        if ilk in ("assets", "scripts"):
            continue
        if ilk == "references" or "/references/" in "/" + n:
            neden = "references/"
        elif n == SKILL_DOSYASI:
            neden = SKILL_DOSYASI
        elif n.lower().endswith(".md"):
            neden = "başka .md"
        else:
            continue
        if (t, neden) not in bulunan:
            bulunan.append((t, neden))
    return bulunan


def _atla(ad, ayar):
    return any(fnmatch.fnmatch(ad, k) for k in ayar.atla)


def _agac(kok, ayar):
    """Skill ağacındaki dosyalar (göreli posix yol, tam yol); atlanan klasörlere girilmez."""
    for d, altlar, dosyalar in os.walk(kok, followlinks=False):
        altlar[:] = sorted(a for a in altlar if not _atla(a, ayar))
        for ad in sorted(dosyalar):
            tam = os.path.join(d, ad)
            yield os.path.relpath(tam, kok).replace("\\", "/"), tam


def _metin_dosyasi(tam):
    try:
        if os.path.getsize(tam) > METIN_AZAMI:
            return None
        ham = Path(tam).read_bytes()
    except OSError:
        return None
    if b"\0" in ham:
        return None
    return ham.decode("utf-8", errors="replace").replace("\r\n", "\n")


def _model_bagimsiz(meta):
    if not isinstance(meta, dict):
        return False
    for a in MODEL_BAGIMSIZ_ANAHTAR:
        v = meta.get(a)
        if v is True or (isinstance(v, str) and v.strip().lower() in EVET):
            return True
    return False


def _model_deseni(ayar):
    kaliplar = MODEL_KALIPLARI + tuple(re.escape(x) for x in ayar.model_adlari)
    return re.compile(r"(?i)(?<![\w-])(?:" + "|".join(kaliplar) + r")(?![\w-])")


# ------------------------------------------------------------------ tek skill
def skill_denetle(klasor, ayar=None, giris_adi=None, etiket=None):
    """Tek skill klasörünü denetler. giris_adi: taramada görünen ad (bağlantı adı olabilir)."""
    ayar = ayar or Ayar()
    klasor = Path(klasor)
    gercek = Path(os.path.realpath(klasor))
    giris_adi = giris_adi or klasor.resolve().name
    sonuc = Sonuc(yol=etiket or str(klasor))
    ekle = _Kayit(sonuc, giris_adi, ayar)
    sin = ayar.sinirlar

    sm = gercek / SKILL_DOSYASI
    if not sm.is_file():
        ekle("B01", "SKILL.md yok")
        return sonuc
    metin = metin_oku(sm)
    fm_metin, govde, govde_bas = onbilgi.ayir(metin)
    fm = {}
    if fm_metin is None:
        ekle("B02", "ön bilgi yok (ilk satır '---' değil ya da kapanış '---' yok)", SKILL_DOSYASI, 1)
    else:
        try:
            fm = onbilgi.oku(fm_metin)
        except ValueError as e:
            ekle("B02", f"ön bilgi ayrıştırılamadı: {e}", SKILL_DOSYASI)
            fm = {}

    govde_satirlari = govde.split("\n")
    if govde_satirlari and govde_satirlari[0] == "":
        govde_satirlari = govde_satirlari[1:]
    if govde_satirlari and govde_satirlari[-1] == "":
        govde_satirlari = govde_satirlari[:-1]
    govde_bayt = len(govde.encode("utf-8"))
    sonuc.olcum = {"govde_satir": len(govde_satirlari), "govde_kb": round(govde_bayt / 1024, 1),
                   "aciklama_uzunluk": 0}

    # B03 / B04 / B05: name
    ad = fm.get("name")
    if isinstance(ad, str) and ad:
        sonuc.ad = ad
    if fm_metin is not None and (ad is None or ad == ""):
        ekle("B03", "name yok", SKILL_DOSYASI)
    elif ad is not None and not isinstance(ad, str):
        ekle("B03", "name metin değil", SKILL_DOSYASI)
    elif isinstance(ad, str):
        if len(ad) > sin["ad_azami"] or not AD_DESENI.match(ad):
            ekle("B03", f"name biçimi geçersiz (küçük harf, rakam, tek tire; en çok {sin['ad_azami']}): {ad}",
                 SKILL_DOSYASI)
        if ad != gercek.name:
            ekle("B04", f"name '{ad}' klasör adı '{gercek.name}' ile aynı değil", SKILL_DOSYASI)
        elif ad != giris_adi:
            ekle("B04", f"name '{ad}' bağlantı adı '{giris_adi}' ile aynı değil", SKILL_DOSYASI)
        for sozcuk in ayar.ayrilmis_adlar:
            if sozcuk in ad.lower():
                ekle("B05", f"name ayrılmış sözcük içeriyor: {sozcuk}", SKILL_DOSYASI)

    # B06 / B07 / B17 / B18: description
    desc = fm.get("description")
    if fm_metin is not None and (desc is None or (isinstance(desc, str) and not desc.strip())):
        ekle("B06", "description yok ya da boş", SKILL_DOSYASI)
        desc = ""
    elif desc is not None and not isinstance(desc, str):
        ekle("B06", "description metin değil", SKILL_DOSYASI)
        desc = ""
    desc = (desc or "").strip()
    sonuc.olcum["aciklama_uzunluk"] = len(desc)
    if desc:
        if len(desc) > sin["aciklama_azami"]:
            ekle("B06", f"description {len(desc)} karakter (>{sin['aciklama_azami']})", SKILL_DOSYASI)
        if "<" in desc or ">" in desc:
            ekle("B07", "description '<' ya da '>' içeriyor", SKILL_DOSYASI)
        if not any(t in desc.lower() for t in OLUMSUZ):
            ekle("B17", "description'da sınır yok (ör. 'Kullanma - ...' ya da 'Do not use for ...')",
                 SKILL_DOSYASI)
        if len(desc) > sin["aciklama_uyari"]:
            ekle("B18", f"description {len(desc)} karakter (>{sin['aciklama_uyari']})", SKILL_DOSYASI)
        elif not TETIK.search(desc[:sin["tetik_karakter"]]):
            ekle("B18", f"ilk {sin['tetik_karakter']} karakterde tetikleyici yok (ör. 'Kullan - ...', 'Use when ...')",
                 SKILL_DOSYASI)

    # B08 / B24 / B09: alanlar
    comp = fm.get("compatibility")
    for alan in fm:
        if alan in TEMEL_ALANLAR or alan in ayar.ek_alanlar:
            continue
        if alan in PLATFORM_ALANLARI:
            if not comp:
                ekle("B24", f"platforma özgü alan '{alan}' var, compatibility yok", SKILL_DOSYASI)
        else:
            ekle("B08", f"bilinmeyen ön bilgi alanı: {alan}", SKILL_DOSYASI)
    if comp is not None:
        if not isinstance(comp, str):
            ekle("B09", "compatibility metin değil", SKILL_DOSYASI)
        elif len(comp) > sin["uyumluluk_azami"]:
            ekle("B09", f"compatibility {len(comp)} karakter (>{sin['uyumluluk_azami']})", SKILL_DOSYASI)
    meta = fm.get("metadata")
    if meta is not None:
        if not isinstance(meta, dict):
            ekle("B09", "metadata eşlem değil", SKILL_DOSYASI)
        else:
            for mk, mv in meta.items():
                if not isinstance(mv, str):
                    ekle("B09", f"metadata.{mk} metin değil (tırnağa alın)", SKILL_DOSYASI)

    # B10 / B19: gövde boyutu
    n = sonuc.olcum["govde_satir"]
    if n > sin["govde_azami_satir"]:
        ekle("B10", f"gövde {n} satır (>{sin['govde_azami_satir']}); ayrıntıyı references/ altına taşıyın",
             SKILL_DOSYASI)
    elif n > sin["govde_uyari_satir"] or govde_bayt > sin["govde_uyari_kb"] * 1024:
        ekle("B19", f"gövde {n} satır / {govde_bayt / 1024:.1f} KB "
                    f"(öneri: en çok {sin['govde_uyari_satir']} satır, {sin['govde_uyari_kb']} KB)", SKILL_DOSYASI)

    # B11: anılan yollar
    for y in goreli_yollar(metin):
        hedef = os.path.realpath(os.path.join(gercek, *y.split("/")))
        if not os.path.exists(hedef) or os.path.commonpath([str(gercek), hedef]) != str(gercek):
            ekle("B11", f"anılan yol yok: {y}", SKILL_DOSYASI)

    # B12 / B21: references/
    refdir = gercek / "references"
    if refdir.is_dir():
        for rel, tam in _agac(refdir, ayar):
            if not rel.lower().endswith(".md"):
                continue
            rel = "references/" + rel
            t = metin_oku(tam)
            for hedef, neden in zincir_baglantilari(kod_bloklarini_at(t), str(gercek), os.path.dirname(tam)):
                ekle("B12", f"referans zinciri ({neden}): {hedef}", rel)
            if len(t.split("\n")) > sin["referans_icindekiler_satir"] and not ICINDEKILER.search(t):
                ekle("B21", f"{sin['referans_icindekiler_satir']} satırdan uzun, içindekiler yok", rel)

    # B13 / B14 / B15: ağaçtaki dosyalar
    for rel, tam in _agac(gercek, ayar):
        ad_ = rel.rsplit("/", 1)[-1]
        if any(fnmatch.fnmatch(ad_, k) for k in KIRLI_KALIPLAR):
            ekle("B13", f"yedek/artık dosya: {rel}", rel)
        icerik = _metin_dosyasi(tam)
        if icerik is None:
            continue
        for no, satir in enumerate(icerik.split("\n"), 1):
            m = EV_YOLU.search(satir)
            if m:
                ekle("B14", "makineye özgü ev dizini yolu; ~, $HOME ya da göreli yol kullanın", rel, no)
            for tur, desen in SIR_KALIPLARI:
                if desen.search(satir):
                    ekle("B15", f"sır görünümlü değer ({tur}); değer yazılmadı", rel, no)
                    break
            else:
                for m in SIR_ATAMA.finditer(satir):
                    deger = m.group(1)
                    if re.search(r"[A-Za-z]", deger) and re.search(r"\d", deger) \
                            and not YER_TUTUCU_SIR.search(deger):
                        ekle("B15", "sır görünümlü değer (atanmış token); değer yazılmadı", rel, no)
                        break

    # B16: modelden bağımsız ilan edilen skill'de model adı
    if _model_bagimsiz(meta):
        desen = _model_deseni(ayar)
        for no, satir in enumerate(govde.split("\n"), govde_bas):
            adlar = [m.group(0) for m in desen.finditer(satir)]
            if adlar:
                ekle("B16", f"model adı: {', '.join(adlar[:3])}", SKILL_DOSYASI, no)

    # B20: tarih
    tarihler = [(no, m.group(0)) for no, satir in enumerate(govde.split("\n"), govde_bas)
                for m in TARIH.finditer(satir)]
    if tarihler:
        ekle("B20", f"gövdede {len(tarihler)} tarih (ilki {tarihler[0][1]})", SKILL_DOSYASI, tarihler[0][0])

    # B23: uzun satır oranı (kod blokları ve tablo satırları hariç)
    duz_satirlar = [s for s in kod_bloklarini_at(govde).split("\n") if s.strip() and not s.lstrip().startswith("|")]
    if duz_satirlar:
        uzun = sum(1 for s in duz_satirlar if len(s) >= sin["uzun_satir"])
        if uzun / len(duz_satirlar) > sin["uzun_satir_oran"]:
            ekle("B23", f"satırların %{round(100 * uzun / len(duz_satirlar))}'i {sin['uzun_satir']}+ karakter",
                 SKILL_DOSYASI)

    # B25: yer tutucu
    for no, satir in enumerate(metin.split("\n"), 1):
        if YER_TUTUCU.search(satir):
            ekle("B25", "doldurulmamış yer tutucu (DOLDUR)", SKILL_DOSYASI, no)
            break
    return sonuc


# ------------------------------------------------------------------ tarama
def etiket(yol):
    """Raporda görünen yol: çalışma klasörüne göreli (içindeyse), posix ayraçla."""
    yol = str(yol)
    try:
        rel = os.path.relpath(yol)
        if not rel.startswith(".."):
            yol = rel
    except ValueError:
        pass
    return yol.replace("\\", "/")


def _skill_mi(p):
    return (p / SKILL_DOSYASI).is_file()


def _icinde_skill_var(p, ayar, derinlik=0):
    if derinlik > 12:
        return False
    try:
        girisler = sorted(os.scandir(p), key=lambda g: g.name)
    except OSError:
        return False
    for g in girisler:
        if g.is_dir() and not _atla(g.name, ayar):
            alt = Path(g.path)
            if _skill_mi(alt) or _icinde_skill_var(alt, ayar, derinlik + 1):
                return True
    return False


def _topla(kok, ayar, skiller, eksikler, ziyaret, derinlik=0):
    gercek = os.path.realpath(kok)
    if gercek in ziyaret or derinlik > 12:
        return
    ziyaret.add(gercek)
    try:
        girisler = sorted((g for g in os.scandir(kok) if g.is_dir() and not _atla(g.name, ayar)),
                          key=lambda g: g.name)
    except OSError:
        return
    alt = [Path(g.path) for g in girisler]
    dogrudan = [p for p in alt if _skill_mi(p)]
    for p in alt:
        if _skill_mi(p):
            skiller.append(p)
        elif _icinde_skill_var(p, ayar):
            _topla(p, ayar, skiller, eksikler, ziyaret, derinlik + 1)
        elif dogrudan:
            eksikler.append(p)


def skill_yollari(yollar, ayar):
    """Verilen yollardan skill klasörleri ve SKILL.md'si olmayan skill adayları.

    Yol bir skill ise (SKILL.md içeriyorsa) yalnız o. Değilse alt klasörler taranır: bir klasörün doğrudan
    altında skill varsa o klasör bir skill kökü sayılır ve SKILL.md'si olmayan kardeş klasörler B01 alır.
    Var olmayan yol FileNotFoundError, skill olmayan dosya ValueError verir.
    """
    skiller, eksikler, ziyaret = [], [], set()
    for y in yollar:
        p = Path(y)
        if not p.exists():
            raise FileNotFoundError(f"yol yok: {y}")
        if p.is_file():
            if p.name != SKILL_DOSYASI:
                raise ValueError(f"skill klasörü ya da SKILL.md bekleniyor: {y}")
            p = p.parent if str(p.parent) not in ("", ".") else Path.cwd()
        if _skill_mi(p):
            skiller.append(p)
        else:
            _topla(p, ayar, skiller, eksikler, ziyaret)
    return skiller, eksikler


def tara(yollar, ayar=None):
    """Yolları tarar; Sonuc listesi döner (sıra: verilen yol sırası, klasör adı)."""
    ayar = ayar or Ayar()
    skiller, eksikler = skill_yollari(yollar, ayar)
    sonuclar = []
    gorulen = {}
    for p in skiller:
        giris = p.name if p.name not in ("", ".", "..") else p.resolve().name
        anahtar = os.path.normcase(os.path.realpath(p))
        if anahtar in gorulen:
            onceki, onceki_giris = gorulen[anahtar]
            if onceki.ad and giris not in (onceki.ad, onceki_giris):
                _Kayit(onceki, onceki_giris, ayar)(
                    "B04", f"name '{onceki.ad}' bağlantı adı '{giris}' ile aynı değil", SKILL_DOSYASI)
            continue
        s = skill_denetle(p, ayar, giris, etiket(p))
        gorulen[anahtar] = (s, giris)
        sonuclar.append(s)
    for p in eksikler:
        s = Sonuc(yol=etiket(p))
        _Kayit(s, p.name, ayar)("B01", "SKILL.md yok")
        sonuclar.append(s)
    # B22: aynı name, farklı klasör
    adlar = {}
    for s in sonuclar:
        if s.ad:
            adlar.setdefault(s.ad, []).append(s)
    for liste in adlar.values():
        if len(liste) > 1:
            for s in liste:
                diger = ", ".join(x.yol for x in liste if x is not s)
                giris = Path(s.yol).name
                _Kayit(s, giris, ayar)("B22", f"aynı name başka klasörde: {diger}", SKILL_DOSYASI)
    return sonuclar


def ozet(sonuclar):
    return {"skill": len(sonuclar),
            "hata": sum(len(s.hatalar) for s in sonuclar),
            "uyari": sum(len(s.uyarilar) for s in sonuclar),
            "muaf": sum(len(s.muaflar) for s in sonuclar)}
