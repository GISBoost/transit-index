import React, { useEffect } from 'react';
import { IconButton } from '../core/IconButton.jsx';
export function Dialog({ open, onClose, title, children, actions, width=520 }) {
  useEffect(()=>{ if(!open) return; const k=e=>{if(e.key==='Escape'&&onClose)onClose();}; window.addEventListener('keydown',k); return ()=>window.removeEventListener('keydown',k); },[open,onClose]);
  if(!open) return null;
  return <div onClick={onClose} style={{position:'fixed',inset:0,background:'var(--scrim)',display:'flex',alignItems:'center',justifyContent:'center',padding:24,zIndex:1000}}>
    <div role="dialog" aria-modal="true" onClick={e=>e.stopPropagation()} style={{width:'100%',maxWidth:width,background:'var(--paper)',color:'var(--ink)',border:'var(--border-w) solid var(--ink)',borderTop:'var(--rule-w) solid var(--ink)',fontFamily:'var(--font-sans)'}}>
      <div style={{display:'flex',alignItems:'flex-start',justifyContent:'space-between',gap:16,padding:'20px 16px 12px 24px'}}>
        <h2 style={{margin:0,fontSize:26,fontWeight:700,letterSpacing:'-0.02em',lineHeight:1.1}}>{title}</h2>
        {onClose&&<IconButton icon="close" label="Zamknij" onClick={onClose} size="sm"/>}
      </div>
      <div style={{padding:'0 24px 24px',fontSize:16,lineHeight:1.45}}>{children}</div>
      {actions&&<div style={{display:'flex',justifyContent:'flex-end',gap:8,padding:'16px 24px',borderTop:'var(--border-w) solid var(--ink)'}}>{actions}</div>}
    </div>
  </div>;
}
