import { tr } from '../i18n';
import { sortRanking } from '../lib/agg';
import { ph } from '../components/common';
import { legend } from '../components/controls';
import { hero, rankCard, rankRows, rule } from '../components/sections';
import type { PageFn } from './site';

/** `/` : hero, ranking (tram / day prerendered; the client applies ?rodzaj=&pora= and switches without reload), legend. */
export const rankingPage: PageFn = (ctx, site) => {
  const t = tr(ctx);
  const items = sortRanking(site.ranking.tram.day, site.cities);
  return {
    title: t('title.ranking'), description: t('desc.ranking'), page: 'ranking', current: '',
    main: hero(t('rank.eyebrow'), t('rank.h1'), t('rank.lead')) + rule() +
      `<section class="idx-wrap idx-section idx-section--tight"><div class="idx-row">${ph(ctx)}<span class="idx-caption idx-mute">${t('rank.ph.note')}</span></div></section>` +
      `<section class="idx-wrap idx-section idx-section--snug idx-fade" aria-label="${t('rank.eyebrow')}">${rankCard(ctx, 'tram', 'day', rankRows(ctx, items, site.cities))}` +
      `<div class="idx-legend-wrap">${legend(ctx)}</div></section>`,
  };
};
