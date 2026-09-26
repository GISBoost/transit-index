export interface StatProps {
  /** Pre-formatted value (locale decimal separator), e.g. "17,6" or "−22%" */
  value: string;
  unit?: string;
  label?: React.ReactNode;
  /** md 48 / lg 96 / xl 200px (fluid below) */
  size?: 'md' | 'lg' | 'xl';
  /** Poster-print wit: offset vermilion copy behind the figure. Hero use only. */
  misregister?: boolean;
  style?: React.CSSProperties;
}
export declare function Stat(props: StatProps): JSX.Element;
