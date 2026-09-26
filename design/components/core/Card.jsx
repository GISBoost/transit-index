import React from 'react';
const SURF={
  white:{bg:'var(--white)',fg:'var(--ink)',bd:'var(--border-w) solid var(--ink)',r:'var(--radius-0)',rule:'var(--ink)'},
  paper:{bg:'var(--paper-2)',fg:'var(--ink)',bd:'none',r:'var(--radius-0)',rule:'var(--ink)'},
  outline:{bg:'transparent',fg:'var(--ink)',bd:'var(--border-w) solid var(--ink)',r:'var(--radius-0)',rule:'var(--ink)'},
  sign:{bg:'var(--ink)',fg:'var(--paper)',bd:'none',r:'var(--radius-sign)',rule:'var(--paper)'},
  red:{bg:'var(--poster-red)',fg:'#fff',bd:'none',r:'var(--radius-0)',rule:'var(--ink)'},
  petrol:{bg:'var(--poster-petrol)',fg:'#fff',bd:'none',r:'var(--radius-0)',rule:'var(--ink)'},
  mustard:{bg:'var(--poster-mustard)',fg:'var(--ink)',bd:'none',r:'var(--radius-0)',rule:'var(--ink)'},
};
export function Card({ children, surface='white', rule=false, padding=24, onClick, style }) {
  const s=SURF[surface]||SURF.white;
  return <div onClick={onClick} style={{background:s.bg,color:s.fg,border:s.bd,borderTop:rule?'var(--rule-w) solid '+s.rule:undefined,borderRadius:s.r,padding,boxSizing:'border-box',cursor:onClick?'pointer':undefined,fontFamily:'var(--font-sans)',...style}}>{children}</div>;
}
