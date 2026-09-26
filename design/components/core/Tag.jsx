import React from 'react';
import { resolveLine } from '../transit/LineBullet.jsx';
export function Tag({ children, line, variant='outline', style }) {
  const c=line?resolveLine(line):null; const solid=variant==='solid'||!!c;
  const bg=c?c.bg:solid?'var(--ink)':'transparent'; const fg=c?c.fg:solid?'var(--paper)':'var(--ink)';
  return <span style={{display:'inline-flex',alignItems:'center',gap:6,height:24,padding:'0 8px',boxSizing:'border-box',background:bg,color:fg,border:'var(--border-w) solid '+(c?c.bg:'var(--ink)'),borderRadius:'var(--radius-0)',fontFamily:'var(--font-sans)',fontSize:11,fontWeight:700,letterSpacing:'var(--tracking-caps)',textTransform:'uppercase',lineHeight:1,whiteSpace:'nowrap',...style}}>{children}</span>;
}
