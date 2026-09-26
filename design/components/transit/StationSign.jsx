import React from 'react';
import { LineBullet } from './LineBullet.jsx';
import { Icon } from '../core/Icon.jsx';
export function StationSign({ title, subtitle, lines=[], metaLeft, metaRight, exit, exitLines=[], exitDirection='north_west', size='md', style }) {
  const lg=size==='lg'; const bs=lg?64:44;
  return <div style={{background:'var(--ink)',color:'var(--paper)',borderRadius:'var(--radius-sign)',overflow:'hidden',fontFamily:'var(--font-sans)',...style}}>
    {(metaLeft||metaRight)&&<div style={{display:'flex',justifyContent:'space-between',gap:16,padding:'10px 16px',fontSize:13,borderBottom:'2px solid var(--paper)'}}><span>{metaLeft}</span><span>{metaRight}</span></div>}
    <div style={{padding:lg?'20px 20px 24px':'14px 16px 18px'}}>
      <div style={{fontSize:lg?44:30,fontWeight:400,letterSpacing:'-0.02em',lineHeight:1.05,textWrap:'balance'}}>{title}</div>
      {subtitle&&<div style={{fontSize:lg?20:16,marginTop:6,lineHeight:1.25}}>{subtitle}</div>}
      {lines.length>0&&<div style={{display:'flex',flexWrap:'wrap',gap:lg?8:6,marginTop:lg?20:14}}>{lines.map((l,i)=><LineBullet key={i} label={l.label} line={l.line} size={bs}/>)}</div>}
    </div>
    {exit&&<div style={{display:'flex',alignItems:'stretch',borderTop:'2px solid var(--paper)',background:'var(--paper)',color:'var(--ink)'}}>
      <span style={{display:'flex',alignItems:'center',padding:'0 10px'}}><Icon name={exitDirection} size={24}/></span>
      <span style={{background:'var(--poster-red)',color:'#fff',fontWeight:700,fontSize:22,padding:'6px 12px',letterSpacing:'-0.02em'}}>Exit</span>
      <span style={{flex:1,display:'flex',alignItems:'center',padding:'4px 10px',fontSize:14,lineHeight:1.15}}>{exit}</span>
      {exitLines.length>0&&<span style={{display:'flex',alignItems:'center',gap:3,paddingRight:10}}>{exitLines.map((l,i)=><LineBullet key={i} label={l.label} line={l.line} size="sm"/>)}</span>}
    </div>}
  </div>;
}
