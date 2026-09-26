export interface IconButtonProps {
  /** Material Symbols name */
  icon: string;
  /** Required accessible label (also tooltip) */
  label: string;
  variant?: 'primary' | 'accent' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  /** circle = signage disc */
  shape?: 'square' | 'circle';
  disabled?: boolean;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  style?: React.CSSProperties;
}
export declare function IconButton(props: IconButtonProps): JSX.Element;
