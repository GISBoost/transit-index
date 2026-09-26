export interface LineBulletProps {
  /** 1–3 characters: line letter/number or rank */
  label: string | number;
  /** Brand line key: vermilion, orange, yellow, green, sky, blue, violet, black (aliases red, cyan, ink) — or any CSS color. Decorative; never use line colors to encode data. */
  line?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number;
  shape?: 'circle' | 'square' | 'diamond';
  textColor?: string;
  style?: React.CSSProperties;
}
export declare function LineBullet(props: LineBulletProps): JSX.Element;
