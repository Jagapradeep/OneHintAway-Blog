import { createHighlighter, type Highlighter } from "shiki";
import pseudo from "@/lib/shiki/pseudo.tmLanguage.json";
import intellijLight from "@/lib/shiki/intellij-light.json";
import { isLocked } from "@/visualizer/access.ts";
import { patternById, patterns } from "@/visualizer/registry.ts";
import { VisualizerLazy } from "./VisualizerLazy";

// Server side of <Visualizer pattern="two-pointers" />. It colours the
// pattern's pseudocode at build time with the site's own grammar and themes
// (the same ones posts use), so no highlighter is sent to readers.
let highlighter: Promise<Highlighter> | undefined;

async function colour(code: string): Promise<string> {
  highlighter ??= createHighlighter({ themes: ["dark-plus", intellijLight as never], langs: [pseudo as never] });
  return (await highlighter).codeToHtml(code, {
    lang: "pseudo",
    themes: { dark: "dark-plus", light: intellijLight.name },
    defaultColor: "dark",
  });
}

export async function Visualizer({ pattern }: { pattern: string }) {
  const p = patternById(pattern);
  if (!p) {
    throw new Error(`<Visualizer pattern="${pattern}" />: no such pattern. Known: ${patterns.map((x) => x.id).join(", ")}`);
  }
  return <VisualizerLazy patternId={p.id} codeHtml={await colour(p.pseudocode.join("\n"))} locked={isLocked(p)} />;
}
