# Transit Index — landing page sample
Scroll journey: a 5-line bundle (A: vermilion/orange/yellow, B: sky/blue) enters the hero from the right, then travels down the page through a station node at each section. Between stations the two sub-bundles split, swing across the corridor with different phase (so they cross over/under with paper casings), and merge again. Lines end at the footer terminus.

- `journey.js` — builds the SVG from DOM station positions with `TransitGeometry` (waypoints → tangent arcs → concentric offsets), animates `stroke-dashoffset` scrubbed by GSAP ScrollTrigger, plus a head (transform/opacity only). Rebuilds on resize, font load and language change. Z-order alternates per segment. Mobile (<~1000px corridor): thin bundle in a left gutter, no swings.
- `prefers-reduced-motion` or no GSAP → static, fully drawn composition. No scroll-jacking; native scroll only.
- `Sections.jsx` — Header, Hero (big speed number + edition stamp), The number (stretch strip + KPIs), Ranking (bars grow on view), Map teaser (schematic stretches in the speed scale + legend), Honest limits, Footer.
- `copy.js` — PL/EN copy and illustrative data. **All numbers are placeholders.**
- Theme toggle (day / night edition) and PL/EN persist in localStorage.
Production target: Astro + MapLibre + GSAP; this sample is React-in-browser for prototyping only.
