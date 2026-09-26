export interface ToastProps {
  /** info = blue, success = green, warning = yellow, danger = red — shown as a solid colored icon block */
  tone?: 'info' | 'success' | 'warning' | 'danger';
  title?: React.ReactNode;
  message?: React.ReactNode;
  action?: React.ReactNode;
  onClose?: () => void;
  style?: React.CSSProperties;
}
export declare function Toast(props: ToastProps): JSX.Element;
