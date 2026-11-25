# Marka çerçevesi

Bu dosya görsel kararların tek kaynağıdır. Skill yöntemi taşır; renk, yazı tipi ve düzen kararı buradan
gelir. `DOLDUR` yazan her alanı kullanıcının kendi beyanı ya da onayıyla doldur. Doldurulmamış alan varsa
en alttaki kurgusal örnekle yalnız **taslak** üretilir ve bu açıkça söylenir; ajan kimlik kararı uydurmaz.

Öncelik: güncel kullanıcı isteği > bu dosyadaki en yeni karar > skill varsayılanları. Bir karar kalıcı
olarak değişince eski satırı silme, Arşiv'e taşı ve neden değiştiğini yaz.

## Kimlik

- Kısa ad ve proje öneki (sol üst kod, ör. `ÖRN-1.04 | KONU`): DOLDUR
- Hissiyat, tek cümle (ör. "teknik broşür", "saha defteri", "laboratuvar raporu"): DOLDUR
- Hedef biçimler (slayt 16:9, dikey 3:4, kare, web bölümü, baskı): DOLDUR

## Renkler

| Rol | Değer | Kural |
|---|---|---|
| Zemin | DOLDUR | Sayfanın ana zemini |
| Mürekkep | DOLDUR | Yazı ve temel çizgi |
| İkincil yazı | DOLDUR | Mürekkebin saydam hali olabilir |
| İnce çizgi | DOLDUR | Cetvel, ızgara, kart çerçevesi |
| Panel | DOLDUR | Opak kart ve not zemini |
| Aksan | DOLDUR | Tek aksan: vurgu, seçili durum, ilerleme |

Kaçınılan renk ve efektler (ör. neon, parlama, gradyan dolgu): DOLDUR

## Tipografi

- Başlık yazı tipi, ağırlık, harf aralığı: DOLDUR
- Etiket ve meta (eşaralıklı mı, büyük harf mi, harf aralığı): DOLDUR
- Formül yazı tipi: DOLDUR
- Sayfa dili (`lang` değeri; Türkçe büyük harf için `tr` gerekir): DOLDUR
- Ondalık ayracı (`,` ya da `.`): DOLDUR

## Düzen ve ayrıntılar

- Izgara (metin bölgesi ve nesne bölgesinin yeri, oranı): DOLDUR
- Köşe biçimi (köşeli ya da yuvarlak) ve çizgi kalınlıkları: DOLDUR
- Etiket biçimi (alt çizgi, çerçeve, dolgu): DOLDUR
- Üst kod, alt ölçek cetveli, `FIG. 01 · BAŞLIK` etiketi kullanılıyor mu: DOLDUR

## Görsel ve hareket tercihleri

- Varsayılan görsel: içerikten kodla çizim (skill varsayılanı). Farklıysa: DOLDUR
- Üretken (yapay zekâ) görsel ve video: yalnız açık istekle (skill varsayılanı). Farklıysa: DOLDUR
- Hareket dili (düz çizgi, gölge yok, adım sayısı, süre): DOLDUR
- Sabit maskot ya da tekrar eden nesne var mı: DOLDUR

## Kurgusal örnek (gerçek bir marka değildir)

Taslak için "Örnek Atölye" adlı uydurma bir kimlik. Şablonlardaki (`cerceve.css`, `levha.py`) değerler budur;
kendi kararların gelince bu bölümü sil ya da Arşiv'e taşı.

| Rol | Değer |
|---|---|
| Zemin | `#F5F2EB` (açık kâğıt) |
| Mürekkep | `#22303A` |
| İkincil yazı | `rgba(34,48,58,.62)` |
| İnce çizgi | `rgba(34,48,58,.18)` |
| Panel | `#FFFFFF` |
| Aksan | `#1F7A8C` (camgöbeği) |

Yazı tipleri sistem yığınları: başlık `system-ui`, etiket `ui-monospace`. Önek `ÖRN-`, ondalık ayracı `,`.

## Arşiv

Geçersiz kalan kararlar; her satırda ne olduğu, neyle değiştiği ve neden.

- (boş)
