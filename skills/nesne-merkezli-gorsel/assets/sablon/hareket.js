/* Adım animasyonu: sahne yalnız ilerleme değerinden (u, 0..1) çizilir. Oynatma, kaydırıcı ve sayfa
   kaydırması aynı fonksiyonu çağırır; geri sarınca aynı kare gelir. Bağımlılık yok.
   Kullanım: Hareket.kur(svg, sahne, {sure: 8000, kaydirici: input, kaydirma: bolum, poster: 0.6})
   sahne(c, u): c = Hareket.cizici(svg); her çağrıda c.temizle() ile başla. */
(function (kok) {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';

  function ease(u) { u = Math.min(1, Math.max(0, u)); return 0.5 - 0.5 * Math.cos(Math.PI * u); }
  // n adımlı anlatımda hangi adım ve adımın içinde nerede: {i, f}
  function adim(u, n) { var x = Math.min(u, 0.999999) * n; return {i: Math.floor(x), f: x - Math.floor(x)}; }
  // eş ölçülü izdüşüm (levha.py ile aynı): x, y taban, z yukarı
  function iso(x, y, z, olcek, mx, my) {
    var c = Math.cos(Math.PI / 6), s = Math.sin(Math.PI / 6);
    return [mx + (x - y) * c * olcek, my + ((x + y) * s - z) * olcek];
  }

  // Renkler CSS değişkenlerinden okunur: marka tek yerde kalır.
  function cizici(svg) {
    var st = getComputedStyle(svg);
    function renk(ad) { return st.getPropertyValue(ad).trim() || 'currentColor'; }
    var R = {temel: [renk('--murekkep'), 1.2, 0.6], yardimci: [renk('--murekkep'), 0.8, 0.3],
             vurgu: [renk('--aksan'), 2.4, 1]};
    function ekle(ad, oz) {
      var e = document.createElementNS(NS, ad);
      for (var k in oz) e.setAttribute(k, oz[k]);
      svg.appendChild(e); return e;
    }
    function cizgiOz(rol, dolgu) {
      var r = R[rol] || R.temel;
      return {stroke: r[0], 'stroke-width': r[1], 'stroke-opacity': r[2], fill: dolgu || 'none'};
    }
    return {
      temizle: function () { while (svg.firstChild) svg.removeChild(svg.firstChild); },
      cizgi: function (nk, rol) {
        var o = cizgiOz(rol); o.points = nk.map(function (p) { return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
        return ekle('polyline', o);
      },
      cokgen: function (nk, rol) {
        var o = cizgiOz(rol, renk('--zemin')); o.points = nk.map(function (p) { return p.join(','); }).join(' ');
        return ekle('polygon', o);
      },
      metin: function (x, y, s, rol, boyut, hiza) {
        var e = ekle('text', {x: x, y: y, fill: (R[rol] || R.temel)[0], 'font-size': boyut || 14,
          'text-anchor': hiza || 'start', 'font-family': renk('--mono-font'), 'letter-spacing': 1.5});
        e.textContent = s; return e;
      }
    };
  }

  function kur(svg, sahne, se) {
    se = se || {};
    var c = cizici(svg), u = 0, bas = null, calisiyor = false, sure = se.sure || 8000;
    function git(x) {
      u = Math.min(1, Math.max(0, x));
      sahne(c, u);
      if (se.kaydirici) se.kaydirici.value = Math.round(u * 1000);
    }
    function kare(t) {
      if (!calisiyor) return;
      if (bas === null) bas = t - u * sure;
      var x = (t - bas) / sure;
      if (x >= 1 && se.dongu === false) { git(1); calisiyor = false; return; }
      git(x % 1);
      requestAnimationFrame(kare);
    }
    function oynat() { if (!calisiyor) { calisiyor = true; bas = null; requestAnimationFrame(kare); } }
    function durdur() { calisiyor = false; }
    if (se.kaydirici) {
      se.kaydirici.min = 0; se.kaydirici.max = 1000;
      se.kaydirici.addEventListener('input', function () { durdur(); git(se.kaydirici.value / 1000); });
    }
    if (se.kaydirma) {  // bölümün görünür ilerlemesi = u (geri kaydırma aynı sahneye döner)
      var guncelle = function () {
        var r = se.kaydirma.getBoundingClientRect(), h = window.innerHeight;
        git((h - r.top) / (h + r.height));
      };
      window.addEventListener('scroll', guncelle, {passive: true}); guncelle();
    } else if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
      git(se.poster || 0);  // hareket istemeyene anlamlı tek kare
    } else {
      git(0); oynat();
    }
    return {git: git, oynat: oynat, durdur: durdur};
  }

  kok.Hareket = {kur: kur, cizici: cizici, ease: ease, adim: adim, iso: iso};
})(window);
