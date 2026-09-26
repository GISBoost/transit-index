import React from 'react';
import { TransitGeometry } from '../transit/LineBundle.jsx';
export const LogoGeometry={
  mark:{box:48,w:6,gap:3,r:22.5,stem:[[16,3],[16,40],[45,40]],offsets:[4.5,-4.5],bar:[[5,12],[31,12]]},
  favicon:{box:16,w:2.5,gap:1.5,r:6.5,stem:[[6,1.5],[6,12.5],[14.75,12.5]],offsets:[2,-2],bar:[[1.5,4.5],[11.5,4.5]]}
};
export function Logo({ variant='lockup', tone='color', size=40, wordmark='Transit Index', credit=false, style }) {
  const uid='tim'+React.useId().replace(/[^a-zA-Z0-9]/g,'');
  const g=size<=20?LogoGeometry.favicon:LogoGeometry.mark;
  const stems=TransitGeometry.bundle(g.stem,g.offsets,g.r), bar=TransitGeometry.path(g.bar,1);
  const c=tone==='mono'?['currentColor','currentColor','currentColor']:['var(--line-black)','var(--line-yellow)','var(--line-vermilion)'];
  const isMark=variant==='mark';
  const mark=<svg width={size} height={size} viewBox={'0 0 '+g.box+' '+g.box} aria-hidden="true" style={{display:'block',flexShrink:0,overflow:'visible'}}>
    <defs><mask id={uid} maskUnits="userSpaceOnUse" x="-2" y="-2" width={g.box+4} height={g.box+4}><rect x="-2" y="-2" width={g.box+4} height={g.box+4} fill="#fff"/><path d={bar} fill="none" stroke="#000" strokeWidth={g.w+2*g.gap} strokeLinecap="round"/></mask></defs>
    <g mask={'url(#'+uid+')'} fill="none" strokeWidth={g.w} strokeLinecap="round" strokeLinejoin="round">{stems.map((d,i)=><path key={i} d={d} style={{stroke:c[i]}}/>)}</g>
    <path d={bar} fill="none" strokeWidth={g.w} strokeLinecap="round" style={{stroke:c[2]}}/>
  </svg>;
  if(isMark) return <span role="img" aria-label={wordmark} style={{display:'inline-flex',color:'var(--ink)',...style}}>{mark}</span>;
  return <span role="img" aria-label={wordmark+(credit?' by GISBoost':'')} style={{display:'inline-flex',alignItems:'center',gap:Math.round(size*0.26),color:'var(--ink)',fontFamily:'var(--font-sans)',...style}}>{mark}
    <span style={{display:'flex',flexDirection:'column',lineHeight:1}}><span style={{fontWeight:700,fontSize:Math.round(size*0.58),letterSpacing:'-0.035em',whiteSpace:'nowrap'}}>{wordmark}</span>
    {credit&&<span style={{fontSize:Math.max(10,Math.round(size*0.24)),marginTop:Math.round(size*0.1),color:'var(--ink-3)',whiteSpace:'nowrap'}}>by GISBoost</span>}</span>
  </span>;
}
