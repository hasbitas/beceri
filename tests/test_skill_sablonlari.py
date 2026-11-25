"""Hazır skill'lerle gelen çalıştırılabilir şablonlar: çalışır ve hesaptan doğru sayı basar."""
import math
import subprocess
import sys
import xml.etree.ElementTree as ET

from conftest import SKILLER

LEVHA = SKILLER / "nesne-merkezli-gorsel" / "assets" / "sablon" / "levha.py"
SVG = "{http://www.w3.org/2000/svg}"


def kos(*argv):
    return subprocess.run([sys.executable, "-I", str(LEVHA), *argv], check=False, capture_output=True, text=True,
                          encoding="utf-8")


def metinler(yol):
    return [t.text for t in ET.parse(yol).getroot().iter(SVG + "text")]


def test_levha_svg_uretir_ve_sayilar_hesaptan(tmp_path):
    cikti = tmp_path / "levhalar"
    r = kos("--cikti", str(cikti))
    assert r.returncode == 0, r.stderr
    assert sorted(p.name for p in cikti.iterdir()) == ["patlatilmis.svg", "rc-sarj.svg"]

    rc = metinler(cikti / "rc-sarj.svg")
    for k in range(1, 6):
        beklenen = f"%{100 * (1 - math.exp(-k)):.1f}".replace(".", ",")
        assert beklenen in rc
    assert "%63,2" in rc

    katman = metinler(cikti / "patlatilmis.svg")
    assert "TOPLAM 13,6 mm · 5 KATMAN" in katman


def test_levha_bilinmeyen_ad_2(tmp_path):
    r = kos("--cikti", str(tmp_path), "yok")
    assert r.returncode == 2 and "bilinmeyen levha" in r.stderr
