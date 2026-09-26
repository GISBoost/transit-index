/** Path generator: waypoints (0/45/90°) → tangent arcs → concentric per-line offsets. Exposed on the namespace as TransitGeometry. */
export declare const TransitGeometry: {
  /** One SVG path "d" per offset. Offsets are along the left normal; for a downward leg +o moves towards -x. */
  bundle(points: [number, number][], offsets?: number[], radius?: number | number[]): string[];
  path(points: [number, number][], radius?: number): string;
  offsetPoints(points: [number, number][], offset: number): [number, number][];
  clean(points: [number, number][]): [number, number][];
};
export interface LineBundleProps {
  /** Centerline waypoints; keep segments at 0/45/90° */
  points: [number, number][];
  /** One brand line key (or CSS color) per line, left→right on a downward leg */
  lines?: string[];
  /** Uniform stroke width */
  width?: number;
  /** Paper gap between parallel lines (and casing overhang) */
  gap?: number;
  /** Centerline bend radius; default 1.6 × bundle width */
  radius?: number;
  /** Paper-colored casing under the bundle so it cuts clean gaps into whatever it crosses */
  casing?: boolean;
  casingColor?: string;
  viewBox?: string;
  svgWidth?: number | string;
  svgHeight?: number | string;
  /** 'g' to compose several bundles in one parent <svg> (draw order = z-order) */
  as?: 'svg' | 'g';
  style?: React.CSSProperties;
}
export declare function LineBundle(props: LineBundleProps): JSX.Element;
