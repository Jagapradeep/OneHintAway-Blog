import type { CSSProperties } from "react";

/** CSS custom properties as an inline style. */
export const vars = (o: Record<string, string | number>) => o as CSSProperties;
