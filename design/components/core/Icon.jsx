import React from 'react';
export function Icon({ name, size = 24, fill = 1, weight = 700, color, title, style }) {
  const opsz = Math.min(48, Math.max(20, size));
  return <span role={title ? 'img' : undefined} aria-label={title} aria-hidden={title ? undefined : 'true'} style={{fontFamily:"'Material Symbols Sharp'",fontWeight:'normal',fontStyle:'normal',fontSize:size,lineHeight:1,width:size,height:size,display:'inline-flex',alignItems:'center',justifyContent:'center',overflow:'hidden',letterSpacing:'normal',textTransform:'none',whiteSpace:'nowrap',direction:'ltr',fontFeatureSettings:"'liga'",WebkitFontSmoothing:'antialiased',fontVariationSettings:"'FILL' "+fill+", 'wght' "+weight+", 'GRAD' 0, 'opsz' "+opsz,color:color||'currentColor',flexShrink:0,userSelect:'none',...style}}>{name}</span>;
}
