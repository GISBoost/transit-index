Station-disc radio button (white disc, ink ring, ink dot when picked). Compose several with a shared `name`.
```jsx
{['Najszybsza','Najmniej przesiadek'].map(o=><Radio key={o} name="route" value={o} label={o} checked={v===o} onChange={setV}/>)}
```
