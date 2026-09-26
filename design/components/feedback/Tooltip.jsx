import React, { useState } from 'react';
export function Tooltip({ content, children, placement='top' }) {
  const [show,setShow]=useState(false); const top=placement==='top';
  return <span onMouseEnter={()=>setShow(true)} onMouseLeave={()=>setShow(false)} onFocus={()=>setShow(true)} onBlur={()=>setShow(false)} style={{position:'relative',display:'inline-flex'}}>
    {children}
    {show&&<span role="tooltip" style={{position:'absolute',left:'50%',transform:'translateX(-50%)',[top?'bottom':'top']:'calc(100% + 8px)',background:'var(--ink)',color:'var(--paper)',fontFamily:'var(--font-sans)',fontSize:13,fontWeight:400,lineHeight:1.2,padding:'6px 10px',whiteSpace:'nowrap',zIndex:50,pointerEvents:'none'}}>
      {content}<span style={{position:'absolute',left:'50%',[top?'bottom':'top']:-4,width:8,height:8,background:'var(--ink)',transform:'translateX(-50%) rotate(45deg)'}}></span>
    </span>}
  </span>;
}
