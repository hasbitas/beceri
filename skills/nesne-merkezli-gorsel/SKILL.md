---
name: nesne-merkezli-gorsel
description: >-
  Konunun gerçek yapısını ya da işleyişini ana nesne yapan teknik görseller üretir. Kullan - sunum, afiş,
  eğitim materyali, web ya da sosyal medya için açıklayıcı görsel, levha, şema, adım animasyonu veya
  etkileşimli deney istendiğinde ya da mevcut görsel dekor gibi durduğunda; renk ve yazı tipleri
  doldurulabilir bir marka çerçevesinden gelir. Kullanma - veri grafiği ve pano tasarımı, fotoğraf ya da
  illüstrasyon üretimi, logo veya marka kimliği yaratma için.
license: MIT
metadata:
  model-agnostic: "true"
---

# Nesne merkezli görsel

Çıktı: konusu değişince anlamsızlaşan, yani içerikle birebir bağlı bir görsel. Ana nesne konunun gerçek
yapısı, işleyişi ya da ilişkisidir (kesit, patlatılmış parça, devre, eğri, matris, akış); süs değildir.
Görsel varsayılan olarak kodla, gerçek veriden ya da hesaptan çizilir ve ekrandaki her sayı hesaplanmıştır.

## Başlamadan

- Marka kararları [brand/frame.md](brand/frame.md) içindedir. Doluysa uygula. Yer tutucular duruyorsa
  kullanıcıdan renk, yazı tipi ve düzen kararlarını iste ya da dosyadaki kurgusal örnekle taslak üret ve
  bunu açıkça söyle. Kimlik kararını kendin uydurma.
- Güncel istek kayıtlı tercihin önüne geçer. Kullanıcı yeni bir yönü kalıcı kabul ederse çerçeveyi
  güncelle; eski kararı silme, Arşiv'e taşı.
- Konuyu çöz: hangi mekanizma anlatılıyor, hangi sayılar doğru olmalı, hedef biçim ne (16:9 slayt,
  dikey 3:4, kare, web bölümü, baskı).

## Akış

1. **Ana nesneyi seç.** Konunun kendisini taşıyan yapıyı bul: parçaları, katmanları, akışı, ilişkiyi.
   Sına: başlık başka bir konu olsa bu görsel yine uyar mı? Uyuyorsa dekordur, değiştir.
2. **Kompozisyonu kur.** Çerçevedeki ızgarayı uygula: metin bölgesi ile nesne bölgesi ayrı; nesne
   bölgesinde tek vurgu. Üst kod, ölçek cetveli ve `FIG.` etiketi çerçeve istiyorsa eklenir.
3. **Kodla çiz.** Levha şablonu: `assets/sablon/levha.py`. Veriyi ve hesabı yaz, çizimi ondan üret;
   etiketlerdeki sayıları aynı hesaptan bas.
4. **Hareket gerekiyorsa** sahneyi tek bir ilerleme değerinden çizen bir fonksiyon yaz
   (`assets/sablon/hareket.js`). Her animasyon tek cümleyle söylenebilen bir metafor taşır; "güzel
   hareket" tek başına yetmez. Gölgesiz, levhalarla aynı çizgi dili.
5. **Etkileşim uygunsa** (eğitim, teknik anlatım) bir deney öner: kullanıcı değer seçer, öğe ekler ya
   da çıkarır, sonucu anında görür (`assets/sablon/deney.js`). Hesabı tarayıcı dışında da sına.
6. **Doğrula.** Başsız tarayıcıyla ekran görüntüsü al, aşağıdaki kontrol listesinden geçir; taşma,
   okunabilirlik ve sayıların doğruluğuna bak.
7. **Teslim et.** İstenen biçimi üret. Neyin kodla, neyin üretken modelle yapıldığını doğru söyle;
   taslağı taslak diye adlandır.

Ayrıntılı tarifler, kod-marka eşlemesi ve yaşanmış teknik tuzaklar:
[references/uretim.md](references/uretim.md). Şablonları uyarlarken ya da bir levha, animasyon veya deney
yazarken oku.

## Kompozisyon sözleşmesi

- Tek aksan rengi vurgu, seçili durum ve ilerleme içindir; geniş alan boyamak için değil.
- Arka plan levhası metinle yarışmaz: metin tarafı gradyanla bastırılır; yoğun tablo ya da formül
  sayfasında levha soluklaşır ve aynı konuyu gösterir. Kartlar opaktır.
- Görsel ve video panelleri içeriği kırpmaz (`contain`, aynı zemin rengi).
- Sabit maskot yok; nesne konuya göre değişir.
- Kaydırmayla anlatımda bütün parçalar aynı ilerleme değerine bağlıdır; geri kaydırma aynı sahneye döner.
- Bilimsel ya da teknik içerikte doğrulanmamış sanatsal görseli kanıt gibi sunma; yanlışsa kodla yeniden
  üret.
- Üretken görsel ve video yalnız kullanıcı açıkça isterse. O zaman da stok-sinematik klişelerden (bokeh,
  ışık huzmesi, parlak cam küre, toz, neon parıltı) kaçın. Ücretli üretimden önce maliyeti göster ve onay
  al; içeriği dış servise göndermeden önce izin iste.

## Kontrol listesi

- [ ] Görsel içerikle birebir bağlı mı (başlık değişince anlamsızlaşıyor mu)?
- [ ] Ekrandaki her sayı kodla hesaplandı mı; birim ve ondalık ayracı doğru mu?
- [ ] Metafor tek cümleyle söylenebiliyor mu?
- [ ] Nesne bölgesinde tek vurgu mu var; çizgi hiyerarşisi okunuyor mu?
- [ ] Metin levhanın üstüne taşmıyor; yoğun sayfada levha soluk ve aynı konuda mı?
- [ ] Kartlar opak; etiketler kırpılmamış; dar ekranda taşma yok mu?
- [ ] Renkler ve yazı tipleri yalnız marka çerçevesinden mi geliyor?
- [ ] Sinematik klişe ve dekoratif efekt yok mu?
- [ ] Hareket istemeyen kullanıcıya anlamlı tek kare gösteriliyor mu?

## Paket

- `brand/frame.md`: doldurulacak marka çerçevesi, kurgusal örnek palet ve Arşiv.
- [references/uretim.md](references/uretim.md): tarifler, bileşen kuralları, doğrulama komutları, tuzaklar.
- `assets/sablon/`: `levha.py` (bağımlılıksız SVG levha), `hareket.js` (ilerleme değerine bağlı sahne),
  `deney.js` (kontrol → hesap → sonuç), `cerceve.css` (marka değişkenli 16:9 sayfa),
  `sayfa.html` (üçünü birleştiren örnek; önce `python levha.py --cikti levhalar` çalıştır).
