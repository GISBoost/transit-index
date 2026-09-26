/** Table view of the map: the always-available equivalent of the map (aria-pressed toggle "Widok tabeli"). */
import { esc, tr, type Ctx } from '../i18n';
import { num, type SpeedClass } from '../lib/idx';
import { classRange } from './controls';
import { lineBadge } from './common';

export interface TableRow { id: string; route: string | null; from: string; to: string; v: number | null; cls: SpeedClass }

export function classLabel(ctx: Ctx, c: SpeedClass): string {
  const t = tr(ctx);
  return c === 'nd' ? t('map.cls.nd') : t('map.cls.n', { n: c, range: classRange(ctx, c) });
}

export function mapTable(ctx: Ctx, rows: TableRow[]): string {
  const t = tr(ctx);
  const body = rows.map((r, i) =>
    `<tr data-id="${esc(r.id)}"><td class="idx-label">${i + 1}</td><td>${esc(r.from)} → ${esc(r.to)}</td><td>${lineBadge(r.route)}</td>` +
    `<td class="is-num">${r.v == null ? '—' : num(r.v, 1, ctx.lang)}</td><td>${classLabel(ctx, r.cls)}</td></tr>`).join('');
  return `<div class="idx-table-scroll"><table class="idx-table"><caption>${t('map.table.caption')}</caption><thead><tr><th scope="col">#</th><th scope="col">${t('col.segment')}</th><th scope="col">${t('col.line')}</th><th scope="col" class="is-num">${t('unit.kmh')}</th><th scope="col">${t('col.class')}</th></tr></thead><tbody>${body}</tbody></table></div>`;
}
