import React, { useState } from 'react';
import { resolveLine } from '../transit/LineBullet.jsx';
export function Tabs({ tabs=[], value, defaultValue, onChange, style }) {
  const [inner,setInner]=useState(defaultValue??(tabs[0]&&tabs[0].id)); const cur=value!==undefined?value:inner;
  const [hov,setHov]=useState(null);
  return <div role="tablist" style={{display:'flex',gap:4,boxShadow:'inset 0 calc(-1 * var(--border-w)) 0 var(--ink)',fontFamily:'var(--font-sans)',overflowX:'auto',overflowY:'hidden',...style}}>
    {tabs.map(t=>{const a=t.id===cur; const c=resolveLine(t.line||'ink'); return <button key={t.id} role="tab" aria-selected={a} onClick={()=>{if(value===undefined)setInner(t.id); onChange&&onChange(t.id);}} onMouseEnter={()=>setHov(t.id)} onMouseLeave={()=>setHov(null)}
      style={{position:'relative',background:'transparent',border:0,padding:'12px 16px 14px',fontFamily:'inherit',fontSize:15,fontWeight:700,color:a||hov===t.id?'var(--ink)':'var(--ink-3)',cursor:'pointer',whiteSpace:'nowrap'}}>
      {t.label}<span style={{position:'absolute',left:0,right:0,bottom:0,height:a?6:0,background:c.bg,transition:'height var(--dur-fast) var(--ease-transit)'}}></span>
    </button>;})}
  </div>;
}
