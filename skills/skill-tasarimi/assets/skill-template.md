---
name: ornek-skill
description: >-
  DOLDUR - skill'in yaptığı işi ve onu tetikleyen isteği yaz. Kullan - kullanıcı bu işi istediğinde.
  Kullanma - benzer görünen ama başka bir iş için.
metadata:
  model-agnostic: "true"
---

# Ornek skill

DOLDUR: Bu skill hangi somut sonuç için kullanılır? Aşağıdaki yazım notlarını gerçek içerikle değiştir;
karar değiştirmeyen bölümü kaldır. Bu dosya tamamlanmış bir skill değil, şablondur.

## Girdi ve koşullar

DOLDUR: İşe başlamadan gerçekten bilinmesi gerekenler ve bunların bulunacağı yer. Kullanıcının mevcut
seçimi varsa koru; aynı soruyu yeniden sorma.

## Uygulama yolu

DOLDUR: Karar noktaları, bağımlılıklar ve uygun araçlar. Bağımsız düşünmeye alan bırak; sıralama ancak
gerçek bir bağımlılık varsa sabit olsun. Ayrıntı gerekiyorsa references/ altına ayrı bir dosya koy,
burada bağlantısını ve hangi durumda okunacağını yaz.

## Sonuç kontrolü

DOLDUR: Hangi gözlem işin bittiğini gösterir? Çıktı nereye yazılır ve nasıl geri okunur? Üretildi,
denetlendi ve doğrulanamadı durumlarını ayır.

## Aksaklık ve alternatif

DOLDUR: Gerçek bir hata görüldüyse belirti, geçerli koşul, alternatif ve kanıt ilişkisini yaz. Deney
yapılmadıysa öneri olduğunu belirt; yeniden deneme ve durma koşulu işe orantılı olsun.
