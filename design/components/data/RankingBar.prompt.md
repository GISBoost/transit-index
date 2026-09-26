One row of the city ranking: rank, city, data-quality flag, ink bar (length = value), tabular value.
```jsx
<RankingBar rank={1} label="Praga" value={20.8} max={24} />
<RankingBar rank={11} label="Wilno" value={15.8} max={24} flag="thin" flagLabel="mała próba" />
```
Bars carry `data-bar` so pages can animate `scaleX` on view. Bars are ink — never rainbow.
