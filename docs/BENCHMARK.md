# Benchmark: kod-v1

> **English summary.** `benchmark/kod-v1/` holds 75 Python programming tasks
> (60 single-file, 15 multi-file packages). Each task has a natural-language
> specification (`task.json`), a reference solution (`gold/`), a deliberately
> buggy solution (`broken/`) and visible/hidden unittest files. A task is valid
> when gold passes all tests while broken and an empty stub fail.
> `python -m beceri.benchmark` (or `beceri benchmark`) offers `listele` (list),
> `dogrula` (validate tasks), `butunluk` (check the SHA-256 manifest), `kos`
> (score a folder of candidate solutions, pass@1 as JSON) and `kalibre`
> (stability, harness probes, difficulty estimate). Everything is stdlib plus
> pytest; task code never runs in-process, only in a subprocess on a temporary
> copy. This is **not** a security sandbox. The tasks were written with AI
> assistance for an internal research project as classic programming exercises;
> they are not copied from a known benchmark, but being public they may end up
> in model training data.

## Görevler

| | sayı | açıklama |
| --- | --- | --- |
| tek dosyalı (`single-file`) | 60 | Tek bir `solution.py` içinde fonksiyon(lar): sayı tabanı çevirme, IBAN/ISBN/Luhn, Roma rakamları, aralık birleştirme, takvim ve iş günü hesabı, metin hizalama, CSV satırı bölme, JSON Pointer, semver, topolojik sıralama, LRU benzetimi, Türkçe büyük/küçük harf ve benzeri. |
| çok dosyalı (`multi-file`) | 15 | 2–4 modüllü küçük paketler: FIFO stok defteri, fatura ve yuvarlama, birim zinciri, rol/ACL çözümleme, tekrar kuralları, faturalama dönemleri, yapılandırma dili ayrıştırıcısı, TTL+LRU önbellek, sipariş durum makinesi, SCC, rota planlama, sürüm/kilit çözümleyici, adil zamanlayıcı, şema doğrulayıcı. Hatalar dosyalar arası sözleşmelerde saklıdır. |

Tanımlar İngilizcedir ve sözleşme düzeyinde ayrıntılıdır: tür denetimi
(`bool` bir `int` sayılır mı), doğrulama sırası, sınır değerleri, yuvarlama
kuralı ve hata türleri açıkça yazılıdır. Testler bu ayrıntıları sınar.

Bölümler (`split.json`, 25'er görev):

- `development`: yöntem geliştirirken serbestçe bakılan görevler.
- `selection`: birkaç yöntem/ayar arasında seçim yapmak için.
- `final`: yalnız son raporda bir kez koşulan görevler. Seçimde kullanmayın.

## Dosya düzeni

```
benchmark/kod-v1/
  README.md
  split.json                 {"format": 1, "groups": {"<task_id>": "development|selection|final"}}
  SHA256SUMS                 bütünlük bildirimi (aşağıya bakın)
  tasks/<task_id>/
    task.json
    gold/<allowed_paths...>      doğru başvuru çözümü (+ readonly_paths)
    broken/<allowed_paths...>    bilerek hatalı çözüm (+ readonly_paths)
    tests_visible/test_*.py      çözücüye gösterilebilecek testler
    tests_hidden/test_*.py       puanlamada kullanılan ek testler
```

`task.json` alanları:

| alan | tür | anlam |
| --- | --- | --- |
| `task_id` | str | Klasör adıyla aynı; `^[a-z0-9][a-z0-9-]{0,63}$`. |
| `kind` | str | `single-file` ya da `multi-file`. |
| `specification` | str | Çözücüye verilen tanım. |
| `allowed_paths` | list[str] | Çözücünün yazacağı/düzenleyeceği dosyalar (göreli POSIX yolu, `..` yok). |
| `readonly_paths` | list[str], isteğe bağlı | Hazır verilen ve değiştirilmeyen dosyalar (ör. boş `fifo/__init__.py`); her koşuda `gold/` kopyası kullanılır. |
| `expected_tests` | {"visible": n, "hidden": m} | Test sayısı (test yöntemi başına bir; alt testler sayılmaz). Bir koşu ancak bu kadar test toplanıp hepsi geçerse "geçti" sayılır. |

## gold, broken ve testler

Her koşu aynı biçimde kurulur: geçici bir klasöre `readonly_paths` (gold'dan)
ve değerlendirilen sürümün `allowed_paths` dosyaları kopyalanır, iki test
klasörü ayrı bir yere kopyalanır ve `sys.executable -m pytest` alt süreçte
çalışır. Bir koşunun sonucu:

- `gecti`: pytest 0 ile bitti, JUnit raporu yazıldı, beklenen sayıda test
  toplandı ve hepsi (alt testler dahil) geçti.
- `kaldi`: testler koştu, en az biri kaldı.
- `hata`: toplama/içe aktarma hatası, rapor yok (ör. süreç `os._exit(0)` ile
  erken çıktı).
- `zaman-asimi`: süre doldu, süreç grubu öldürüldü.

`dogrula` her görev için üç koşu yapar ve görevi ancak şu durumda geçerli sayar:
gold `gecti`, broken `gecti` değil, boş taslak (izinli dosyalar boş) `gecti`
değil, ve `expected_tests` gold'un sayımıyla aynı. Broken'ın test hatası yerine
zaman aşımı ya da içe aktarma hatasıyla kalması uyarı olarak gösterilir.

`tests_hidden` adı "puanlamada kullanılan, çözücüye gösterilmeyen" anlamındadır;
depo açık olduğu için gerçekte gizli değildir. Görünür testleri çözücüye verip
gizlileri yalnız puanlamada kullanmak bir tercih; araç her zaman ikisini birden
koşar.

## Çalıştırma

Gereken: Python 3.11+ ve pytest. Depo kökünde (kurulu değilse `PYTHONPATH=src`
ile):

```bash
python -m beceri.benchmark listele                # ya da: beceri benchmark listele
python -m beceri.benchmark butunluk
python -m beceri.benchmark dogrula                # tüm görevler; --gorev ID, --bolum, --json, --ayrinti
python -m beceri.benchmark kos --cozum-dizini cozumler/ --cikti rapor.json
python -m beceri.benchmark kalibre --tekrar 3 --sonda
```

Ortak seçenekler: `--veri DIR` (varsayılan `benchmark/kod-v1`, ya da
`BECERI_BENCHMARK` ortam değişkeni), `--zaman-asimi SN` (koşu başına, 60),
`--paralel N`. Çıkış kodları: `0` başarılı, `1` bulgu var (geçersiz görev,
bozuk bütünlük, kararsız görev), `2` kullanım/altyapı hatası (pytest yok, veri
yok, geçersiz görev kimliği).

### kos: aday çözümleri puanlama

Çözüm dizini görev başına bir klasör içerir ve yalnız `allowed_paths`
dosyaları okunur; testler, `conftest.py` ve başka dosyalar yok sayılır,
sembolik bağlar reddedilir:

```
cozumler/
  base-convert/solution.py
  a-fifo-ledger/fifo/lots.py
  a-fifo-ledger/fifo/costing.py
  a-fifo-ledger/fifo/ledger.py
```

Eksik görev ya da eksik dosya `eksik` sayılır (kaldı). `--cozum-dizini` birden
çok kez verilirse her dizin bir örnektir; görev başına `pass@1 = geçen / örnek`
ve toplam `pass@1` görevlerin ortalamasıdır (bölüm bazında da verilir). Rapor
JSON'dur ve veri bütünlüğünün durumu ile `SHA256SUMS` parmak izini içerir;
sonuç bildirirken bu parmak izini de yazın.

Çözücüye hangi başlangıç durumunun verildiğini (boş dosyalar mı, `broken/`
kopyası mı: "yazma" ya da "onarım" kipi) ve görünür testlerin gösterilip
gösterilmediğini sonuçla birlikte belirtin; bu seçimler puanı belirgin biçimde
değiştirir.

### kalibre: model çağrısı olmadan kalibrasyon

- Kararlılık: gold ve broken `--tekrar N` kez koşulur; gold her seferinde
  geçmeli, broken hiç geçmemeli ve sonuçları değişmemeli (rastgelelik/zaman
  bağımlılığı yakalanır).
- `--sonda`: koşucuyu kandırmaya çalışan çözümler: test toplanırken
  `os._exit(0)`, sahte "passed" özeti basıp çıkma, sonsuz döngü ve (POSIX'te)
  çıktı seli. Hiçbiri `gecti` sayılmamalı.
- `--cozum-dizini` (tekrarlanabilir): birden çok çözüm koşusundan görev başına
  çözülme oranı ve kaba zorluk etiketi (`kolay` ≥ 2/3, `orta`, `zor` < 1/3,
  `cozulmedi`). Örnekler bir modelden ya da insanlardan gelebilir; araç model
  çağırmaz.

## Görev ekleme

1. `tasks/<yeni-id>/` altında `task.json`, `gold/`, `broken/`,
   `tests_visible/`, `tests_hidden/` oluşturun. Testler `unittest` ya da düz
   pytest olabilir; çözümü `import solution` (ya da paket adıyla) içe aktarır.
2. Broken, gerçekçi ve tanımdan bulunabilir hatalar içermeli; en az bir hata
   yalnız gizli testte görünmeli. Tanımda testlerin dayandığı her kural yazılı
   olmalı.
3. `split.json` içine bölümünü ekleyin.
4. `python -m beceri.benchmark dogrula --gorev <yeni-id>` çalıştırın;
   `expected_tests` eksikse çıktı gold sayımını verir, `task.json`'a ekleyip
   tekrar koşun. `kalibre --gorev <yeni-id> --sonda` ile kararlılığı denetleyin.
5. `python -m beceri.benchmark butunluk --yaz` ile `SHA256SUMS`'ı yeniden
   üretin ve değişikliği bununla birlikte gönderin.

Var olan bir görevi değiştirmek sonuçları eskileriyle karşılaştırılamaz yapar;
bunun yerine yeni bir veri sürümü (`kod-v2`) açmayı düşünün.

## Bütünlük bildirimi

`SHA256SUMS`, veri klasöründeki her dosyanın (kendisi hariç; `__pycache__` ve
`.pyc` yok sayılır) SHA-256 özetini `sha256sum` biçiminde tutar.
`butunluk` eksik, değişmiş ve bildirimde olmayan dosyaları raporlar; Linux'ta
`cd benchmark/kod-v1 && sha256sum -c SHA256SUMS` ile de denetlenebilir. Dosyalar
LF satır sonuyla saklanır (`.gitattributes`); satır sonlarını çeviren bir
checkout özetleri bozar.

## Güvenlik

Görev ve aday kodu hiçbir zaman bu süreçte içe aktarılmaz: her koşu geçici bir
kopyada, temizlenmiş ortam değişkenleriyle (`PYTHONPATH` yalnız çalışma
klasörü, eklenti otomatik yükleme kapalı), zaman aşımıyla ve POSIX'te yeni bir
süreç grubunda, dosya boyutu ve CPU sınırıyla çalışır. Bu bir kum havuzu
**değildir**: aday kod dosya sistemine ve ağa erişebilir, test çerçevesini
yamalayabilir. Güvenilmeyen çözümleri tek kullanımlık bir konteynerde ya da
sanal makinede puanlayın.

## Kaynak ve sınırlar

- Görevler, tanımlar, testler, gold ve broken çözümler bir iç araştırma projesi
  için **yapay zekâ desteğiyle** klasik programlama alıştırmaları olarak
  yazıldı; üçü (`chunk-tail`, `clamp-bounds`, `stable-unique`) koşucu
  kalibrasyonu için yazılmış küçük sentetik görevlerdir. Tümü bu depodaki
  `dogrula` ile otomatik olarak doğrulandı; tek tek insan incelemesinden
  geçtikleri iddia edilmez.
- Bilinen bir benchmark'tan kopyalanmadı. Tanımlar ve testler HumanEval/MBPP
  tarzı kalıplar (`Write a function to...`, `>>>` örnekli docstring'ler,
  bilinen fonksiyon adları) ve yarışma sitesi biçimi (`Example 1:`,
  `Constraints:`) için tarandı; eşleşme bulunmadı. Bununla birlikte konuların
  bir kısmı (edit distance, Roma rakamları, Luhn, spiral sıra, kayan pencere
  maksimumu, top-k, metin iki yana yaslama, topolojik sıralama) yaygın klasik
  problemlerdir; benzerleri kamuya açık kaynaklarda bol bulunur. Buradaki
  ayrıntılı sözleşmeler (tür, sıra, sınır kuralları) özgündür.
- **Kirlenme uyarısı:** Açık yayımlanan görevler zamanla model eğitim verisine
  sızabilir. Sonuçları yayın tarihiyle birlikte bildirin, `final` bölümünü
  ayarlama için kullanmayın; kirlenmeden şüpheleniyorsanız yeni görevlerle bir
  veri sürümü açın.
- Testler sonlu örneklerdir; geçen bir çözüm tanımı her durumda doğru
  uygulamış olmayabilir.
