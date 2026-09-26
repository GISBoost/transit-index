/** Ranking page: toggles (mode / period) without reload, state in the URL, loading / empty / error states, FLIP reorder. */
import { tr, type Ctx } from '../i18n';
import { loadCities, loadRanking } from '../lib/data';
import { MODE_KEYS, PERIOD_KEYS, sortRanking } from '../lib/agg';
import { readRank, writeRank, type RankState } from '../lib/params';
import type { City, Ranking } from '../lib/schema';
import { rankEmpty, rankError, rankRows, rankSkeleton } from '../components/sections';
import { blip, flip, growBar, observe } from '../motion';
import { bindSeg } from './controls';

export function initRanking(ctx: Ctx): void {
  const root = document.querySelector<HTMLElement>('[data-ranking]');
  const body = root?.querySelector<HTMLElement>('[data-rank-body]');
  const live = document.querySelector<HTMLElement>('[data-live]');
  if (!root || !body) return;
  const t = tr(ctx);
  let state: RankState = readRank(new URLSearchParams(location.search));
  let data: { cities: City[]; ranking: Ranking } | null = null;
  let failed = false;

  const kOf = (row: HTMLElement): number => parseFloat(row.querySelector<HTMLElement>('.idx-bar__fill')?.style.getPropertyValue('--k') ?? '0') || 0;

  /** Update rows in place by city, so bars can grow from their old value and rows can slide (FLIP). */
  function paint(animate: boolean): void {
    if (!data) return;
    const { cities, ranking } = data;
    const items = sortRanking(ranking[state.mode][state.period], cities);
    if (!items.some((i) => i.kmh != null)) { body!.innerHTML = rankEmpty(ctx); return; }
    const existing = new Map([...body!.querySelectorAll<HTMLElement>('.idx-rrow[data-key]')].map((r) => [r.dataset.key as string, r]));
    const build = (): void => {
      body!.querySelectorAll('.idx-rrow:not([data-key]), [aria-busy], .idx-rank__state').forEach((n) => n.remove());
      const olds = new Map<string, number>();
      existing.forEach((r, k) => olds.set(k, kOf(r)));
      const fresh = new Map<string, HTMLElement>();
      const tmp = document.createElement('div');
      tmp.innerHTML = rankRows(ctx, items, cities);
      tmp.querySelectorAll<HTMLElement>('.idx-rrow').forEach((r) => fresh.set(r.dataset.key as string, r));
      items.forEach((it, i) => {
        const nu = fresh.get(it.slug) as HTMLElement, old = existing.get(it.slug);
        if (old && !old.classList.contains('idx-rrow--out') && !nu.classList.contains('idx-rrow--out')) {
          // same kind of row: patch text, class and connector, animate the bar
          old.querySelector('.idx-rrow__rank')!.textContent = nu.querySelector('.idx-rrow__rank')!.textContent;
          old.querySelector('.idx-rrow__val')!.innerHTML = nu.querySelector('.idx-rrow__val')!.innerHTML;
          old.querySelector('.idx-rrow__name')!.innerHTML = nu.querySelector('.idx-rrow__name')!.innerHTML;
          old.querySelector('.idx-conn')!.className = nu.querySelector('.idx-conn')!.className;
          old.querySelector('.idx-conn .idx-node')!.className = nu.querySelector('.idx-conn .idx-node')!.className;
          const fill = old.querySelector<HTMLElement>('.idx-bar__fill'), nf = nu.querySelector<HTMLElement>('.idx-bar__fill');
          if (fill && nf) { fill.className = nf.className; growBar(fill, olds.get(it.slug) ?? 0, parseFloat(nf.style.getPropertyValue('--k'))); }
          old.style.setProperty('--i', String(i));
          blip(old);
          body!.append(old);
        } else {
          old?.remove();
          body!.append(nu);
        }
      });
      existing.forEach((r, k) => { if (!fresh.has(k)) r.remove(); });
      body!.querySelectorAll('.idx-conn--done').forEach((c) => c.classList.remove('idx-conn--done'));
    };
    if (animate) flip(body!, build); else build();
    observe(root!);
    if (live) live.textContent = t('rank.live', { mode: t(MODE_KEYS[state.mode]), period: t(PERIOD_KEYS[state.period]), n: items.filter((i) => i.pos != null).length });
  }

  function show(first = false): void {
    if (failed) { body!.innerHTML = rankError(ctx); root!.classList.add('idx-rank--error'); return; }
    root!.classList.remove('idx-rank--error');
    if (!data) { body!.innerHTML = rankSkeleton(ctx); return; }
    // the prerendered markup is tram / day: nothing to do when that is what the URL asks for
    if (first && state.mode === 'tram' && state.period === 'day' && body!.querySelector('.idx-rrow[data-key]')) return;
    paint(!first);
  }

  function load(): void {
    failed = false; data = null;
    Promise.all([loadCities(ctx.base), loadRanking(ctx.base)])
      .then(([cities, ranking]) => { data = { cities, ranking }; show(true); })
      .catch(() => { failed = true; show(); });
  }

  function set(patch: Partial<RankState>): void {
    state = { ...state, ...patch };
    const q = writeRank(state);
    history.replaceState(null, '', `${location.pathname}${q ? `?${q}` : ''}${location.hash}`);
    show();
  }

  root.querySelectorAll<HTMLElement>('[data-seg]').forEach((g) => {
    const name = g.dataset.seg as 'mode' | 'period';
    const h = bindSeg(g, (v) => set(name === 'mode' ? { mode: v as RankState['mode'] } : { period: v as RankState['period'] }));
    h.set(name === 'mode' ? state.mode : state.period);
  });
  body.addEventListener('click', (e) => { if ((e.target as HTMLElement).closest('[data-retry]')) { body.innerHTML = rankSkeleton(ctx); load(); } });

  // hover/focus: the connector above the row becomes the "travelled" part and the node lights up
  const travel = (row: HTMLElement | null): void => {
    const rows = [...body.querySelectorAll<HTMLElement>('.idx-rrow[data-key]')], i = row ? rows.indexOf(row) : -1;
    rows.forEach((r, k) => r.querySelector('.idx-conn')?.classList.toggle('idx-conn--done', k <= i && i >= 0));
    rows.forEach((r) => r.classList.toggle('is-lit', r === row));
  };
  body.addEventListener('pointerover', (e) => travel((e.target as HTMLElement).closest('.idx-rrow[data-key]')));
  body.addEventListener('focusin', (e) => travel((e.target as HTMLElement).closest('.idx-rrow[data-key]')));
  body.addEventListener('pointerleave', () => travel(null));
  body.addEventListener('focusout', () => travel(null));

  if (state.mode !== 'tram' || state.period !== 'day') body.innerHTML = rankSkeleton(ctx);
  load();
}
