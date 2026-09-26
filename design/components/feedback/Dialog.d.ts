export interface DialogProps {
  open: boolean;
  onClose?: () => void;
  title: React.ReactNode;
  children?: React.ReactNode;
  /** Buttons rendered right-aligned in the footer */
  actions?: React.ReactNode;
  width?: number;
}
export declare function Dialog(props: DialogProps): JSX.Element | null;
