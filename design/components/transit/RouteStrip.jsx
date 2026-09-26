import React from 'react';
import { resolveLine, LineBullet } from './LineBullet.jsx';
export function RouteStrip({ stops=[], line='vermilion', current=-1, labelAngle=-40, thickness=10, onStopClick, style }) {
  const c=resolveLine(line); const n=Math.max(1,stops.length); const rot=labelAngle!==0; const LH=rot?120:0; const DOT=28;
  return <div style={{position:'relative',display:'grid',gridTemplateColumns:'repeat('+n+',minmax(0,1fr))',fontFamily:'var(--font-condensed)',color:'var(--ink)',...style}}>
    <div style={{position:'absolute',left:'calc(100% / '+(2*n)+')',right:'calc(100% / '+(2*n)+')',top:LH+DOT/2-thickness/2,height:thickness,background:c.bg}}></div>
    {stops.map((s,i)=>{
      const x=!!(s.lines&&s.lines.length); const cur=i===current; const big=x||s.terminus; const d=big?24:16;
      return <div key={i} onClick={onStopClick?()=>onStopClick(i,s):undefined} style={{position:'relative',display:'flex',flexDirection:'column',alignItems:'center',cursor:onStopClick?'pointer':undefined,minWidth:0}}>
        {rot&&<div style={{height:LH,width:'100%',position:'relative'}}><span style={{position:'absolute',left:'50%',bottom:4,transformOrigin:'0 100%',transform:'rotate('+labelAngle+'deg)',whiteSpace:'nowrap',fontSize:13,fontWeight:cur||s.terminus?700:400,paddingLeft:6}}>{s.name}</span></div>}
        <div style={{height:DOT,display:'flex',alignItems:'center'}}><span style={{width:d,height:d,borderRadius:'50%',background:cur?'var(--ink)':'var(--white)',border:(big?4:3)+'px solid '+(big||cur?'var(--ink)':c.bg),boxSizing:'border-box',position:'relative',zIndex:1}}></span></div>
        {!rot&&<span style={{marginTop:6,fontSize:12,fontWeight:cur||s.terminus?700:400,textAlign:'center',textWrap:'balance',lineHeight:1.2,padding:'0 2px'}}>{s.name}</span>}
        {x&&<div style={{display:'flex',gap:3,marginTop:6,flexWrap:'wrap',justifyContent:'center'}}>{s.lines.map((l,j)=><LineBullet key={j} label={l.label} line={l.line} size="xs"/>)}</div>}
      </div>;})}
  </div>;
}
