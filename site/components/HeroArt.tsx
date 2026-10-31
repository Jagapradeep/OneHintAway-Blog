// Decorative art for the home page: a search path down a binary search tree and a
// sliding window (k = 3) moving over post 07's array, with its running sum.
// Pure SVG drawn with the theme tokens, so it follows light and dark. The motion is CSS
// (.hero-art in globals.css) and stops for readers who ask for reduced motion.
const CELLS = [2, 1, 5, 1, 3, 2];
const SUMS = [8, 7, 9, 6];
const CELL = 66;
const STEP = 74; // cell width + gap
const X0 = 24;

const TREE = [
  { x: 240, y: 50, v: 8, hot: true },
  { x: 150, y: 122, v: 3 },
  { x: 330, y: 122, v: 10, hot: true },
  { x: 100, y: 190, v: 1 },
  { x: 200, y: 190, v: 6 },
  { x: 380, y: 190, v: 14, hot: true },
];
const EDGES: [number, number, boolean?][] = [
  [0, 1],
  [0, 2, true],
  [1, 3],
  [1, 4],
  [2, 5, true],
];

export function HeroArt() {
  return (
    <svg className="hero-art" viewBox="0 0 480 420" role="img" aria-hidden="true" focusable="false">
      {/* Binary search tree: the gold path is the search for 14 */}
      <g className="art-tree">
        {EDGES.map(([a, b, hot]) => (
          <line
            key={`${a}-${b}`}
            x1={TREE[a].x}
            y1={TREE[a].y}
            x2={TREE[b].x}
            y2={TREE[b].y}
            className={hot ? "art-edge art-hot" : "art-edge"}
          />
        ))}
        {TREE.map((n, i) => (
          <g key={n.v} className={n.hot ? "art-node art-node-hot" : "art-node"} style={{ animationDelay: `${i * 0.12}s` }}>
            <circle cx={n.x} cy={n.y} r="19" />
            <text x={n.x} y={n.y + 5} textAnchor="middle">
              {n.v}
            </text>
          </g>
        ))}
      </g>

      {/* Array with indices */}
      <g className="art-array">
        {CELLS.map((v, i) => (
          <g key={i}>
            <text className="art-index" x={X0 + i * STEP + CELL / 2} y="238" textAnchor="middle">
              {i}
            </text>
            <rect className="art-cell" x={X0 + i * STEP} y="250" width={CELL} height={CELL} rx="12" />
            <text className="art-value" x={X0 + i * STEP + CELL / 2} y="292" textAnchor="middle">
              {v}
            </text>
          </g>
        ))}
      </g>

      {/* The window and its two pointers slide one cell at a time */}
      <g className="art-window">
        <rect x={X0 - 6} y="244" width={CELL * 3 + 8 * 2 + 12} height={CELL + 12} rx="16" />
        <path d={`M${X0 + CELL / 2} 330 l-7 11 h14 z`} />
        <text x={X0 + CELL / 2} y="362" textAnchor="middle">
          L
        </text>
        <path d={`M${X0 + 2 * STEP + CELL / 2} 330 l-7 11 h14 z`} />
        <text x={X0 + 2 * STEP + CELL / 2} y="362" textAnchor="middle">
          R
        </text>
      </g>

      <g className="art-sums">
        {SUMS.map((s, i) => (
          <text key={i} className={`art-sum art-sum-${i}`} x="460" y="404" textAnchor="end">
            window sum = {s}
            {s === 9 ? "  ★ best" : ""}
          </text>
        ))}
        <text className="art-k" x="20" y="404">
          k = 3
        </text>
      </g>
    </svg>
  );
}
