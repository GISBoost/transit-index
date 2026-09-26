export interface SignArrowProps {
  direction?: 'n' | 'ne' | 'e' | 'se' | 's' | 'sw' | 'w' | 'nw';
  /** Line color key or CSS color for the disc */
  line?: string;
  size?: number;
  arrowColor?: string;
  style?: React.CSSProperties;
}
export declare function SignArrow(props: SignArrowProps): JSX.Element;
