"""Profiller: esnek (varsayılan) ve siki; seçim önceliği, S kuralları, siki iskeleti."""
import json

import pytest
from conftest import SKILLER, skill

from beceri.ayar import Ayar, ayar_kur
from beceri.cli import main
from beceri.dogrula import adim_sorunlari, skill_denetle, tara
from beceri.kurallar import KURAL, KURALLAR
from beceri.yeni import olustur, olustur_metin

pytestmark = pytest.mark.usefixtures("calisma_klasoru")

TABLO = ("| # | Nesne | Eylem | Yetki | Kanıt |\n|---|---|---|---|---|\n"
         "| 1 | `rapor.md` | oku | yok | dosya açıldı |\n"
         "| 2 | `rapor.md` | düzelt | kullanıcı | fark çıktısı |\n")
BOLUMLER = {
    "Amaç": "Raporu düzeltir.\n",
    "Ne zaman kullan / kullanma": "- Kullan: rapor istenince.\n- Kullanma: özet için.\n",
    "Adımlar": TABLO,
    "Değişmezler ve yasaklar": "- Kaynağı silme.\n",
    "Çıktı / rapor biçimi": "Düzeltilmiş dosya ve fark özeti.\n",
    "Referanslar": "- Yok.\n",
}


def siki_govde(baslik="# Rapor\n", **degisen):
    """Geçerli siki gövde; degisen: {bölüm adı: içerik ya da None (bölümü çıkar)}."""
    bolumler = dict(BOLUMLER)
    for ad, icerik in degisen.items():
        bolumler[ad.replace("_", " ")] = icerik
    parcalar = [baslik]
    for ad, icerik in bolumler.items():
        if icerik is not None:
            parcalar.append(f"\n## {ad}\n\n{icerik}")
    return "".join(parcalar)


SIKI = 'metadata:\n  profil: "siki"\n'


def kodlar(sonuc):
    return [b.kural for b in sonuc.hatalar + sonuc.uyarilar]


def siki_denetle(klasor, **ayar):
    return skill_denetle(klasor, (ayar_kur(ayar) if ayar else Ayar()).zorla("siki"))


def adimlar(metin):
    return adim_sorunlari([(i, s) for i, s in enumerate(metin.split("\n"), 1)])


# ------------------------------------------------------------------ seçim ve öncelik
def test_varsayilan_esnek_s_kurallari_denetlenmez(tmp_path):
    s = skill_denetle(skill(tmp_path, "x", govde="Gövde.\n"))
    assert s.profil == "esnek" and kodlar(s) == []


def test_siki_gecerli_govde_temiz(tmp_path):
    s = siki_denetle(skill(tmp_path, "x", govde=siki_govde()))
    assert s.profil == "siki" and kodlar(s) == []


def test_oncelik_cli_metadata_ayar(tmp_path):
    duz = skill(tmp_path, "duz", govde="Gövde.\n")
    bildiren = skill(tmp_path, "bildiren", govde="Gövde.\n", ek_onbilgi=SIKI)
    esnek_bildiren = skill(tmp_path, "esnek-bildiren", govde="Gövde.\n",
                           ek_onbilgi='metadata:\n  profil: "esnek"\n')
    # ayar yok: skill'in bildirdiği geçerli
    assert skill_denetle(duz).profil == "esnek"
    assert skill_denetle(bildiren).profil == "siki"
    # ayar siki: bildirmeyen siki, esnek bildiren esnek kalır
    a = ayar_kur({"profil": "siki"})
    assert skill_denetle(duz, a).profil == "siki"
    assert skill_denetle(esnek_bildiren, a).profil == "esnek"
    # --profil hepsini geçersiz kılar
    assert skill_denetle(bildiren, a.zorla("esnek")).profil == "esnek"
    assert "S01" in kodlar(skill_denetle(esnek_bildiren, Ayar().zorla("siki")))


def test_b26_bilinmeyen_metadata_profil(tmp_path):
    k = skill(tmp_path, "x", ek_onbilgi='metadata:\n  profil: "kati"\n')
    s = skill_denetle(k)
    assert kodlar(s) == ["B26"] and s.profil == "esnek"
    assert "kati" in s.hatalar[0].mesaj


@pytest.mark.parametrize("ham", [{"profil": "kati"}, {"profil": 1}, {"profil": ""}])
def test_ayar_profil_gecersiz(ham):
    with pytest.raises(ValueError, match="profil"):
        ayar_kur(ham)


def test_ayar_profil_buyuk_harf_ve_zorla():
    assert ayar_kur({"profil": "SIKI"}).profil == "siki"
    with pytest.raises(ValueError):
        Ayar().zorla("orta")


def test_kural_profilleri():
    assert {k.profil for k in KURALLAR} == {"ortak", "esnek", "siki"}
    assert KURAL["B19"].profil == "esnek"
    assert [k.kimlik for k in KURALLAR if k.profil == "siki"] == [f"S{i:02d}" for i in range(1, 8)]


# ------------------------------------------------------------------ S01 / S02
def test_s01_baslik_ve_eksik_bolum(tmp_path):
    s = siki_denetle(skill(tmp_path, "a", govde=siki_govde(baslik="Giriş.\n")))
    assert kodlar(s) == ["S01"] and "başlık" in s.hatalar[0].mesaj
    s = siki_denetle(skill(tmp_path, "b", govde=siki_govde(Referanslar=None, Amaç=None)))
    assert kodlar(s) == ["S01"]
    assert s.hatalar[0].mesaj == "eksik bölüm: '## Amaç', '## Referanslar'"
    s = siki_denetle(skill(tmp_path, "c", govde="## Amaç\n\nx\n\n" + siki_govde(Amaç=None)))
    assert kodlar(s) == ["S01"] and "ilk başlık" in s.hatalar[0].mesaj
    s = siki_denetle(skill(tmp_path, "d", govde=siki_govde() + "\n# İkinci\n"))
    assert kodlar(s) == ["S01"] and "birden çok" in s.hatalar[0].mesaj


def test_s02_sira_tanimsiz_tekrar(tmp_path):
    govde = siki_govde().replace("## Amaç", "## Referanslar_", 1)
    govde = govde.replace("## Referanslar\n", "## Amaç\n").replace("## Referanslar_", "## Referanslar")
    s = siki_denetle(skill(tmp_path, "a", govde=govde))
    assert kodlar(s) == ["S02"] and "sırası" in s.hatalar[0].mesaj
    s = siki_denetle(skill(tmp_path, "b", govde=siki_govde() + "\n## Notlar\n\nx\n"))
    assert kodlar(s) == ["S02"] and "tanımsız" in s.hatalar[0].mesaj
    s = siki_denetle(skill(tmp_path, "c", govde=siki_govde() + "\n## Referanslar\n\n- Yok.\n"))
    assert kodlar(s) == ["S02"] and "iki kez" in s.hatalar[0].mesaj


def test_s02_alt_baslik_kod_blogu_ve_ascii_yazim_serbest(tmp_path):
    govde = siki_govde(Adımlar=TABLO + "\n### Ayrıntı\n\n```\n## Kod içinde\n```\n")
    govde = govde.replace("## Amaç", "## amac").replace("## Çıktı / rapor biçimi", "## Cikti/Rapor Bicimi")
    assert kodlar(siki_denetle(skill(tmp_path, "a", govde=govde))) == []


# ------------------------------------------------------------------ S03 / S04
def test_s03_amac(tmp_path):
    assert kodlar(siki_denetle(skill(tmp_path, "a", govde=siki_govde(Amaç="Bir.\nİki.\n")))) == []
    s = siki_denetle(skill(tmp_path, "b", govde=siki_govde(Amaç="Bir.\nİki.\nÜç.\n")))
    assert kodlar(s) == ["S03"] and "3 satır" in s.hatalar[0].mesaj
    assert kodlar(siki_denetle(skill(tmp_path, "c", govde=siki_govde(Amaç="")))) == ["S03"]
    k = skill(tmp_path, "d", govde=siki_govde(Amaç="Bir.\nİki.\nÜç.\n"))
    assert kodlar(siki_denetle(k, sinirlar={"amac_azami_satir": 3})) == []


def test_s04_govde_siki_sinir_b19_yerine(tmp_path):
    uzun = siki_govde(Referanslar="- Yok.\n" + "satır\n" * 140)
    s = siki_denetle(skill(tmp_path, "a", govde=uzun))
    assert kodlar(s) == ["S04"] and s.hatalar[0].kural == "S04"
    assert kodlar(skill_denetle(skill(tmp_path, "b", govde=uzun))) == ["B19"]
    kb = siki_govde(Referanslar="- Yok.\n" + ("k" * 99 + "\n") * 125)
    assert kodlar(siki_denetle(skill(tmp_path, "c", govde=kb))) == ["S04"]
    assert kodlar(siki_denetle(skill(tmp_path, "d", govde=siki_govde()))) == []


# ------------------------------------------------------------------ S05
def test_s05_tablo_ve_liste_bicimi_gecer():
    assert adimlar(TABLO) == (2, [])
    tablo = "| Nesne | Eylem | Yetki | Kanıt |\n|:---|---|---|---:|\n| a | b | yok | c |\n"
    assert adimlar(tablo) == (1, [])
    liste = ("Önce bağlamı oku.\n"
             "1. **`rapor.md`** — oku · yetki: yok · kanıt: dosya açıldı\n"
             "   - ayrıntı serbest\n"
             "2. **yayın** - gönder ; yetki: ekip lideri ; kanit: yayın kaydı\n")
    assert adimlar(liste) == (2, [])


@pytest.mark.parametrize("metin, parca", [
    ("| # | Nesne | Eylem | Yetki | Kanıt |\n|---|---|---|---|---|\n| 1 | a | b |  | c |\n", "yetki boş"),
    ("| Nesne | Eylem | Yetki | Kanıt |\n|---|---|---|---|\n| a | b | bilinmiyor | c |\n", "yetki belirsiz"),
    ("| Nesne | Eylem | Yetki | Kanıt |\n|---|---|---|---|\n| a | b | yok | yok |\n", "kanıt 'yok'"),
    ("| Nesne | Eylem | Yetki | Kanıt |\n|---|---|---|---|\n| a | b | yok |\n", "hücre"),
    ("| Nesne | Eylem | Kanıt |\n|---|---|---|\n| a | b | c |\n", "tablosu başlığı"),
    ("| Nesne | Eylem | Yetki | Kanıt |\n| a | b | yok | c |\n", "tablosu başlığı"),
    ("1. **a** — b · kanıt: c\n", "eksik: yetki:"),
    ("1. Dosyayı oku.\n", "eksik: **nesne**, eylem, yetki:, kanıt:"),
    ("1. **a** — b · yetki: ? · kanıt: c\n", "yetki boş"),
    ("- **a** — b · yetki: yok · kanıt: c\n", "numaralı madde"),
])
def test_s05_hatali_adim(metin, parca):
    _, sorunlar = adimlar(metin)
    assert len(sorunlar) == 1 and parca in sorunlar[0][1], sorunlar


def test_s05_skillde_satir_numarasi_ve_bos_bolum(tmp_path):
    govde = siki_govde(Adımlar=TABLO.replace("| kullanıcı |", "| - |"))
    s = siki_denetle(skill(tmp_path, "a", govde=govde))
    assert kodlar(s) == ["S05"]
    satir = (tmp_path / "a" / "SKILL.md").read_text(encoding="utf-8").split("\n")[s.hatalar[0].satir - 1]
    assert satir.startswith("| 2 |")
    s = siki_denetle(skill(tmp_path, "b", govde=siki_govde(Adımlar="Adımlar sonra yazılacak.\n")))
    assert kodlar(s) == ["S05"] and "adım yok" in s.hatalar[0].mesaj


# ------------------------------------------------------------------ S06 / S07
@pytest.mark.parametrize("satir", ["Başarı %87 oldu.", "Süre 340 ms.", "Yanıt 2,5 sn sürdü.", "3x hızlandı.",
                                   "15 Mart 2026 sürümü.", "Ocak 2025'te değişti.", "Sonuç 12/03/2026 günü."])
def test_s06_olcum_ve_tarih(tmp_path, satir):
    s = siki_denetle(skill(tmp_path, "a", govde=siki_govde(Değişmezler_ve_yasaklar=f"- {satir}\n")))
    assert kodlar(s) == ["S06"] and s.uyarilar[0].satir is not None


@pytest.mark.parametrize("satir", ["Gövde `150` satır ve `12 KB` sınırı.", "2 adım, 3 dosya.",
                                   "Sürüm 1.2 ile uyumlu.", "Mayıs ayında değil, her zaman."])
def test_s06_olcum_olmayan_gecer(tmp_path, satir):
    govde = siki_govde(Değişmezler_ve_yasaklar=f"- {satir}\n\n```\nsüre 340 ms\n```\n")
    assert kodlar(siki_denetle(skill(tmp_path, "a", govde=govde))) == []


def test_s07_ic_ice_referans(tmp_path):
    govde = siki_govde(Referanslar="- [ayrıntı](references/a/b.md): gerekince.\n")
    s = siki_denetle(skill(tmp_path, "a", govde=govde, dosyalar={"references/a/b.md": "# B\n"}))
    assert kodlar(s) == ["S07"] and s.hatalar[0].dosya == "references/a/b.md"
    govde = siki_govde(Referanslar="- [ayrıntı](references/b.md): gerekince.\n")
    assert kodlar(siki_denetle(skill(tmp_path, "b", govde=govde, dosyalar={"references/b.md": "# B\n"}))) == []


# ------------------------------------------------------------------ ayar etkileşimi
def test_s_kurali_kapat_muaf_onem(tmp_path):
    k = skill(tmp_path, "x", govde=siki_govde(Amaç="Bir.\nİki.\nÜç.\n"))
    assert kodlar(siki_denetle(k, kapali=["S03"])) == []
    s = siki_denetle(k, muaf=[{"skill": "x", "kural": "S03", "gerekce": "geçiş"}])
    assert kodlar(s) == [] and s.muaflar[0].kural == "S03"
    s = siki_denetle(k, onem={"S03": "uyari"})
    assert [b.kural for b in s.uyarilar] == ["S03"]


def test_gonderilen_skiller_siki_bilgilendirici_kalir():
    sonuclar = tara([SKILLER], Ayar().zorla("siki"))
    for s in sonuclar:
        assert s.profil == "siki"
        assert {b.kural for b in s.hatalar} == {"S01", "S02"}
        assert any("eksik bölüm" in b.mesaj for b in s.hatalar)
    assert all(kodlar(s) == [] for s in tara([SKILLER]))


# ------------------------------------------------------------------ yeni
def test_siki_iskelet_yalniz_yer_tutucu_doldurulunca_temiz(tmp_path):
    k = olustur("rapor-yazimi", tmp_path, profil="siki")
    s = skill_denetle(k)
    assert s.profil == "siki" and s.hatalar == [] and [b.kural for b in s.uyarilar] == ["B25"]
    metin = (k / "SKILL.md").read_text(encoding="utf-8").replace("DOLDUR: ", "").replace("DOLDUR - ", "")
    (k / "SKILL.md").write_text(metin, encoding="utf-8")
    s = skill_denetle(k)
    assert s.hatalar == [] and s.uyarilar == []


def test_esnek_isaret_yalniz_istenince():
    assert "profil:" not in olustur_metin("x")
    assert '  profil: "esnek"\n' in olustur_metin("x", isaretle=True)
    assert '  profil: "siki"\n' in olustur_metin("x", profil="siki")
    with pytest.raises(ValueError):
        olustur_metin("x", profil="orta")


def test_skill_tasarimi_siki_sablonu_ile_ayni():
    asset = (SKILLER / "skill-tasarimi" / "assets" / "skill-template-siki.md").read_text(encoding="utf-8")
    assert asset == olustur_metin("ornek-skill", profil="siki")


# ------------------------------------------------------------------ komut satırı
def kos(capsys, *argv):
    kod = main(list(argv))
    cikti = capsys.readouterr()
    return kod, cikti.out, cikti.err


def test_cli_profil_bayragi_ve_json(tmp_path, capsys):
    skill(tmp_path / "skills", "iyi")
    kod, out, _ = kos(capsys, "dogrula", "skills")
    assert kod == 0 and "[TAMAM] skills/iyi\n" in out
    kod, out, _ = kos(capsys, "dogrula", "--profil", "siki", "skills")
    assert kod == 1 and "[HATA] skills/iyi (siki)" in out and "S01 hata" in out
    kod, out, _ = kos(capsys, "dogrula", "--json", "--profil", "siki", "skills")
    assert json.loads(out)["skiller"][0]["profil"] == "siki"
    (tmp_path / ".beceri.toml").write_text('profil = "siki"\n', encoding="utf-8")
    assert kos(capsys, "dogrula", "skills")[0] == 1
    assert kos(capsys, "dogrula", "--profil", "esnek", "skills")[0] == 0
    with pytest.raises(SystemExit) as e:
        main(["dogrula", "--profil", "orta", "skills"])
    assert e.value.code == 2


def test_cli_yeni_siki_ve_ayardan(tmp_path, capsys):
    kod, out, _ = kos(capsys, "yeni", "not-alma", "--profil", "siki", "--hedef", "skills")
    assert kod == 0 and "(siki)" in out and "B25 uyari" in out
    assert kos(capsys, "dogrula", "skills")[0] == 0
    assert kos(capsys, "dogrula", "--kati", "--kapat", "B25", "skills")[0] == 0
    (tmp_path / ".beceri.toml").write_text('profil = "siki"\n', encoding="utf-8")
    kod, out, _ = kos(capsys, "yeni", "esnek-not", "--profil", "esnek", "--hedef", "skills")
    assert kod == 0 and "(siki)" not in out
    metin = (tmp_path / "skills" / "esnek-not" / "SKILL.md").read_text(encoding="utf-8")
    assert '  profil: "esnek"' in metin
    assert kos(capsys, "dogrula", "skills")[0] == 0
    kod, out, _ = kos(capsys, "yeni", "varsayilan", "--hedef", "skills")
    assert kod == 0 and "(siki)" in out


def test_cli_kurallar_profil_sutunu(capsys):
    kod, out, _ = kos(capsys, "kurallar")
    assert kod == 0 and "S05  hata   siki " in out and "B19  uyari  esnek" in out
    veri = json.loads(kos(capsys, "kurallar", "--json")[1])
    assert {k["profil"] for k in veri} == {"ortak", "esnek", "siki"}
