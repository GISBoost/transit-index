/** Client entry. gisboost-1.css is loaded from the page head (first); the order here is tokens -> bundle -> site. */
import '../design/tokens.css';
import '../css/bundle.css';
import '../css/site.css';
import '../css/motion.css';
import type { Lang } from './i18n';
import { readThresholds } from './lib/idx';
import { initMotion } from './motion';
import { initChrome } from './client/chrome';

const root = document.querySelector<HTMLElement>('.idx-frame');
if (root) {
  const { page, lang, base } = root.dataset as { page: string; lang: Lang; base: string };
  const ctx = { lang, base };
  readThresholds();
  initChrome(base, lang);
  initMotion();
  // page modules are separate chunks; the map module (MapLibre) is imported by them on demand
  if (page === 'ranking') void import('./client/ranking').then((m) => m.initRanking(ctx));
  else if (page === 'city') void import('./client/city').then((m) => m.initCity(ctx));
  else if (page === 'map') void import('./client/mappage').then((m) => m.initMap(ctx));
  else if (page === 'method') void import('./client/scrolly').then((m) => m.initScrolly());
}
(window as unknown as { __idx: boolean }).__idx = true;
