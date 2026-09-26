/** The only place that sets things in motion. Rules (design/guidelines/50-ruch.md): animate transform and opacity only,
 *  at most idx-dur-reveal (600 ms), times and curves from the tokens, no scroll hijacking, no loops except the loader.
 *  Everything degrades: no JS = content visible; prefers-reduced-motion = final state at once; no animation-timeline =
 *  the camera flight is done by GSAP ScrollTrigger (see client/scrolly.ts), still transform-only. */

export const reduced = (): boolean => matchMedia('(prefers-reduced-motion: reduce)').matches;

const tok = (name: string): string => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
/** Token duration in ms ("400ms" -> 400). */
export const ms = (name: string): number => parseFloat(tok(name));
/** Token easing, usable directly in WAAPI. */
export const ease = (name: string): string => tok(name);

const TARGETS = '.idx-hero, .idx-rank, .idx-fade, .idx-rule, [data-reveal], [data-lines], [data-stagger], [data-chart]';
let io: IntersectionObserver | null = null;

/** Headings enter line by line: words become inline-blocks, each word gets the index of its visual line (--l). */
function splitHeadings(root: ParentNode): void {
  root.querySelectorAll<HTMLElement>('[data-lines]:not([data-split])').forEach((h) => {
    const words = (h.textContent ?? '').trim().split(/\s+/);
    h.textContent = '';
    words.forEach((w, i) => {
      const s = document.createElement('span');
      s.className = 'idx-w'; s.textContent = w;
      h.append(s);
      if (i < words.length - 1) h.append(' ');
    });
    h.dataset.split = '1';
    const measure = (): void => {
      const spans = [...h.querySelectorAll<HTMLElement>('.idx-w')];
      const tops = [...new Set(spans.map((s) => s.offsetTop))].sort((a, b) => a - b);
      spans.forEach((s) => s.style.setProperty('--l', String(tops.indexOf(s.offsetTop))));
    };
    measure();
    document.fonts?.ready.then(measure);
  });
}

/** Children of [data-stagger] enter one after another (index -> --i, 50 ms each in motion.css). */
function indexChildren(root: ParentNode): void {
  root.querySelectorAll<HTMLElement>('[data-stagger]').forEach((c) => [...c.children].forEach((k, i) => (k as HTMLElement).style.setProperty('--i', String(i))));
}

export function observe(root: ParentNode = document): void {
  const targets = [...root.querySelectorAll<HTMLElement>(TARGETS)].filter((t) => !t.classList.contains('is-in'));
  if (reduced() || !('IntersectionObserver' in window)) { targets.forEach((t) => t.classList.add('is-in')); return; }
  io ??= new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      const t = e.target as HTMLElement;
      t.classList.add('is-in');
      io?.unobserve(t);
      if (t.matches('[data-chart]')) drawChart(t);
    }
  }, { threshold: 0.15, rootMargin: '0px 0px -6% 0px' });
  targets.forEach((t) => io?.observe(t));
}

export function initMotion(): void {
  if (!reduced()) { splitHeadings(document); indexChildren(document); }
  observe(document);
}

/* ---------- hourly chart: the measured line is drawn by sliding a clip rect (transform), then the end dot pulses once ---------- */
let clipN = 0;
function drawChart(fig: HTMLElement): void {
  if (reduced()) return;
  const svg = [...fig.querySelectorAll<SVGSVGElement>('.idx-chart__v svg')].find((x) => x.getClientRects().length > 0), line = svg?.querySelector('.c-meas'), dot = svg?.querySelector<SVGElement>('.c-dot');
  const defs = svg?.querySelector('defs');
  if (!svg || !line || !defs) return;
  const ns = 'http://www.w3.org/2000/svg', id = `idxclip${++clipN}`, vb = svg.viewBox.baseVal;
  const cp = document.createElementNS(ns, 'clipPath'), r = document.createElementNS(ns, 'rect');
  cp.id = id;
  r.setAttribute('width', String(vb.width)); r.setAttribute('height', String(vb.height));
  r.style.transformBox = 'fill-box'; r.style.transformOrigin = 'left';
  cp.append(r); defs.append(cp);
  line.setAttribute('clip-path', `url(#${id})`);
  const dur = ms('--idx-dur-reveal'), easing = ease('--idx-ease-out');
  r.animate([{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }], { duration: dur, easing, fill: 'both' }).finished.then(() => line.removeAttribute('clip-path'), () => line.removeAttribute('clip-path'));
  if (dot) {
    dot.style.transformBox = 'fill-box'; dot.style.transformOrigin = 'center';
    dot.animate([{ opacity: 0 }, { opacity: 1 }], { duration: ms('--idx-dur-base'), delay: dur * 0.8, easing, fill: 'backwards' });
    dot.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.9)' }, { transform: 'scale(1)' }], { duration: dur, delay: dur, easing: ease('--idx-ease-inout') });
  }
}

/* ---------- FLIP: reorder rows, animating only transform (and opacity for rows that appear) ---------- */
export function flip(container: HTMLElement, mutate: () => void, key = '[data-key]'): void {
  const rows = (): HTMLElement[] => [...container.querySelectorAll<HTMLElement>(key)];
  const first = new Map(rows().map((r) => [r.dataset.key as string, r.getBoundingClientRect().top]));
  mutate();
  if (reduced()) return;
  const dur = ms('--idx-dur-slow'), easing = ease('--idx-ease-out');
  for (const r of rows()) {
    const f = first.get(r.dataset.key as string);
    if (f == null) { r.animate([{ opacity: 0 }, { opacity: 1 }], { duration: ms('--idx-dur-base'), easing }); continue; }
    const dy = f - r.getBoundingClientRect().top;
    if (dy) r.animate([{ transform: `translateY(${dy}px)` }, { transform: 'none' }], { duration: dur, easing });
  }
}

/** Animate a bar's scaleX between two values (the CSS transition does not survive a DOM move, WAAPI does). */
export function growBar(fill: HTMLElement, from: number, to: number): void {
  fill.style.setProperty('--k', String(to));
  if (reduced() || from === to) return;
  fill.animate([{ transform: `scaleX(${from})` }, { transform: `scaleX(${to})` }], { duration: ms('--idx-dur-slow'), easing: ease('--idx-ease-out') });
}

/** Soft crossfade of a row that got new values (opacity only). */
export function blip(el: HTMLElement): void {
  if (!reduced()) el.animate([{ opacity: 0.35 }, { opacity: 1 }], { duration: ms('--idx-dur-base'), easing: ease('--idx-ease-out') });
}

/* ---------- sliding indicator (segmented control, topbar): a transform-only pill behind the items ---------- */
export interface Slider { sync(animate?: boolean): void }
export function slider(host: HTMLElement, ind: HTMLElement, items: () => HTMLElement[], active: () => HTMLElement | null, opts: { hover?: boolean; from?: HTMLElement | null } = {}): Slider {
  const place = (el: HTMLElement | null, animate: boolean): void => {
    if (!el) { ind.style.opacity = '0'; return; }
    ind.style.opacity = '';
    if (!animate || reduced()) ind.style.transition = 'none';
    ind.style.setProperty('--x', String(el.offsetLeft));
    ind.style.setProperty('--w', String(el.offsetWidth));
    if (!animate || reduced()) { void ind.offsetWidth; ind.style.transition = ''; }
  };
  const sync = (animate = true): void => place(active(), animate);
  if (opts.from) place(opts.from, false);
  requestAnimationFrame(() => sync(true));
  if (opts.hover) {
    for (const it of items()) {
      it.addEventListener('pointerenter', () => place(it, true));
      it.addEventListener('focus', () => place(it, true));
    }
    host.addEventListener('pointerleave', () => sync(true));
    host.addEventListener('focusout', () => sync(true));
  }
  new ResizeObserver(() => sync(false)).observe(host);
  document.fonts?.ready.then(() => sync(false));
  return { sync };
}

/** Theme switch: a veil in the old background colour fades out over the new theme (opacity only, no flicker). */
export function themeVeil(apply: () => void): void {
  if (reduced()) { apply(); return; }
  const v = document.createElement('div');
  v.className = 'idx-veil';
  v.style.background = getComputedStyle(document.body).backgroundColor;
  document.body.append(v);
  apply();
  v.animate([{ opacity: 1 }, { opacity: 0 }], { duration: ms('--idx-dur-base'), easing: ease('--idx-ease-inout') }).finished.then(() => v.remove(), () => v.remove());
}

/** Element enters with opacity + translateY (popups, drawers); direction is the offset it comes from. */
export function enter(el: HTMLElement, dy = 8, dur = '--idx-dur-base'): void {
  if (reduced()) return;
  el.animate([{ opacity: 0, transform: `translateY(${dy}px)` }, { opacity: 1, transform: 'none' }], { duration: ms(dur), easing: ease('--idx-ease-out') });
}
