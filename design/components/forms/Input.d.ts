export interface InputProps {
  label?: string;
  value?: string;
  defaultValue?: string;
  placeholder?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  hint?: string;
  /** Error message — turns border poster red */
  error?: string;
  disabled?: boolean;
  /** Material Symbols name */
  iconLeft?: string;
  type?: string;
  id?: string;
  style?: React.CSSProperties;
}
export declare function Input(props: InputProps): JSX.Element;
