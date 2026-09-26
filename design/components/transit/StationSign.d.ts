/**
 * @startingPoint section="Transit" subtitle="Dark station sign with line bullets and exit strip" viewport="420x320"
 */
export interface StationSignProps {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  /** Lines serving the station */
  lines?: { label: string; line: string }[];
  metaLeft?: React.ReactNode;
  metaRight?: React.ReactNode;
  /** Text for the exit strip (strip hidden if omitted) */
  exit?: React.ReactNode;
  exitLines?: { label: string; line: string }[];
  /** Material Symbols arrow name, e.g. north_west, north_east, east */
  exitDirection?: string;
  size?: 'md' | 'lg';
  style?: React.CSSProperties;
}
export declare function StationSign(props: StationSignProps): JSX.Element;
