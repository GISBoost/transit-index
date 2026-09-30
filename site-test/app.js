/* M4 test page: PMTiles over HTTP range requests + MapLibre. Colours come from the design tokens
   (CSS custom properties, tokens/colors.css copied from design/ at build time), never literals. */
(function () {
  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const protocol = new pmtiles.Protocol();
  maplibregl.addProtocol("pmtiles", protocol.tile);
  const esc = (x) => String(x).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const $ = (id) => document.getElementById(id);
  const state = { cfg: null, city: null, band: "all", map: null, errors: 0, tilesLoaded: 0 };

  function speedStep(field, classes) {
    const stops = [css("--speed-1")];
    classes.forEach((edge, i) => { stops.push(edge, css("--speed-" + (i + 2))); });
    return ["case", ["==", ["typeof", ["get", field]], "number"], ["step", ["get", field], ...stops], css("--speed-nodata")];
  }

  function widthExpr() { return ["interpolate", ["linear"], ["zoom"], 8, 0.6, 12, 1.6, 15, 4]; }
  function offsetExpr() { return ["interpolate", ["linear"], ["zoom"], 12, 0.8, 15, 3]; }

  function buildStyle(city) {
    const sources = { segments: { type: "vector", url: "pmtiles://" + city.tiles, attribution: "Dane: Transit Index (CC BY 4.0); źródło: " + (city.attribution ? esc(city.attribution.source) : "patrz docs/licenses.md") } };
    const layers = [{ id: "bg", type: "background", paint: { "background-color": css("--map-base") } }];
    if (city.basemap) {
      sources.base = { type: "vector", url: "pmtiles://" + city.basemap, attribution: "© OpenStreetMap contributors (ODbL), Protomaps" };
      const road = (id, kinds, w) => ({ id, type: "line", source: "base", "source-layer": "roads",
        filter: ["in", ["get", "kind"], ["literal", kinds]], layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": css("--map-street"), "line-width": ["interpolate", ["exponential", 1.6], ["zoom"], 8, w * 0.3, 15, w * 4] } });
      layers.push(
        { id: "earth", type: "fill", source: "base", "source-layer": "earth", paint: { "fill-color": css("--map-base") } },
        { id: "water", type: "fill", source: "base", "source-layer": "water", paint: { "fill-color": css("--paper-3") } },
        road("roads-minor", ["minor_road", "other"], 0.5), road("roads-medium", ["medium_road"], 0.8),
        road("roads-major", ["major_road", "highway"], 1.2));
    }
    const field = "v_" + state.band, qf = "q_" + state.band;
    const color = speedStep(field, state.cfg.speed_classes_kmh);
    const base = { type: "line", source: "segments", "source-layer": state.cfg.layer, layout: { "line-cap": "butt" } };
    layers.push(
      { ...base, id: "seg-ok", filter: ["==", ["get", qf], "ok"], paint: { "line-color": color, "line-width": widthExpr(), "line-offset": offsetExpr() } },
      { ...base, id: "seg-thin", filter: ["==", ["get", qf], "thin"], paint: { "line-color": color, "line-width": widthExpr(), "line-offset": offsetExpr(), "line-dasharray": [2, 1.5] } },
      { ...base, id: "seg-none", filter: ["==", ["get", qf], "none"], paint: { "line-color": css("--speed-nodata"), "line-width": widthExpr(), "line-offset": offsetExpr() } });
    return { version: 8, sources, layers };
  }

  function legend() {
    const c = state.cfg.speed_classes_kmh, el = $("legend");
    const items = [];
    const label = (i) => i === 0 ? "< " + c[0] : i === c.length ? "≥ " + c[c.length - 1] : c[i - 1] + "–" + c[i];
    for (let i = 0; i <= c.length; i++) items.push(`<span><i style="background:var(--speed-${i + 1})"></i>${label(i)} km/h</span>`);
    items.push('<span class="thin"><i></i>mało obserwacji (kreskowane)</span>', '<span><i style="background:var(--speed-nodata)"></i>brak danych</span>');
    el.innerHTML = items.join("");
  }

  function info() {
    const c = state.city;
    const pct = (x) => x == null ? "n/d" : (100 * x).toFixed(1).replace(".", ",") + "%";
    $("info").innerHTML = `<dl><dt>Odcinki:</dt><dd>${c.segments}</dd><dt>Geometria prosta (długość):</dt><dd>${pct(c.straight_share_length)}</dd>` +
      `<dt>Kafle:</dt><dd>${(c.tiles_bytes / 1e6).toFixed(1).replace(".", ",")} MB</dd><dt>Podkład:</dt><dd>${c.basemap ? (c.basemap_bytes / 1e6).toFixed(1).replace(".", ",") + " MB" : "brak (tło jednolite)"}</dd></dl>`;
  }

  function attribution() {
    const a = state.city.attribution;
    if (!a) { $("attrib").innerHTML = ""; return; }
    const lic = a.license ? esc(a.license) + (a.verified ? "" : " (do potwierdzenia)") : "nie ustalona" + (a.license_note ? ": " + esc(a.license_note) : "");
    $("attrib").innerHTML = `<h2>Źródło danych</h2><dl><dt>Operator:</dt><dd><a href="${esc(a.url)}" target="_blank" rel="noopener">${esc(a.source)}</a></dd>` +
      `<dt>Licencja źródła:</dt><dd>${lic}</dd>` + (a.obligations ? `<dt>Wymagania:</dt><dd>${esc(a.obligations)}</dd>` : "") + `</dl>` +
      `<p class="note">${esc(a.processing_note)} Wyniki: ${esc(a.results_license)}. Ustalenia licencyjne wstępne, nie opinia prawna.` +
      (a.osm ? " Kształty tras mogą pochodzić z OSM (© współtwórcy OpenStreetMap, ODbL)." : "") + `</p>`;
  }

  function mount() {
    const city = state.city;
    if (state.map) state.map.remove();
    state.errors = 0; state.tilesLoaded = 0;
    const map = state.map = new maplibregl.Map({ container: "map", style: buildStyle(city), bounds: city.bounds, fitBoundsOptions: { padding: 20 }, hash: true, attributionControl: { compact: true } });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }));
    map.on("error", (e) => { state.errors++; console.warn("map error", e && e.error && e.error.message); });
    map.on("data", (e) => { if (e.tile) state.tilesLoaded++; });
    map.on("click", (e) => {
      const f = map.queryRenderedFeatures(e.point, { layers: ["seg-ok", "seg-thin", "seg-none"] })[0];
      if (!f) return;
      const p = f.properties, v = (k) => p[k] == null || p[k] === "null" ? "n/d" : String(p[k]).replace(".", ",");
      new maplibregl.Popup().setLngLat(e.lngLat).setHTML(
        `<strong>${esc(p.from_name)} → ${esc(p.to_name)}</strong><br>tryb: ${esc(p.mode)}, linie: ${esc(p.routes)}<br>długość: ${v("length_m")} m<br>` +
        `prędkość (mediana): ${v("v_" + state.band)} km/h [${esc(p["q_" + state.band])}]<br>n = ${v("n_all")}, dni = ${v("n_days")}<br>geometria: ${esc(p.geometry_quality)}`).addTo(map);
    });
    info();
    attribution();
  }

  async function rangeTest() {
    const out = $("range-out"), url = new URL(state.city.tiles, location.href).href, lines = [];
    out.textContent = "Trwa…";
    const say = (s) => { lines.push(s); out.textContent = lines.join("\n"); };
    say("Przeglądarka: " + navigator.userAgent);
    say("Plik: " + url);
    let bad = 0;
    async function probe(name, start, end) {
      try {
        const r = await fetch(url, { headers: { Range: `bytes=${start}-${end}` }, cache: "no-store" });
        const buf = new Uint8Array(await r.arrayBuffer());
        const ok = r.status === 206 && buf.length === end - start + 1;
        if (!ok) bad++;
        say(`${ok ? "OK    " : "BŁĄD  "}${name}: status ${r.status}, otrzymano ${buf.length} B (oczekiwano ${end - start + 1}), Content-Range: ${r.headers.get("Content-Range") || "brak"}`);
        return buf;
      } catch (e) { bad++; say(`BŁĄD  ${name}: ${e.message}`); return null; }
    }
    const head = await probe("nagłówek (0–126)", 0, 126);
    if (head) { const magic = String.fromCharCode(...head.slice(0, 7)); if (magic !== "PMTiles") { bad++; say("BŁĄD  sygnatura PMTiles: " + magic); } else say("OK    sygnatura PMTiles, wersja " + head[7]); }
    await probe("zakres od 16 KiB (16384–32767)", 16384, 32767);
    const size = state.city.tiles_bytes, mid = Math.floor(size / 2);
    await probe(`zakres środkowy (${mid}–${mid + 999})`, mid, Math.min(mid + 999, size - 1));
    const before = state.errors;
    say("Ładowanie kafli mapy: " + state.tilesLoaded + " zdarzeń danych, " + before + " błędów od otwarcia miasta");
    if (before) bad++;
    say(bad ? `WYNIK: PROBLEM (${bad}). Skopiuj ten raport do docs/progress.md.` : "WYNIK: OK. Sprawdź ponadto, że mapa rysuje odcinki po przesunięciu i przybliżeniu.");
  }

  async function init() {
    state.cfg = await (await fetch("config.json")).json();
    const sel = $("city");
    state.cfg.cities.forEach((c) => sel.add(new Option(c.name, c.id)));
    const pick = () => { state.city = state.cfg.cities.find((c) => c.id === sel.value); mount(); };
    sel.addEventListener("change", pick);
    $("band").addEventListener("change", (e) => { state.band = e.target.value; state.map.setStyle(buildStyle(state.city)); });
    $("night").addEventListener("change", (e) => {
      document.documentElement.dataset.theme = e.target.checked ? "night" : "";
      legend(); state.map.setStyle(buildStyle(state.city));
    });
    $("run-range").addEventListener("click", rangeTest);
    legend(); pick();
  }
  init();
})();
