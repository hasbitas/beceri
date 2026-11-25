"""Ön bilgi ayrıştırıcısı: skill'lerin kullandığı YAML alt kümesi ve gerçek YAML'ın reddettiği yazımlar."""
import pytest

from beceri import onbilgi


@pytest.mark.parametrize("metin, beklenen", [
    ("name: a\ndescription: b c", {"name": "a", "description": "b c"}),
    ("description: >-\n  Bir\n  iki.\n\n  Üç\n", {"description": "Bir iki.\nÜç"}),
    ("description: |\n  a\n   b\n  c\n\n", {"description": "a\n b\nc\n"}),
    ("description: |+\n  a\n\n\nx: 1", {"description": "a\n\n\n", "x": 1}),
    ("description: >\n  a\n  b\n    girinti\n  c\n", {"description": "a b\n  girinti\nc\n"}),
    ('metadata:\n  surum: "1.0"\n  model-agnostic: "true"', {"metadata": {"surum": "1.0", "model-agnostic": "true"}}),
    ("allowed-tools: Read, Grep, Bash(git:*)", {"allowed-tools": "Read, Grep, Bash(git:*)"}),
    ("allowed-tools:\n  - Read\n  - Grep", {"allowed-tools": ["Read", "Grep"]}),
    ("a:\n- x\n- y\nb: z", {"a": ["x", "y"], "b": "z"}),
    ("paths: [\"a/**\", 'b', c]", {"paths": ["a/**", "b", "c"]}),
    ("x: {a: 1, b: iki}", {"x": {"a": 1, "b": "iki"}}),
    ("description: düz\n  devam\n  ve son", {"description": "düz devam ve son"}),
    ("description: 'it''s'  # yorum", {"description": "it's"}),
    ('description: "kaçış \\" \\u00e7 \\n x"', {"description": 'kaçış " ç \n x'}),
    ("hooks:\n  Olay:\n    - matcher: Bash\n      hooks:\n        - type: command\n",
     {"hooks": {"Olay": [{"matcher": "Bash", "hooks": [{"type": "command"}]}]}}),
    ("n: 1.5\nm: -3\nk: ~\nb: true\ny: yes", {"n": 1.5, "m": -3, "k": None, "b": True, "y": "yes"}),
    ("# yorum\nname: x # yorum\n", {"name": "x"}),
    ('description: "çok\n  satırlı"', {"description": "çok satırlı"}),
    ("description: >-\n  a: b burada serbest\n", {"description": "a: b burada serbest"}),
    ("", {}),
])
def test_ayristirma(metin, beklenen):
    assert onbilgi.oku(metin) == beklenen


@pytest.mark.parametrize("metin", [
    "description: Use when: x",
    "description: x:",
    "a: 1\na: 2",
    "description: 'kapanmamış",
    "name: x\n   y: z",
    "description: @x",
    "name: a\n\tb: c",
    "x: [a, b",
    "- a\n- b",
    "x: 'a' fazlası",
])
def test_reddedilen_yazimlar(metin):
    with pytest.raises(ValueError):
        onbilgi.oku(metin)


def test_desteklenmeyen_yapi_ayri_hata(monkeypatch):
    import builtins

    gercek_import = builtins.__import__

    def yaml_yok(ad, *args, **kwargs):
        if ad == "yaml":
            raise ImportError("yok")
        return gercek_import(ad, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", yaml_yok)
    with pytest.raises(onbilgi.Desteklenmiyor):
        onbilgi.oku("x: &capa deger\ny: *capa")


def test_ayir():
    fm, govde, bas = onbilgi.ayir("\ufeff---\r\nname: x\r\n---\r\n\r\n# Başlık\r\n")
    assert fm == "name: x"
    assert govde == "\n# Başlık\n"
    assert bas == 4
    assert onbilgi.ayir("# yok\n") == (None, "# yok\n", 1)
    assert onbilgi.ayir("---\nname: x\n")[0] is None
