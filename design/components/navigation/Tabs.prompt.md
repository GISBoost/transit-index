Horizontal tabs on a 2px ink baseline; active tab gets a 6px line-colored bar.
```jsx
<Tabs tabs={[{id:'lines',label:'Linie'},{id:'map',label:'Schemat'},{id:'stops',label:'Stacje'}]} onChange={setTab} />
```
Give each tab a `line` to color-code by route.
