# beceri

Ajan skill'i yazanlar için **bağımlılıksız araç takımı**. Skill, bir kodlama ajanının (Claude Code, Codex,
Cursor ve benzerleri) gerektiğinde yüklediği `SKILL.md` paketidir: ön bilgi (`name`, `description`), talimat
gövdesi ve isteğe bağlı `references/`, `scripts/`, `assets/` klasörleri. beceri bu paketleri doğrular, yenisini
genel bir şablondan açar, iki hazır skill getirir ve kodlama benchmark'ı için bir koşucu barındırır.

Yalnız standart kütüphane, Python 3.11+. YAML ön bilgi PyYAML olmadan ayrıştırılır. Model ya da ağ çağrısı yoktur.

**English summary.** `beceri` ("skill" in Turkish) is a dependency-free toolkit for people who write AI-agent
skills (SKILL.md packages). `beceri dogrula <path>...` validates one skill folder or a whole tree against 25
stable rules (B01–B25): parseable frontmatter (a strict, safe YAML subset parser is built in; no PyYAML needed),
required `name`/`description`, name format and folder match, description length and trigger/boundary wording,
body size, referenced files that exist, one-level references, leftover backup files, machine-specific home
paths, secret-looking values (never printed), and model names in skills that declare themselves model-agnostic.
Rules can be disabled, re-graded or exempted per skill in `.beceri.toml` or `[tool.beceri]`; output is human
readable or `--json`; exit codes are 0 clean, 1 errors, 2 usage. `beceri yeni <name>` scaffolds a skill from a
generic template that passes validation. Two ready skills ship in `skills/`: skill design and coding-benchmark
task authoring. `beceri benchmark ...` runs the bundled coding benchmark (see `docs/BENCHMARK.md`). Docs and
identifiers are Turkish.

## Kurulum

```
pip install -e .            # beceri komutu
pip install -e ".[dev]"     # + pytest, ruff
```

## Kullanım

```
beceri dogrula <yol>... [--json] [--kati] [--ayar DOSYA | --ayarsiz] [--kapat B20,B23]
beceri yeni <ad> [--hedef DIZIN] [--aciklama METIN]
beceri kurallar [--json]
beceri benchmark ...
```

`<yol>` bir skill klasörü, bir `SKILL.md` ya da skill'leri içeren herhangi bir klasör olabilir. Klasörün doğrudan
altında skill varsa o klasör bir **skill kökü** sayılır ve `SKILL.md`'si olmayan kardeş klasörler B01 alır;
yoksa alt klasörlerde skill aranır (ör. bir deponun kökü ya da eklenti ağacı). Gizli klasörler, `__pycache__`
ve `node_modules` atlanır.

Çıkış kodları: **0** hata yok (uyarı olabilir), **1** hata var (`--kati` ya da `kati = true` ile uyarı da),
skill bulunamadı ya da `yeni` için klasör zaten var, **2** kullanım ya da ayar hatası.

```
$ beceri dogrula skills
[TAMAM] skills/kodlama-benchmark-yazimi
[TAMAM] skills/skill-tasarimi
2 skill: 0 hata, 0 uyarı
```

`--json` çıktısı: `{"beceri", "ayar", "kati", "skiller": [{"yol", "ad", "hatalar", "uyarilar", "muaflar",
"olcum"}], "ozet": {"skill", "hata", "uyari", "muaf"}}`; her bulgu `{"kural", "mesaj", "dosya", "satir",
"gerekce"}` taşır.

### Yeni skill

```
beceri yeni rapor-yazimi --hedef skills
```

`skills/rapor-yazimi/SKILL.md` genel şablondan yazılır ve hemen doğrulanır. Şablondaki `DOLDUR` yer tutucuları
B25 uyarısı verir: iskelet hatasız geçer, `--kati` ise yer tutucular doldurulana kadar kalır.

## Kurallar

| Kimlik | Önem | Ne denetler |
|---|---|---|
| B01 | hata | Skill klasöründe `SKILL.md` yok. |
| B02 | hata | Ön bilgi yok, kapanmıyor ya da ayrıştırılamıyor. |
| B03 | hata | `name` yok ya da biçimi geçersiz (küçük harf, rakam, tek tire; en çok 64). |
| B04 | hata | `name` klasörün (ya da ona giden bağlantının) adıyla aynı değil. |
| B05 | hata | `name` ayrılmış sözcük içeriyor (varsayılan: claude, anthropic). |
| B06 | hata | `description` yok, boş, metin değil ya da 1024 karakteri aşıyor. |
| B07 | hata | `description` `<` ya da `>` içeriyor. |
| B08 | hata | Bilinmeyen ön bilgi alanı. |
| B09 | hata | `compatibility` metin değil ya da 500'ü aşıyor; `metadata` metin→metin eşlemi değil. |
| B10 | hata | Gövde 500 satırı aşıyor. |
| B11 | hata | `SKILL.md`'de anılan `references/`, `scripts/`, `assets/` yolu yok. |
| B12 | hata | `references/` dosyası başka bir referansa ya da `SKILL.md`'ye zincirleniyor. |
| B13 | hata | Yedek ya da artık dosya (`*.bak`, `*.orig`, `*~`, `SKILL.v*.md`). |
| B14 | hata | Makineye özgü ev dizini yolu (kullanıcı adı taşıyan `/home/…`, `/Users/…`, `C:\Users\…`, `/root`). |
| B15 | hata | Sır görünümlü değer (bilinen anahtar biçimi, özel anahtar, atanmış uzun token); değer yazılmaz. |
| B16 | hata | `metadata.model-agnostic: "true"` ilan eden skill'in gövdesinde model adı. |
| B17 | uyarı | `description` ne zaman kullanılmayacağını söylemiyor. |
| B18 | uyarı | Tetikleyici ilk 200 karakterde yok ya da `description` 500'ü aşıyor. |
| B19 | uyarı | Gövde 150 satırı ya da 12 KB'ı aşıyor. |
| B20 | uyarı | Gövdede tarih var. |
| B21 | uyarı | 100 satırı aşan referans dosyasında içindekiler yok. |
| B22 | uyarı | Aynı `name` başka bir taranan klasörde de var. |
| B23 | uyarı | Gövde satırlarının %20'den fazlası 120 karakteri aşıyor (kod bloğu ve tablo hariç). |
| B24 | uyarı | Platforma özgü ön bilgi alanı var ama `compatibility` yok. |
| B25 | uyarı | Şablondan kalan `DOLDUR` yer tutucusu. |

Kimlikler kalıcıdır; kaldırılan bir kuralın kimliği yeniden kullanılmaz. `beceri kurallar` listeyi basar.

İzin verilen ön bilgi alanları açık skill biçimindekilerdir: `name`, `description`, `license`, `compatibility`,
`metadata`, `allowed-tools`. Claude Code'un ek alanları (`disable-model-invocation`, `user-invocable`,
`argument-hint`, `model`, `hooks` …) B08 değil B24 alır: `compatibility` ile hangi platform için olduğunu yaz.

### Ön bilgi ayrıştırıcısı

Skill'lerin kullandığı YAML alt kümesi (eşlem, liste, düz/tırnaklı değer, `|` ve `>` blokları, tek satırlık
`[a, b]` ve `{a: b}`, yorumlar) bağımlılıksız ayrıştırılır. Gerçek YAML'ın da reddettiği yazımlar B02 alır;
en sık rastlananı tırnaksız değerdeki `: ` dizisidir (`description: Use when: ...`). Değeri tırnağa al ya da
`>-` bloğu kullan. Tipler YAML 1.2 çekirdek şemasına göredir (`yes` metindir, `true` mantıksal). Çapa, takma
ad ve etiket alt kümede yoktur; PyYAML kuruluysa yalnız bu durumda `yaml.safe_load` kullanılır.

## Ayar

`.beceri.toml` (anahtarlar en üst düzeyde) ya da `pyproject.toml` içinde `[tool.beceri]`. Çalışma klasöründen
köke doğru ilk bulunan kullanılır; `.git` içeren klasörde arama durur. `--ayar DOSYA` açık yol verir,
`--ayarsiz` aramayı kapatır. Bilinmeyen anahtar ya da kural kimliği 2 ile çıkar.

```toml
[tool.beceri]
kapali = ["B20"]                  # kapatılan kurallar
kati = false                      # true: uyarılar da çıkışı 1 yapar
ek_alanlar = ["x-ekip"]           # izin verilen ek ön bilgi alanları
ayrilmis_adlar = ["claude", "anthropic"]
model_adlari = ["ozel-model"]     # B16 için ek model adları
atla = [".*", "__pycache__", "node_modules", "arsiv"]

[tool.beceri.sinirlar]            # varsayılanlar
ad_azami = 64
aciklama_azami = 1024
aciklama_uyari = 500
tetik_karakter = 200
uyumluluk_azami = 500
govde_azami_satir = 500
govde_uyari_satir = 150
govde_uyari_kb = 12
uzun_satir = 120
uzun_satir_oran = 0.20
referans_icindekiler_satir = 100

[tool.beceri.onem]
B16 = "uyari"                     # önemi değiştir

[[tool.beceri.muaf]]              # tek skill için gerekçeli muafiyet
skill = "eski-skill"
kural = "B23"
gerekce = "geniş tablo satırları"
```

Muaf tutulan bulgular raporda `muaf` olarak gerekçesiyle görünür ve çıkış kodunu etkilemez.

## Hazır skill'ler

`skills/` altında, doğrulamadan uyarısız geçen iki genel skill. Ajanının skill klasörüne kopyalayarak kullan
(ör. projede `.claude/skills/` ya da `.agents/skills/`).

| Skill | Ne için |
|---|---|
| [`skill-tasarimi`](skills/skill-tasarimi/SKILL.md) | Bir yöntemden ya da referans skill'den yeni skill tasarlamak, var olanı gözden geçirmek. Başlangıç şablonu `assets/` altında; `beceri yeni` ile aynıdır. |
| [`kodlama-benchmark-yazimi`](skills/kodlama-benchmark-yazimi/SKILL.md) | Kodlama ajanları için benchmark görevi yazmak: görünür spec, referans ve tek noktalı hatalı çözüm, bağımsız oracle'lı gizli testler. |

İkisi de `metadata.model-agnostic: "true"` taşır; B16 gövdelerinde model adı olmadığını denetler.

## Benchmark

`beceri benchmark ...` komutu `beceri.benchmark` modülüne aynen aktarılır. Ayrıntı:
[docs/BENCHMARK.md](docs/BENCHMARK.md). Modül kurulumda yoksa komut açık bir hata verip 2 ile çıkar.

## Geliştirme

```
pip install -e ".[dev]"
python -m pytest -q
python -m ruff check src tests
python -m beceri dogrula --kati skills
```

## Lisans

MIT. Bkz. [LICENSE](LICENSE).
