import React from 'react';
import { resolveLine } from './LineBullet.jsx';
function _sub(a,b){return [a[0]-b[0],a[1]-b[1]];}
function _add(a,b){return [a[0]+b[0],a[1]+b[1]];}
function _mul(a,k){return [a[0]*k,a[1]*k];}
function _unit(v){const l=Math.hypot(v[0],v[1])||1;return [v[0]/l,v[1]/l];}
function _dot(a,b){return a[0]*b[0]+a[1]*b[1];}
function _f(n){return Math.round(n*100)/100;}
function _clean(pts){
  const out=[pts[0]];
  for(let i=1;i<pts.length;i++){const p=pts[i],q=out[out.length-1];
    if(Math.hypot(p[0]-q[0],p[1]-q[1])<1e-6) continue;
    if(out.length>=2){const d1=_unit(_sub(q,out[out.length-2])),d2=_unit(_sub(p,q));
      if(Math.abs(d1[0]*d2[1]-d1[1]*d2[0])<1e-6&&_dot(d1,d2)>0){out[out.length-1]=p;continue;}}
    out.push(p);}
  return out;
}
function _angle(d1,d2){return Math.acos(Math.max(-1,Math.min(1,_dot(d1,d2))));}
function _radii(c,radius){
  const rs=[];
  for(let i=1;i<c.length-1;i++){
    const d1=_unit(_sub(c[i],c[i-1])),d2=_unit(_sub(c[i+1],c[i]));const tn=Math.tan(_angle(d1,d2)/2);
    const lp=Math.hypot(..._sub(c[i],c[i-1]))*(i===1?1:0.5),ln=Math.hypot(..._sub(c[i+1],c[i]))*(i===c.length-2?1:0.5);
    const R=Array.isArray(radius)?radius[i-1]:radius; rs.push(tn>1e-6?Math.min(R,Math.min(lp,ln)/tn):R);
  }
  return rs;
}
function _offsetPts(c,o){
  const n=c.length,dirs=[];for(let i=0;i<n-1;i++)dirs.push(_unit(_sub(c[i+1],c[i])));
  const nr=dirs.map(d=>[-d[1],d[0]]);
  return c.map((p,i)=>{if(i===0)return _add(p,_mul(nr[0],o)); if(i===n-1)return _add(p,_mul(nr[n-2],o));
    const m=_add(nr[i-1],nr[i]),k=1+_dot(nr[i-1],nr[i]); return _add(p,_mul(m,o/k));});
}
function _toPath(p,rs){
  let d='M'+_f(p[0][0])+' '+_f(p[0][1]);
  for(let i=1;i<p.length-1;i++){
    const d1=_unit(_sub(p[i],p[i-1])),d2=_unit(_sub(p[i+1],p[i])),th=_angle(d1,d2),r=rs[i-1];
    if(th<1e-4||r<=0){d+=' L'+_f(p[i][0])+' '+_f(p[i][1]);continue;}
    const t=r*Math.tan(th/2),A=_sub(p[i],_mul(d1,t)),B=_add(p[i],_mul(d2,t)),cr=d1[0]*d2[1]-d1[1]*d2[0];
    d+=' L'+_f(A[0])+' '+_f(A[1])+' A'+_f(r)+' '+_f(r)+' 0 0 '+(cr>0?1:0)+' '+_f(B[0])+' '+_f(B[1]);
  }
  const e=p[p.length-1]; return d+' L'+_f(e[0])+' '+_f(e[1]);
}
/* waypoints -> tangent arcs -> per-line offsets. Offsets are along the left normal (-dy,dx); for a downward leg +o = towards -x.
   Arcs of every offset line share the centerline's arc centre, so bundles stay concentric (r - o*side). */
function _bundle(points,offsets,radius){
  const c=_clean(points);if(c.length<2)return offsets.map(()=>'');
  const rs=_radii(c,radius),dirs=[];for(let i=0;i<c.length-1;i++)dirs.push(_unit(_sub(c[i+1],c[i])));
  const nr=dirs.map(d=>[-d[1],d[0]]);
  return offsets.map(o=>{const p=_offsetPts(c,o);const r2=rs.map((r,i)=>{const s=_dot(nr[i],dirs[i+1])>0?1:-1;return Math.max(0.01,r-o*s);});return _toPath(p,r2);});
}
export const TransitGeometry={bundle:(pts,offsets=[0],radius=40)=>_bundle(pts,offsets,radius),path:(pts,radius=40)=>_bundle(pts,[0],radius)[0],offsetPoints:_offsetPts,clean:_clean};

export function LineBundle({ points=[], lines=['vermilion','orange','yellow'], width=10, gap=4, radius, casing=true, casingColor='var(--paper)', viewBox, svgWidth, svgHeight, as='svg', style }) {
  const n=lines.length, s=width+gap, bw=n*width+(n-1)*gap, r=radius??bw*1.6;
  const offs=lines.map((_,j)=>((n-1)/2-j)*s);
  const ds=TransitGeometry.bundle(points,offs,r), cd=TransitGeometry.path(points,r);
  const g=<g fill="none" strokeLinecap="round" strokeLinejoin="round">
    {casing&&<path d={cd} strokeWidth={bw+2*gap} style={{stroke:casingColor}}/>}
    {ds.map((d,j)=><path key={j} d={d} strokeWidth={width} style={{stroke:resolveLine(lines[j]).bg}}/>)}
  </g>;
  if(as==='g') return g;
  let vb=viewBox;
  if(!vb&&points.length){const pad=bw/2+gap;const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);const x0=Math.min(...xs)-pad,y0=Math.min(...ys)-pad;vb=[x0,y0,Math.max(...xs)+pad-x0,Math.max(...ys)+pad-y0].join(' ');}
  return <svg viewBox={vb} width={svgWidth} height={svgHeight} style={{display:'block',overflow:'visible',...style}} aria-hidden="true">{g}</svg>;
}
