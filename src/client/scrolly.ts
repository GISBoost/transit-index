/** Scrollytelling: steps are activated by IntersectionObserver (never by taking over the scroll). The camera flight is a
 *  transform driven by scroll: CSS animation-timeline where supported (motion.css), otherwise GSAP ScrollTrigger scrubbing
 *  the same transform (no jumps, no pinning that blocks scrolling). */
import { reduced } from '../motion';

const FLIGHT = [
  { scale: 1, xPercent: 0, yPercent: 0 },
  { scale: 1.55, xPercent: -6, yPercent: 4 },
  { scale: 1.2, xPercent: 5, yPercent: -3 },
];

export function initScrolly(): void {
  const root = document.querySelector<HTMLElement>('[data-scrolly]');
  if (!root) return;
  const steps = [...root.querySelectorAll<HTMLElement>('.idx-step')], map = root.querySelector<HTMLElement>('.idx-map'), fly = root.querySelector<HTMLElement>('[data-fly]');
  if (!steps.length || !map || !fly) return;

  const activate = (i: number): void => {
    steps.forEach((s, k) => { s.classList.toggle('is-active', k === i); s.classList.toggle('is-done', k < i); });
    fly.querySelectorAll<SVGElement>('.m-seg').forEach((s) => {
      const c = s.getAttribute('data-cls');
      s.classList.toggle('on', i === 0 || (i === 1 && (c === '1' || c === '2')) || (i === 2 && c === 'nd'));
    });
    map.classList.toggle('is-dim', i > 0);
  };
  activate(0);
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((es) => { for (const e of es) if (e.isIntersecting) activate(steps.indexOf(e.target as HTMLElement)); }, { rootMargin: '-40% 0px -40% 0px', threshold: 0 });
    steps.forEach((s) => io.observe(s));
  }
  steps.forEach((s, i) => s.addEventListener('focus', () => activate(i)));
  root.classList.add('is-enhanced');

  if (reduced() || CSS.supports('animation-timeline: view()')) return; // CSS does it (or nothing, under reduced motion)
  void (async () => {
    const [{ gsap }, { ScrollTrigger }] = await Promise.all([import('gsap'), import('gsap/ScrollTrigger')]);
    gsap.registerPlugin(ScrollTrigger);
    gsap.fromTo(fly, FLIGHT[0], { scale: FLIGHT[1].scale, xPercent: FLIGHT[1].xPercent, yPercent: FLIGHT[1].yPercent, ease: 'none', scrollTrigger: { trigger: root, start: 'top 60%', end: 'center 40%', scrub: true } });
    gsap.to(fly, { scale: FLIGHT[2].scale, xPercent: FLIGHT[2].xPercent, yPercent: FLIGHT[2].yPercent, ease: 'none', scrollTrigger: { trigger: root, start: 'center 40%', end: 'bottom 70%', scrub: true } });
  })();
}
