// The One Hint Away profile icon (same as app/icon.svg), without its black background
// so it sits on either theme: outlines follow the text colour, the last square is yellow.
export function BrandMark() {
  return (
    <svg className="brand-mark" viewBox="276 276 528 528" aria-hidden="true" focusable="false">
      <g fill="none" stroke="currentColor" strokeWidth="28">
        <rect x="290" y="290" width="212" height="212" rx="34" />
        <rect x="578" y="290" width="212" height="212" rx="34" />
        <rect x="290" y="578" width="212" height="212" rx="34" />
      </g>
      <rect className="brand-mark-hint" x="564" y="564" width="240" height="240" rx="48" />
    </svg>
  );
}
