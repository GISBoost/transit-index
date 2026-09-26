import React, { useState } from 'react';
import { Icon } from './Icon.jsx';
const SIZES = { sm:{h:32,px:12,fs:13,ic:16,gap:6}, md:{h:44,px:18,fs:15,ic:20,gap:8}, lg:{h:56,px:24,fs:18,ic:24,gap:10} };
const VARIANTS = {
  primary:{bg:'var(--ink)',fg:'var(--paper)',bd:'var(--ink)',hbg:'var(--ink-2)',hfg:'var(--paper)',hbd:'var(--ink-2)'},
  accent:{bg:'var(--poster-red)',fg:'#fff',bd:'var(--poster-red)',hbg:'var(--poster-red-dark)',hfg:'#fff',hbd:'var(--poster-red-dark)'},
  secondary:{bg:'transparent',fg:'var(--ink)',bd:'var(--ink)',hbg:'var(--ink)',hfg:'var(--paper)',hbd:'var(--ink)'},
  ghost:{bg:'transparent',fg:'var(--ink)',bd:'transparent',hbg:'var(--paper-2)',hfg:'var(--ink)',hbd:'transparent'},
  inverse:{bg:'var(--paper)',fg:'var(--ink)',bd:'var(--paper)',hbg:'#fff',hfg:'var(--ink)',hbd:'#fff'},
};
export function Button({ children, variant='primary', size='md', iconLeft, iconRight, disabled=false, fullWidth=false, type='button', onClick, style }) {
  const [hover,setHover]=useState(false); const [down,setDown]=useState(false);
  const s=SIZES[size]||SIZES.md; const v=VARIANTS[variant]||VARIANTS.primary; const h=hover&&!disabled;
  return <button type={type} disabled={disabled} onClick={onClick}
    onMouseEnter={()=>setHover(true)} onMouseLeave={()=>{setHover(false);setDown(false);}} onMouseDown={()=>setDown(true)} onMouseUp={()=>setDown(false)}
    style={{display:fullWidth?'flex':'inline-flex',width:fullWidth?'100%':undefined,alignItems:'center',justifyContent:'center',gap:s.gap,height:s.h,padding:'0 '+s.px+'px',boxSizing:'border-box',fontFamily:'var(--font-sans)',fontSize:s.fs,fontWeight:700,letterSpacing:'-0.005em',lineHeight:1,background:h?v.hbg:v.bg,color:h?v.hfg:v.fg,border:'var(--border-w) solid '+(h?v.hbd:v.bd),borderRadius:'var(--radius-0)',cursor:disabled?'not-allowed':'pointer',opacity:disabled?0.4:1,transform:down&&!disabled?'translateY(1px)':'none',transition:'background var(--dur-fast) var(--ease-transit), color var(--dur-fast) var(--ease-transit), border-color var(--dur-fast) var(--ease-transit)',whiteSpace:'nowrap',...style}}>
    {iconLeft&&<Icon name={iconLeft} size={s.ic}/>}{children}{iconRight&&<Icon name={iconRight} size={s.ic}/>}
  </button>;
}
