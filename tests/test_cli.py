"""Komut satırı: çıktı biçimleri, çıkış kodları, ayar bayrakları, benchmark aktarımı."""
import json
import os
import subprocess
import sys
import types

import pytest
from conftest import KOK, SKILLER, skill

from beceri import __version__
from beceri.cli import main
from beceri.kurallar import KURALLAR

pytestmark = pytest.mark.usefixtures("calisma_klasoru")


def kos(capsys, *argv):
    kod = main(list(argv))
    cikti = capsys.readouterr()
    return kod, cikti.out, cikti.err


# ------------------------------------------------------------------ dogrula
def test_temiz_cikis_0(tmp_path, capsys):
    skill(tmp_path / "skills", "iyi")
    kod, out, _ = kos(capsys, "dogrula", "skills")
    assert kod == 0
    assert "[TAMAM] skills/iyi" in out
    assert out.rstrip().endswith("1 skill: 0 hata, 0 uyarı")


def test_hata_cikis_1_ve_insan_ciktisi(tmp_path, capsys):
    skill(tmp_path / "skills", "kotu", name="Kotu")
    kod, out, _ = kos(capsys, "dogrula", "skills")
    assert kod == 1
    assert "[HATA] skills/kotu" in out
    assert "B03 hata  SKILL.md: name biçimi geçersiz" in out
    assert "B04 hata" in out


def test_uyari_cikis_0_kati_1(tmp_path, capsys):
    skill(tmp_path, "uyarili", govde="2026-01-15\n")
    kod, out, _ = kos(capsys, "dogrula", "uyarili")
    assert kod == 0 and "[UYARI] uyarili" in out and "B20 uyari SKILL.md:7" in out
    assert kos(capsys, "dogrula", "--kati", "uyarili")[0] == 1
    (tmp_path / ".beceri.toml").write_text("kati = true\n", encoding="utf-8")
    assert kos(capsys, "dogrula", "uyarili")[0] == 1
    assert kos(capsys, "dogrula", "--ayarsiz", "uyarili")[0] == 0


def test_json_ciktisi(tmp_path, capsys):
    skill(tmp_path / "skills", "iyi")
    skill(tmp_path / "skills", "kotu", aciklama="Kullan - x. Kullanma - <y>.")
    kod, out, _ = kos(capsys, "dogrula", "--json", "skills")
    assert kod == 1
    veri = json.loads(out)
    assert veri["beceri"] == __version__
    assert veri["ozet"] == {"skill": 2, "hata": 1, "uyari": 0, "muaf": 0}
    kotu = next(s for s in veri["skiller"] if s["ad"] == "kotu")
    assert kotu["yol"] == "skills/kotu"
    assert kotu["hatalar"] == [{"kural": "B07", "mesaj": "description '<' ya da '>' içeriyor",
                                "dosya": "SKILL.md", "satir": None, "gerekce": None}]
    assert set(kotu["olcum"]) == {"govde_satir", "govde_kb", "aciklama_uzunluk"}


def test_kapat_bayragi_ve_ayar_dosyasi(tmp_path, capsys):
    skill(tmp_path, "x", govde="2026-01-15\n", ek_onbilgi="sahip: ekip\n")
    assert kos(capsys, "dogrula", "x")[0] == 1
    assert kos(capsys, "dogrula", "--kapat", "B08", "x")[0] == 0
    (tmp_path / "pyproject.toml").write_text(
        '[tool.beceri]\nek_alanlar = ["sahip"]\n\n[[tool.beceri.muaf]]\nskill = "x"\nkural = "B20"\n'
        'gerekce = "sürüm notu"\n', encoding="utf-8")
    kod, out, _ = kos(capsys, "dogrula", "--kati", "x")
    assert kod == 0
    assert "B20 muaf" in out and "[gerekçe: sürüm notu]" in out and "1 muaf" in out


def test_acik_ayar_yolu(tmp_path, capsys):
    skill(tmp_path, "x", govde="2026-01-15\n")
    (tmp_path / "ozel.toml").write_text('kapali = ["B20"]\n', encoding="utf-8")
    kod, out, _ = kos(capsys, "dogrula", "--kati", "--ayar", "ozel.toml", "x")
    assert kod == 0, out


@pytest.mark.parametrize("argv", [
    ["dogrula", "yok"],
    ["dogrula", "--kapat", "B99", "."],
    ["dogrula", "--ayar", "yok.toml", "."],
])
def test_kullanim_hatalari_2(capsys, argv):
    kod, _, err = kos(capsys, *argv)
    assert kod == 2
    assert err.startswith("beceri: ")


def test_bozuk_ayar_2(tmp_path, capsys):
    skill(tmp_path, "x")
    (tmp_path / ".beceri.toml").write_text('bilinmez = 1\n', encoding="utf-8")
    kod, _, err = kos(capsys, "dogrula", "x")
    assert kod == 2 and "bilinmeyen ayar anahtarı" in err


def test_skill_olmayan_dosya_2(tmp_path, capsys):
    (tmp_path / "not.md").write_text("x", encoding="utf-8")
    assert kos(capsys, "dogrula", "not.md")[0] == 2


def test_argparse_hatasi_2(capsys):
    with pytest.raises(SystemExit) as e:
        main(["dogrula"])
    assert e.value.code == 2
    with pytest.raises(SystemExit) as e:
        main([])
    assert e.value.code == 2


def test_skill_bulunamadi_1(tmp_path, capsys):
    (tmp_path / "bos").mkdir()
    kod, _, err = kos(capsys, "dogrula", "bos")
    assert kod == 1 and "skill bulunamadı" in err


def test_gonderilen_skiller_kati(capsys):
    kod, out, _ = kos(capsys, "dogrula", "--kati", "--ayarsiz", str(SKILLER))
    assert kod == 0, out
    assert "3 skill: 0 hata, 0 uyarı" in out


# ------------------------------------------------------------------ yeni
def test_yeni_ve_dogrula(tmp_path, capsys):
    kod, out, _ = kos(capsys, "yeni", "not-alma", "--hedef", "skills")
    assert kod == 0
    assert "oluşturuldu: skills" in out and "B25 uyari" in out
    assert (tmp_path / "skills" / "not-alma" / "SKILL.md").is_file()
    assert kos(capsys, "dogrula", "skills")[0] == 0
    assert kos(capsys, "dogrula", "--kati", "skills")[0] == 1
    kod, _, err = kos(capsys, "yeni", "not-alma", "--hedef", "skills")
    assert kod == 1 and "zaten var" in err


def test_yeni_gecersiz_ad_2(capsys):
    kod, _, err = kos(capsys, "yeni", "Kotu_Ad")
    assert kod == 2 and "geçersiz ad" in err


# ------------------------------------------------------------------ kurallar
def test_kurallar_listesi(capsys):
    kod, out, _ = kos(capsys, "kurallar")
    assert kod == 0
    assert len(out.strip().splitlines()) == len(KURALLAR)
    kod, out, _ = kos(capsys, "kurallar", "--json")
    veri = json.loads(out)
    assert [k["kimlik"] for k in veri] == [k.kimlik for k in KURALLAR]
    assert {k["onem"] for k in veri} == {"hata", "uyari"}


# ------------------------------------------------------------------ benchmark
def test_benchmark_aktarim(monkeypatch, capsys):
    alinan = []

    def sahte_main(argv):
        alinan.append(argv)
        return 3

    monkeypatch.setitem(sys.modules, "beceri.benchmark", types.SimpleNamespace(main=sahte_main))
    assert main(["benchmark", "kos", "--json", "-x"]) == 3
    assert alinan == [["kos", "--json", "-x"]]


def test_benchmark_modulu_yoksa_2(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "beceri.benchmark", None)
    kod, _, err = kos(capsys, "benchmark", "--help")
    assert kod == 2
    assert "benchmark modülü bulunamadı" in err


def test_benchmark_ic_import_hatasi_gizlenmez(monkeypatch):
    def bozuk(ad, *args, **kwargs):
        if ad == "beceri.benchmark":
            raise ModuleNotFoundError("bağımlılık yok", name="olmayan_paket")
        raise AssertionError(ad)

    monkeypatch.setattr("importlib.import_module", bozuk)
    with pytest.raises(ModuleNotFoundError):
        main(["benchmark"])


# ------------------------------------------------------------------ modül olarak
def test_python_m_beceri(tmp_path):
    skill(tmp_path, "iyi")
    ortam = dict(os.environ, PYTHONPATH=str(KOK / "src"), PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-m", "beceri", "dogrula", "iyi"], check=False, cwd=tmp_path, env=ortam,
                       capture_output=True)
    assert r.returncode == 0, r.stderr
    assert b"\r\n" not in r.stdout
    assert "[TAMAM] iyi" in r.stdout.decode("utf-8")
    r = subprocess.run([sys.executable, "-m", "beceri", "--version"], check=False, cwd=tmp_path, env=ortam,
                       capture_output=True, text=True)
    assert r.stdout.strip() == f"beceri {__version__}"
