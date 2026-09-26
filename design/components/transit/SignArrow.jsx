import React from 'react';
import { resolveLine } from './LineBullet.jsx';
import { Icon } from '../core/Icon.jsx';
const DIR={n:'north',ne:'north_east',e:'east',se:'south_east',s:'south',sw:'south_west',w:'west',nw:'north_west'};
export function SignArrow({ direction='ne', line='yellow', size=96, arrowColor, style }) {
  const c=resolveLine(line);
  return <span role="img" aria-label={'Arrow '+direction} style={{width:size,height:size,borderRadius:'50%',background:c.bg,display:'inline-flex',alignItems:'center',justifyContent:'center',flexShrink:0,...style}}><Icon name={DIR[direction]||direction} size={Math.round(size*0.7)} color={arrowColor||c.fg}/></span>;
}
