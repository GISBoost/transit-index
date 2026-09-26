# Transit Index Design System

**Transit Index** (working name) is a website that indexes how well public transport *actually* works in about a dozen Polish and European cities. It is computed from vehicle-position data (GTFS-Realtime), not timetables: bus and tram speed, slowdown against fast trips, and reliability. Each edition publishes a city ranking with data-quality flags, a page per city (KPIs, an hourly "scheduled vs measured" speed profile, the slowest stretches), a full-screen map with every stop-to-stop stretch coloured by speed, downloads, a methodology page, a data-quality page and an edition archive.
- **Audience:** urban planners, transport officials, journalists and transit enthusiasts, often arriving on phones from social media.
- **Languages:** Polish and English.
- **Build target:** a static site (Astro, MapLibre, GSAP).
- **Ownership:** a side project of **GISBoost**. The look is deliberately separate from GISBoost's own design; GISBoost appears only as a small "by GISBoost" credit.

**Style:** Polish Poster School (flat colour, confident asymmetry, wit, slightly hand-made secondary elements) combined with classic vector transit-diagram geometry (uniform stroke weight, 0/45/90° only, parallel bundles with paper gaps, route bullets). Data areas stay rigorous and calm.

## Sources
- **Code and design files:** there is no codebase or Figma file yet.
- **Brief:** the product description, font order, colour rules, speed-scale rules, landing-page brief and bend rules all come from the product owner in chat.
- **Moodboard:** style reference only (third-party works, not for reuse), in `assets/reference/`:
  - the METRO Warszawa poster
  - a Vignelli tribute poster
  - the "Life in Transit" poster
  - an NYC signage study
  - Helvetica route bullets
  - a line-colours study (robertaehnelt.de)
  - a subway-lines slide template

## Index
- `styles.css` imports `tokens/fonts.css`, `colors.css` (light and `[data-theme="night"]`), `typography.css`, `spacing.css` and `base.css` (grain, resets).
- `guidelines/` holds the foundation cards: Colors, Type, Spacing, Brand, Night edition.
- `components/` holds the React primitives. Each has a `.d.ts`, a `.prompt.md` and one card per folder.
- `ui_kits/landing/` is the landing-page sample: the scroll journey, PL/EN, day/night. Approved.
- **Planned pages:** the maps (full-screen speed map per city) live on separate pages/tabs, not inside the landing. The landing only teases them.
- `templates/social-card/` is the share card (1200×630 and 1080×1350).
- `assets/logo/` holds the mark, lockup, mono, night and favicon SVGs.
- `assets/reference/` holds the moodboard.
- Also at the root: `thumbnail.html` and `SKILL.md`.

## Components
- **brand/** — Logo
- **core/** — Icon, Button, IconButton, Card, Tag
- **transit/** — LineBundle (+ `TransitGeometry` path generator), LineBullet, LineSwatch, RouteStrip, StationSign, SignArrow
- **data/** — Stat, RankingBar, SpeedLegend
- **forms/** — Input, Select, Checkbox, Radio, Switch
- **navigation/** — Tabs
- **feedback/** — Dialog, Toast, Tooltip

**Intentional additions:** there was no source inventory, so this is a standard set plus brand primitives:
- Icon: a wrapper for Material Symbols.
- LineBundle and TransitGeometry: every line motif goes through the generator.
- Stat, RankingBar and SpeedLegend: the core data surfaces of the site.

## CONTENT FUNDAMENTALS
- **Tone:** precise, honest about limits, no hype. The data are reconstructed, so say so. *"To rekonstrukcja."* / *"It is a reconstruction."*
- **Voice:** a public-information voice. It is short and declarative and uses real units: *"Mediana zmierzonej prędkości, 12 miast."* Impersonal by default. "My/we" is allowed only for the method (*"porównujemy…"*, "we compare").
- **No superlatives or exclamation marks.**
- **No emoji.** Unicode arrows (→ ←) are allowed in text.
- **Casing:** sentence case everywhere. Caps appear only in condensed labels and kickers (`12px bold, +0.08em`): *"03 · RANKING"*, *"MAŁA PRÓBA"*.
- **Numbers:**
  - Always tabular.
  - Polish uses a decimal comma and a thin space for thousands (*17,6 km/h*, *41 200*); English uses *17.6*, *41,200*.
  - The minus sign is `−`, not a hyphen.
  - Ranges use an en dash (*6:00–20:00*).
- **Units:** km/h and %. State the base of every comparison, e.g. *"vs szybkie przejazdy"* (fast trips), never "vs timetable" unless it really is the timetable.
- **Every figure carries its flag:** mała próba / thin sample, luki w danych / feed gaps.
- **Wit** lives in graphics, not in copy: the edition stamp, misregistered print, lines crossing.

## VISUAL FOUNDATIONS
- **Themes:**
  - **Day:** cream paper (`#EFE8D8`) with near-black ink.
  - **Night edition** (`[data-theme="night"]`): deep blue-black `#121827` with cream text.
  - `--paper` and `--ink` are *roles* (ground and figure), so components flip automatically.
  - Body text is ≥4.5:1 in both themes.
- **Line palette** (vermilion, orange, yellow, green, sky, blue, violet, black) is **brand and decoration only; it never encodes data.** Night variants are lighter and ≥3:1 against the night ground; black becomes cream.
- **Speed scale** (`--speed-1` slowest … `--speed-5` fastest) is for data only:
  - It is sequential by lightness, running blue→violet→plum, with no red–green pair.
  - In day, slow is the darkest class; in night, slow is the brightest. The slow end is always the most contrasting.
  - Every class is ≥3:1 against `--map-base` in both themes (the colour cards verify this live).
  - "No data" is a distinct grey (`--speed-nodata`).
  - A thin sample is hatched (diagonal hatch in legends and bars, dashes on map lines).
  - Ranking bars are ink, never rainbow.
- **Type:** Hanken Grotesk, with Archivo Narrow for condensed.
  - Bold 700 for poster headlines (−0.02 to −0.04em); Regular 400 for text; Condensed for labels, route strips, stop names and legends.
  - Only the weights 400 and 700 are used.
  - Figures are tabular (verified live on the Type → Numerals card).
  - Every specimen shows *Zażółć gęślą jaźń, ĄĆĘŁŃÓŚŹŻ*.
- **Line geometry:**
  - Uniform stroke; 0/45/90° only; round caps and joins.
  - Default 10px lines with 4px gaps.
  - The bend radius is 1.6 × bundle width, with **concentric arcs** (r, r+gap, …) so spacing stays constant through bends.
  - Crossings: the upper bundle has a paper-coloured casing that cuts a clean gap into the lower one.
  - All paths come from `TransitGeometry.bundle(waypoints, offsets, radius)`; never draw polylines by hand.
- **Backgrounds:** flat paper plus a subtle **grain overlay in the day theme only** (fixed noise layer, `--grain`). No gradients. The only textures are grain and hatching.
- **Poster devices:**
  - Flat colour fields meeting at hard edges.
  - Asymmetric layouts: content column on the left, line corridor on the right.
  - An edition stamp rotated −9°.
  - An optional vermilion "misregistered" copy behind hero figures.
- **Borders and elevation:** 2px ink rules, and an 8px top rule for headers and sheets. There are no shadows anywhere.
- **Radii:**
  - 0 by default.
  - 12px on signage panels only.
  - Round for bullets, stops and station pills.
- **Cards:** square and flat, with a 2px ink border or 8px top rule, or a solid poster-colour block. Never a coloured left border.
- **Layout:** the content column is `min(56vw, 760px)` from a 6vw gutter. The corridor to the right belongs to the lines. On mobile the lines move into a 48px left gutter.
- **Motion:**
  - Scroll-scrubbed draw-on (GSAP ScrollTrigger) with no scroll-jacking.
  - Only transform, opacity and stroke-dashoffset are animated.
  - `prefers-reduced-motion` gives a static, fully drawn page.
  - UI transitions: 120–200ms `--ease-transit`.
- **States:**
  - Hover: primary buttons darken; outline buttons invert; links turn poster red.
  - Press: 1px nudge.
  - Focus: 2px blue ring.
- **Transparency:** only the modal scrim. No blur.
- **Imagery:** none by default. If photos are used, frame them with a 2px ink border and keep them flat.

## LOGO
- **Selected mark: B "t"** (product-owner decision). Concepts A and C stay in the system as documented alternatives, not for use.
- **"t" in detail:** A 2-line stem bends once to the right with concentric arcs and is crossed once by a vermilion bar with a knocked-out gap. It reads as *t*, *+* or an index mark.
- **Built from the line rules:** same angles, a bend radius of 1.5 × bundle width, and a gap of half the stroke.
- **Favicon:** a separate pixel-fitted 16px geometry, one colour, with gaps as masks (transparent). The favicon SVG follows `prefers-color-scheme`.
- **Files** (`assets/logo/`):
  - `mark.svg`, `mark-night.svg`, `mark-mono.svg`, `mark-mono-cream.svg`
  - `favicon.svg`, `favicon-color.svg`
  - `lockup.svg`, `lockup-night.svg`, `lockup-mono.svg`
- **Lockup text:** it uses live font text; outline it before handing files to print.
- **Alternatives** (the Brand → Logo exploration card): A "Krzyżówka" X and C "Bullet".
- **In code:** `<Logo variant="mark|lockup" tone="color|mono" credit />`.

## ICONOGRAPHY
- **Icon set:** Material Symbols Sharp (CDN), filled, weight 700. This is a substitute; no brand icon set exists.
- **Arrows** on discs (`SignArrow`) are used for wayfinding.
- **Data-quality glyphs:** `texture` (thin sample), `report` (gaps).
- **Never:** emoji, literal buses or trains in brand marks, or PNG icons.

## Fonts — final
- **Chosen:** Hanken Grotesk (OFL, Google Fonts) for display and text, at weights 400 and 700 only; Archivo Narrow (OFL) for condensed labels, stop names and legends.
- **Stack:** `"Hanken Grotesk","Helvetica Neue",Helvetica,Arial,sans-serif` and `"Archivo Narrow",…`.
- TeX Gyre Heros and Nimbus Sans were considered and not used.
