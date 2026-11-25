"""Skill iskeleti: şablondan açılan klasör doğrulamadan hatasız geçer."""
import pytest
from conftest import SKILLER

from beceri.ayar import Ayar
from beceri.dogrula import skill_denetle
from beceri.yeni import olustur, olustur_metin

pytestmark = pytest.mark.usefixtures("calisma_klasoru")


def test_iskelet_hatasiz_yalniz_yer_tutucu_uyarisi(tmp_path):
    k = olustur("rapor-yazimi", tmp_path / "skills")
    assert (k / "SKILL.md").is_file()
    s = skill_denetle(k)
    assert s.hatalar == []
    assert [b.kural for b in s.uyarilar] == ["B25"]
    assert s.ad == "rapor-yazimi"


def test_iskelet_doldurulunca_temiz(tmp_path):
    k = olustur("rapor-yazimi", tmp_path, aciklama="Rapor yazar. Kullan - rapor istenince. Kullanma - özet için.")
    metin = (k / "SKILL.md").read_text(encoding="utf-8").replace("DOLDUR: ", "")
    (k / "SKILL.md").write_text(metin, encoding="utf-8")
    s = skill_denetle(k)
    assert s.hatalar == [] and s.uyarilar == []


def test_uzun_aciklama_satirlara_bolunur(tmp_path):
    aciklama = "Kullan - " + "uzun bir açıklama sözcüğü " * 20 + "Kullanma - y."
    k = olustur("uzun", tmp_path, aciklama=aciklama)
    satirlar = (k / "SKILL.md").read_text(encoding="utf-8").splitlines()
    assert all(len(s) <= 102 for s in satirlar[:8])
    assert skill_denetle(k).hatalar == []


@pytest.mark.parametrize("ad", ["Buyuk", "a--b", "", "claude-x", "x" * 65])
def test_gecersiz_ad(tmp_path, ad):
    with pytest.raises(ValueError):
        olustur(ad, tmp_path)
    assert list(tmp_path.iterdir()) == [tmp_path / ".git"]


@pytest.mark.parametrize("aciklama", ["<x> yapar", "   ", "a" * 1025])
def test_gecersiz_aciklama(tmp_path, aciklama):
    with pytest.raises(ValueError):
        olustur("x", tmp_path, aciklama=aciklama)


def test_var_olan_klasor(tmp_path):
    olustur("x", tmp_path)
    with pytest.raises(FileExistsError):
        olustur("x", tmp_path)


def test_ayrilmis_ad_ayardan(tmp_path):
    olustur("claude-x", tmp_path, ayrilmis=())
    with pytest.raises(ValueError):
        olustur("firma-x", tmp_path, ayrilmis=("firma",))


def test_skill_tasarimi_sablonu_ile_ayni():
    asset = (SKILLER / "skill-tasarimi" / "assets" / "skill-template.md").read_text(encoding="utf-8")
    assert asset == olustur_metin("ornek-skill")


def test_iskelet_ayarla_dogrulanir(tmp_path):
    k = olustur("x", tmp_path)
    s = skill_denetle(k, Ayar().kapat(["B25"]))
    assert s.hatalar == [] and s.uyarilar == []
