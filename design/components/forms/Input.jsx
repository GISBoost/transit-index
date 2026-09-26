import React, { useState } from 'react';
import { Icon } from '../core/Icon.jsx';
export function Input({ label, value, defaultValue, placeholder, onChange, hint, error, disabled=false, iconLeft, type='text', id, style }) {
  const [focus,setFocus]=useState(false); const fid=id||(label?'in-'+String(label).replace(/\W+/g,'-').toLowerCase():undefined);
  const bd=error?'var(--danger)':focus?'var(--focus-ring)':'var(--ink)';
  return <div style={{display:'flex',flexDirection:'column',gap:6,fontFamily:'var(--font-sans)',opacity:disabled?0.45:1,...style}}>
    {label&&<label htmlFor={fid} style={{fontSize:13,fontWeight:700,color:'var(--ink)'}}>{label}</label>}
    <div style={{display:'flex',alignItems:'center',gap:8,height:44,padding:'0 12px',boxSizing:'border-box',background:'var(--white)',border:'var(--border-w) solid '+bd,boxShadow:focus?'0 0 0 2px '+bd:'none',transition:'box-shadow var(--dur-fast) var(--ease-transit)'}}>
      {iconLeft&&<Icon name={iconLeft} size={20} color="var(--ink-3)"/>}
      <input id={fid} type={type} value={value} defaultValue={defaultValue} placeholder={placeholder} disabled={disabled} onChange={onChange} onFocus={()=>setFocus(true)} onBlur={()=>setFocus(false)}
        style={{flex:1,minWidth:0,border:0,outline:0,background:'transparent',fontFamily:'inherit',fontSize:16,color:'var(--ink)',height:'100%',padding:0}}/>
    </div>
    {(error||hint)&&<span style={{fontSize:13,color:error?'var(--danger)':'var(--text-muted)'}}>{error||hint}</span>}
  </div>;
}
