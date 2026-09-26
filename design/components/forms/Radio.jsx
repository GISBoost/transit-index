import React from 'react';
export function Radio({ label, checked=false, name, value, onChange, disabled=false, style }) {
  const pick=()=>{if(!disabled&&onChange)onChange(value);};
  return <label style={{display:'inline-flex',alignItems:'center',gap:10,cursor:disabled?'not-allowed':'pointer',opacity:disabled?0.45:1,fontFamily:'var(--font-sans)',fontSize:15,color:'var(--ink)',...style}}>
    <input type="radio" name={name} value={value} checked={checked} onChange={pick} disabled={disabled} style={{position:'absolute',opacity:0,width:0,height:0}}/>
    <span style={{width:22,height:22,borderRadius:'50%',boxSizing:'border-box',border:'3px solid var(--ink)',background:'var(--white)',display:'inline-flex',alignItems:'center',justifyContent:'center',flexShrink:0}}>{checked&&<span style={{width:10,height:10,borderRadius:'50%',background:'var(--ink)'}}></span>}</span>
    {label&&<span>{label}</span>}
  </label>;
}
