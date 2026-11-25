"""Teknik levha: konunun gerçek hesabından çizilen, bağımlılıksız SVG (yalnız standart kütüphane).

Kullanım:
    python levha.py --cikti levhalar                  # tüm örnek levhalar
    python levha.py --cikti levhalar rc-sarj          # yalnız biri
    python levha.py --marka marka.json --cikti levhalar

Renk ve yazı tipleri MARKA sözlüğünden gelir. Buradaki değerler kurgusal örnektir: kendi marka çerçevendeki
değerlerle değiştir ya da aynı anahtarları taşıyan bir JSON dosyasını --marka ile ver. Yeni levha için bir
fonksiyon yaz ve LEVHALAR'a ekle. Çizim sağ ~%60'ta yoğunlaşır; sol taraf sayfadaki metne kalır. Ekrana yazılan
her sayı aynı fonksiyondaki hesaptan gelir, elle yazılmaz.
"""
import argparse
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

MARKA = {
    "zemin": "#F5F2EB",       # kurgusal örnek palet; kendi çerçevenle değiştir
    "murekkep": "#22303A",
    "aksan": "#1F7A8C",
    "mono": "ui-monospace, Menlo, Consolas, monospace",
    "kod": "ÖRN / TEKNİK LEVHA",  # sol üst etiket; proje önekiyle değiştir
    "ondalik": ",",               # sayılarda ondalık ayracı
}
G, Y = 1600, 900  # 16:9 tuval (piksel)
ROLLER = {  # çizgi hiyerarşisi: (renk anahtarı, kalınlık, opaklık)
    "temel": ("murekkep", 1.2, 0.55),
    "yardimci": ("murekkep", 0.8, 0.32),
    "vurgu": ("aksan", 2.4, 1.0),
    "ince-vurgu": ("aksan", 1.0, 0.8),
}


def sayi(x, basamak=1):
    return f"{x:.{basamak}f}".replace(".", MARKA["ondalik"])


class Levha:
    def __init__(self):
        self.ogeler = []

    def _stil(self, rol, kesik=False, dolgu="none"):
        renk, kalinlik, opaklik = ROLLER[rol]
        s = f'fill="{dolgu}" stroke="{MARKA[renk]}" stroke-width="{kalinlik}" stroke-opacity="{opaklik}"'
        return s + (' stroke-dasharray="6 6"' if kesik else "")

    def cizgi(self, noktalar, rol="temel", kesik=False):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in noktalar)
        self.ogeler.append(f'<polyline points="{d}" {self._stil(rol, kesik)} stroke-linejoin="round"/>')

    def cokgen(self, noktalar, rol="temel", dolgu=None):
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in noktalar)
        self.ogeler.append(f'<polygon points="{d}" {self._stil(rol, dolgu=dolgu or MARKA["zemin"])}/>')

    def nokta(self, x, y, r=5, rol="vurgu"):
        renk = MARKA[ROLLER[rol][0]]
        self.ogeler.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{renk}"/>')

    def metin(self, x, y, s, rol="temel", boyut=15, hiza="start", opaklik=None):
        renk, _, op = ROLLER[rol]
        op = op if opaklik is None else opaklik
        self.ogeler.append(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{MARKA[renk]}" fill-opacity="{max(op, 0.6)}" '
            f'font-size="{boyut}" text-anchor="{hiza}" letter-spacing="1.5">{escape(s)}</text>')

    def cerceve(self, no, baslik, x0=620, x1=1550, y0=50, y1=850):
        """Köşe işaretleri, alt ölçek cetveli, FIG etiketi ve sol üst kod."""
        k = 35
        for x, y, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            self.cizgi([(x + k * dx, y), (x, y), (x, y + k * dy)])
        for i, x in enumerate(range(x0 + 40, x1 - 30, 20)):
            self.cizgi([(x, y1), (x, y1 - (16 if i % 5 == 0 else 8))], "yardimci")
        self.metin(x1, y0 - 22, f"FIG. {no:02d} · {baslik}", boyut=15, hiza="end")
        self.metin(x0, y0 - 22, MARKA["kod"], "ince-vurgu", boyut=15)

    def svg(self):
        bas = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {G} {Y}" width="{G}" height="{Y}" '
               f'font-family="{escape(MARKA["mono"])}">')
        return "\n".join([bas, f'<rect width="{G}" height="{Y}" fill="{MARKA["zemin"]}"/>', *self.ogeler,
                          "</svg>\n"])


class Olcek:
    """Veri koordinatını piksel dikdörtgenine eşler (SVG'de y aşağı doğru artar)."""

    def __init__(self, x, y, g, y_, xa, ya):
        self.x, self.y, self.g, self.y_, self.xa, self.ya = x, y, g, y_, xa, ya

    def __call__(self, vx, vy):
        (x0, x1), (y0, y1) = self.xa, self.ya
        return self.x + (vx - x0) / (x1 - x0) * self.g, self.y + self.y_ - (vy - y0) / (y1 - y0) * self.y_


def iso(x, y, z, olcek=220, merkez=(1000, 450)):
    """Eş ölçülü izdüşüm: x, y taban düzlemi, z yukarı."""
    c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    return merkez[0] + (x - y) * c * olcek, merkez[1] + ((x + y) * s - z) * olcek


# ---------------------------------------------------------------- örnek levhalar
def rc_sarj():
    """Eğri levhası: RC devresinde dolma ve boşalma; τ katlarındaki yüzdeler hesaptan."""
    lv = Levha()
    lv.cerceve(1, "RC ŞARJI · V(t) = V₀(1 − e^(−t/τ))")
    o = Olcek(720, 150, 760, 560, (0, 5), (0, 1))
    for v in (0, 0.25, 0.5, 0.75, 1):
        lv.cizgi([o(0, v), o(5, v)], "yardimci")
        lv.metin(*o(-0.08, v - 0.01), sayi(v, 2), boyut=13, hiza="end")
    ts = [5 * i / 200 for i in range(201)]
    lv.cizgi([o(t, math.exp(-t)) for t in ts], "temel", kesik=True)
    lv.cizgi([o(t, 1 - math.exp(-t)) for t in ts], "vurgu")
    for k in range(1, 6):
        v = 1 - math.exp(-k)
        lv.cizgi([o(k, 0), o(k, v)], "yardimci", kesik=True)
        lv.metin(*o(k, -0.07), f"{k}τ" if k > 1 else "τ", boyut=14, hiza="middle")
        lv.nokta(*o(k, v), r=4)
        lv.metin(*o(k - 0.05, v + 0.04), f"%{sayi(100 * v)}", "ince-vurgu", boyut=13, hiza="end")
    t_yari = math.log(2)  # dolma ve boşalma eğrilerinin kesiştiği an
    lv.nokta(*o(t_yari, 0.5), r=4, rol="temel")
    lv.cizgi([o(t_yari, 0.5), o(1.15, 0.38)], "yardimci")
    lv.metin(*o(1.2, 0.37), f"t = τ·ln2 ≈ {sayi(t_yari, 2)}τ · %50", boyut=13)
    return lv


KATMANLAR = [  # alttan üste: (ad, kalınlık mm); örnek veri, konuna göre değiştir
    ("GÖVDE", 6.0), ("PİL", 4.0), ("DEVRE KARTI", 1.6), ("SENSÖR", 1.2), ("KAPAK", 0.8)]


def patlatilmis(acilma=1.0, vurgu=3):
    """Nesne levhası: katmanlı yapının patlatılmış görünümü. acilma 0 = kapalı, 1 = tam açık."""
    lv = Levha()
    lv.cerceve(2, "KATMANLI YAPI · PATLATILMIŞ GÖRÜNÜM")
    mm, bosluk = 0.03, 0.30 * acilma
    yukseklik = sum(k for _, k in KATMANLAR) * mm + bosluk * (len(KATMANLAR) - 1)
    z = (1 - yukseklik) / 2  # yığın tuvalin dikey ortasına gelsin
    for i, (ad, kalinlik) in enumerate(KATMANLAR):
        zt = z + kalinlik * mm
        rol = "vurgu" if i == vurgu else "temel"
        lv.cokgen([iso(1, 0, z), iso(1, 1, z), iso(1, 1, zt), iso(1, 0, zt)], rol)
        lv.cokgen([iso(1, 1, z), iso(0, 1, z), iso(0, 1, zt), iso(1, 1, zt)], rol)
        lv.cokgen([iso(0, 0, zt), iso(1, 0, zt), iso(1, 1, zt), iso(0, 1, zt)], rol)
        ax, ay = iso(1, 0, (z + zt) / 2)
        lv.cizgi([(ax + 8, ay), (1330, ay)], "ince-vurgu" if i == vurgu else "yardimci")
        lv.metin(1340, ay + 5, f"{ad} · {sayi(kalinlik)} mm", "ince-vurgu" if i == vurgu else "temel", boyut=14)
        z = zt + bosluk
    toplam = sum(k for _, k in KATMANLAR)
    lv.cizgi([iso(0.5, 0.5, (1 - yukseklik) / 2 - 0.2), iso(0.5, 0.5, z + 0.1)], "yardimci", kesik=True)
    lv.metin(700, 800, f"TOPLAM {sayi(toplam)} mm · {len(KATMANLAR)} KATMAN", boyut=14)
    return lv


LEVHALAR = {"rc-sarj": rc_sarj, "patlatilmis": patlatilmis}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ad", nargs="*", help="levha adları (boşsa hepsi): " + ", ".join(LEVHALAR))
    ap.add_argument("--cikti", default="levhalar", help="çıktı klasörü")
    ap.add_argument("--marka", help="MARKA anahtarlarını taşıyan JSON dosyası")
    a = ap.parse_args(argv)
    if a.marka:
        MARKA.update(json.loads(Path(a.marka).read_text(encoding="utf-8")))
    hedef = Path(a.cikti)
    hedef.mkdir(parents=True, exist_ok=True)
    for ad in a.ad or LEVHALAR:
        if ad not in LEVHALAR:
            ap.error(f"bilinmeyen levha: {ad}")
        yol = hedef / f"{ad}.svg"
        yol.write_text(LEVHALAR[ad]().svg(), encoding="utf-8", newline="\n")
        print(yol)


if __name__ == "__main__":
    main()
