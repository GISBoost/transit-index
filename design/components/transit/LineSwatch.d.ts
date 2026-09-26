export interface LineSwatchProps {
  /** Line color key or CSS color */
  line?: string;
  label?: React.ReactNode;
  /** Black tick near the end — marks a branch / terminus variant */
  marker?: boolean;
  height?: number;
  labelWidth?: number;
  style?: React.CSSProperties;
}
export declare function LineSwatch(props: LineSwatchProps): JSX.Element;
