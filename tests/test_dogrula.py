"""Doğrulama kuralları: her kural için geçen ve kalan sentetik skill; ayar dosyası etkileri."""
import os
import sys

import pytest
from conftest import GECERLI_ACIKLAMA, SKILLER, skill

from beceri import ayar as ayar_mod
from beceri.ayar import Ayar, ayar_kur
from beceri.dogrula import ozet, skill_denetle, skill_yollari, tara
from beceri.kurallar import KURAL, KURALLAR

pytestmark = pytest.mark.usefixtures("calisma_klasoru")

# Sır ve ev dizini örnekleri parçalanarak yazılır: depo taraması bunları gerçek bulgu sanmasın.
EV = "/ho" + "me/ayse/proje/notlar.md"
EV_WIN = "C:\\" + "Us" + "ers\\ayse\\Desktop\\x.txt"
AWS = "AKIA" + "ABCDEFGH" + "IJKLMNOP"
GITHUB = "gh" + "p_" + "a1B2" * 9
OZEL_ANAHTAR = "-----BEGIN " + "RSA PRIVATE KEY-----"
ATAMA = 'api_key = "' + "q8Zt4mN2vB7xK1pL9wR3" + '"'


def kodlar(sonuc, tur=None):
    if tur == "hata":
        return [b.kural for b in sonuc.hatalar]
    if tur == "uyari":
        return [b.kural for b in sonuc.uyarilar]
    return [b.kural for b in sonuc.hatalar + sonuc.uyarilar]


def denetle(klasor, **ayar):
    return skill_denetle(klasor, ayar_kur(ayar) if ayar else Ayar())


# ------------------------------------------------------------------ temel
def test_temiz_skill_bulgusuz(tmp_path):
    s = denetle(skill(tmp_path, "temiz"))
    assert kodlar(s) == []
    assert s.ad == "temiz"
    assert s.olcum["govde_satir"] == 3
    assert s.olcum["aciklama_uzunluk"] == len(GECERLI_ACIKLAMA)


def test_kural_kimlikleri_kalici_ve_sirali():
    kimlikler = [k.kimlik for k in KURALLAR]
    assert kimlikler == [f"B{i:02d}" for i in range(1, len(KURALLAR) + 1)]
    assert all(k.onem in ("hata", "uyari") and k.aciklama for k in KURALLAR)


def test_gonderilen_skiller_kati_gecer():
    sonuclar = tara([SKILLER])
    assert {s.ad for s in sonuclar} == {"skill-tasarimi", "kodlama-benchmark-yazimi", "nesne-merkezli-gorsel"}
    assert ozet(sonuclar)["hata"] == 0
    assert ozet(sonuclar)["uyari"] == 0


# ------------------------------------------------------------------ B01
def test_b01_skill_kokunde_skillmd_olmayan_klasor(tmp_path):
    kok = tmp_path / "skills"
    skill(kok, "iyi")
    (kok / "bos").mkdir()
    sonuclar = {s.yol.rsplit("/", 1)[-1]: s for s in tara([kok])}
    assert kodlar(sonuclar["bos"]) == ["B01"]
    assert kodlar(sonuclar["iyi"]) == []


def test_b01_skill_olmayan_agacta_ilgisiz_klasorler_sayilmaz(tmp_path):
    skill(tmp_path / "depo" / "skills", "iyi")
    (tmp_path / "depo" / "src" / "paket").mkdir(parents=True)
    (tmp_path / "depo" / ".gizli").mkdir()
    sonuclar = tara([tmp_path / "depo"])
    assert [s.ad for s in sonuclar] == ["iyi"]
    assert kodlar(sonuclar[0]) == []


def test_b01_tek_klasor_skillmd_yok(tmp_path):
    (tmp_path / "x").mkdir()
    assert kodlar(denetle(tmp_path / "x")) == ["B01"]


# ------------------------------------------------------------------ B02
@pytest.mark.parametrize("metin", [
    "# başlık yok\n",
    "---\nname: x\ndescription: y\n",
    "---\nname: x\ndescription: Use when: x\n---\n",
    "---\nname: x\nname: y\n---\n",
    "---\n- a\n- b\n---\n",
])
def test_b02_onbilgi_yok_ya_da_bozuk(tmp_path, metin):
    k = tmp_path / "x"
    k.mkdir()
    (k / "SKILL.md").write_text(metin, encoding="utf-8")
    assert "B02" in kodlar(denetle(k))


def test_b02_crlf_ve_bom_kabul(tmp_path):
    k = skill(tmp_path, "crlf")
    metin = (k / "SKILL.md").read_text(encoding="utf-8")
    (k / "SKILL.md").write_bytes(("\ufeff" + metin).replace("\n", "\r\n").encode("utf-8"))
    assert kodlar(denetle(k)) == []


# ------------------------------------------------------------------ B03 / B04 / B05
@pytest.mark.parametrize("ad", ["Buyuk", "iki--tire", "-bas", "son-", "alt_cizgi", "a" * 65])
def test_b03_ad_bicimi(tmp_path, ad):
    k = skill(tmp_path, "klasor", name=ad)
    assert "B03" in kodlar(denetle(k))


def test_b03_ad_yok_ya_da_metin_degil(tmp_path):
    k = skill(tmp_path, "a", onbilgi=f"description: {GECERLI_ACIKLAMA}")
    assert kodlar(denetle(k)) == ["B03"]
    k = skill(tmp_path, "b", onbilgi=f"name: 5\ndescription: {GECERLI_ACIKLAMA}")
    assert kodlar(denetle(k)) == ["B03"]


def test_b03_azami_uzunluk_ayardan(tmp_path):
    ad = "a" * 70
    assert "B03" not in kodlar(denetle(skill(tmp_path, ad), sinirlar={"ad_azami": 80}))


def test_b04_ad_klasorle_ayni_degil(tmp_path):
    s = denetle(skill(tmp_path, "klasor", name="baska-ad"))
    assert kodlar(s) == ["B04"]
    assert "klasor" in s.hatalar[0].mesaj


@pytest.mark.skipif(sys.platform == "win32", reason="sembolik bağlantı izni gerekir")
def test_b04_baglanti_adi(tmp_path):
    hedef = skill(tmp_path / "gercek", "ornek")
    (tmp_path / "kurulu").mkdir()
    os.symlink(hedef, tmp_path / "kurulu" / "takma-ad")
    sonuclar = tara([tmp_path / "kurulu"])
    assert kodlar(sonuclar[0]) == ["B04"]
    assert "takma-ad" in sonuclar[0].hatalar[0].mesaj


def test_b05_ayrilmis_sozcuk(tmp_path):
    assert kodlar(denetle(skill(tmp_path, "claude-yardimci"))) == ["B05"]
    assert kodlar(denetle(skill(tmp_path, "anthropic-x"))) == ["B05"]
    assert kodlar(denetle(skill(tmp_path, "firma-araci"), ayrilmis_adlar=["firma"])) == ["B05"]
    assert kodlar(denetle(skill(tmp_path, "claude-iki"), ayrilmis_adlar=[])) == []


# ------------------------------------------------------------------ B06 / B07 / B17 / B18
def test_b06_aciklama_yok_bos_metin_degil(tmp_path):
    assert kodlar(denetle(skill(tmp_path, "a", onbilgi="name: a"))) == ["B06"]
    assert kodlar(denetle(skill(tmp_path, "b", onbilgi="name: b\ndescription: ''"))) == ["B06"]
    assert kodlar(denetle(skill(tmp_path, "c", onbilgi="name: c\ndescription: [x, y]"))) == ["B06"]


def test_b06_aciklama_cok_uzun(tmp_path):
    uzun = "Kullan - x. Kullanma - y. " + "a" * 1000
    s = denetle(skill(tmp_path, "uzun", aciklama=uzun))
    assert "B06" in kodlar(s, "hata")
    s = denetle(skill(tmp_path, "uzun2", aciklama=uzun), sinirlar={"aciklama_azami": 2000, "aciklama_uyari": 1500})
    assert kodlar(s) == []


def test_b07_acili_ayrac(tmp_path):
    assert kodlar(denetle(skill(tmp_path, "x", aciklama="Kullan - <etiket> için. Kullanma - y."))) == ["B07"]


def test_b17_sinir_yok(tmp_path):
    assert kodlar(denetle(skill(tmp_path, "x", aciklama="Kullan - kullanıcı x istediğinde."))) == ["B17"]
    for olumsuz in ("Do not use for y.", "Not for y.", "Kullanma - y."):
        assert kodlar(denetle(skill(tmp_path, "y", aciklama="Use when asked. " + olumsuz))) == []


def test_b18_tetik_gec_ya_da_uzun(tmp_path):
    gec = "Belge üretir. " + "x " * 120 + "Kullan - istenince. Kullanma - y."
    assert kodlar(denetle(skill(tmp_path, "a", aciklama=gec))) == ["B18"]
    uzun = "Kullan - istenince. Kullanma - y. " + "z" * 500
    s = denetle(skill(tmp_path, "b", aciklama=uzun))
    assert kodlar(s) == ["B18"] and "karakter" in s.uyarilar[0].mesaj


# ------------------------------------------------------------------ B08 / B09 / B24
def test_b08_bilinmeyen_alan(tmp_path):
    k = skill(tmp_path, "x", ek_onbilgi="sahip: ekip\n")
    assert kodlar(denetle(k)) == ["B08"]
    assert kodlar(denetle(k, ek_alanlar=["sahip"])) == []


def test_temel_alanlar_serbest(tmp_path):
    ek = 'license: MIT\ncompatibility: Python 3.11+\nallowed-tools: Read Grep\nmetadata:\n  surum: "1.0"\n'
    assert kodlar(denetle(skill(tmp_path, "x", ek_onbilgi=ek))) == []


@pytest.mark.parametrize("ek", [
    "compatibility: [a, b]\n",
    "compatibility: " + "c" * 501 + "\n",
    "metadata: metin\n",
    "metadata:\n  surum: 1.0\n",
])
def test_b09_compatibility_metadata(tmp_path, ek):
    assert kodlar(denetle(skill(tmp_path, "x", ek_onbilgi=ek))) == ["B09"]


def test_b24_platform_alani(tmp_path):
    assert kodlar(denetle(skill(tmp_path, "a", ek_onbilgi="user-invocable: false\n"))) == ["B24"]
    ek = "user-invocable: false\ncompatibility: Claude Code\n"
    assert kodlar(denetle(skill(tmp_path, "b", ek_onbilgi=ek))) == []


# ------------------------------------------------------------------ B10 / B19 / B23
def test_b10_govde_azami(tmp_path):
    s = denetle(skill(tmp_path, "a", govde="satır\n" * 501))
    assert kodlar(s) == ["B10"]
    s = denetle(skill(tmp_path, "b", govde="satır\n" * 500))
    assert kodlar(s) == ["B19"]
    s = denetle(skill(tmp_path, "c", govde="satır\n" * 501), sinirlar={"govde_azami_satir": 600,
                                                                     "govde_uyari_satir": 600})
    assert kodlar(s) == []


def test_b19_govde_oneri(tmp_path):
    assert kodlar(denetle(skill(tmp_path, "a", govde="s\n" * 150))) == []
    assert kodlar(denetle(skill(tmp_path, "b", govde="s\n" * 151))) == ["B19"]
    kb = ("k" * 99 + "\n") * 130
    assert kodlar(denetle(skill(tmp_path, "c", govde=kb))) == ["B19"]


def test_b23_uzun_satir_orani(tmp_path):
    uzun = "u" * 130 + "\n"
    assert kodlar(denetle(skill(tmp_path, "a", govde="kısa\n" * 3 + uzun))) == ["B23"]
    assert kodlar(denetle(skill(tmp_path, "b", govde="kısa\n" * 9 + uzun))) == []
    kod = "kısa\n```sh\n" + uzun * 5 + "```\n| " + "t" * 130 + " |\n"
    assert kodlar(denetle(skill(tmp_path, "c", govde=kod))) == []


# ------------------------------------------------------------------ B11 / B12 / B21
def test_b11_anilan_yol(tmp_path):
    govde = "Ayrıntı: [rehber](references/rehber.md) ve `scripts/kos.py`.\n"
    s = denetle(skill(tmp_path, "a", govde=govde))
    assert sorted(b.mesaj for b in s.hatalar) == ["anılan yol yok: references/rehber.md",
                                                 "anılan yol yok: scripts/kos.py"]
    k = skill(tmp_path, "b", govde=govde, dosyalar={"references/rehber.md": "# R\n", "scripts/kos.py": "pass\n"})
    assert kodlar(denetle(k)) == []


def test_b11_kod_blogu_ve_klasor_sayilmaz(tmp_path):
    govde = "```\ncat references/yok.md\n```\nKlasör: `references/`\n"
    assert kodlar(denetle(skill(tmp_path, "a", govde=govde))) == []


def test_b12_referans_zinciri(tmp_path):
    dosyalar = {"references/a.md": "Bkz. [b](b.md) ve [şablon](../assets/s.txt).\n",
                "references/b.md": "# B\n", "assets/s.txt": "x\n"}
    s = denetle(skill(tmp_path, "x", govde="[a](references/a.md)\n", dosyalar=dosyalar))
    assert kodlar(s) == ["B12"]
    assert s.hatalar[0].dosya == "references/a.md"
    dosyalar["references/a.md"] = "Bkz. [şablon](../assets/s.txt) ve https://ornek.test/x.md\n"
    s = denetle(skill(tmp_path, "y", govde="[a](references/a.md)\n", dosyalar=dosyalar))
    assert kodlar(s) == []


def test_b12_skillmd_geri_baglanti(tmp_path):
    dosyalar = {"references/a.md": "Geri: [ana](../SKILL.md)\n"}
    assert kodlar(denetle(skill(tmp_path, "x", govde="[a](references/a.md)\n", dosyalar=dosyalar))) == ["B12"]


def test_b21_icindekiler(tmp_path):
    uzun = "# R\n" + "satır\n" * 101
    k = skill(tmp_path, "a", govde="[r](references/r.md)\n", dosyalar={"references/r.md": uzun})
    assert kodlar(denetle(k)) == ["B21"]
    for baslik in ("## İçindekiler\n", "## Contents\n"):
        k = skill(tmp_path, "b", govde="[r](references/r.md)\n", dosyalar={"references/r.md": baslik + uzun})
        assert kodlar(denetle(k)) == []


# ------------------------------------------------------------------ B13 / B14 / B15
@pytest.mark.parametrize("ad", ["notlar.bak", "SKILL.md.bak.1", "x.orig", "taslak.md~", "SKILL.v2.md"])
def test_b13_artik_dosya(tmp_path, ad):
    assert kodlar(denetle(skill(tmp_path, "x", dosyalar={ad: "eski\n"}))) == ["B13"]


@pytest.mark.parametrize("yol", [EV, EV_WIN, "/root/.config/x"])
def test_b14_ev_dizini(tmp_path, yol):
    s = denetle(skill(tmp_path, "a", govde=f"Dosya: {yol}\n"))
    assert kodlar(s) == ["B14"]
    assert s.hatalar[0].satir is not None
    s = denetle(skill(tmp_path, "b", dosyalar={"scripts/x.py": f"YOL = '{yol}'\n"}))
    assert kodlar(s) == ["B14"]
    assert s.hatalar[0].dosya == "scripts/x.py"


@pytest.mark.parametrize("yol", ["~/.config/x", "$HOME/x", "/ho" + "me/<kullanici>/x", "/rootfs/x", "/usr/bin/env"])
def test_b14_tasinabilir_yollar_gecer(tmp_path, yol):
    assert kodlar(denetle(skill(tmp_path, "a", govde=f"Dosya: `{yol}`\n"))) == []


@pytest.mark.parametrize("sir", [AWS, GITHUB, OZEL_ANAHTAR, ATAMA, "sk-" + "proj-" + "Ab3" * 10])
def test_b15_sir(tmp_path, sir):
    s = denetle(skill(tmp_path, "a", dosyalar={"assets/ayar.txt": f"x\n{sir}\n"}))
    assert kodlar(s) == ["B15"]
    assert s.hatalar[0].satir == 2
    tum = " ".join(b.mesaj for b in s.hatalar)
    assert sir not in tum and sir[-8:] not in tum


@pytest.mark.parametrize("satir", ['api_key = "<anahtarin>"', 'token: "your-token-here-123456"',
                                   'password = "${SIFRE_DEGISKENI_1234}"', 'secret = "kisa1"'])
def test_b15_yer_tutucu_gecer(tmp_path, satir):
    assert kodlar(denetle(skill(tmp_path, "a", govde=satir + "\n"))) == []


def test_b15_ikili_dosya_atlanir(tmp_path):
    assert kodlar(denetle(skill(tmp_path, "a", dosyalar={"assets/r.bin": b"\0" + AWS.encode()}))) == []


# ------------------------------------------------------------------ B16
MODEL_BAGIMSIZ = 'metadata:\n  model-agnostic: "true"\n'


def test_b16_model_adi(tmp_path):
    govde = "Özet için sonnet yeterli; kod için gpt-5 kullan.\n"
    s = denetle(skill(tmp_path, "a", ek_onbilgi=MODEL_BAGIMSIZ, govde=govde))
    assert kodlar(s) == ["B16"]
    assert s.hatalar[0].satir == 9
    assert "sonnet" in s.hatalar[0].mesaj
    assert kodlar(denetle(skill(tmp_path, "b", govde=govde))) == []


def test_b16_bildirim_bicimleri_ve_ek_adlar(tmp_path):
    ek = 'metadata:\n  model-bagimsiz: "evet"\n'
    assert kodlar(denetle(skill(tmp_path, "a", ek_onbilgi=ek, govde="claude-x-9 ile\n"))) == ["B16"]
    k = skill(tmp_path, "b", ek_onbilgi=MODEL_BAGIMSIZ, govde="ozelmodel ile koş\n")
    assert kodlar(denetle(k)) == []
    assert kodlar(denetle(k, model_adlari=["ozelmodel"])) == ["B16"]


def test_b16_urun_adlari_sayilmaz(tmp_path):
    govde = "Claude Code, Codex ve Cursor için; gpt veya opusculum sözcükleri model değildir.\n"
    assert kodlar(denetle(skill(tmp_path, "a", ek_onbilgi=MODEL_BAGIMSIZ, govde=govde))) == []


# ------------------------------------------------------------------ B20 / B22 / B25
def test_b20_tarih(tmp_path):
    s = denetle(skill(tmp_path, "a", govde="# X\n\n2026-01-15 tarihinde değişti.\n"))
    assert kodlar(s) == ["B20"]
    assert s.uyarilar[0].satir == 9
    assert kodlar(denetle(skill(tmp_path, "b", govde="Sürüm 12026-01-150\n"))) == []


def test_b22_ayni_ad(tmp_path):
    skill(tmp_path / "k1", "ayni")
    skill(tmp_path / "k2", "ayni")
    sonuclar = tara([tmp_path / "k1", tmp_path / "k2"])
    assert [kodlar(s) for s in sonuclar] == [["B22"], ["B22"]]


def test_b22_ayni_klasor_iki_kez_tek_sayilir(tmp_path):
    k = skill(tmp_path, "tek")
    assert [kodlar(s) for s in tara([k, k])] == [[]]


def test_b25_yer_tutucu(tmp_path):
    assert kodlar(denetle(skill(tmp_path, "a", govde="DOLDUR: amaç\n"))) == ["B25"]


# ------------------------------------------------------------------ ayar
def test_ayar_kapali_onem_muaf(tmp_path):
    k = skill(tmp_path, "x", aciklama="Kullan - istenince.", govde="2026-01-15\n")
    assert sorted(kodlar(denetle(k))) == ["B17", "B20"]
    assert kodlar(denetle(k, kapali=["b20"])) == ["B17"]
    s = denetle(k, onem={"B17": "hata"})
    assert kodlar(s, "hata") == ["B17"] and kodlar(s, "uyari") == ["B20"]
    s = denetle(k, muaf=[{"skill": "x", "kural": "B20", "gerekce": "sürüm notu"}])
    assert kodlar(s) == ["B17"]
    assert s.muaflar[0].kural == "B20" and s.muaflar[0].gerekce == "sürüm notu"


@pytest.mark.parametrize("ham, parca", [
    ({"bilinmez": 1}, "bilinmeyen ayar"),
    ({"kapali": ["B99"]}, "bilinmeyen kural"),
    ({"kapali": "B01"}, "metin listesi"),
    ({"kati": "evet"}, "true/false"),
    ({"sinirlar": {"yok": 1}}, "bilinmeyen sınır"),
    ({"sinirlar": {"govde_azami_satir": 0}}, "pozitif"),
    ({"sinirlar": {"govde_azami_satir": 1.5}}, "sayı"),
    ({"onem": {"B01": "kritik"}}, "hata"),
    ({"muaf": [{"skill": "x", "kural": "B01"}]}, "gerekce"),
])
def test_ayar_hatalari(ham, parca):
    with pytest.raises(ValueError, match=parca):
        ayar_kur(ham)


def test_ayar_dosyasi_bulma(tmp_path):
    (tmp_path / "proje" / "alt").mkdir(parents=True)
    assert ayar_mod.bul(tmp_path / "proje" / "alt") is None
    (tmp_path / "proje" / "pyproject.toml").write_text("[project]\nname = 'x'\n", encoding="utf-8")
    assert ayar_mod.bul(tmp_path / "proje" / "alt") is None
    (tmp_path / "proje" / "pyproject.toml").write_text("[tool.beceri]\nkapali = ['B20']\n", encoding="utf-8")
    bulunan = ayar_mod.bul(tmp_path / "proje" / "alt")
    assert bulunan.name == "pyproject.toml"
    assert ayar_mod.dosyadan(bulunan).kapali == {"B20"}
    (tmp_path / "proje" / "alt" / ".beceri.toml").write_text("kati = true\n", encoding="utf-8")
    a = ayar_mod.yukle(baslangic=tmp_path / "proje" / "alt")
    assert a.kati is True and a.kapali == frozenset()


def test_ayar_bozuk_toml(tmp_path):
    (tmp_path / ".beceri.toml").write_text("kati = = 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="okunamadı"):
        ayar_mod.yukle()


def test_ayar_kapat_bilinmeyen():
    with pytest.raises(ValueError):
        Ayar().kapat(["B77"])
    assert Ayar().kapat(["b01", " B02 "]).kapali == {"B01", "B02"}


def test_ayar_atla(tmp_path):
    skill(tmp_path / "skills", "a")
    skill(tmp_path / "skills" / "arsiv", "b")
    yollar, _ = skill_yollari([tmp_path / "skills"], ayar_kur({"atla": ["arsiv"]}))
    assert [p.name for p in yollar] == ["a"]


# ------------------------------------------------------------------ tarama
def test_yollar_skillmd_dosyasi_ve_hatalar(tmp_path):
    k = skill(tmp_path, "a")
    yollar, _ = skill_yollari([k / "SKILL.md"], Ayar())
    assert yollar == [k]
    with pytest.raises(FileNotFoundError):
        skill_yollari([tmp_path / "yok"], Ayar())
    (tmp_path / "not.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        skill_yollari([tmp_path / "not.txt"], Ayar())


def test_ic_ice_skill_agaci(tmp_path):
    skill(tmp_path / "eklentiler" / "e1" / "skills", "s1")
    skill(tmp_path / "eklentiler" / "e2" / "skills", "s2")
    assert sorted(s.ad for s in tara([tmp_path / "eklentiler"])) == ["s1", "s2"]


def test_kural_tablosu_tam():
    assert set(KURAL) == {f"B{i:02d}" for i in range(1, 26)}
