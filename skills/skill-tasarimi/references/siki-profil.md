# Siki profil

Skill `metadata.profil: "siki"` taşıyorsa ya da kullanıcı siki biçim istediyse bu notu izle. Başlangıç için
[siki şablon](../assets/skill-template-siki.md) ya da `beceri yeni --profil siki <ad>`.

## Gövde iskeleti

Tek `#` başlık, ardından yalnız şu `##` bölümleri, bu sırayla; alt başlık `###` olur:

1. `## Amaç`: üretilen somut sonuç, en çok iki dolu satır.
2. `## Ne zaman kullan / kullanma`: tetikleyen istek ve karıştırılan komşu iş.
3. `## Adımlar`: her adım dört alanlı (aşağıda).
4. `## Değişmezler ve yasaklar`: her koşulda geçerli kurallar. Bir kural tek yerde yazılır; başka bölüm
   ya da skill onu tekrar etmez, gerekirse adını anar.
5. `## Çıktı / rapor biçimi`: teslim edilen çıktı; üretildi, doğrulandı, doğrulanamadı ayrımı.
6. `## Referanslar`: referans dosyaları ve ne zaman okunacakları; yoksa "Yok."

Gövde kısa kalır (`beceri` sınırı: satır ve KB). Tarih, ölçüm sonucu ve neden-böyle-karar anlatısı gövdeye
girmez; gerekiyorsa references klasöründe bir tarihçe dosyasına yazılır. Bu klasör tek seviyedir: alt
klasör açılmaz, referanslar birbirine bağlanmaz.

## Adım satırı

Her adım dört soruyu cevaplar:

| Alan | Soru |
|---|---|
| Nesne | Hangi dosya, kayıt, komut ya da dış sistem? |
| Eylem | Ne yapılır? |
| Yetki | Kim onaylar? Yalnız okuyan adımda `yok`. |
| Kanıt | Sonuç nerede, nasıl doğrulanır? |

Tablo biçimi (önerilen), isteğe bağlı sıra sütunuyla:

```
| # | Nesne | Eylem | Yetki | Kanıt |
|---|---|---|---|---|
| 1 | `CHANGELOG.md` | son sürüm girdisini oku | yok | girdi rapora alındı |
| 2 | sürüm etiketi | oluştur ve gönder | sürüm sorumlusu | uzak depoda etiket görünür |
```

Numaralı madde biçimi, tek satırda:

```
1. **`CHANGELOG.md`** — son sürüm girdisini oku · yetki: yok · kanıt: girdi rapora alındı
```

Dışarı çıkan, para harcayan ya da geri alınamayan eylemde yetki somut bir kişi ya da roldür; `bilinmiyor`
yazılmaz. Kanıt `yok` olamaz: doğrulanamıyorsa adım çıktıda "doğrulanamadı" olarak raporlanır. Bölümde
kısa bir giriş paragrafı ve girintili alt madde serbesttir; girintisiz `-` maddesi adım yerine geçmez.

## Teslimden önce

- `beceri dogrula --kati <klasör>` hatasız; profil skill'in kendi bildiriminden okunur.
- Description ilk cümlelerde tetikleyiciyi ve "Kullanma" sınırını söylüyor.
- Değişmezlerdeki her kural yalnız bir yerde; aynı cümle referanslarda tekrar etmiyor.
- Bir tetiklemesi gereken, bir tetiklememesi gereken ve bir komşu skill'le karışabilecek istemle gözden
  geçirildi; statik denetim canlı başarı gibi bildirilmedi.
