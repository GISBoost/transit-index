export interface RankingBarProps {
  rank: number;
  label: React.ReactNode;
  /** null = no data */
  value: number | null;
  /** Value mapped to 100% bar length */
  max?: number;
  unit?: string;
  decimals?: number;
  /** Decimal separator: pl → "17,6", en → "17.6" */
  locale?: 'pl' | 'en';
  /** Data-quality flag: thin = hatched bar; gaps = feed gaps icon */
  flag?: 'thin' | 'gaps' | null;
  flagLabel?: string;
  /** Emphasis (e.g. the reader's city) — poster red, not a data encoding */
  highlight?: boolean;
  onClick?: () => void;
  style?: React.CSSProperties;
}
export declare function RankingBar(props: RankingBarProps): JSX.Element;
