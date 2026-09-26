export interface TagProps {
  children?: React.ReactNode;
  /** Line color key (red, orange, yellow, green, teal, cyan, blue, navy, violet, pink, brown, grey, sand) or any CSS color — renders solid in that color */
  line?: string;
  variant?: 'outline' | 'solid';
  style?: React.CSSProperties;
}
export declare function Tag(props: TagProps): JSX.Element;
