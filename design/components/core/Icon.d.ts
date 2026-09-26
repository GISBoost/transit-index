export interface IconProps {
  /** Material Symbols (Sharp) ligature name, e.g. "north_east", "train", "search" */
  name: string;
  size?: number;
  /** 1 = filled (default, signage), 0 = outline */
  fill?: 0 | 1;
  weight?: 100 | 200 | 300 | 400 | 500 | 600 | 700;
  color?: string;
  /** Accessible label; omit for decorative icons */
  title?: string;
  style?: React.CSSProperties;
}
export declare function Icon(props: IconProps): JSX.Element;
