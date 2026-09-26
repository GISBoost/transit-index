import React, { useState } from 'react';
import { Icon } from '../core/Icon.jsx';
export function Checkbox({ label, checked, defaultChecked=false, onChange, disabled=false, style }) {
  const [inner,setInner]=useState(defaultChecked); const on=checked!==undefined?checked:inner;
  const toggle=()=>{if(disabled)return; const n=!on; if(checked===undefined)setInner(n); onChange&&onChange(n);};
  return <label style={{display:'inline-flex',alignItems:'center',gap:10,cursor:disabled?'not-allowed':'pointer',opacity:disabled?0.45:1,fontFamily:'var(--font-sans)',fontSize:15,color:'var(--ink)',...style}}>
    <span role="checkbox" aria-checked={on} tabIndex={0} onClick={toggle} onKeyDown={e=>{if(e.key===' '){e.preventDefault();toggle();}}}
      style={{width:22,height:22,boxSizing:'border-box',border:'var(--border-w) solid var(--ink)',background:on?'var(--ink)':'var(--white)',display:'inline-flex',alignItems:'center',justifyContent:'center',color:'var(--paper)',transition:'background var(--dur-fast) var(--ease-transit)',flexShrink:0}}>{on&&<Icon name="check" size={18}/>}</span>
    {label&&<span onClick={toggle}>{label}</span>}
  </label>;
}
