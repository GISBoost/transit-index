import React from 'react';
import { Icon } from '../core/Icon.jsx';
export function RankingBar({ rank, label, value, max=25, unit='km/h', decimals=1, locale='pl', flag, flagLabel, highlight=false, onClick, style }) {
  const fmt=(value==null?'—':Number(value).toLocaleString(locale==='en'?'en-GB':'pl-PL',{minimumFractionDigits:decimals,maximumFractionDigits:decimals}));
  const pct=value==null?0:Math.max(0,Math.min(1,value/max))*100;
  const thin=flag==='thin';
  const barBg=thin?'repeating-linear-gradient(135deg,var(--ink) 0 3px,transparent 3px 6px)':(highlight?'var(--accent)':'var(--ink)');
  return <div onClick={onClick} style={{display:'grid',gridTemplateColumns:'32px minmax(96px,160px) minmax(0,1fr) 88px',alignItems:'center',gap:12,padding:'8px 0',borderBottom:'1px solid var(--border-subtle)',fontFamily:'var(--font-sans)',color:'var(--ink)',cursor:onClick?'pointer':undefined,...style}}>
    <span style={{fontFamily:'var(--font-condensed)',fontWeight:700,fontSize:15,fontVariantNumeric:'tabular-nums',color:'var(--ink-3)'}}>{String(rank).padStart(2,'0')}</span>
    <span style={{display:'flex',alignItems:'center',gap:6,minWidth:0}}><span style={{fontWeight:700,fontSize:17,letterSpacing:'-0.01em',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{label}</span>
      {flag&&<span title={flagLabel} style={{display:'inline-flex',alignItems:'center',gap:2,fontFamily:'var(--font-condensed)',fontSize:11,fontWeight:700,textTransform:'uppercase',letterSpacing:'.06em',color:'var(--ink-3)',whiteSpace:'nowrap'}}><Icon name={flag==='thin'?'texture':'report'} size={14}/>{flagLabel}</span>}</span>
    <span style={{height:14,position:'relative',background:'transparent'}}><span data-bar="" style={{position:'absolute',left:0,top:0,bottom:0,width:pct+'%',background:barBg,outline:thin?'2px solid var(--ink)':'none',outlineOffset:-2,transformOrigin:'0 50%'}}></span></span>
    <span style={{textAlign:'right',fontVariantNumeric:'tabular-nums',whiteSpace:'nowrap'}}><b style={{fontSize:18}}>{fmt}</b> <span style={{fontSize:12,color:'var(--ink-3)'}}>{unit}</span></span>
  </div>;
}
