import type { Metadata } from "next";
import Link from "next/link";
import { PAYWALL_ON } from "@/visualizer/access.ts";
import { patterns } from "@/visualizer/registry.ts";

export const metadata: Metadata = {
  title: "Visualize | One Hint Away",
  description: "Step through each pattern on your own input: two pointers, sliding window, monotonic stack.",
};

// The gallery: one card per pattern, grouped by roadmap section. Each card
// opens the pattern's own page, where the player has the screen to itself.
export default function VisualizePage() {
  const sections = [...new Set(patterns.map((p) => p.section))];
  return (
    <article className="prose vz-page">
      <h1 className="chrome">Visualize</h1>
      <p className="lead">Pick a pattern and step through it on your own numbers. Each step shows the line of pseudocode that is running.</p>

      {sections.map((section) => (
        <section key={section}>
          <h2>{section}</h2>
          <div className="vz-cards">
            {patterns
              .filter((p) => p.section === section)
              .map((p) => (
                <Link key={p.id} href={`/visualize/${p.id}/`} className="vz-card">
                  <strong>{p.title}</strong>
                  <span>{p.blurb}</span>
                  {PAYWALL_ON && <em className="vz-badge">{p.tier === "paid" ? "Preview" : "Free"}</em>}
                </Link>
              ))}
          </div>
        </section>
      ))}
    </article>
  );
}
