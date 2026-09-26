export interface SpeedLegendProps {
  title?: string;
  unit?: string;
  /** Exactly one label per speed class, slowest → fastest (maps to --speed-1 … --speed-5) */
  labels?: string[];
  slowLabel?: string;
  fastLabel?: string;
  noDataLabel?: string;
  /** Label for hatched (thin-sample) stretches */
  thinLabel?: string;
  style?: React.CSSProperties;
}
export declare function SpeedLegend(props: SpeedLegendProps): JSX.Element;
