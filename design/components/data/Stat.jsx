import React from 'react';
const SZ={md:{v:48,u:18,l:14},lg:{v:96,u:28,l:16},xl:{v:200,u:44,l:18}};
export function Stat({ value, unit, label, size='lg', misregister=false, style }) {
  const s=SZ[size]||SZ.lg;
  const num={fontWeight:700,fontSize:'min('+s.v+'px, '+(s.v/9.6)+'vw + 24px)',lineHeight:.88,letterSpacing:'-0.045em',fontVariantNumeric:'tabular-nums',whiteSpace:'nowrap'};
  return <div style={{fontFamily:'var(--font-sans)',color:'var(--ink)',display:'flex',flexDirection:'column',gap:10,...style}}>
    <div style={{display:'flex',alignItems:'baseline',gap:Math.round(s.u*0.4)}}>
      <span style={{position:'relative',display:'inline-block'}}>
        {misregister&&<span aria-hidden="true" style={{...num,position:'absolute',left:'0.035em',top:'0.03em',color:'var(--poster-red)'}}>{value}</span>}
        <span style={{...num,position:'relative'}}>{value}</span>
      </span>
      {unit&&<span style={{fontSize:s.u,fontWeight:700,letterSpacing:'-0.02em'}}>{unit}</span>}
    </div>
    {label&&<div style={{fontSize:s.l,lineHeight:1.4,maxWidth:420,textWrap:'pretty'}}>{label}</div>}
  </div>;
}
