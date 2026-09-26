/** /dane/, /metodyka/, /jakosc-danych/, /archiwum/ and the 404. Method text is a template ("treść wzorcowa"). */
import { esc, tr, url, type Ctx } from '../i18n';
import { getThresholds, icon, speedClass } from '../lib/idx';
import { DEFAULT_CITY, speedOf } from '../lib/agg';
import { cityName, quality, sectionHead } from '../components/common';
import { legend } from '../components/controls';
import { downloadCard, hero, methodNote, networkSvg, rule } from '../components/sections';
import type { PageFn } from './site';

const tpl = (ctx: Ctx): string => `<span class="idx-ph">${tr(ctx)('ph.template')}</span>`;
const section = (inner: string, cls = ''): string => `<section class="idx-wrap idx-section idx-fade ${cls}">${inner}</section>`;

export const dataPage: PageFn = (ctx, site) => {
  const t = tr(ctx), m = site.manifest;
  return {
    title: t('title.data'), description: t('desc.data'), page: 'data', current: 'dane',
    main: hero(t('nav.data'), t('data.h1'), t('data.lead')) + rule() +
      section(`<div class="idx-row">${m.placeholder ? `<span class="idx-ph">${t('ph')}</span>` : ''}<span class="idx-caption idx-mute">${t('data.note')}</span></div>` +
        `<div class="idx-cardgrid idx-block" data-stagger>${m.files.map((f) => downloadCard(ctx, f, m.edition)).join('')}</div>`, 'idx-section--tight'),
  };
};

/** Scrollytelling: pinned schematic network + 3 steps; the camera flight is a transform driven by scroll (motion.css / client). */
function scrolly(ctx: Ctx, svg: string): string {
  const t = tr(ctx);
  const steps = [1, 2, 3].map((n) =>
    `<section class="idx-step${n === 1 ? ' is-active' : ''}" aria-labelledby="st${n}" tabindex="0" data-step="${n - 1}"><span class="idx-conn"><i class="idx-node idx-node--sm"></i></span><div class="idx-step__body"><p class="idx-cap" style="margin: 0">${t('scr.step', { i: n, n: 3 })}</p><h3 id="st${n}" class="idx-display-md" style="margin-top: var(--idx-space-2)">${t(`scr.s${n}.h`)}</h3><p class="idx-body idx-mute" style="margin-top: var(--idx-space-3)">${t(`scr.s${n}.p`)}</p></div></section>`).join('');
  return `<div class="idx-scrolly idx-block" data-scrolly><div class="idx-scrolly__stage"><div class="idx-map idx-map--stage"><div class="idx-fly" data-fly>${svg}</div><p class="idx-caption idx-map__attr"><span class="idx-ph">${t('ph')}</span></p></div></div><div class="idx-scrolly__steps">${steps}</div></div>`;
}

export const methodPage: PageFn = (ctx, site) => {
  const t = tr(ctx);
  const c = site.cities.find((x) => x.slug === DEFAULT_CITY) ?? site.cities[0], fc = site.segments.get(c.slug);
  if (!fc) throw new Error(`missing segments for ${c.slug}`);
  const cls = fc.features.map((f) => speedClass(speedOf(f.properties, 'p50', { hour: null, period: 'day' }, site.manifest.peak_hours)));
  const parts = [1, 2, 3, 4].map((n) => `<div class="idx-method__item"><i class="idx-node idx-node--sm${n === 1 ? ' idx-node--solid' : ''}"></i><div><dt class="idx-body-strong">${t(`mth.s${n}.t`)}</dt><dd class="idx-body idx-mute">${t(`mth.s${n}.d`, { list: getThresholds().join(' / ') })}</dd></div></div>`).join('');
  return {
    title: t('title.method'), description: t('desc.method'), page: 'method', current: 'metodyka',
    main: hero(t('nav.method'), t('mth.h1'), t('mth.lead'), `<p style="margin-top: var(--idx-space-5)">${tpl(ctx)}</p>`) + rule() +
      section(`<div class="idx-read"><dl class="idx-method__list">${parts}</dl></div>`, 'idx-section--tight') +
      section(`<div class="idx-read">${methodNote(ctx, 'full', 'mt')}</div>`) +
      section(sectionHead(t('scr.eyebrow'), t('scr.h2')) + scrolly(ctx, networkSvg(fc, cls, t('scr.map.aria'))) + `<div class="idx-block idx-legend-wrap">${legend(ctx)}</div>`),
  };
};

export const qualityPage: PageFn = (ctx, site) => {
  const t = tr(ctx);
  const states = (['ranked', 'limited', 'out'] as const).map((q) => `<div>${quality(ctx, q)}<p class="idx-caption idx-mute" style="margin-top: var(--idx-space-2)">${t(`qual.${q}`)}</p></div>`).join('');
  const rows = site.cities.map((c) => {
    const hrs = c.hourly.meas.filter((v) => v != null).length;
    return `<tr><td><a href="${url(ctx, `miasto/${c.slug}`)}">${cityName(ctx, c)}</a></td><td>${quality(ctx, c.quality)}</td><td class="is-num">${c.coverage == null ? 'XX' : `${c.coverage} %`}</td><td class="is-num">${hrs} / 24</td><td class="is-num">${c.kpi.n ?? 'XX'}</td></tr>`;
  }).join('');
  return {
    title: t('title.quality'), description: t('desc.quality'), page: 'quality', current: 'jakosc-danych',
    main: hero(t('nav.quality'), t('qual.h1'), t('qual.lead')) + rule() +
      section(`<div class="idx-cardgrid" data-stagger>${states}</div><div class="idx-row idx-block">${site.manifest.placeholder ? `<span class="idx-ph">${t('ph')}</span>` : ''}<span class="idx-caption idx-mute">${t('qual.note')}</span></div>` +
        `<div class="idx-rank idx-block"><div class="idx-table-scroll"><table class="idx-table"><caption>${t('qual.table.caption')}</caption><thead><tr><th scope="col">${t('col.city')}</th><th scope="col">${t('col.state')}</th><th scope="col" class="is-num">${t('col.coverage')}</th><th scope="col" class="is-num">${t('col.hours')}</th><th scope="col" class="is-num">${t('col.sample')}</th></tr></thead><tbody>${rows}</tbody></table></div></div>`, 'idx-section--tight') +
      section(`<div class="idx-read">${methodNote(ctx, 'short')}</div>`),
  };
};

export const archivePage: PageFn = (ctx, site) => {
  const t = tr(ctx), eds = site.manifest.editions;
  const rows = eds.map((e, i) => `<a class="idx-rrow idx-rrow--edition" href="${url(ctx, 'dane')}"><span class="idx-conn${i === 0 ? ' idx-conn--first' : ''}${i === eds.length - 1 ? ' idx-conn--last' : ''}"><i class="idx-node idx-node--sm${e.current ? ' idx-node--solid' : ''}"></i></span><span class="idx-rrow__name"><span class="idx-rrow__city">${t('dl.edition', { e: esc(e.edition) })}</span>${e.current ? `<span class="idx-tag">${t('arch.current')}</span>` : ''}</span><span class="idx-rrow__val idx-label idx-mute">${e.published ? esc(e.published) : 'XXXX-XX-XX'} ${icon('arrow-right', 16)}</span></a>`).join('');
  return {
    title: t('title.archive'), description: t('desc.archive'), page: 'archive', current: 'archiwum',
    main: hero(t('nav.archive'), t('arch.h1'), t('arch.lead')) + rule() +
      section(`<div class="idx-row">${site.manifest.placeholder ? `<span class="idx-ph">${t('ph')}</span>` : ''}</div><div class="idx-rank idx-block idx-read">${rows}</div>`, 'idx-section--tight'),
  };
};

export const notFoundPage: PageFn = (ctx) => {
  const t = tr(ctx);
  return {
    title: t('title.404'), description: t('nf.p'), page: 'notfound', current: null,
    main: hero('404', t('nf.h1'), t('nf.p'), `<p style="margin-top: var(--idx-space-6)"><a class="idx-btn idx-btn--primary" href="${url(ctx, '')}">${t('nf.back')}</a></p>`),
  };
};
