"""Pytest: src yolu; testler geliştiricinin ayar dosyasına bağlanmasın."""
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
SRC = str(KOK / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

SKILLER = KOK / "skills"

GECERLI_ACIKLAMA = "Örnek işi yapar. Kullan - kullanıcı örnek iş istediğinde. Kullanma - başka işler için."


@pytest.fixture
def calisma_klasoru(monkeypatch, tmp_path):
    """Test boş bir klasörde başlar; .git ayar aramasını orada durdurur. Modüller usefixtures ile ister."""
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def skill(kok, ad="ornek", *, name=None, aciklama=GECERLI_ACIKLAMA, ek_onbilgi="", govde="# Örnek\n\nGövde.\n",
          onbilgi=None, dosyalar=None):
    """kok/ad/SKILL.md yazar; dosyalar: {göreli yol: metin}. Skill klasörünü döndürür."""
    klasor = Path(kok) / ad
    klasor.mkdir(parents=True, exist_ok=True)
    if onbilgi is None:
        onbilgi = f"name: {ad if name is None else name}\ndescription: >-\n  {aciklama}\n{ek_onbilgi}"
    metin = f"---\n{onbilgi.rstrip()}\n---\n\n{govde}" if onbilgi is not False else govde
    (klasor / "SKILL.md").write_bytes(metin.encode("utf-8"))
    for rel, icerik in (dosyalar or {}).items():
        p = klasor / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(icerik.encode("utf-8") if isinstance(icerik, str) else icerik)
    return klasor
