/** Behaviour of SegmentedControl (radiogroup with arrow keys + sliding indicator). */
import { slider } from '../motion';

export interface SegHandle { set(value: string, silent?: boolean): void; value(): string | null; clear(): void }

export function bindSeg(group: HTMLElement, onChange: (value: string) => void): SegHandle {
  const opts = (): HTMLButtonElement[] => [...group.querySelectorAll<HTMLButtonElement>('[role="radio"]')];
  const checked = (): HTMLButtonElement | null => opts().find((o) => o.getAttribute('aria-checked') === 'true') ?? null;
  group.classList.add('idx-seg--anim');
  const ind = document.createElement('span');
  ind.className = 'idx-seg__ind'; ind.setAttribute('aria-hidden', 'true');
  group.prepend(ind);
  const sl = slider(group, ind, opts, checked);

  const select = (o: HTMLButtonElement, fire: boolean): void => {
    for (const x of opts()) { const on = x === o; x.setAttribute('aria-checked', String(on)); x.tabIndex = on ? 0 : -1; }
    sl.sync(true);
    if (fire) onChange(o.dataset.v as string);
  };
  group.addEventListener('click', (e) => {
    const o = (e.target as HTMLElement).closest<HTMLButtonElement>('[role="radio"]');
    if (o && o !== checked()) select(o, true);
  });
  group.addEventListener('keydown', (e) => {
    const list = opts(), i = list.indexOf(document.activeElement as HTMLButtonElement);
    if (i < 0) return;
    const step = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0;
    const to = e.key === 'Home' ? 0 : e.key === 'End' ? list.length - 1 : step ? (i + step + list.length) % list.length : -1;
    if (to < 0) return;
    e.preventDefault();
    select(list[to], true);
    list[to].focus();
  });
  return {
    set(value, silent = true) {
      const o = opts().find((x) => x.dataset.v === value);
      if (o) select(o, !silent);
    },
    value: () => checked()?.dataset.v ?? null,
    clear() { for (const x of opts()) { x.setAttribute('aria-checked', 'false'); x.tabIndex = -1; } opts()[0].tabIndex = 0; sl.sync(true); },
  };
}
