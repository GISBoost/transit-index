/* @ds-bundle: {"format":4,"namespace":"IDX","components":[{"name":"TopBar"},{"name":"LangSwitch"},{"name":"Button"},{"name":"SegmentedControl"},{"name":"LineStop"},{"name":"LineBadge"},{"name":"QualityBadge"},{"name":"HeroKpi"},{"name":"KpiTile"},{"name":"RankingTable"},{"name":"SpeedLegend"},{"name":"MapPanel"},{"name":"SegmentPopup"},{"name":"Scrollytelling"},{"name":"HourlyProfile"},{"name":"CityCard"},{"name":"MethodNote"},{"name":"DownloadCard"},{"name":"Footer"},{"name":"Icons"}]} */
(function () {
  'use strict';

  /* ---------- ikony: jeden zestaw liniowy, siatka 24, kreska 1,5 px, bez emoji ---------- */
  var P = {
    'arrow-right': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'arrow-up-right': '<path d="M7 17 17 7M8 7h9v9"/>',
    'download': '<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>',
    'sliders': '<path d="M4 8h9M17 8h3M4 16h3M11 16h9"/><circle cx="15" cy="8" r="2"/><circle cx="9" cy="16" r="2"/>',
    'clock': '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
    'map': '<path d="M9 4 4 6v14l5-2 6 2 5-2V4l-5 2-6-2zM9 4v14M15 6v14"/>',
    'table': '<rect x="4" y="5" width="16" height="14" rx="1.5"/><path d="M4 10h16M10 5v14"/>',
    'info': '<circle cx="12" cy="12" r="8"/><path d="M12 11v5M12 8h.01"/>',
    'warning': '<path d="M12 4 21 20H3z"/><path d="M12 10v4M12 17h.01"/>',
    'check': '<path d="M5 12.5 9.5 17 19 7"/>',
    'close': '<path d="M6 6l12 12M18 6 6 18"/>',
    'chevron-down': '<path d="M6 9l6 6 6-6"/>',
    'external': '<path d="M14 5h5v5M19 5l-8 8M18 14v4a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h4"/>',
    'search': '<circle cx="11" cy="11" r="6"/><path d="M16 16l4 4"/>',
    'layers': '<path d="M12 4l8 4-8 4-8-4zM4 12l8 4 8-4M4 16l8 4 8-4"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>'
  };
  function icon(name, size) {
    size = size || 20;
    var p = P[name] || '';
    return '<svg class="idx-icon" width="' + size + '" height="' + size + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + p + '</svg>';
  }

  /* ---------- liczby: przecinek dziesiętny ---------- */
  function num(n, d) { return fmt(n, d).replace(',', '<span class="idx-comma">,</span>'); }
  function fmt(n, d) {
    d = d == null ? 1 : d;
    return Number(n).toLocaleString('pl-PL', { minimumFractionDigits: d, maximumFractionDigits: d });
  }

  /* ---------- klasa prędkości: progi z tokenów (--idx-speed-t1..t5) ---------- */
  function thresholds() {
    var cs = getComputedStyle(document.documentElement), t = [];
    for (var i = 1; i <= 5; i++) t.push(parseFloat(cs.getPropertyValue('--idx-speed-t' + i)));
    return t;
  }
  function speedClass(kmh) {
    if (kmh == null || isNaN(kmh)) return 'nd';
    var t = thresholds();
    for (var i = 0; i < t.length; i++) if (kmh < t[i]) return i + 1;
    return 6;
  }

  /* ---------- hydratacja: ikony, cyfry, słupki ---------- */
  function hydrate(root) {
    root = root || document;
    Array.prototype.forEach.call(root.querySelectorAll('[data-icon]'), function (el) {
      if (el.getAttribute('data-hydrated')) return;
      el.insertAdjacentHTML('afterbegin', icon(el.getAttribute('data-icon'), +el.getAttribute('data-size') || 20));
      el.setAttribute('data-hydrated', '1');
    });
    Array.prototype.forEach.call(root.querySelectorAll('[data-digits]'), function (el) {
      if (el.getAttribute('data-hydrated')) return;
      var s = el.getAttribute('data-digits'), out = '';
      for (var i = 0; i < s.length; i++) out += '<span class="idx-digit' + (s[i] === ',' || s[i] === '.' ? ' idx-digit--p' : '') + '" aria-hidden="true" style="--i:' + i + '">' + s[i] + '</span>';
      el.innerHTML = out + '<span class="idx-sr">' + s + '</span>';
      el.setAttribute('data-hydrated', '1');
    });
    Array.prototype.forEach.call(root.querySelectorAll('[data-k]'), function (el, i) {
      el.style.setProperty('--k', el.getAttribute('data-k'));
      el.style.setProperty('--i', el.getAttribute('data-i') || i);
    });
  }

  /* ---------- ruch: wejście w widok. Bez JS lub przy reduced-motion treść jest od razu widoczna ---------- */
  function motion(root) {
    root = root || document;
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    var targets = root.querySelectorAll('.idx-hero, .idx-rank, .idx-fade, [data-reveal]');
    if (reduce || !('IntersectionObserver' in window)) { Array.prototype.forEach.call(targets, function (t) { t.classList.add('is-in'); }); return; }
    document.documentElement.classList.add('idx-js');
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { threshold: 0.15 });
    Array.prototype.forEach.call(targets, function (t) { io.observe(t); });
  }

  /* ---------- wykres: profil godzinowy, rozkładowe kontra zmierzone ---------- */
  var uid = 0;
  function hourly(el, o) {
    var plan = o.plan, meas = o.meas, W = 720, H = 320, L = 44, R = 104, T = 28, B = 36;
    var ymax = o.ymax || 30, iw = W - L - R, ih = H - T - B, id = 'idxh' + (++uid);
    function x(h) { return L + (h + 0.5) * iw / 24; }
    function y(v) { return T + ih - v / ymax * ih; }
    var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-labelledby="' + id + 't ' + id + 'd"><title id="' + id + 't">' + (o.title || 'Profil godzinowy prędkości') + '</title><desc id="' + id + 'd">' + (o.desc || 'Prędkość rozkładowa i zmierzona (rekonstrukcja z GTFS-RT) w każdej godzinie doby. Oś pionowa zaczyna się od zera.') + '</desc>';
    s += '<defs><pattern id="' + id + 'p" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line class="c-hatch" x1="0" y1="0" x2="0" y2="7"/></pattern></defs>';
    for (var g = 0; g <= ymax; g += 10) {
      s += '<line class="c-grid" x1="' + L + '" x2="' + (W - R) + '" y1="' + y(g) + '" y2="' + y(g) + '"/><text class="c-axis" x="' + (L - 8) + '" y="' + (y(g) + 4) + '" text-anchor="end">' + g + '</text>';
    }
    s += '<text class="c-axis" x="' + L + '" y="' + (T - 12) + '">km/h</text>';
    for (var h = 0; h < 24; h += 3) s += '<text class="c-axis" x="' + x(h) + '" y="' + (H - 10) + '" text-anchor="middle">' + h + ':00</text>';
    /* godziny z próbą poniżej progu: kreskowanie z podpisem, nie pustka */
    var runs = [], st = null;
    for (var i = 0; i < 24; i++) { if (meas[i] == null) { if (st == null) st = i; } else if (st != null) { runs.push([st, i - 1]); st = null; } }
    if (st != null) runs.push([st, 23]);
    runs.forEach(function (r) {
      var x0 = x(r[0]) - iw / 48, x1 = x(r[1]) + iw / 48;
      s += '<rect x="' + x0 + '" y="' + T + '" width="' + (x1 - x0) + '" height="' + ih + '" fill="url(#' + id + 'p)"/><rect class="c-hatch-frame" x="' + x0 + '" y="' + T + '" width="' + (x1 - x0) + '" height="' + ih + '"/>';
      if (x1 - x0 > 60) s += '<text class="c-nodata-t" x="' + ((x0 + x1) / 2) + '" y="' + (T + 16) + '" text-anchor="middle">za mało danych</text>';
    });
    var pp = plan.map(function (v, k) { return (k ? 'L' : 'M') + x(k).toFixed(1) + ' ' + y(v).toFixed(1); }).join('');
    s += '<path class="c-plan" d="' + pp + '"/>';
    var d = '', pen = false;
    meas.forEach(function (v, k) { if (v == null) { pen = false; return; } d += (pen ? 'L' : 'M') + x(k).toFixed(1) + ' ' + y(v).toFixed(1); pen = true; });
    s += '<path class="c-meas" d="' + d + '"/>';
    var lastM = 23; while (lastM > 0 && meas[lastM] == null) lastM--;
    var yp = y(plan[23]), ym = y(meas[lastM]);
    if (Math.abs(yp - ym) < 18) { if (yp < ym) { yp -= 9; ym += 9; } else { yp += 9; ym -= 9; } }
    s += '<circle class="c-dot" cx="' + x(lastM) + '" cy="' + y(meas[lastM]) + '" r="4"/>';
    s += '<text class="c-lab-plan" x="' + (W - R + 10) + '" y="' + (yp + 4) + '">rozkładowe</text><text class="c-lab-meas" x="' + (W - R + 10) + '" y="' + (ym + 4) + '">zmierzone</text>';
    el.innerHTML = s + '</svg>';
  }

  /* ---------- dane zastępcze: schemat sieci do podglądów. Nie odwzorowuje żadnego miasta. ---------- */
  function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function mockMap(el, o) {
    o = o || {};
    var W = 640, H = 400, cx = 300, cy = 200, r = rng(o.seed || 7), s = '';
    s += '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + (o.label || 'Schemat poglądowy sieci: odcinki między przystankami w kolorach klas prędkości. Dane zastępcze.') + '" preserveAspectRatio="xMidYMid slice">';
    s += '<rect class="m-land" width="' + W + '" height="' + H + '"/>';
    s += '<path class="m-water" d="M-10 300 C 90 250, 170 330, 260 300 S 420 230, 520 270 S 620 330, 660 300 L 660 340 C 610 372, 540 316, 500 312 S 330 290, 260 350 S 60 320, -10 340 Z"/>';
    s += '<ellipse class="m-bound" cx="' + cx + '" cy="' + cy + '" rx="270" ry="170" stroke-width="1.2"/>';
    for (var q = 0; q < 9; q++) { var yy = 30 + q * 42; s += '<path class="m-road" stroke-width="1" d="M0 ' + yy + ' C 160 ' + (yy + 14) + ', 420 ' + (yy - 12) + ', ' + W + ' ' + (yy + 6) + '"/>'; }
    for (var q2 = 0; q2 < 12; q2++) { var xx = 20 + q2 * 56; s += '<path class="m-road" stroke-width="1" d="M' + xx + ' 0 C ' + (xx + 20) + ' 140, ' + (xx - 16) + ' 260, ' + (xx + 8) + ' ' + H + '"/>'; }
    var segs = [], nodes = [], N = o.lines || 9, ring = [];
    for (var a = 0; a < N; a++) {
      var ang = a / N * Math.PI * 2 + r() * 0.35, len = 150 + r() * 90, pts = [[cx, cy]], k = 7 + Math.floor(r() * 3);
      for (var j = 1; j <= k; j++) {
        var rr = len * j / k, an = ang + (r() - 0.5) * 0.16;
        pts.push([cx + Math.cos(an) * rr * 1.3, cy + Math.sin(an) * rr * 0.82]);
      }
      for (var m = 0; m < pts.length - 1; m++) {
        var d0 = m / (pts.length - 1), v = 8 + d0 * 22 + (r() - 0.5) * 9, cls = r() < 0.07 ? 'nd' : speedClass(v);
        segs.push({ a: pts[m], b: pts[m + 1], cls: cls });
      }
      pts.forEach(function (p) { nodes.push(p); });
    }
    for (var rg = 0; rg < 2; rg++) {
      var rad = 70 + rg * 70, pr = null;
      for (var t = 0; t <= 20; t++) {
        var an2 = t / 20 * Math.PI * 2, pt = [cx + Math.cos(an2) * rad * 1.3, cy + Math.sin(an2) * rad * 0.82];
        if (pr && (t % 5 !== 4 || rg)) { var v2 = 10 + rg * 6 + r() * 12; segs.push({ a: pr, b: pt, cls: speedClass(v2) }); }
        pr = pt; nodes.push(pt);
      }
    }
    segs.forEach(function (g, i) {
      s += '<path class="m-seg ' + (g.cls === 'nd' ? 'nd' : 'k' + g.cls) + '" data-cls="' + g.cls + '" data-i="' + i + '" d="M' + g.a[0].toFixed(1) + ' ' + g.a[1].toFixed(1) + ' L' + g.b[0].toFixed(1) + ' ' + g.b[1].toFixed(1) + '"/>';
    });
    nodes.forEach(function (p, i) { if (i % 2 === 0) s += '<circle class="m-stop" cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="2.6"/>'; });
    s += '<text class="m-label" x="' + (cx + 8) + '" y="' + (cy - 10) + '">centrum</text><text class="m-label" x="60" y="352">rzeka</text>';
    if (o.selected != null && segs[o.selected]) { var sg = segs[o.selected], mx = (sg.a[0] + sg.b[0]) / 2, my = (sg.a[1] + sg.b[1]) / 2; s += '<circle class="m-sel" cx="' + mx.toFixed(1) + '" cy="' + my.toFixed(1) + '" r="11"/>'; el.setAttribute('data-sel-x', (mx / W * 100).toFixed(1)); el.setAttribute('data-sel-y', (my / H * 100).toFixed(1)); }
    el.innerHTML = s + '</svg>';
    return segs;
  }

  window.IDX = { icon: icon, fmt: fmt, num: num, speedClass: speedClass, hydrate: hydrate, motion: motion, chart: { hourly: hourly }, demo: { mockMap: mockMap, icons: Object.keys(P) } };
})();
