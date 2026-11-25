---
name: kodlama-benchmark-yazimi
description: >-
  Kodlama ajanları için benchmark görevi yazar - görünür spec, referans çözüm, tek noktalı hatalı çözüm
  ve gizli testler. Kullan - bir kodlama-ajanı değerlendirme görevi ya da görev seti hazırlanırken veya
  mevcut bir görevin testleri güçlendirilirken. Kullanma - böyle bir görevi çözmek ya da projenin kendi
  test paketini onarmak için.
license: MIT
metadata:
  model-agnostic: "true"
---

# Kodlama benchmark görevi yazımı

Çıktı: çözücü ajana yalnız görünür spec'i veren, doğru çözümü geçiren, gerçekçi hatalı çözümleri
düşüren ve sonucu her ortamda aynı veren bir görev klasörü.

## Akış

1. Sözleşmeyi çıkar: klasör, tam dosya listesi, metadata anahtarları ve sabit değerleri, public API,
   çözücünün değiştirebileceği dosyalar, test çatısı ve istenen bitiş cevabı. Göreli yolları gerçek
   çalışma klasöründen çöz.
2. Önce görünür spec'i yaz: girdi biçimleri, çıktı biçimi ve sırası, boş girdi, geçersiz girdinin
   istisna sınıfları, değiştirme ve sahiplik garantileri, sınır anlamları. Testler hangi geçersiz
   koşulun önce geldiğini ayırıyorsa doğrulama sırasını yaz. Test edilen her davranış spec'ten çıkmalı;
   spec'te kod ve hata ipucu olmasın.
3. Yalnız standart kütüphaneyle doğru bir referans çözüm ve gerçekçi bir hatalı çözüm yaz. Hatalı çözüm
   tek noktalı, anlamsal bir hata taşısın (stub ya da keyfi çökme değil); ilgisiz doğru davranışı
   korusun.
4. Her spec kuralını olası küçük bir hatayla ve onu ayıran testle eşleştir: yanlış sınır, atlanan
   doğrulama, yanlış sıra ya da öncelik, eksik durum güncellemesi. Normal ve boş girdiyi, geçersiz tip
   ve değeri, kural etkileşimlerini kapsa. Tekrarlı örnekler yerine aşağıdaki küçük bağımsız oracle'ı
   ve ayırt edici sınır örneklerini kullan; istenen test çatısına ve asgari test sayısına uy.
5. İki sürümü de teslim klasörünün dışında, ayrı geçici klasörlerde koş: aday dosyayı beklenen adla ve
   testleri yanına kopyala, testleri orada çalıştır (ör. `python3 -m unittest -v`). Teslim klasöründen
   import etme; derlenmiş dosya bırakır.
6. Referans sıfır çıkış kodu vermeli; hatalı sürüm amaçlanan kusuru gösteren bir assertion ile düşmeli
   (import hatası sayılmaz). Bu tek hatanın yakalanması kapsam kanıtı değildir: kural-test eşlemesindeki
   açıkları kapat. Tanıyı okuyup yalnız başarısız denetimleri düzelt; başarılı koşuları gereksiz yere
   tekrarlama.
7. Metadata'nın anahtar kümesini ve sabit değerlerini, teslim ağacının tam dosya ve klasör listesini
   doğrula.
8. İstenen bitiş biçimini aynen ver; tek satırlık bir işaret isteniyorsa açıklama ekleme.

## Genel test ilkeleri

- Uygunsa küçük, **bağımsız bir oracle** ile sınırlı bir alanı belirlenimci olarak tara. Referansın
  algoritmasını ya da yardımcılarını kopyalama; beklenen sonucu adaydan üretme. Alanı eşdeğer sınıfları,
  istisnaları ve etkileşimleri içerecek biçimde seç; yalnız kolay bir aralığı taramak kapsam değildir.
  Kartezyen çarpımı küçük tut, alt testlerle (ör. `subTest`) adlandır.
- Her eşik ve istisna için hemen altını, kendisini ve hemen üstünü ayır. Periyodik ya da tekrarlı
  kurallarda tam küçük bir çevrim ve farklı büyük ofsetler dene; oracle alanı dışındaki uçları ayrı
  hedefli örneklerle kapsa.
- Oracle'ı birkaç açık beklenen sonuçla denetle. Gidiş-dönüş ve metamorfik özellikler tek başına
  yeterli değildir: aynı yanlışlık iki yönde de tutarlı olabilir. Sırayı, bağ kırmayı ve hata sınıfını
  spec'in istediği kesinlikte karşılaştır.
- Kimliği eşitlikten ayrı test et: "taze çıktı" ya da "paylaşılan referans yok" sözü varsa iç içe
  kapların kimliklerini de karşılaştır.
- Kısa yollardan önce tam doğrulama sözü varsa, geçersiz öğeyi sona koy ve boş ya da sıfır sonuç kısa
  yoluyla birlikte dene.
- Spec'te tanımlanmamış doğrulama sırasını test etme; bu çözücüye görünmez bir şart yükler.
- Dilin tip hiyerarşisindeki tuzakları ayrı yaz: Python'da `bool`, `int`'in alt sınıfıdır; bool'u ve
  int alt sınıflarını kabul ya da ret kuralını ayrı ayrı belirt ve test et.
- Sınırsız büyüklükte sayı sözü varsa, dilin sayı-metin dönüşüm sınırını aşan girdileri test et.
- Girdinin başarıda ve hatada korunmasını yalnız söz verildiyse denetle. Sıra bağımsızlığı vaat
  edilmedikçe permütasyonların aynı sonucu vermesini isteme; bağ kırma karşı örneklerini ayrıca seç.
- Büyük ya da uç girdileri yalnız sözleşme gerektiriyorsa ekle; platforma bağlı süre eşikleri ve
  ortamın varsayılan kaynak sınırlarıyla geçerli çözümleri eleme. Kapsamı artırmak için uzun spec,
  büyük tarama ya da ek araç turu gerekmez.
- Kenar kavramları açık örnekle ayır (kapalı aralıkların uç paylaşması ile ardışık tamsayılar
  arasındaki boşluk gibi).
