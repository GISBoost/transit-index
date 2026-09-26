import React from 'react';
import { Icon } from '../core/Icon.jsx';
import { IconButton } from '../core/IconButton.jsx';
const TONES={info:{bg:'var(--line-blue)',fg:'#fff',ic:'info'},success:{bg:'var(--line-green)',fg:'#fff',ic:'check'},warning:{bg:'var(--line-yellow)',fg:'var(--ink)',ic:'warning'},danger:{bg:'var(--poster-red)',fg:'#fff',ic:'block'}};
export function Toast({ tone='info', title, message, action, onClose, style }) {
  const t=TONES[tone]||TONES.info;
  return <div role="status" style={{display:'flex',alignItems:'stretch',background:'var(--ink)',color:'var(--paper)',minWidth:300,maxWidth:460,fontFamily:'var(--font-sans)',...style}}>
    <span style={{width:52,flexShrink:0,background:t.bg,color:t.fg,display:'flex',alignItems:'center',justifyContent:'center'}}><Icon name={t.ic} size={26}/></span>
    <div style={{flex:1,padding:'12px 14px',minWidth:0}}>
      {title&&<div style={{fontWeight:700,fontSize:15,lineHeight:1.25}}>{title}</div>}
      {message&&<div style={{fontSize:14,lineHeight:1.35,marginTop:title?2:0,color:'var(--paper-2)'}}>{message}</div>}
      {action&&<div style={{marginTop:8}}>{action}</div>}
    </div>
    {onClose&&<span style={{padding:6,display:'flex',alignItems:'flex-start'}}><IconButton icon="close" label="Zamknij" size="sm" onClick={onClose} style={{color:'var(--paper)'}}/></span>}
  </div>;
}
