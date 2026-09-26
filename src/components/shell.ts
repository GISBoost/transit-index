/** Page chrome: TopBar (+ LangSwitch + theme toggle) and Footer. */
import { tr, url, type Ctx, type Lang } from '../i18n';
import { icon } from '../lib/idx';

export const NAV: { route: string; key: string }[] = [
  { route: '', key: 'nav.ranking' },
  { route: 'mapa', key: 'nav.map' },
  { route: 'dane', key: 'nav.data' },
  { route: 'metodyka', key: 'nav.method' },
  { route: 'jakosc-danych', key: 'nav.quality' },
  { route: 'archiwum', key: 'nav.archive' },
];

/** LangSwitch: two 44 px positions, active = aria-pressed (underlined, not colour alone). Wired in src/client/lang.ts. */
export const langSwitch = (ctx: Ctx, chrome: boolean): string => {
  const t = tr(ctx);
  const btn = (l: Lang) => `<button type="button" aria-pressed="${ctx.lang === l}" lang="${l}" data-lang="${l}">${l.toUpperCase()}</button>`;
  return `<div class="idx-lang${chrome ? ' idx-lang--chrome' : ''}" role="group" aria-label="${t('lang.aria')}">${btn('pl')}<span class="idx-lang__sep" aria-hidden="true"></span>${btn('en')}</div>`;
};

/** `current` is a nav route; `section` marks it as the current section instead of the current page (city pages). */
export function topbar(ctx: Ctx, current: string | null, section = false): string {
  const t = tr(ctx);
  const links = NAV.map((n) => {
    const on = n.route === current;
    return `<a class="idx-topbar__link" href="${url(ctx, n.route)}"${on ? ` aria-current="${section ? 'true' : 'page'}"` : ''}>${t(n.key)}</a>`;
  }).join('');
  return `<header class="idx-topbar" data-topbar><div class="idx-topbar__brand"><a class="idx-topbar__mark" href="https://gisboost.github.io/">GISBoost</a><a class="idx-topbar__sub" href="${url(ctx, '')}">${t('site.sub')}</a></div>` +
    `<nav class="idx-topbar__nav" aria-label="${t('nav.aria')}" data-nav>${links}<button type="button" class="idx-topbar__link" data-theme-toggle aria-pressed="false">${t('nav.theme')}</button>${langSwitch(ctx, true)}<span class="idx-topbar__ind" aria-hidden="true" data-ind></span></nav></header>`;
}

export function footer(ctx: Ctx): string {
  const t = tr(ctx);
  return `<footer class="idx-footer"><div class="idx-wrap"><div class="idx-footer__cols">` +
    `<div><p class="idx-display-sm" style="color: var(--ink)">${t('site.name')}</p><p class="idx-ui" style="margin-top: var(--idx-space-2); max-width: 32ch">${t('footer.about')}</p><div style="margin-top: var(--idx-space-4)">${langSwitch(ctx, false)}</div></div>` +
    `<div><h2 class="idx-ui-strong">${t('footer.data')}</h2><ul class="idx-ui"><li><a href="https://www.openstreetmap.org/copyright">${t('footer.osm')}</a></li><li><a href="https://opendatacommons.org/licenses/odbl/1-0/">${t('footer.odbl')}</a></li><li>${t('footer.operators')}</li></ul></div>` +
    `<div><h2 class="idx-ui-strong">${t('footer.project')}</h2><ul class="idx-ui"><li><a href="${url(ctx, 'metodyka')}">${t('nav.method')}</a></li><li><a href="${url(ctx, 'jakosc-danych')}">${t('nav.quality')}</a></li><li><a href="${url(ctx, 'archiwum')}">${t('footer.archive')}</a></li><li><a href="https://gisboost.github.io/">GISBoost ${icon('external', 16)}</a></li></ul></div>` +
    `</div><p class="idx-caption" style="margin-top: var(--idx-space-6)">${t('footer.author')}</p></div></footer>`;
}
