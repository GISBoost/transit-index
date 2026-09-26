import React, { useState } from 'react';
import { resolveLine } from '../transit/LineBullet.jsx';
export function Switch({ label, checked, defaultChecked=false, onChange, line='green', disabled=false, style }) {
  const [inner,setInner]=useState(defaultChecked); const on=checked!==undefined?checked:inner; const c=resolveLine(line);
  const toggle=()=>{if(disabled)return; const n=!on; if(checked===undefined)setInner(n); onChange&&onChange(n);};
  return <label style={{display:'inline-flex',alignItems:'center',gap:10,cursor:disabled?'not-allowed':'pointer',opacity:disabled?0.45:1,fontFamily:'var(--font-sans)',fontSize:15,color:'var(--ink)',...style}}>
    <span role="switch" aria-checked={on} tabIndex={0} onClick={toggle} onKeyDown={e=>{if(e.key===' '){e.preventDefault();toggle();}}} style={{position:'relative',width:48,height:24,flexShrink:0}}>
      <span style={{position:'absolute',left:4,right:4,top:8,height:8,background:on?c.bg:'var(--paper-3)',transition:'background var(--dur-base) var(--ease-transit)'}}></span>
      <span style={{position:'absolute',top:0,left:on?24:0,width:24,height:24,borderRadius:'50%',boxSizing:'border-box',background:on?'var(--ink)':'var(--white)',border:'4px solid var(--ink)',transition:'left var(--dur-base) var(--ease-transit), background var(--dur-base) var(--ease-transit)'}}></span>
    </span>
    {label&&<span onClick={toggle}>{label}</span>}
  </label>;
}
