# Üretim tarifleri

Levha, hareket ve deney üretirken ya da şablonları yeni bir projeye uyarlarken oku.

## İçindekiler

1. Marka değerlerini koda bağlamak
2. Bileşen kuralları
3. Levha
4. Adım animasyonu
5. Etkileşimli deney
6. Ekran görüntüsüyle doğrulama
7. Teknik tuzaklar

## 1. Marka değerlerini koda bağlamak

Marka çerçevesindeki değerler üç yerde yaşar ve aynı adları taşır:

| Çerçeve rolü | CSS (`:root`) | Python `MARKA` |
|---|---|---|
| Zemin | `--zemin` | `zemin` |
| Mürekkep | `--murekkep` | `murekkep` |
| Aksan | `--aksan` | `aksan` |
| Panel, ikincil yazı, ince çizgi | `--panel`, `--ikincil`, `--cizgi` | (levha çizgi opaklığıyla verir) |
| Etiket yazı tipi | `--mono-font` | `mono` |

JavaScript renkleri CSS değişkenlerinden okur; ayrı kopya tutma. Levha bağımsız bir SVG dosyası olduğu için
renkleri öznitelik olarak yazar: marka değişince levhaları yeniden üret (`--marka marka.json`).

## 2. Bileşen kuralları

| Öğe | Kural |
|---|---|
| Başlık | Ağır ve sıkı; kapakta ekranın yaklaşık dörtte biri |
| Alt başlık, etiket | Eşaralıklı, küçük, harf aralıklı; renkli olan yalnız aksan |
| Kart, not | Opak panel zemin, 1 piksel ince çizgi; seçili kart aksan çerçeve |
| Tablo | Başlık satırı etiket stilinde, satırlar ince çizgiyle ayrılır |
| Düğme | Köşe biçimi çerçeveye uyar; seçili durum aksan dolgu |
| Üst kod, alt cetvel | Sayfanın yerini ve ilerlemesini söyler; içerikle yarışmaz |

## 3. Levha

Şablon: [levha.py](../assets/sablon/levha.py) (yalnız standart kütüphane, SVG çıktı).

- `Levha.cerceve()` köşe işaretleri, ölçek cetveli, `FIG.` numarası ve sol üst kodu verir. Çizim sağ
  ~%60'ta durur; sol taraf sayfa metnine kalır ve CSS gradyanıyla bastırılır.
- Çizgi hiyerarşisi üç rol: temel (nesnenin kendisi), yardımcı (ızgara, kılavuz), vurgu (anlatılan tek şey).
  Bir levhada birden çok vurgu varsa hiyerarşi bozulmuştur.
- Sayılar hesaptan basılır (`sayi()` ondalık ayracını çerçeveden alır). Eğri, matris, devre, kesit ya da
  patlatılmış çizim gerçek veriden ya da formülden üretilir; "temsili" çizgi çizme.
- Yeni levha: veriyi ve hesabı fonksiyonun başına, çizimi sonuna koy; `LEVHALAR`'a ekle.
- Raster gerekiyorsa SVG'yi tarayıcıyla ekran görüntüsüne çevir; ayrı bir çizim kütüphanesi şart değil.

## 4. Adım animasyonu

Şablon: [hareket.js](../assets/sablon/hareket.js); örnek sahne [sayfa.html](../assets/sablon/sayfa.html) içinde.

- Sahne `sahne(c, u)` saf bir fonksiyondur: yalnız `u` (0..1) ile çizer, dış durumu değiştirmez. Böylece
  otomatik oynatma, kaydırıcı ve sayfa kaydırması aynı kareyi verir; geri kaydırma aynı sahneye döner.
- Anlatımı 3-5 adıma böl (`Hareket.adim(u, n)`): bütün → ayrışma → okuma → birleşme gibi. Her adımın
  ekranda adı ve ilerleme çizgisi olsun.
- Geçişlerde `Hareket.ease`; ani sıçrama yalnız anlamlıysa (ölçüm, durum değişimi).
- Video gerekiyorsa aynı sahneyi kare kare dışa aktar ve yerel bir kodlayıcıyla birleştir; ücretli ya da
  çevrimiçi servise gönderme kullanıcının onayına bağlıdır. Dikey biçimde altta başlık kutusu için ~%30 boş bırak.
- `prefers-reduced-motion` açıkken anlamlı tek kare (`poster`) gösterilir.

## 5. Etkileşimli deney

Şablon: [deney.js](../assets/sablon/deney.js). Kalıp: kontrol → gerçek hesap → çubuk ya da şekil
çıktısı → adlandırılmış sonuç.

- `hesapla` saf fonksiyondur; tarayıcı dışında birkaç bilinen değerle sına (ör. RC'de t = τ için %63,2).
- Kontroller bir kez kurulur, değişimde yalnız çıktı yenilenir; kaydırıcı sürüklenirken HTML'i baştan yazma.
- Ön ayarlı düğmeler anlatımdaki örnek değerleri verir; kaydırıcı keşif içindir.
- Sonuç satırı bir adla biter ("t = 1,00τ", "sınır aşıldı"): kullanıcı ne gördüğünü okuyabilsin.
- Bir görev cümlesi (`data-gorev`) deneyi alıştırmaya çevirir; cevabını kendin hesaplayıp doğrula.

## 6. Ekran görüntüsüyle doğrulama

Başsız (headless) bir Chromium türevi yeterlidir:

```
chrome --headless=new --hide-scrollbars --window-size=1600,900 --screenshot=cikti.png sayfa.html
chrome --headless=new --virtual-time-budget=2000 --dump-dom sayfa.html
```

`--dump-dom` deneyin hesapladığı metni gösterir; beklenen sayıyla karşılaştır. Sanal zaman
`requestAnimationFrame` döngüsünü ilerletmeyebilir: animasyonu denetlerken sahneyi `git(u)` ile belirli
karelere götürüp her birinin görüntüsünü al. Konsol hatası için `--enable-logging=stderr --v=0`.

## 7. Teknik tuzaklar

- `text-transform: uppercase` Yunan harflerini de büyütür (τ → Τ); formül taşıyan etikette kullanma.
- Türkçe büyük harf için `<html lang="tr">` gerekir; yoksa "i" yanlış büyür.
- Python'da `"İ".lower()` birleşik nokta üretir; anahtar eşlemede önce `İ`/`I` harflerini elle dönüştür.
- CSS `url()` içinde boşluk ya da Türkçe karakter varsa tırnağa al.
- JavaScript belge yorumunun içine `/* */` koyma; dış yorumu erken kapatır ve dosya hiç çalışmaz.
- Medya panelinde `object-fit: contain` ve aynı zemin rengi; `cover` nesneyi kırpar.
- Yarı saydam kartın içinden levha çizgisi görünür; kartlar opak olsun.
- Yoğun tablo sayfasında başka konunun levhası (ör. bir tablonun arkasında ilgisiz bir matris) hatadır.
