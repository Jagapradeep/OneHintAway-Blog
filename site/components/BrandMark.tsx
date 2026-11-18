// The One Hint Away logo, exactly as app/icon.svg and the email logo draw it: a black tile,
// white outlines and a yellow last square. Its colours are fixed, so it looks the same in
// the light and the dark theme (and in browser tabs, emails and on Instagram).
export function BrandMark() {
  return (
    <svg className="brand-mark" viewBox="216 216 648 648" aria-hidden="true" focusable="false">
      <rect x="216" y="216" width="648" height="648" rx="136" fill="#000" />
      <g fill="none" stroke="#f5f5f5" strokeWidth="28">
        <rect x="290" y="290" width="212" height="212" rx="34" />
        <rect x="578" y="290" width="212" height="212" rx="34" />
        <rect x="290" y="578" width="212" height="212" rx="34" />
      </g>
      <rect x="564" y="564" width="240" height="240" rx="48" fill="#ffd447" />
    </svg>
  );
}
