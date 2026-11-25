"""beceri.benchmark testleri: bütünlük, doğrulama, puanlama ve yol güvenliği."""
import json
import os
import shutil
import sys
import textwrap
from pathlib import Path

import pytest

from beceri import benchmark

KOK = Path(__file__).resolve().parents[1]
VERI = KOK / "benchmark" / benchmark.VARSAYILAN_VERI


def calistir(capsys, *argv):
    kod = benchmark.main(list(argv))
    cikti = capsys.readouterr()
    return kod, cikti.out, cikti.err


DOGRU = "def add(a, b):\n    return a + b\n"
YANLIS = "def add(a, b):\n    return a - b\n"
TEST = textwrap.dedent("""\
    import unittest
    import solution

    class AddTests(unittest.TestCase):
        def test_{ad}(self):
            self.assertEqual(solution.add(2, 3), 5)
            self.assertEqual(solution.add(-1, 1), 0)
""")


def sentetik_gorev(kok: Path, kimlik: str, gold: str = DOGRU, broken: str = YANLIS,
                   allowed=("solution.py",), beklenen=True) -> Path:
    klasor = kok / "tasks" / kimlik
    for surum, icerik in (("gold", gold), ("broken", broken)):
        (klasor / surum).mkdir(parents=True)
        (klasor / surum / "solution.py").write_text(icerik, encoding="utf-8")
    for alt, ad in (("tests_visible", "gorunur"), ("tests_hidden", "gizli")):
        (klasor / alt).mkdir()
        (klasor / alt / "test_solution.py").write_text(TEST.format(ad=ad), encoding="utf-8")
    veri = {"task_id": kimlik, "kind": "single-file",
            "specification": "Implement add(a, b) in solution.py returning a + b.",
            "allowed_paths": list(allowed)}
    if beklenen:
        veri["expected_tests"] = {"visible": 1, "hidden": 1}
    (klasor / "task.json").write_text(json.dumps(veri), encoding="utf-8")
    return klasor


@pytest.fixture
def sentetik_veri(tmp_path):
    kok = tmp_path / "veri"
    sentetik_gorev(kok, "toy-add")
    sentetik_gorev(kok, "toy-add-two")
    (kok / "split.json").write_text(json.dumps(
        {"format": 1, "groups": {"toy-add": "development", "toy-add-two": "final"}}), encoding="utf-8")
    return kok


# --------------------------------------------------------------------------
# Gönderilen veri


def test_gonderilen_veri_yapisi():
    veri = benchmark.veri_yukle(VERI)
    assert len(veri.gorevler) == 75
    assert all(g.bolum in benchmark.BOLUMLER for g in veri.gorevler.values())
    assert all(g.beklenen for g in veri.gorevler.values())
    for g in veri.gorevler.values():
        for surum in ("gold", "broken"):
            for p in g.izinli + g.salt_okunur:
                assert (g.klasor / surum / p).is_file(), (g.kimlik, surum, p)


def test_manifest_gonderilen_veride_tamam(capsys):
    sonuc = benchmark.butunluk_denetle(VERI)
    assert sonuc["tamam"], sonuc
    kod, out, _ = calistir(capsys, "butunluk", "--veri", str(VERI))
    assert kod == 0 and "Bütünlük tamam" in out


def test_manifest_degisiklik_eksik_ve_fazla_dosyayi_yakalar(capsys, sentetik_veri):
    assert calistir(capsys, "butunluk", "--veri", str(sentetik_veri), "--yaz")[0] == 0
    assert calistir(capsys, "butunluk", "--veri", str(sentetik_veri))[0] == 0
    hedef = sentetik_veri / "tasks" / "toy-add" / "gold" / "solution.py"
    hedef.write_text(DOGRU + "# değişti\n", encoding="utf-8")
    (sentetik_veri / "tasks" / "toy-add" / "fazla.txt").write_text("x", encoding="utf-8")
    (sentetik_veri / "split.json").unlink()
    sonuc = benchmark.butunluk_denetle(sentetik_veri)
    assert sonuc["degisik"] == ["tasks/toy-add/gold/solution.py"]
    assert sonuc["fazla"] == ["tasks/toy-add/fazla.txt"]
    assert sonuc["eksik"] == ["split.json"]
    assert calistir(capsys, "butunluk", "--veri", str(sentetik_veri))[0] == 1


def test_manifest_yol_gecisini_reddeder(capsys, sentetik_veri):
    (sentetik_veri / benchmark.MANIFEST).write_text("0" * 64 + "  ../disari.txt\n", encoding="utf-8")
    assert calistir(capsys, "butunluk", "--veri", str(sentetik_veri))[0] == 2


def test_listele(capsys):
    kod, out, _ = calistir(capsys, "listele", "--veri", str(VERI), "--json")
    assert kod == 0
    veri = json.loads(out)
    assert veri["gorev_sayisi"] == 75
    assert veri["bolumler"] == {"development": 25, "selection": 25, "final": 25}
    assert veri["turler"] == {"single-file": 60, "multi-file": 15}


# --------------------------------------------------------------------------
# dogrula


def test_dogrula_gercek_gorevler(capsys):
    kod, out, _ = calistir(capsys, "dogrula", "--veri", str(VERI), "--json", "--paralel", "3",
                           "--gorev", "clamp-bounds", "--gorev", "chunk-tail", "--gorev", "a-fifo-ledger")
    assert kod == 0, out
    rapor = json.loads(out)
    assert rapor["gecerli"] == 3 and rapor["gecersiz"] == []
    for kimlik, sonuc in rapor["gorevler"].items():
        assert sonuc["gold"]["durum"] == "gecti", kimlik
        assert sonuc["gold"]["gecen_test"] == sonuc["gold"]["toplam_test"] > 0
        assert sonuc["broken"]["durum"] != "gecti", kimlik
        assert sonuc["taslak"]["durum"] != "gecti", kimlik


def test_dogrula_broken_gecerse_gorev_gecersiz(capsys, tmp_path):
    kok = tmp_path / "veri"
    sentetik_gorev(kok, "toy-add", broken=DOGRU)
    kod, out, _ = calistir(capsys, "dogrula", "--veri", str(kok))
    assert kod == 1
    assert "GEÇERSİZ" in out and "broken testleri geçiyor" in out


def test_dogrula_beklenen_test_sayisi_eksikse_bildirir(capsys, tmp_path):
    kok = tmp_path / "veri"
    sentetik_gorev(kok, "toy-add", beklenen=False)
    kod, out, _ = calistir(capsys, "dogrula", "--veri", str(kok))
    assert kod == 1
    assert '{"visible": 1, "hidden": 1}' in out


def test_dogrula_gecerli_sentetik_gorev(capsys, sentetik_veri):
    kod, out, _ = calistir(capsys, "dogrula", "--veri", str(sentetik_veri))
    assert kod == 0, out
    assert "2/2 görev geçerli" in out


# --------------------------------------------------------------------------
# kos


def cozum_yaz(kok: Path, kimlik: str, icerik: str, ad: str = "solution.py") -> None:
    (kok / kimlik).mkdir(parents=True, exist_ok=True)
    (kok / kimlik / ad).write_text(icerik, encoding="utf-8")


def test_kos_puanlama(capsys, sentetik_veri, tmp_path):
    ornek1, ornek2 = tmp_path / "o1", tmp_path / "o2"
    cozum_yaz(ornek1, "toy-add", DOGRU)
    cozum_yaz(ornek1, "toy-add-two", YANLIS)
    cozum_yaz(ornek2, "toy-add", DOGRU)
    # toy-add-two ikinci örnekte yok: eksik sayılır.
    cikti = tmp_path / "rapor.json"
    kod, out, _ = calistir(capsys, "kos", "--veri", str(sentetik_veri), "--cozum-dizini", str(ornek1),
                           "--cozum-dizini", str(ornek2), "--cikti", str(cikti))
    assert kod == 0
    rapor = json.loads(out)
    assert json.loads(cikti.read_text(encoding="utf-8")) == rapor
    assert rapor["ornek_sayisi"] == 2
    assert rapor["gorevler"]["toy-add"]["pass@1"] == 1.0
    assert rapor["gorevler"]["toy-add-two"]["pass@1"] == 0.0
    assert [k["durum"] for k in rapor["gorevler"]["toy-add-two"]["kosular"]] == ["kaldi", "eksik"]
    assert rapor["toplam"]["pass@1"] == 0.5
    assert rapor["toplam"]["cozulen"] == 1
    assert rapor["toplam"]["bolumlere_gore"] == {"development": 1.0, "final": 0.0}


def test_kos_gercek_gorev_gold_ve_broken(capsys, tmp_path):
    gorev = VERI / "tasks" / "clamp-bounds"
    iyi, kotu = tmp_path / "iyi", tmp_path / "kotu"
    for hedef, surum in ((iyi, "gold"), (kotu, "broken")):
        (hedef / "clamp-bounds").mkdir(parents=True)
        shutil.copy(gorev / surum / "solution.py", hedef / "clamp-bounds" / "solution.py")
    kod, out, _ = calistir(capsys, "kos", "--veri", str(VERI), "--gorev", "clamp-bounds",
                           "--cozum-dizini", str(iyi), "--cozum-dizini", str(kotu))
    assert kod == 0
    rapor = json.loads(out)
    assert rapor["butunluk"]["tamam"] is True
    assert rapor["gorevler"]["clamp-bounds"]["pass@1"] == 0.5


def test_kos_aday_conftest_ve_test_dosyalarini_yok_sayar(capsys, sentetik_veri, tmp_path):
    aday = tmp_path / "aday"
    cozum_yaz(aday, "toy-add", YANLIS)
    # Allowed_paths dışındaki dosyalar kopyalanmaz; testleri ezme denemesi işe yaramaz.
    cozum_yaz(aday, "toy-add", "import pytest\npytest.skip('x', allow_module_level=True)\n", "conftest.py")
    cozum_yaz(aday, "toy-add", "def test_x():\n    pass\n", "test_solution.py")
    kod, out, _ = calistir(capsys, "kos", "--veri", str(sentetik_veri), "--gorev", "toy-add",
                           "--cozum-dizini", str(aday))
    assert kod == 0
    assert json.loads(out)["gorevler"]["toy-add"]["pass@1"] == 0.0


@pytest.mark.parametrize("sonda", ["bos-cikis", "sahte-basari", "sonsuz-dongu"])
def test_kos_kosucuyu_kandirma_sondalari_gecmez(capsys, sentetik_veri, tmp_path, sonda):
    aday = tmp_path / "aday"
    cozum_yaz(aday, "toy-add", benchmark.SONDALAR[sonda])
    kod, out, _ = calistir(capsys, "kos", "--veri", str(sentetik_veri), "--gorev", "toy-add",
                           "--cozum-dizini", str(aday), "--zaman-asimi", "3")
    assert kod == 0
    sonuc = json.loads(out)["gorevler"]["toy-add"]
    assert sonuc["pass@1"] == 0.0
    assert sonuc["kosular"][0]["durum"] in ("hata", "zaman-asimi")


@pytest.mark.skipif(os.name != "posix", reason="sembolik bağ testi POSIX'e özgü")
def test_kos_sembolik_bag_reddedilir(capsys, sentetik_veri, tmp_path):
    disari = tmp_path / "disari.py"
    disari.write_text(DOGRU, encoding="utf-8")
    aday = tmp_path / "aday"
    (aday / "toy-add").mkdir(parents=True)
    (aday / "toy-add" / "solution.py").symlink_to(disari)
    kod, out, _ = calistir(capsys, "kos", "--veri", str(sentetik_veri), "--gorev", "toy-add",
                           "--cozum-dizini", str(aday))
    assert kod == 0
    assert json.loads(out)["gorevler"]["toy-add"]["kosular"][0]["durum"] == "eksik"


# --------------------------------------------------------------------------
# Yol güvenliği ve kullanım hataları


@pytest.mark.parametrize("kimlik", ["../tasks", "..", "a/b", "/etc", "A-Upper", "x\\y", ""])
def test_gorev_kimliginde_yol_gecisi_reddedilir(capsys, tmp_path, kimlik):
    kod, _, err = calistir(capsys, "dogrula", "--veri", str(VERI), "--gorev", kimlik)
    assert kod == 2 and "geçersiz görev kimliği" in err
    kod, _, err = calistir(capsys, "kos", "--veri", str(VERI), "--gorev", kimlik,
                           "--cozum-dizini", str(tmp_path))
    assert kod == 2


def test_bilinmeyen_gorev(capsys):
    kod, _, err = calistir(capsys, "dogrula", "--veri", str(VERI), "--gorev", "yok-boyle-gorev")
    assert kod == 2 and "bilinmeyen görev" in err


@pytest.mark.parametrize("yol", ["../disari.py", "/abs.py", "a/../b.py", "a\\b.py", "./x.py", "C:/x.py"])
def test_task_json_guvensiz_allowed_paths_reddedilir(capsys, tmp_path, yol):
    kok = tmp_path / "veri"
    sentetik_gorev(kok, "toy-add", allowed=(yol,))
    kod, _, err = calistir(capsys, "listele", "--veri", str(kok))
    assert kod == 2 and "hata:" in err


def test_task_id_klasorle_eslesmeli(capsys, tmp_path):
    kok = tmp_path / "veri"
    klasor = sentetik_gorev(kok, "toy-add")
    veri = json.loads((klasor / "task.json").read_text(encoding="utf-8"))
    veri["task_id"] = "baska"
    (klasor / "task.json").write_text(json.dumps(veri), encoding="utf-8")
    assert calistir(capsys, "listele", "--veri", str(kok))[0] == 2


def test_kullanim_hatalari(capsys, tmp_path):
    assert calistir(capsys)[0] == 2
    assert calistir(capsys, "bilinmeyen")[0] == 2
    assert calistir(capsys, "listele", "--veri", str(tmp_path / "yok"))[0] == 2
    assert calistir(capsys, "kos", "--veri", str(VERI), "--cozum-dizini", str(tmp_path / "yok"),
                    "--gorev", "clamp-bounds")[0] == 2
    assert calistir(capsys, "--help")[0] == 0


def test_kalibre_sentetik(capsys, sentetik_veri, tmp_path):
    aday = tmp_path / "aday"
    cozum_yaz(aday, "toy-add", DOGRU)
    kod, out, _ = calistir(capsys, "kalibre", "--veri", str(sentetik_veri), "--tekrar", "2",
                           "--sonda", "--sonda-zaman-asimi", "3", "--cozum-dizini", str(aday))
    assert kod == 0, out
    rapor = json.loads(out)
    assert rapor["sorunlu"] == []
    assert rapor["zorluk"]["toy-add"]["etiket"] == "kolay"
    assert rapor["zorluk"]["toy-add-two"]["etiket"] == "cozulmedi"
    assert all(d != "gecti" for d in rapor["gorevler"]["toy-add"]["sondalar"].values())


def test_gorev_kodu_bu_surecte_calistirilmaz(sentetik_veri, monkeypatch):
    # Gold kodu bu süreçte içe aktarılsaydı 'solution' modülü sys.modules'a girerdi.
    monkeypatch.delitem(sys.modules, "solution", raising=False)
    veri = benchmark.veri_yukle(sentetik_veri)
    kosu = benchmark.testleri_kos(veri.gorevler["toy-add"],
                                  benchmark.gold_dosyalari(veri.gorevler["toy-add"]), 30)
    assert kosu.basarili
    assert "solution" not in sys.modules
