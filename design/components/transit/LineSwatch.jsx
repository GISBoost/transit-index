import React from 'react';
import { resolveLine } from './LineBullet.jsx';
export function LineSwatch({ line='red', label, marker=false, height=14, labelWidth=88, style }) {
  const c=resolveLine(line);
  return <div style={{display:'flex',alignItems:'center',gap:12,fontFamily:'var(--font-sans)',...style}}>
    {label!=null&&<span style={{width:labelWidth,flexShrink:0,fontSize:13,fontWeight:700,color:'var(--ink)',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{label}</span>}
    <div style={{flex:1,display:'flex',gap:6,height}}>
      <div style={{flex:1,background:c.bg,position:'relative'}}>{marker&&<span style={{position:'absolute',right:8,top:0,bottom:0,width:Math.max(4,Math.round(height*0.55)),background:'var(--ink)'}}></span>}</div>
      <div style={{width:Math.round(height*1.3),background:c.bg}}></div>
    </div>
  </div>;
}
