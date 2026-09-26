/** City page: the mini-map. The prerendered SVG schematic is the no-JS view; MapLibre replaces it when it is near the viewport. */
import { tr, type Ctx } from '../i18n';
import { loadCities, loadManifest, loadSegments } from '../lib/data';
import { reduced } from '../motion';

export function initCity(ctx: Ctx): void {
  const box = document.querySelector<HTMLElement>('[data-minimap]');
  const canvas = box?.querySelector<HTMLElement>('[data-map-canvas]');
  if (!box || !canvas) return;
  const slug = box.dataset.city as string;
  let started = false;
  const start = async (): Promise<void> => {
    if (started) return;
    started = true;
    try {
      const [cities, fc, manifest] = await Promise.all([loadCities(ctx.base), loadSegments(ctx.base, slug), loadManifest(ctx.base)]);
      const city = cities.find((c) => c.slug === slug);
      if (!city) return;
      const { createSpeedMap } = await import('../map/speedmap');
      const map = createSpeedMap(canvas, { interactive: false, peak: manifest.peak_hours });
      await map.ready;
      map.setCity(fc, city);
      map.update({ mode: null, perc: 'p50', sel: { hour: null, period: 'peak' } });
      if (!map.hasTiles) {
        const n = document.createElement('p');
        n.className = 'idx-caption idx-map__notice'; n.textContent = tr(ctx)('map.notiles');
        box.append(n);
      }
      // hand over from the static schematic once the segments have faded in (the wave takes about a second)
      window.setTimeout(() => box.classList.add('idx-map--live'), reduced() ? 0 : 1100);
    } catch (e) { console.warn('mini-map unavailable, keeping the static schematic:', e); }
  };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); void start(); } }, { rootMargin: '300px' });
    io.observe(box);
  } else void start();
}
