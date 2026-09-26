Parallel-line bundle with constant-radius concentric bends and paper casing — the brand's core motif (decoration only).
```jsx
<LineBundle points={[[0,40],[200,40],[280,120],[280,300]]} lines={['vermilion','orange','yellow']} />
<svg viewBox="0 0 400 300"><LineBundle as="g" points={a} lines={['sky','blue']}/><LineBundle as="g" points={b} lines={['vermilion']}/></svg>
```
Never draw bundle paths by hand: use `TransitGeometry.bundle(points, offsets, radius)`. Later bundles pass over earlier ones; their casing cuts the gap.
