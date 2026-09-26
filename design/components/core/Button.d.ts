export interface ButtonProps {
  children?: React.ReactNode;
  /** primary = ink block, accent = poster red, secondary = ink outline (inverts on hover), ghost = text only, inverse = paper on dark */
  variant?: 'primary' | 'accent' | 'secondary' | 'ghost' | 'inverse';
  size?: 'sm' | 'md' | 'lg';
  /** Material Symbols name */
  iconLeft?: string;
  iconRight?: string;
  disabled?: boolean;
  fullWidth?: boolean;
  type?: 'button' | 'submit' | 'reset';
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  style?: React.CSSProperties;
}
export declare function Button(props: ButtonProps): JSX.Element;
