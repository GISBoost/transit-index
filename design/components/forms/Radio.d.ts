export interface RadioProps {
  label?: React.ReactNode;
  checked?: boolean;
  name?: string;
  value: string;
  /** Called with this radio's value when picked */
  onChange?: (value: string) => void;
  disabled?: boolean;
  style?: React.CSSProperties;
}
export declare function Radio(props: RadioProps): JSX.Element;
