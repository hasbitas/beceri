/* Etkileşimli deney: kontrol → gerçek hesap → çubuk çıktısı → adlandırılmış sonuç. Bağımlılık yok.
   Kontroller bir kez kurulur; değer değişince yalnız çıktı yenilenir (kaydırıcı sürüklenirken bozulmaz).
   Kullanım:
     Deney.kur(el, {
       kontroller: [{ad: 'r', etiket: 'R', birim: 'kΩ', secenekler: [1, 2, 5], min: 1, max: 10, adim: 1, deger: 2}],
       hesapla: function (d) { return {satirlar: [{etiket, oran, metin}], sonuc: '...'}; }  // oran 0..1
     });
   hesapla saf bir fonksiyondur: tarayıcı dışında ayrıca test et. */
(function (kok) {
  'use strict';
  var dil = (document.documentElement.lang || undefined);
  function sayi(x, basamak) {
    return Number(x).toLocaleString(dil, {minimumFractionDigits: basamak || 0, maximumFractionDigits: basamak || 0});
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; });
  }

  function kur(el, tanim) {
    var d = {}, html = '<div class="lab-l">';
    tanim.kontroller.forEach(function (k) {
      d[k.ad] = k.deger;
      html += '<div class="lab-row" data-k="' + esc(k.ad) + '"><span class="lab-k">' + esc(k.etiket) + '</span>';
      (k.secenekler || []).forEach(function (v) {
        html += '<button type="button" class="lab-b" data-v="' + v + '">' + esc(sayi(v, k.basamak) + ' ' + (k.birim || '')) +
          '</button>';
      });
      if (k.min !== undefined) {
        html += '<input type="range" min="' + k.min + '" max="' + k.max + '" step="' + (k.adim || 1) +
          '" aria-label="' + esc(k.etiket) + '"><output></output>';
      }
      html += '</div>';
    });
    html += (el.dataset.gorev ? '<p class="lab-task">' + esc(el.dataset.gorev) + '</p>' : '') +
      '</div><div class="lab-r"><div data-cikti></div><div class="lab-nm" data-sonuc aria-live="polite"></div></div>';
    el.innerHTML = html;

    function yenile() {
      tanim.kontroller.forEach(function (k) {
        var satir = el.querySelector('[data-k="' + k.ad + '"]');
        satir.querySelectorAll('button').forEach(function (b) { b.classList.toggle('on', +b.dataset.v === d[k.ad]); });
        var r = satir.querySelector('input');
        if (r) { r.value = d[k.ad]; satir.querySelector('output').textContent = sayi(d[k.ad], k.basamak) + ' ' + (k.birim || ''); }
      });
      var s = tanim.hesapla(Object.assign({}, d));
      el.querySelector('[data-cikti]').innerHTML = s.satirlar.map(function (x) {
        var w = Math.max(0, Math.min(1, x.oran)) * 100;
        return '<div class="lb"><span>' + esc(x.etiket) + '</span><span class="lb-bar"><i style="width:' + w.toFixed(1) +
          '%"></i></span><span>' + esc(x.metin) + '</span></div>';
      }).join('');
      el.querySelector('[data-sonuc]').textContent = s.sonuc || '';
    }
    el.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-v]'); if (!b) return;
      d[b.closest('[data-k]').dataset.k] = +b.dataset.v; yenile();
    });
    el.addEventListener('input', function (e) {
      if (e.target.type !== 'range') return;
      d[e.target.closest('[data-k]').dataset.k] = +e.target.value; yenile();
    });
    yenile();
    return {degerler: d, yenile: yenile};
  }

  kok.Deney = {kur: kur, sayi: sayi};
})(window);
