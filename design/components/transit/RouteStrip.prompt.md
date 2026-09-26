Linear route diagram — one colored line, stops as white discs, interchanges as ink-ringed discs with bullets.
```jsx
<RouteStrip line="red" current={2} stops={[
  {name:'Kabaty',terminus:true},{name:'Natolin'},{name:'Centrum',lines:[{label:'M2',line:'yellow'}]},{name:'Młociny',terminus:true}]} />
```
`labelAngle={-40}` = diagonal labels (classic diagram); `0` = labels below for narrow widths.
