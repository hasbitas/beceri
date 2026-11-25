"""beceri komut satırı.

  beceri dogrula <yol>... [--json] [--kati] [--profil esnek|siki] [--ayar DOSYA | --ayarsiz] [--kapat B20,B23]
  beceri yeni <ad> [--hedef DIZIN] [--aciklama METIN] [--profil esnek|siki]
  beceri kurallar [--json]
  beceri benchmark ...          (beceri.benchmark modülüne aynen aktarılır)

Çıkış kodları: 0 temiz (uyarı olabilir); 1 hata bulundu (--kati ya da ayarda kati=true ise uyarı da),
skill bulunamadı ya da hedef klasör zaten var; 2 kullanım ya da ayar hatası.
"""
import argparse
import importlib
import json
import sys

from beceri import __version__
from beceri import ayar as ayar_mod
from beceri.dogrula import ozet, skill_denetle, tara
from beceri.kurallar import ESNEK, KURALLAR, PROFILLER
from beceri.yeni import olustur


def _yaz(metin, dosya=None):
    """Konsol kodlamasından bağımsız UTF-8 ve LF bas."""
    dosya = dosya or sys.stdout
    tampon = getattr(dosya, "buffer", None)
    if tampon is not None:
        dosya.flush()
        tampon.write((metin + "\n").encode("utf-8"))
        tampon.flush()
    else:
        dosya.write(metin + "\n")


def _hata(metin):
    _yaz(f"beceri: {metin}", sys.stderr)


def parser():
    ap = argparse.ArgumentParser(prog="beceri", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"beceri {__version__}")
    alt = ap.add_subparsers(dest="komut", required=True)
    d = alt.add_parser("dogrula", help="skill klasörünü ya da skill ağacını doğrula")
    d.add_argument("yollar", nargs="+", help="skill klasörü, SKILL.md ya da skill'leri içeren klasör")
    d.add_argument("--json", action="store_true", help="makine okunur çıktı")
    d.add_argument("--kati", action="store_true", help="uyarılar da çıkışı 1 yapar")
    d.add_argument("--profil", choices=PROFILLER,
                   help="her skill'i bu profille denetle (skill'in metadata.profil'ini ve ayarı geçersiz kılar)")
    grup = d.add_mutually_exclusive_group()
    grup.add_argument("--ayar", help=".beceri.toml ya da pyproject.toml yolu")
    grup.add_argument("--ayarsiz", action="store_true", help="ayar dosyası arama; varsayılanları kullan")
    d.add_argument("--kapat", default="", help="virgülle ayrılmış kapatılacak kural kimlikleri")
    y = alt.add_parser("yeni", help="genel şablondan yeni skill klasörü oluştur")
    y.add_argument("ad", help="skill adı (küçük harf, rakam, tire)")
    y.add_argument("--hedef", default=".", help="skill klasörünün açılacağı dizin (varsayılan: .)")
    y.add_argument("--aciklama", help="description metni (varsayılan: doldurulacak yer tutucu)")
    y.add_argument("--profil", choices=PROFILLER, help="şablon profili (varsayılan: ayardaki profil ya da esnek)")
    k = alt.add_parser("kurallar", help="kural listesini yaz")
    k.add_argument("--json", action="store_true")
    alt.add_parser("benchmark", help="benchmark araçları (beceri.benchmark); ayrıntı: beceri benchmark --help",
                   add_help=False)
    return ap


def _ayar(a):
    if getattr(a, "ayarsiz", False):
        ayar = ayar_mod.Ayar()
    else:
        ayar = ayar_mod.yukle(getattr(a, "ayar", None))
    kapat = getattr(a, "kapat", "")
    if kapat:
        ayar = ayar.kapat(kapat.split(","))
    if getattr(a, "profil", None):
        ayar = ayar.zorla(a.profil)
    return ayar


def _rapor(sonuclar, ayar, json_mu, kati):
    oz = ozet(sonuclar)
    if json_mu:
        _yaz(json.dumps({"beceri": __version__, "ayar": ayar.kaynak or None, "kati": kati,
                         "skiller": [s.sozluk() for s in sonuclar], "ozet": oz},
                        ensure_ascii=False, indent=2))
        return
    for s in sonuclar:
        if s.hatalar:
            durum = "HATA"
        elif s.uyarilar:
            durum = "UYARI"
        else:
            durum = "TAMAM"
        _yaz(f"[{durum}] {s.yol}" + (f" ({s.profil})" if s.profil != ESNEK else ""))
        for tur, liste in (("hata", s.hatalar), ("uyari", s.uyarilar), ("muaf", s.muaflar)):
            for b in liste:
                yer = f"{b.yer()}: " if b.yer() else ""
                ek = f"  [gerekçe: {b.gerekce}]" if b.gerekce else ""
                _yaz(f"  {b.kural} {tur:<5} {yer}{b.mesaj}{ek}")
    muaf = f", {oz['muaf']} muaf" if oz["muaf"] else ""
    _yaz(f"{oz['skill']} skill: {oz['hata']} hata, {oz['uyari']} uyarı{muaf}")


def _cikis(sonuclar, kati):
    oz = ozet(sonuclar)
    return 1 if oz["hata"] or (kati and oz["uyari"]) else 0


def dogrula_komutu(a):
    try:
        ayar = _ayar(a)
    except ValueError as e:
        _hata(str(e))
        return 2
    try:
        sonuclar = tara(a.yollar, ayar)
    except (FileNotFoundError, ValueError) as e:
        _hata(str(e))
        return 2
    kati = a.kati or ayar.kati
    if not sonuclar:
        if a.json:
            _rapor(sonuclar, ayar, True, kati)
        _hata("skill bulunamadı: " + ", ".join(a.yollar))
        return 1
    _rapor(sonuclar, ayar, a.json, kati)
    return _cikis(sonuclar, kati)


def yeni_komutu(a):
    try:
        ayar = ayar_mod.yukle()
    except ValueError as e:
        _hata(str(e))
        return 2
    profil = a.profil or ayar.profil
    try:
        klasor = olustur(a.ad, a.hedef, a.aciklama, ayar.ayrilmis_adlar, ayar.sinirlar["ad_azami"], profil,
                         isaretle=profil != ESNEK or ayar.profil != ESNEK)
    except FileExistsError as e:
        _hata(str(e))
        return 1
    except (ValueError, OSError) as e:
        _hata(str(e))
        return 2
    _yaz(f"oluşturuldu: {klasor / 'SKILL.md'}")
    sonuc = skill_denetle(klasor, ayar.zorla(profil), a.ad, str(klasor).replace("\\", "/"))
    _rapor([sonuc], ayar, False, False)
    return _cikis([sonuc], False)


def kurallar_komutu(a):
    if a.json:
        _yaz(json.dumps([{"kimlik": k.kimlik, "onem": k.onem, "profil": k.profil, "aciklama": k.aciklama}
                         for k in KURALLAR], ensure_ascii=False, indent=2))
    else:
        for k in KURALLAR:
            _yaz(f"{k.kimlik}  {k.onem:<5}  {k.profil:<5}  {k.aciklama}")
    return 0


def benchmark_komutu(argv):
    """beceri.benchmark.main(argv) -> int; modül yoksa açık bir hata (2)."""
    try:
        modul = importlib.import_module("beceri.benchmark")
    except ModuleNotFoundError as e:
        if e.name != "beceri.benchmark":
            raise
        _hata("benchmark modülü bulunamadı (beceri.benchmark); bu kurulumda benchmark araçları yok")
        return 2
    sonuc = modul.main(list(argv))
    return int(sonuc or 0)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "benchmark":
        return benchmark_komutu(argv[1:])
    a = parser().parse_args(argv)
    if a.komut == "dogrula":
        return dogrula_komutu(a)
    if a.komut == "yeni":
        return yeni_komutu(a)
    return kurallar_komutu(a)


def utf8_konsol():
    """Konsol akışlarını UTF-8'e çevirir: cp1252 gibi kod sayfalarında Türkçe çıktı çökmesin."""
    for akis in (sys.stdout, sys.stderr):
        if hasattr(akis, "reconfigure"):
            akis.reconfigure(encoding="utf-8", errors="replace")


def cli():
    utf8_konsol()
    sys.exit(main())
