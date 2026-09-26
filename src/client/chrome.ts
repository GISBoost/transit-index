/** Topbar behaviour (sliding current-page indicator, compact on scroll), theme toggle, language switch. */
import { slider, themeVeil } from '../motion';
import { parsePath, type Lang } from '../i18n';

export type Theme = 'light' | 'dark';
export const currentTheme = (): Theme => {
  const t = document.documentElement.dataset.theme;
  return t === 'light' || t === 'dark' ? t : matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const notify = (): void => { document.dispatchEvent(new CustomEvent('idx:theme', { detail: currentTheme() })); };

function initTheme(): void {
  const btn = document.querySelector<HTMLButtonElement>('[data-theme-toggle]');
  const sync = (): void => btn?.setAttribute('aria-pressed', String(currentTheme() === 'dark'));
  sync();
  btn?.addEventListener('click', () => {
    const next: Theme = currentTheme() === 'dark' ? 'light' : 'dark';
    themeVeil(() => {
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem('idx-theme', next); } catch { /* storage may be blocked */ }
      sync(); notify();
    });
  });
  // follow the OS while the user has not chosen
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { if (!document.documentElement.dataset.theme) { sync(); notify(); } });
}

function initLang(base: string, lang: Lang): void {
  document.querySelectorAll<HTMLButtonElement>('button[data-lang]').forEach((b) => {
    b.addEventListener('click', () => {
      const to = b.dataset.lang as Lang;
      try { localStorage.setItem('idx-lang', to); } catch { /* ignore */ }
      if (to === lang) return;
      const { route } = parsePath(location.pathname.slice(base.length - 1));
      location.href = `${base}${to === 'en' ? 'en/' : ''}${route ? `${route}/` : ''}${location.search}${location.hash}`;
    });
  });
  // First visit to a Polish URL by someone who chose English before: follow the stored choice (URL stays the source of truth afterwards).
  try {
    const stored = localStorage.getItem('idx-lang');
    const internal = document.referrer && new URL(document.referrer).origin === location.origin;
    if (stored === 'en' && lang === 'pl' && !internal) {
      const { route } = parsePath(location.pathname.slice(base.length - 1));
      location.replace(`${base}en/${route ? `${route}/` : ''}${location.search}${location.hash}`);
    }
  } catch { /* ignore */ }
}

function initTopbar(): void {
  const bar = document.querySelector<HTMLElement>('[data-topbar]'), nav = document.querySelector<HTMLElement>('[data-nav]'), ind = nav?.querySelector<HTMLElement>('[data-ind]');
  if (!bar || !nav || !ind) return;
  bar.classList.add('idx-topbar--anim');
  const links = (): HTMLElement[] => [...nav.querySelectorAll<HTMLElement>('a.idx-topbar__link')];
  const active = (): HTMLElement | null => links().find((l) => l.hasAttribute('aria-current')) ?? null;
  const cur = links().indexOf(active() as HTMLElement);
  let from: HTMLElement | null = null;
  try {
    const prev = Number(sessionStorage.getItem('idx-nav-prev'));
    if (cur >= 0 && Number.isInteger(prev) && sessionStorage.getItem('idx-nav-prev') != null && prev !== cur) from = links()[prev] ?? null;
    if (cur >= 0) sessionStorage.setItem('idx-nav-prev', String(cur));
  } catch { /* ignore */ }
  slider(nav, ind, links, active, { hover: true, from });
  // compact on scroll: content scales down a little (transform only; the bar keeps its layout height)
  let ticking = false;
  const onScroll = (): void => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { bar.classList.toggle('is-compact', scrollY > 8); ticking = false; });
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

export function initChrome(base: string, lang: Lang): void {
  initTheme(); initLang(base, lang); initTopbar();
}
