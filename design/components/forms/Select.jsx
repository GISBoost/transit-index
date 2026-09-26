import React, { useState } from 'react';
import { Icon } from '../core/Icon.jsx';
export function Select({ label, options=[], value, defaultValue, onChange, disabled=false, id, style }) {
  const [focus,setFocus]=useState(false); const fid=id||(label?'sel-'+String(label).replace(/\W+/g,'-').toLowerCase():undefined);
  const bd=focus?'var(--focus-ring)':'var(--ink)';
  return <div style={{display:'flex',flexDirection:'column',gap:6,fontFamily:'var(--font-sans)',opacity:disabled?0.45:1,...style}}>
    {label&&<label htmlFor={fid} style={{fontSize:13,fontWeight:700}}>{label}</label>}
    <div style={{position:'relative'}}>
      <select id={fid} value={value} defaultValue={defaultValue} onChange={onChange} disabled={disabled} onFocus={()=>setFocus(true)} onBlur={()=>setFocus(false)}
        style={{appearance:'none',WebkitAppearance:'none',width:'100%',height:44,padding:'0 40px 0 12px',background:'var(--white)',border:'var(--border-w) solid '+bd,boxShadow:focus?'0 0 0 2px '+bd:'none',borderRadius:0,fontFamily:'inherit',fontSize:16,color:'var(--ink)',outline:0,cursor:'pointer'}}>
        {options.map(o=>{const v=typeof o==='string'?o:o.value; const l=typeof o==='string'?o:o.label; return <option key={v} value={v}>{l}</option>;})}
      </select>
      <span style={{position:'absolute',right:10,top:0,bottom:0,display:'flex',alignItems:'center',pointerEvents:'none'}}><Icon name="expand_more" size={22}/></span>
    </div>
  </div>;
}
