"""beceri benchmark: görev listesi, doğrulama, bütünlük, puanlama ve kalibrasyon.

Yalnız standart kütüphane kullanır. Görev klasöründeki kod hiçbir zaman bu
süreçte içe aktarılmaz veya çalıştırılmaz: her test koşusu geçici bir kopyada,
temizlenmiş ortam değişkenleriyle ve zaman aşımıyla ``sys.executable -m pytest``
alt sürecinde çalışır. Bu bir güvenlik kum havuzu değildir; güvenilmeyen aday
kodu yalıtılmış bir makinede veya konteynerde çalıştırın.

Alt komutlar::

    listele                         görevleri, bölümleri ve sayıları gösterir
    dogrula [--gorev ID]            gold geçer, broken ve boş taslak kalır mı
    butunluk [--yaz]                SHA256SUMS bildirimini doğrular / yeniden yazar
    kos --cozum-dizini DIR          aday çözümleri puanlar (pass@1, JSON)
    kalibre [--tekrar N] [--sonda]  kararlılık, koşucu sondaları, zorluk tahmini

Çıkış kodları: 0 başarılı, 1 bulgu var (geçersiz görev, bozuk bütünlük...),
2 kullanım veya altyapı hatası (pytest yok, veri bulunamadı, geçersiz kimlik).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

VARSAYILAN_VERI = "kod-v1"
MANIFEST = "SHA256SUMS"
ORTAM_DEGISKENI = "BECERI_BENCHMARK"
GOREV_KIMLIGI = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
BOLUMLER = ("development", "selection", "final")
TURLER = ("single-file", "multi-file")
TEST_KLASORLERI = (("visible", "tests_visible"), ("hidden", "tests_hidden"))
YOKSAYILAN = {"__pycache__", ".pytest_cache"}
DOSYA_SINIRI = 64 * 1024 * 1024  # POSIX: alt sürecin yazabileceği en büyük dosya
CIKTI_KUYRUGU = 4000

# POSIX'te kaynak sınırlarını koyup pytest'e geçen küçük başlatıcı. preexec_fn
# iş parçacıklarıyla güvenli olmadığı için sınırlar alt süreçte kendi içinde kurulur.
_BASLATICI = (
    "import os, sys\n"
    "try:\n"
    "    import resource\n"
    "    lim = int(os.environ.get('BECERI_DOSYA_SINIRI', '0'))\n"
    "    if lim:\n"
    "        resource.setrlimit(resource.RLIMIT_FSIZE, (lim, lim))\n"
    "    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))\n"
    "    cpu = int(os.environ.get('BECERI_CPU_SINIRI', '0'))\n"
    "    if cpu:\n"
    "        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))\n"
    "except Exception:\n"
    "    pass\n"
    "os.execv(sys.executable, [sys.executable] + sys.argv[1:])\n"
)

SONDALAR = {
    # Test toplanırken süreci başarılı çıkış koduyla bitirir.
    "bos-cikis": "import os\nos._exit(0)\n",
    # Başarılı bir pytest özeti basıp çıkar.
    "sahte-basari": "import os, sys\nsys.stdout.write('99 passed in 0.01s\\n')\nsys.stdout.flush()\nos._exit(0)\n",
    # Sonsuz döngü: zaman aşımıyla bitmeli.
    "sonsuz-dongu": "while True:\n    pass\n",
    # Çıktı seli: dosya boyutu sınırı ya da zaman aşımıyla bitmeli (yalnız POSIX).
    "cikti-seli": "import os\nwhile True:\n    os.write(1, b'x' * 65536)\n",
}


class KullanimHatasi(Exception):
    """Çıkış kodu 2 ile sonuçlanan kullanım veya altyapı hatası."""


# --------------------------------------------------------------------------
# Veri yükleme


@dataclass
class Gorev:
    kimlik: str
    klasor: Path
    tur: str
    tanim: str
    izinli: list[str]
    salt_okunur: list[str]
    beklenen: dict[str, int] | None
    bolum: str | None = None

    @property
    def beklenen_toplam(self) -> int | None:
        if not self.beklenen:
            return None
        return sum(self.beklenen.values())


@dataclass
class Veri:
    kok: Path
    gorevler: dict[str, Gorev] = field(default_factory=dict)


def guvenli_goreli_yol(metin: object) -> str:
    """Göreli, '..' içermeyen POSIX yolu kabul eder; değilse KullanimHatasi."""
    if not isinstance(metin, str) or not metin or "\\" in metin or "\x00" in metin:
        raise KullanimHatasi(f"geçersiz yol: {metin!r}")
    yol = PurePosixPath(metin)
    if yol.is_absolute() or re.match(r"^[A-Za-z]:", metin):
        raise KullanimHatasi(f"mutlak yol kabul edilmez: {metin!r}")
    if any(p in ("", ".", "..") for p in metin.split("/")):
        raise KullanimHatasi(f"geçersiz yol parçası: {metin!r}")
    return yol.as_posix()


def gorev_kimligi_dogrula(kimlik: str) -> str:
    if not isinstance(kimlik, str) or not GOREV_KIMLIGI.match(kimlik):
        raise KullanimHatasi(f"geçersiz görev kimliği: {kimlik!r} (yalnız a-z, 0-9 ve '-')")
    return kimlik


def veri_dizini_bul(arg: str | None) -> Path:
    adaylar: list[Path] = []
    if arg:
        adaylar.append(Path(arg))
    elif os.environ.get(ORTAM_DEGISKENI):
        adaylar.append(Path(os.environ[ORTAM_DEGISKENI]))
    else:
        for ust in Path(__file__).resolve().parents:
            adaylar.append(ust / "benchmark" / VARSAYILAN_VERI)
        adaylar.append(Path.cwd() / "benchmark" / VARSAYILAN_VERI)
    for aday in adaylar:
        if (aday / "tasks").is_dir():
            return aday.resolve()
    raise KullanimHatasi(
        "benchmark verisi bulunamadı; --veri DIR ya da "
        f"{ORTAM_DEGISKENI} ortam değişkeniyle 'tasks/' içeren klasörü verin"
    )


def _json_oku(yol: Path) -> object:
    try:
        return json.loads(yol.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise KullanimHatasi(f"okunamadı: {yol}: {exc}") from exc


def gorev_yukle(klasor: Path) -> Gorev:
    kimlik = gorev_kimligi_dogrula(klasor.name)
    veri = _json_oku(klasor / "task.json")
    if not isinstance(veri, dict):
        raise KullanimHatasi(f"{kimlik}: task.json bir nesne olmalı")
    if veri.get("task_id") != kimlik:
        raise KullanimHatasi(f"{kimlik}: task_id klasör adıyla aynı olmalı")
    tur = veri.get("kind", "single-file")
    if tur not in TURLER:
        raise KullanimHatasi(f"{kimlik}: kind {TURLER} içinden biri olmalı")
    tanim = veri.get("specification")
    if not isinstance(tanim, str) or not tanim.strip():
        raise KullanimHatasi(f"{kimlik}: specification boş olamaz")
    izinli = veri.get("allowed_paths")
    if not isinstance(izinli, list) or not izinli:
        raise KullanimHatasi(f"{kimlik}: allowed_paths boş olmayan bir liste olmalı")
    salt = veri.get("readonly_paths", [])
    if not isinstance(salt, list):
        raise KullanimHatasi(f"{kimlik}: readonly_paths bir liste olmalı")
    izinli = [guvenli_goreli_yol(p) for p in izinli]
    salt = [guvenli_goreli_yol(p) for p in salt]
    if len(set(izinli + salt)) != len(izinli) + len(salt):
        raise KullanimHatasi(f"{kimlik}: allowed_paths ve readonly_paths çakışıyor")
    beklenen = veri.get("expected_tests")
    if beklenen is not None and (
            not isinstance(beklenen, dict) or set(beklenen) != {"visible", "hidden"}
            or not all(isinstance(v, int) and not isinstance(v, bool) and v >= 0 for v in beklenen.values())):
        raise KullanimHatasi(f"{kimlik}: expected_tests {{'visible': n, 'hidden': m}} olmalı")
    return Gorev(kimlik, klasor, tur, tanim, izinli, salt, beklenen)


def veri_yukle(kok: Path) -> Veri:
    veri = Veri(kok)
    gorev_kok = kok / "tasks"
    for klasor in sorted(gorev_kok.iterdir()):
        if klasor.name in YOKSAYILAN or not klasor.is_dir():
            continue
        if klasor.is_symlink():
            raise KullanimHatasi(f"görev klasörü sembolik bağ olamaz: {klasor.name}")
        gorev = gorev_yukle(klasor)
        veri.gorevler[gorev.kimlik] = gorev
    bolum_dosyasi = kok / "split.json"
    if bolum_dosyasi.exists():
        bolum = _json_oku(bolum_dosyasi)
        gruplar = bolum.get("groups", {}) if isinstance(bolum, dict) else {}
        for kimlik, ad in gruplar.items():
            if kimlik in veri.gorevler and ad in BOLUMLER:
                veri.gorevler[kimlik].bolum = ad
    return veri


def gorevleri_sec(veri: Veri, kimlikler: list[str] | None, bolum: str | None = None) -> list[Gorev]:
    if kimlikler:
        secilen = []
        for kimlik in kimlikler:
            gorev_kimligi_dogrula(kimlik)
            if kimlik not in veri.gorevler:
                raise KullanimHatasi(f"bilinmeyen görev: {kimlik}")
            secilen.append(veri.gorevler[kimlik])
    else:
        secilen = list(veri.gorevler.values())
    if bolum:
        secilen = [g for g in secilen if g.bolum == bolum]
    if not secilen:
        raise KullanimHatasi("seçimle eşleşen görev yok")
    return secilen


# --------------------------------------------------------------------------
# Test koşucusu


@dataclass
class Kosu:
    durum: str  # gecti, kaldi, zaman-asimi, hata
    gecen: int = 0
    toplam: int = 0
    gorunur: tuple[int, int] = (0, 0)  # (geçen, toplam)
    gizli: tuple[int, int] = (0, 0)
    donus_kodu: int | None = None
    cikti: str = ""

    @property
    def basarili(self) -> bool:
        return self.durum == "gecti"

    def ozet(self) -> str:
        if self.durum in ("zaman-asimi", "hata", "eksik"):
            return self.durum
        return f"{self.gecen}/{self.toplam}"

    def sozluk(self) -> dict:
        return {"durum": self.durum, "gecen_test": self.gecen, "toplam_test": self.toplam}


def temiz_ortam(tmp: Path, calisma: Path, zaman_asimi: float) -> dict[str, str]:
    """Yalnız yorumlayıcının bulunması için gerekenleri taşıyan ortam."""
    ortam: dict[str, str] = {}
    for anahtar in ("PATH", "SYSTEMROOT", "SystemRoot", "WINDIR", "COMSPEC", "PATHEXT",
                    "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "LANG", "LC_ALL"):
        if anahtar in os.environ:
            ortam[anahtar] = os.environ[anahtar]
    gecici = tmp / "tmp"
    gecici.mkdir(exist_ok=True)
    ortam.update({
        "PYTHONPATH": str(calisma),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "TMPDIR": str(gecici), "TEMP": str(gecici), "TMP": str(gecici),
        "BECERI_DOSYA_SINIRI": str(DOSYA_SINIRI),
        "BECERI_CPU_SINIRI": str(int(zaman_asimi) + 5),
    })
    return ortam


def _kopyala(kaynak: Path, hedef: Path) -> None:
    hedef.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(kaynak, hedef)


def _junit_oku(yol: Path) -> dict[str, dict[tuple[str, str], bool]] | None:
    """Bölüm -> {(sınıf, ad): geçti mi}. Alt testler aynı kimlikle tekrarlanabilir."""
    try:
        kok = ET.parse(yol).getroot()
    except (OSError, ET.ParseError):
        return None
    sonuc: dict[str, dict[tuple[str, str], bool]] = {"visible": {}, "hidden": {}}
    for vaka in kok.iter("testcase"):
        sinif = vaka.get("classname", "")
        bolum = next((b for b, _ in TEST_KLASORLERI if sinif.startswith(f"tests.{b}.")), None)
        if bolum is None:
            continue
        anahtar = (sinif, vaka.get("name", ""))
        basarisiz = any(c.tag in ("failure", "error", "skipped") for c in vaka)
        sonuc[bolum][anahtar] = sonuc[bolum].get(anahtar, True) and not basarisiz
    return sonuc


def _sureci_bitir(surec: subprocess.Popen) -> None:
    try:
        if os.name == "posix":
            os.killpg(surec.pid, signal.SIGKILL)
        else:
            surec.kill()
    except (ProcessLookupError, PermissionError, OSError):
        pass
    try:
        surec.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass


def testleri_kos(gorev: Gorev, dosyalar: dict[str, Path | bytes], zaman_asimi: float) -> Kosu:
    """dosyalar: göreli yol -> kaynak dosya ya da içerik. Geçici kopyada pytest koşar."""
    tmp = Path(tempfile.mkdtemp(prefix="beceri-"))
    try:
        calisma = tmp / "ws"
        calisma.mkdir()
        for goreli, kaynak in dosyalar.items():
            hedef = calisma / guvenli_goreli_yol(goreli)
            if isinstance(kaynak, bytes):
                hedef.parent.mkdir(parents=True, exist_ok=True)
                hedef.write_bytes(kaynak)
            else:
                _kopyala(kaynak, hedef)
        for bolum, klasor_adi in TEST_KLASORLERI:
            kaynak_klasor = gorev.klasor / klasor_adi
            hedef_klasor = tmp / "tests" / bolum
            hedef_klasor.mkdir(parents=True)
            if kaynak_klasor.is_dir():
                for dosya in sorted(kaynak_klasor.iterdir()):
                    if dosya.is_file() and not dosya.is_symlink() and dosya.suffix == ".py":
                        _kopyala(dosya, hedef_klasor / dosya.name)
        ayar = tmp / "pytest.ini"
        ayar.write_text("[pytest]\n", encoding="utf-8")
        junit = tmp / "junit.xml"
        pytest_argumanlari = [
            "-m", "pytest", "-q", "--tb=line", "-p", "no:cacheprovider", "-c", str(ayar),
            "--rootdir", str(tmp), "--import-mode=importlib",
            "--junitxml", str(junit), "-o", "junit_family=xunit2",
            str(tmp / "tests" / "visible"), str(tmp / "tests" / "hidden"),
        ]
        if os.name == "posix":
            komut = [sys.executable, "-c", _BASLATICI] + pytest_argumanlari
        else:
            komut = [sys.executable] + pytest_argumanlari
        cikti_yolu = tmp / "cikti.txt"
        ek: dict = {"start_new_session": True} if os.name == "posix" else {
            "creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)}
        with open(cikti_yolu, "wb") as cikti:
            surec = subprocess.Popen(komut, cwd=calisma, env=temiz_ortam(tmp, calisma, zaman_asimi),
                                     stdin=subprocess.DEVNULL, stdout=cikti, stderr=subprocess.STDOUT, **ek)
            try:
                donus = surec.wait(timeout=zaman_asimi)
                zaman_doldu = False
            except subprocess.TimeoutExpired:
                _sureci_bitir(surec)
                donus, zaman_doldu = surec.returncode, True
            if os.name == "posix" and not zaman_doldu:
                # Arka planda kalan torun süreçleri de temizle.
                try:
                    os.killpg(surec.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError, OSError):
                    pass
        try:
            with open(cikti_yolu, "rb") as f:
                f.seek(max(0, cikti_yolu.stat().st_size - CIKTI_KUYRUGU))
                kuyruk = f.read().decode("utf-8", "replace")
        except OSError:
            kuyruk = ""
        if zaman_doldu:
            return Kosu("zaman-asimi", donus_kodu=donus, cikti=kuyruk)
        vakalar = _junit_oku(junit) if junit.exists() else None
        if vakalar is None:
            return Kosu("hata", donus_kodu=donus, cikti=kuyruk)
        gor = vakalar["visible"]
        giz = vakalar["hidden"]
        gorunur = (sum(gor.values()), len(gor))
        gizli = (sum(giz.values()), len(giz))
        gecen, toplam = gorunur[0] + gizli[0], gorunur[1] + gizli[1]
        kosu = Kosu("kaldi", gecen, toplam, gorunur, gizli, donus, kuyruk)
        beklenen = gorev.beklenen
        sayi_tamam = beklenen is None or (gorunur[1] == beklenen["visible"] and gizli[1] == beklenen["hidden"])
        if donus == 0 and toplam > 0 and gecen == toplam and sayi_tamam:
            kosu.durum = "gecti"
        elif donus not in (0, 1) and gecen == 0 and toplam == 0:
            kosu.durum = "hata"
        return kosu
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def pytest_hazir_mi() -> None:
    with tempfile.TemporaryDirectory(prefix="beceri-") as tmp:
        ortam = temiz_ortam(Path(tmp), Path(tmp), 30)
        try:
            sonuc = subprocess.run([sys.executable, "-c", "import pytest"], env=ortam,
                                   capture_output=True, timeout=60, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise KullanimHatasi(f"pytest denetlenemedi: {exc}") from exc
    if sonuc.returncode != 0:
        raise KullanimHatasi(
            f"pytest bulunamadı ({sys.executable}). Kurmak için: "
            f"{Path(sys.executable).name} -m pip install pytest"
        )


def _salt_okunur(gorev: Gorev) -> dict[str, Path | bytes]:
    return {p: gorev.klasor / "gold" / p for p in gorev.salt_okunur}


def gold_dosyalari(gorev: Gorev, surum: str = "gold") -> dict[str, Path | bytes]:
    dosyalar = _salt_okunur(gorev)
    for p in gorev.izinli:
        dosyalar[p] = gorev.klasor / surum / p
    return dosyalar


def taslak_dosyalari(gorev: Gorev, icerik: bytes = b"") -> dict[str, Path | bytes]:
    dosyalar = _salt_okunur(gorev)
    for i, p in enumerate(gorev.izinli):
        dosyalar[p] = icerik if i == 0 else b""
    return dosyalar


def aday_dosyalari(gorev: Gorev, kok: Path) -> dict[str, Path | bytes] | None:
    """Aday klasöründen yalnız allowed_paths dosyalarını alır; eksikse None."""
    gorev_klasoru = kok / gorev.kimlik
    if not gorev_klasoru.is_dir() or gorev_klasoru.is_symlink():
        return None
    gercek_kok = gorev_klasoru.resolve()
    dosyalar = _salt_okunur(gorev)
    for p in gorev.izinli:
        aday = gorev_klasoru / p
        if aday.is_symlink() or not aday.is_file():
            return None
        try:
            aday.resolve().relative_to(gercek_kok)
        except ValueError:
            return None
        dosyalar[p] = aday
    return dosyalar


def _paralel(fonksiyon, ogeler, is_sayisi: int):
    if is_sayisi <= 1:
        return [fonksiyon(o) for o in ogeler]
    with ThreadPoolExecutor(max_workers=is_sayisi) as havuz:
        return list(havuz.map(fonksiyon, ogeler))


# --------------------------------------------------------------------------
# Alt komutlar


def komut_listele(args) -> int:
    veri = veri_yukle(veri_dizini_bul(args.veri))
    gorevler = gorevleri_sec(veri, None, args.bolum)
    bolum_say = {b: sum(g.bolum == b for g in gorevler) for b in BOLUMLER}
    tur_say = {t: sum(g.tur == t for g in gorevler) for t in TURLER}
    if args.json:
        print(json.dumps({
            "veri": veri.kok.name,
            "gorev_sayisi": len(gorevler),
            "bolumler": bolum_say,
            "turler": tur_say,
            "gorevler": [{"task_id": g.kimlik, "bolum": g.bolum, "kind": g.tur,
                          "allowed_paths": g.izinli, "expected_tests": g.beklenen}
                         for g in gorevler],
        }, ensure_ascii=False, indent=2))
        return 0
    print(f"{'GÖREV':<24} {'BÖLÜM':<12} {'TÜR':<12} {'DOSYA':>5} {'TEST(g/h)':>10}")
    for g in gorevler:
        test = f"{g.beklenen['visible']}/{g.beklenen['hidden']}" if g.beklenen else "-"
        print(f"{g.kimlik:<24} {g.bolum or '-':<12} {g.tur:<12} {len(g.izinli):>5} {test:>10}")
    print(f"\nToplam: {len(gorevler)} görev | "
          + ", ".join(f"{b} {n}" for b, n in bolum_say.items()) + " | "
          + ", ".join(f"{t} {n}" for t, n in tur_say.items()))
    return 0


def gorev_dogrula(gorev: Gorev, zaman_asimi: float) -> dict:
    gold = testleri_kos(gorev, gold_dosyalari(gorev, "gold"), zaman_asimi)
    broken = testleri_kos(gorev, gold_dosyalari(gorev, "broken"), zaman_asimi)
    taslak = testleri_kos(gorev, taslak_dosyalari(gorev), zaman_asimi)
    sorunlar: list[str] = []
    for surum in ("gold", "broken"):
        for p in gorev.izinli + gorev.salt_okunur:
            if not (gorev.klasor / surum / p).is_file():
                sorunlar.append(f"{surum}/{p} eksik")
    if gorev.beklenen is None:
        sorunlar.append("expected_tests yok; gold sayımı: "
                        f'{{"visible": {gold.gorunur[1]}, "hidden": {gold.gizli[1]}}}')
    if not gold.basarili:
        if gold.durum == "kaldi" and gold.gecen == gold.toplam and gorev.beklenen:
            sorunlar.append(f"gold test sayısı beklenenden farklı ({gold.gorunur[1]}/{gold.gizli[1]})")
        else:
            sorunlar.append(f"gold geçmedi ({gold.ozet()})")
    if broken.basarili:
        sorunlar.append("broken testleri geçiyor (testler hatayı yakalamıyor)")
    if taslak.basarili:
        sorunlar.append("boş taslak testleri geçiyor")
    uyarilar = []
    if broken.durum in ("zaman-asimi", "hata"):
        uyarilar.append(f"broken sıradan test hatası yerine '{broken.durum}' ile kaldı")
    return {"gorev": gorev, "gold": gold, "broken": broken, "taslak": taslak,
            "sorunlar": sorunlar, "uyarilar": uyarilar}


def komut_dogrula(args) -> int:
    veri = veri_yukle(veri_dizini_bul(args.veri))
    gorevler = gorevleri_sec(veri, args.gorev, args.bolum)
    pytest_hazir_mi()
    sonuclar = []

    def isle(g):
        return gorev_dogrula(g, args.zaman_asimi)

    for s in _paralel_sirali(isle, gorevler, args.paralel, sonuclar):
        if not args.json:
            g = s["gorev"]
            etiket = "GEÇERLİ " if not s["sorunlar"] else "GEÇERSİZ"
            print(f"[{etiket}] {g.kimlik:<24} gold {s['gold'].ozet():>9}  "
                  f"broken {s['broken'].ozet():>9}  boş {s['taslak'].ozet():>9}", flush=True)
            for sorun in s["sorunlar"]:
                print(f"           - {sorun}")
            for uyari in s["uyarilar"]:
                print(f"           ~ {uyari}")
            if args.ayrinti and s["sorunlar"]:
                for ad in ("gold", "broken", "taslak"):
                    if s[ad].cikti:
                        print(f"           --- {ad} çıktısı (son kısım) ---\n{s[ad].cikti}")
    gecersiz = [s["gorev"].kimlik for s in sonuclar if s["sorunlar"]]
    if args.json:
        print(json.dumps({
            "gorev_sayisi": len(sonuclar),
            "gecerli": len(sonuclar) - len(gecersiz),
            "gecersiz": gecersiz,
            "gorevler": {s["gorev"].kimlik: {
                "gecerli": not s["sorunlar"], "sorunlar": s["sorunlar"], "uyarilar": s["uyarilar"],
                "gold": s["gold"].sozluk(), "broken": s["broken"].sozluk(),
                "taslak": s["taslak"].sozluk()} for s in sonuclar},
        }, ensure_ascii=False, indent=2))
    else:
        print(f"\nSonuç: {len(sonuclar) - len(gecersiz)}/{len(sonuclar)} görev geçerli"
              + (f"; geçersiz: {', '.join(gecersiz)}" if gecersiz else ""))
    return 1 if gecersiz else 0


def _paralel_sirali(fonksiyon, ogeler, is_sayisi, toplayici):
    """Sonuçları girdi sırasıyla, hazır oldukça verir ve toplayıcıya ekler."""
    if is_sayisi <= 1:
        for o in ogeler:
            sonuc = fonksiyon(o)
            toplayici.append(sonuc)
            yield sonuc
        return
    with ThreadPoolExecutor(max_workers=is_sayisi) as havuz:
        for sonuc in havuz.map(fonksiyon, ogeler):
            toplayici.append(sonuc)
            yield sonuc


def _dosya_ozeti(yol: Path) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def _veri_dosyalari(kok: Path) -> list[str]:
    dosyalar = []
    for yol in kok.rglob("*"):
        goreli = yol.relative_to(kok)
        if any(p in YOKSAYILAN for p in goreli.parts) or yol.suffix == ".pyc":
            continue
        if yol.is_file() and goreli.as_posix() != MANIFEST:
            dosyalar.append(goreli.as_posix())
    return sorted(dosyalar)


def butunluk_denetle(kok: Path) -> dict:
    manifest = kok / MANIFEST
    if not manifest.is_file():
        raise KullanimHatasi(f"{MANIFEST} bulunamadı: {kok}")
    kayitlar: dict[str, str] = {}
    for no, satir in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not satir.strip():
            continue
        m = re.match(r"^([0-9a-f]{64}) [ *](.+)$", satir)
        if not m:
            raise KullanimHatasi(f"{MANIFEST}:{no}: biçim 'sha256  yol' olmalı")
        kayitlar[guvenli_goreli_yol(m.group(2))] = m.group(1)
    mevcut = set(_veri_dosyalari(kok))
    eksik = sorted(p for p in kayitlar if p not in mevcut)
    fazla = sorted(p for p in mevcut if p not in kayitlar)
    degisik = sorted(p for p in kayitlar if p in mevcut and _dosya_ozeti(kok / p) != kayitlar[p])
    return {"dosya_sayisi": len(kayitlar), "eksik": eksik, "fazla": fazla, "degisik": degisik,
            "tamam": not (eksik or fazla or degisik),
            "parmak_izi": "sha256:" + _dosya_ozeti(manifest)}


def butunluk_yaz(kok: Path) -> int:
    satirlar = [f"{_dosya_ozeti(kok / p)}  {p}\n" for p in _veri_dosyalari(kok)]
    with open(kok / MANIFEST, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(satirlar)
    return len(satirlar)


def komut_butunluk(args) -> int:
    kok = veri_dizini_bul(args.veri)
    if args.yaz:
        n = butunluk_yaz(kok)
        print(f"{MANIFEST} yazıldı: {n} dosya")
        return 0
    sonuc = butunluk_denetle(kok)
    for anahtar, baslik in (("eksik", "eksik"), ("degisik", "değişmiş"), ("fazla", "bildirimde yok")):
        for p in sonuc[anahtar]:
            print(f"{baslik}: {p}")
    if sonuc["tamam"]:
        print(f"Bütünlük tamam: {sonuc['dosya_sayisi']} dosya ({sonuc['parmak_izi']})")
        return 0
    print("Bütünlük BOZUK")
    return 1


def aday_puanla(veri: Veri, gorevler: list[Gorev], dizinler: list[Path],
                zaman_asimi: float, is_sayisi: int) -> dict:
    for d in dizinler:
        if not d.is_dir():
            raise KullanimHatasi(f"çözüm dizini bulunamadı: {d}")

    def isle(gorev: Gorev) -> tuple[str, list[Kosu]]:
        kosular = []
        for d in dizinler:
            dosyalar = aday_dosyalari(gorev, d)
            kosular.append(Kosu("eksik") if dosyalar is None
                           else testleri_kos(gorev, dosyalar, zaman_asimi))
        return gorev.kimlik, kosular

    sonuclar = dict(_paralel(isle, gorevler, is_sayisi))
    n = len(dizinler)
    rapor_gorevler = {}
    for g in gorevler:
        kosular = sonuclar[g.kimlik]
        c = sum(k.basarili for k in kosular)
        rapor_gorevler[g.kimlik] = {"bolum": g.bolum, "kind": g.tur, "gecen": c, "ornek": n,
                                    "pass@1": round(c / n, 4), "kosular": [k.sozluk() for k in kosular]}
    def ortalama(secim):
        degerler = [rapor_gorevler[g.kimlik]["pass@1"] for g in secim]
        return round(sum(degerler) / len(degerler), 4) if degerler else None
    try:
        butunluk = butunluk_denetle(veri.kok)
        butunluk_ozet = {"tamam": butunluk["tamam"], "parmak_izi": butunluk["parmak_izi"]}
    except KullanimHatasi as exc:
        butunluk_ozet = {"tamam": False, "hata": str(exc)}
    return {
        "veri": veri.kok.name,
        "butunluk": butunluk_ozet,
        "ornek_sayisi": n,
        "gorevler": rapor_gorevler,
        "toplam": {
            "gorev_sayisi": len(gorevler),
            "cozulen": sum(1 for v in rapor_gorevler.values() if v["gecen"] == n),
            "pass@1": ortalama(gorevler),
            "bolumlere_gore": {b: ortalama([g for g in gorevler if g.bolum == b])
                               for b in BOLUMLER if any(g.bolum == b for g in gorevler)},
        },
    }


def _json_yaz(rapor: dict, cikti: str | None) -> None:
    metin = json.dumps(rapor, ensure_ascii=False, indent=2)
    if cikti:
        Path(cikti).write_text(metin + "\n", encoding="utf-8")
    print(metin)


def komut_kos(args) -> int:
    veri = veri_yukle(veri_dizini_bul(args.veri))
    gorevler = gorevleri_sec(veri, args.gorev, args.bolum)
    pytest_hazir_mi()
    rapor = aday_puanla(veri, gorevler, [Path(d) for d in args.cozum_dizini],
                        args.zaman_asimi, args.paralel)
    _json_yaz(rapor, args.cikti)
    return 0


def zorluk_etiketi(oran: float) -> str:
    if oran == 0:
        return "cozulmedi"
    if oran < 1 / 3:
        return "zor"
    if oran < 2 / 3:
        return "orta"
    return "kolay"


def komut_kalibre(args) -> int:
    veri = veri_yukle(veri_dizini_bul(args.veri))
    gorevler = gorevleri_sec(veri, args.gorev, args.bolum)
    if args.tekrar < 1:
        raise KullanimHatasi("--tekrar en az 1 olmalı")
    pytest_hazir_mi()
    sondalar = {}
    if args.sonda:
        sondalar = {ad: kod for ad, kod in SONDALAR.items() if ad != "cikti-seli" or os.name == "posix"}
    sonda_zaman = min(args.zaman_asimi, args.sonda_zaman_asimi)

    def isle(gorev: Gorev) -> dict:
        gold = [testleri_kos(gorev, gold_dosyalari(gorev, "gold"), args.zaman_asimi) for _ in range(args.tekrar)]
        broken = [testleri_kos(gorev, gold_dosyalari(gorev, "broken"), args.zaman_asimi) for _ in range(args.tekrar)]
        sorunlar = []
        if not all(k.basarili for k in gold):
            sorunlar.append("gold her tekrarda geçmedi: " + ", ".join(k.ozet() for k in gold))
        if any(k.basarili for k in broken):
            sorunlar.append("broken en az bir tekrarda geçti")
        if len({(k.durum, k.gecen, k.toplam) for k in broken}) > 1:
            sorunlar.append("broken sonuçları tekrarlar arasında değişiyor: "
                            + ", ".join(k.ozet() for k in broken))
        sonda_sonuc = {}
        for ad, kod in sondalar.items():
            k = testleri_kos(gorev, taslak_dosyalari(gorev, kod.encode()), sonda_zaman)
            sonda_sonuc[ad] = k.durum
            if k.basarili:
                sorunlar.append(f"sonda '{ad}' geçti sayıldı")
        return {"gorev": gorev.kimlik, "kararli": not sorunlar, "sorunlar": sorunlar,
                "gold": [k.ozet() for k in gold], "broken": [k.ozet() for k in broken],
                "sondalar": sonda_sonuc}

    satirlar = _paralel(isle, gorevler, args.paralel)
    rapor: dict = {
        "veri": veri.kok.name, "tekrar": args.tekrar, "sondalar": sorted(sondalar),
        "gorevler": {s.pop("gorev"): s for s in satirlar},
    }
    sorunlu = sorted(k for k, v in rapor["gorevler"].items() if not v["kararli"])
    rapor["sorunlu"] = sorunlu
    if args.cozum_dizini:
        puan = aday_puanla(veri, gorevler, [Path(d) for d in args.cozum_dizini],
                           args.zaman_asimi, args.paralel)
        rapor["zorluk"] = {k: {"pass@1": v["pass@1"], "ornek": v["ornek"],
                               "etiket": zorluk_etiketi(v["pass@1"])}
                           for k, v in puan["gorevler"].items()}
        dagilim: dict[str, int] = {}
        for v in rapor["zorluk"].values():
            dagilim[v["etiket"]] = dagilim.get(v["etiket"], 0) + 1
        rapor["zorluk_dagilimi"] = dagilim
    _json_yaz(rapor, args.cikti)
    return 1 if sorunlu else 0


# --------------------------------------------------------------------------
# Komut satırı


def ayristirici() -> argparse.ArgumentParser:
    ortak = argparse.ArgumentParser(add_help=False)
    ortak.add_argument("--veri", metavar="DIR",
                       help=f"veri klasörü ('tasks/' içeren; varsayılan benchmark/{VARSAYILAN_VERI}, "
                            f"ya da {ORTAM_DEGISKENI})")
    secim = argparse.ArgumentParser(add_help=False)
    secim.add_argument("--gorev", action="append", metavar="ID", help="yalnız bu görev (tekrarlanabilir)")
    secim.add_argument("--bolum", choices=BOLUMLER, help="yalnız bu bölüm")
    kosucu = argparse.ArgumentParser(add_help=False)
    kosucu.add_argument("--zaman-asimi", type=float, default=60.0, metavar="SN",
                        help="pytest koşusu başına zaman aşımı (varsayılan 60)")
    kosucu.add_argument("--paralel", type=int, default=min(4, os.cpu_count() or 1), metavar="N",
                        help="aynı anda işlenecek görev sayısı")

    p = argparse.ArgumentParser(prog="beceri benchmark", description="beceri benchmark araçları")
    alt = p.add_subparsers(dest="komut", required=True)

    a = alt.add_parser("listele", parents=[ortak], help="görevleri listele")
    a.add_argument("--bolum", choices=BOLUMLER)
    a.add_argument("--json", action="store_true")
    a.set_defaults(fonksiyon=komut_listele)

    a = alt.add_parser("dogrula", parents=[ortak, secim, kosucu],
                       help="gold geçer, broken ve boş taslak kalır mı")
    a.add_argument("--json", action="store_true")
    a.add_argument("--ayrinti", action="store_true", help="sorunlu koşuların çıktısını göster")
    a.set_defaults(fonksiyon=komut_dogrula)

    a = alt.add_parser("butunluk", parents=[ortak], help=f"{MANIFEST} bildirimini doğrula")
    a.add_argument("--yaz", action="store_true", help="bildirimi yeniden üret (görev ekledikten sonra)")
    a.set_defaults(fonksiyon=komut_butunluk)

    a = alt.add_parser("kos", parents=[ortak, secim, kosucu], help="aday çözümleri puanla (JSON)")
    a.add_argument("--cozum-dizini", action="append", required=True, metavar="DIR",
                   help="<DIR>/<görev>/<allowed_path> düzeninde çözümler; birden çok verilirse "
                        "her biri bir örnek sayılır")
    a.add_argument("--cikti", metavar="DOSYA", help="JSON raporu ayrıca bu dosyaya yaz")
    a.set_defaults(fonksiyon=komut_kos)

    a = alt.add_parser("kalibre", parents=[ortak, secim, kosucu],
                       help="kararlılık, koşucu sondaları ve zorluk tahmini (model çağrısı yok)")
    a.add_argument("--tekrar", type=int, default=3, metavar="N", help="gold/broken tekrar sayısı")
    a.add_argument("--sonda", action="store_true",
                   help="koşucuyu kandırmaya çalışan sonda çözümlerini de çalıştır")
    a.add_argument("--sonda-zaman-asimi", type=float, default=10.0, metavar="SN")
    a.add_argument("--cozum-dizini", action="append", metavar="DIR",
                   help="zorluk tahmini için çözüm koşuları (tekrarlanabilir)")
    a.add_argument("--cikti", metavar="DOSYA")
    a.set_defaults(fonksiyon=komut_kalibre)
    return p


def main(argv: list[str]) -> int:
    try:
        args = ayristirici().parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2
    if getattr(args, "paralel", 1) < 1:
        print("hata: --paralel en az 1 olmalı", file=sys.stderr)
        return 2
    try:
        return args.fonksiyon(args)
    except KullanimHatasi as exc:
        print(f"hata: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
