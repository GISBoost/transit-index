export interface RouteStop {
  name: string;
  /** Interchange lines shown as small bullets under the stop */
  lines?: { label: string; line: string }[];
  terminus?: boolean;
}
/**
 * @startingPoint section="Transit" subtitle="Linear route diagram with stops and interchanges" viewport="900x260"
 */
export interface RouteStripProps {
  stops: RouteStop[];
  /** Line color key or CSS color */
  line?: string;
  /** Index of the highlighted (you-are-here) stop */
  current?: number;
  /** -40 (default) for diagonal labels above; 0 for centered labels below */
  labelAngle?: number;
  thickness?: number;
  onStopClick?: (index: number, stop: RouteStop) => void;
  style?: React.CSSProperties;
}
export declare function RouteStrip(props: RouteStripProps): JSX.Element;
