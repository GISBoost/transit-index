import React from 'react';
export function SpeedLegend({ title='Prędkość', unit='km/h', labels=['< 10','10–14','14–18','18–22','> 22'], slowLabel='wolniej', fastLabel='szybciej', noDataLabel='brak danych', thinLabel='mała próba', style }) {
  const sw={height:8,width:'100%'};
  const lab={fontFamily:'var(--font-condensed)',fontSize:13,lineHeight:1.1,fontVariantNumeric:'tabular-nums',whiteSpace:'nowrap'};
  return <div style={{fontFamily:'var(--font-sans)',color:'var(--ink)',display:'flex',flexDirection:'column',gap:8,...style}}>
    <div style={{display:'flex',justifyContent:'space-between',alignItems:'baseline',gap:12}}><b style={{fontSize:13}}>{title}</b><span style={{...lab,color:'var(--ink-3)'}}>{unit}</span></div>
    <div style={{display:'flex',gap:16,alignItems:'flex-start',flexWrap:'wrap'}}>
      <div style={{display:'grid',gridTemplateColumns:'repeat('+labels.length+',minmax(44px,1fr))',gap:3,flex:'1 1 240px'}}>
        {labels.map((l,i)=><div key={i} style={{display:'flex',flexDirection:'column',gap:5}}><span style={{...sw,background:'var(--speed-'+(i+1)+')'}}></span><span style={lab}>{l}</span></div>)}
        <span style={{...lab,gridColumn:'1 / span 2',color:'var(--ink-3)'}}>← {slowLabel}</span><span style={{...lab,gridColumn:(labels.length-1)+' / span 2',textAlign:'right',color:'var(--ink-3)'}}>{fastLabel} →</span>
      </div>
      <div style={{display:'flex',gap:12}}>
        <div style={{display:'flex',flexDirection:'column',gap:5,width:64}}><span style={{...sw,background:'var(--speed-nodata)'}}></span><span style={lab}>{noDataLabel}</span></div>
        <div style={{display:'flex',flexDirection:'column',gap:5,width:64}}><span style={{...sw,background:'repeating-linear-gradient(135deg,var(--speed-3) 0 3px,var(--map-base) 3px 6px)',outline:'1px solid var(--speed-3)',outlineOffset:-1}}></span><span style={lab}>{thinLabel}</span></div>
      </div>
    </div>
  </div>;
}
