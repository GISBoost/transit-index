export interface TabItem {
  id: string;
  label: React.ReactNode;
  /** Line color for the active bar (default ink) */
  line?: string;
}
export interface TabsProps {
  tabs: TabItem[];
  value?: string;
  defaultValue?: string;
  onChange?: (id: string) => void;
  style?: React.CSSProperties;
}
export declare function Tabs(props: TabsProps): JSX.Element;
