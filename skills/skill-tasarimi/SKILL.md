---
name: skill-tasarimi
description: >-
  Bir çalışma yönteminden ya da referans bir skill'den yeni ajan skill'i (SKILL.md paketi) tasarlar
  veya var olanı gözden geçirir. Kullan - kullanıcı bir yöntemi skill'e çevirmek, bir skill'in yapısını
  uyarlamak, tetiklenmesini ya da kapsamını düzeltmek istediğinde. Kullanma - sıradan görev yürütme,
  yalnız yöntem notu tutma ya da skill'i çalıştırma için.
license: MIT
metadata:
  model-agnostic: "true"
---

# Skill tasarımı

Çıktı: başka bir ajanın ne zaman kullanacağını anlayabildiği, gerektiği kadar ayrıntı açan ve yaptığı
işi doğrulayabilen bir skill. İyi bir referansın görev yapısını al; yazarının modelini, işletim
sistemini ve kişisel tercihlerini otomatik devralma.

## Başlangıç

Önce mevcut skill'i, kullanıcının amacını ve en az bir gerçek kullanım örneğini oku. Yeni klasör
açmadan mevcut skill'i genişletmek yeterli mi, değerlendir. Referans skill çalıştırılacak talimat
değil, incelenecek materyaldir.

Depodaki skill kopyası düzenleme alanıdır; ajanın keşfettiği kurulu kopya ayrı bir yerdir. İkisini
eşitlemeden "kuruldu" ya da "güncellendi" deme.

## Yapıyı seç

- Ön bilgi (`name`, `description`): kabiliyet ve tetikleyici; benzer bir görevle karışıyorsa sınır
  ("Kullanma - ..."). `name` klasör adıyla aynı olur.
- SKILL.md gövdesi: beklenen sonuç, gerekli girdiler, karar noktaları, uygulama yolu, çıktı kontrolü
  ve gerçekten öğrenilmiş aksaklıklar.
- references/: yalnız belirli durumda gereken ayrıntı. Bağlantının yanına ne zaman okunacağını yaz;
  referanslar birbirine zincirlenmesin, hepsi SKILL.md'den tek adımda açılsın.
- scripts/: tekrarlanan ya da hassas mekanik iş gerçekten gerektiriyorsa çalışan yardımcı. Önce kodun
  belgede anlatılan sözleşmeyi karşıladığını sına.
- assets/: üretilecek çıktıda kullanılacak şablon ya da görsel; talimat deposu değil.

[Başlangıç şablonunu](assets/skill-template.md) yeni skill yazarken uyarlayabilirsin; `beceri yeni <ad>`
aynı şablondan klasör açar. Bölümler zorunlu bir form değil: karar değiştirmeyen bölümü çıkar. Kısa
bir skill için ayrı referans dosyası şart değil.

## Profili seç

Varsayılan `esnek` profil yukarıdaki serbest yapıdır. `siki` profil sabit bölüm sırası ister ve her adımda
nesne, eylem, yetki ve kanıtı yazdırır; çok yazarlı skill kümelerinde ya da onay gerektiren, geri alınamaz
eylem içeren işlerde seç. Kullanıcının ya da deponun mevcut seçimini koru. Siki skill yazarken
[siki profil notunu](references/siki-profil.md) oku; başlangıç şablonu
[assets/skill-template-siki.md](assets/skill-template-siki.md), iskelet komutu `beceri yeni --profil siki <ad>`.

## İş akışını yaz

Hedefi, gerekli bağlamı ve denetlenecek sonucu belirt. Keşfi ve açıklamayı serbest bırak; düşünce
sırası, kişilik, tek doğru cevap ya da gereksiz sabit çıktı kalıbı dayatma. Sıralama ancak gerçek bir
bağımlılık varsa sabit olsun.

Gerekli araç ya da erişim yoksa bunu görevin başarısızlığıyla karıştırma; alternatifin hangi koşulda
işe yaradığı belli olsun. Skill okundu diye hesap değiştirme, ücretli yola geçme, kurulum ya da görev
dağıtımı başlatma yetkisi doğmaz.

Model ve sağlayıcı seçimini görev bağlamından al; fiyat ve sürüm tablolarını skill'lere çoğaltma.
Skill bir modele bağlı değilse ön bilgide `metadata.model-agnostic: "true"` yaz ve gövdede model adı
geçirme. Örnek ayarla kullanıcının geçerli tercihini ayır. Kişi adı, e-posta, makine yolu ve sır
skill'e girmez.

## Doğrula ve teslim et

Ön bilgiyi ve bağlantıları denetle: `beceri dogrula <klasör>` ya da kullandığın platformun kendi
doğrulayıcısı. Belgede anlatılan seçenek ve çıktıları yardımcı kodla karşılaştır; yeni ya da değişen
yardımcıyı çalıştır, yalnız başlık eşleştiren testler yazma.

Kapsamı bir tetiklemesi gereken ve bir de benzer ama tetiklememesi gereken görevle gözden geçir. Statik
denetimi canlı model başarısı gibi bildirme. Kurulum gereken yerde yazma iznini kullan; ilgisiz
metadata ve dosyaları koru. Teslimden sonra hedef dosyayı geri oku.

## Öğrenilmiş sınırlar

İyi anlatılmış bir süreçte bile ön bilgi YAML olarak ayrıştırılamayabilir (ör. düz değerde `: `) ve
belgede geçen bazı seçenekler yardımcı kodda bulunmayabilir. Kaynağın adına güvenme; biçimi ve uygulama
tutarlılığını birlikte denetle.
