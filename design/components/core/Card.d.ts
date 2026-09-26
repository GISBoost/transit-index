export interface CardProps {
  children?: React.ReactNode;
  /** white/outline/paper = print surfaces (square), sign = dark signage panel (12px radius), red/petrol/mustard = poster color blocks */
  surface?: 'white' | 'paper' | 'outline' | 'sign' | 'red' | 'petrol' | 'mustard';
  /** 8px top rule — the poster "header bar" */
  rule?: boolean;
  padding?: number | string;
  onClick?: () => void;
  style?: React.CSSProperties;
}
export declare function Card(props: CardProps): JSX.Element;
