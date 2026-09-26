import React from 'react';
export const LINES=['vermilion','orange','yellow','green','sky','blue','violet','black'];
const ALIAS={red:'vermilion',cyan:'sky',ink:'black'};
const DARK=new Set(['yellow','orange','sky']);
export function resolveLine(k){
  if(!k) return {bg:'var(--line-black)',fg:'var(--paper)'};
  const key=ALIAS[k]||k;
  if(key==='black') return {bg:'var(--line-black)',fg:'var(--paper)'};
  if(key==='paper') return {bg:'var(--paper)',fg:'var(--ink)'};
  if(LINES.includes(key)) return {bg:'var(--line-'+key+')',fg:DARK.has(key)?'#1E1D26':'#fff'};
  return {bg:k,fg:'#fff'};
}
const SZ={xs:18,sm:24,md:36,lg:56,xl:96};
export function LineBullet({ label, line='vermilion', size='md', shape='circle', textColor, style }) {
  const d=typeof size==='number'?size:(SZ[size]||36); const c=resolveLine(line); const len=String(label??'').length;
  const fs=Math.round(d*(len>2?0.4:len>1?0.5:0.62));
  const inner=<span style={{fontFamily:'var(--font-sans)',fontWeight:700,fontSize:fs,lineHeight:1,letterSpacing:'-0.02em',fontVariantNumeric:'tabular-nums',color:textColor||c.fg,transform:shape==='diamond'?'rotate(-45deg)':undefined}}>{label}</span>;
  return <span style={{width:shape==='diamond'?d*0.78:d,height:shape==='diamond'?d*0.78:d,margin:shape==='diamond'?d*0.11:0,borderRadius:shape==='circle'?'50%':'var(--radius-0)',transform:shape==='diamond'?'rotate(45deg)':undefined,display:'inline-flex',alignItems:'center',justifyContent:'center',background:c.bg,flexShrink:0,boxSizing:'border-box',...style}}>{inner}</span>;
}
