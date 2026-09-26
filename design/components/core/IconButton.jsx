import React, { useState } from 'react';
import { Icon } from './Icon.jsx';
const SIZES={sm:{d:32,ic:18},md:{d:44,ic:22},lg:{d:56,ic:28}};
const VARIANTS={
  primary:{bg:'var(--ink)',fg:'var(--paper)',bd:'var(--ink)',hbg:'var(--ink-2)',hfg:'var(--paper)'},
  accent:{bg:'var(--poster-red)',fg:'#fff',bd:'var(--poster-red)',hbg:'var(--poster-red-dark)',hfg:'#fff'},
  secondary:{bg:'transparent',fg:'var(--ink)',bd:'var(--ink)',hbg:'var(--ink)',hfg:'var(--paper)'},
  ghost:{bg:'transparent',fg:'var(--ink)',bd:'transparent',hbg:'var(--paper-2)',hfg:'var(--ink)'},
};
export function IconButton({ icon, label, variant='ghost', size='md', shape='square', disabled=false, onClick, style }) {
  const [hover,setHover]=useState(false);
  const s=SIZES[size]||SIZES.md; const v=VARIANTS[variant]||VARIANTS.ghost; const h=hover&&!disabled;
  return <button type="button" aria-label={label} title={label} disabled={disabled} onClick={onClick} onMouseEnter={()=>setHover(true)} onMouseLeave={()=>setHover(false)}
    style={{width:s.d,height:s.d,padding:0,display:'inline-flex',alignItems:'center',justifyContent:'center',boxSizing:'border-box',background:h?v.hbg:v.bg,color:h?v.hfg:v.fg,border:'var(--border-w) solid '+(h&&variant!=='ghost'?v.hbg:v.bd),borderRadius:shape==='circle'?'50%':'var(--radius-0)',cursor:disabled?'not-allowed':'pointer',opacity:disabled?0.4:1,transition:'background var(--dur-fast) var(--ease-transit), color var(--dur-fast) var(--ease-transit)',...style}}>
    <Icon name={icon} size={s.ic}/>
  </button>;
}
