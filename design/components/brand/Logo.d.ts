export declare const LogoGeometry: Record<'mark' | 'favicon', { box: number; w: number; gap: number; r: number; stem: [number, number][]; offsets: number[]; bar: [number, number][] }>;
export interface LogoProps {
  /** mark = symbol only; lockup = symbol + wordmark */
  variant?: 'mark' | 'lockup';
  /** color = ink/yellow/vermilion (follows theme); mono = currentColor, gaps knocked out (transparent) */
  tone?: 'color' | 'mono';
  /** Mark height in px. ≤20 switches to the favicon-optimised geometry */
  size?: number;
  /** Working name — may change */
  wordmark?: string;
  /** Adds the small "by GISBoost" credit line under the wordmark */
  credit?: boolean;
  style?: React.CSSProperties;
}
export declare function Logo(props: LogoProps): JSX.Element;
