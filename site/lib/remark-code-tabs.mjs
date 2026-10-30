// Remark plugin: turns the solutions-file layout into one tabbed code block.
//
//   ## Java        ## Python        ## C++        ## JavaScript
//   ```java ...    ```python ...    ```cpp ...    ```javascript ...
//
// A run of 2+ consecutive language sections (or 2+ back-to-back language code blocks)
// becomes  ## Code  +  <CodeTabs><CodeTab lang="java">...</CodeTab>...</CodeTabs>.
// It also drops the leading "# NN · Title" (the page template shows the title)
// and the "## Practice" section (the template renders practice links from frontmatter).

const LANGS = [
  // order matters: "javascript" must be checked before "java"
  { id: "javascript", match: (s) => s.startsWith("javascript") || s === "js" },
  { id: "java", match: (s) => s.startsWith("java") },
  { id: "python", match: (s) => s.startsWith("python") || s === "py" },
  { id: "cpp", match: (s) => s.startsWith("c++") || s === "cpp" },
];

function langOf(text) {
  const s = (text || "").trim().toLowerCase();
  return LANGS.find((l) => l.match(s))?.id;
}

function textOf(node) {
  if (node.type === "text" || node.type === "inlineCode") return node.value;
  return (node.children || []).map(textOf).join("");
}

const attr = (name, value) => ({ type: "mdxJsxAttribute", name, value });
const jsx = (name, attributes, children) => ({ type: "mdxJsxFlowElement", name, attributes, children });

function isLangHeading(node) {
  return node.type === "heading" && node.depth >= 2 && langOf(textOf(node));
}

// Index just past the section that starts with heading `nodes[i]`.
function sectionEnd(nodes, i) {
  const depth = nodes[i].depth;
  let j = i + 1;
  while (j < nodes.length && !(nodes[j].type === "heading" && nodes[j].depth <= depth)) j++;
  return j;
}

export default function remarkCodeTabs() {
  return (tree) => {
    let nodes = tree.children;

    // Drop the leading H1 (after the YAML node, if any).
    const firstContent = nodes.findIndex((n) => n.type !== "yaml");
    if (firstContent >= 0 && nodes[firstContent].type === "heading" && nodes[firstContent].depth === 1) {
      nodes.splice(firstContent, 1);
    }

    // Drop the "## Practice" list (the template renders it from frontmatter with links).
    // Any other text there, like "Verified: ...", is kept under "How it was tested".
    const p = nodes.findIndex((n) => n.type === "heading" && n.depth === 2 && /^practice\b/i.test(textOf(n)));
    if (p >= 0) {
      const end = sectionEnd(nodes, p);
      const rest = nodes.slice(p + 1, end).filter((n) => n.type !== "list");
      const replacement = rest.length
        ? [{ type: "heading", depth: 2, children: [{ type: "text", value: "How it was tested" }] }, ...rest]
        : [];
      nodes.splice(p, end - p, ...replacement);
    }

    const out = [];
    let i = 0;
    while (i < nodes.length) {
      const tabs = [];
      let j = i;
      let headingDepth = 0;

      if (isLangHeading(nodes[i])) {
        // Case 1: consecutive "## Language" sections.
        headingDepth = nodes[i].depth;
        while (j < nodes.length && isLangHeading(nodes[j]) && nodes[j].depth === headingDepth) {
          let end = sectionEnd(nodes, j);
          const isLast = !(end < nodes.length && isLangHeading(nodes[end]) && nodes[end].depth === headingDepth);
          if (isLast) {
            // Text after the last section's code is about all languages
            // ("use long in Java and long long in C++"), so keep it outside the tabs.
            const lastCode = nodes.slice(j + 1, end).findLastIndex((n) => n.type === "code");
            if (lastCode >= 0) end = j + 1 + lastCode + 1;
          }
          tabs.push(jsx("CodeTab", [attr("lang", langOf(textOf(nodes[j])))], nodes.slice(j + 1, end)));
          j = end;
        }
      } else {
        // Case 2: back-to-back fenced blocks with no headings.
        while (j < nodes.length && nodes[j].type === "code" && langOf(nodes[j].lang)) {
          tabs.push(jsx("CodeTab", [attr("lang", langOf(nodes[j].lang))], [nodes[j]]));
          j++;
        }
      }

      if (tabs.length >= 2) {
        if (headingDepth) {
          out.push({ type: "heading", depth: headingDepth, children: [{ type: "text", value: "Code" }] });
        }
        const langs = tabs.map((t) => t.attributes[0].value).join(",");
        out.push(jsx("CodeTabs", [attr("langs", langs)], tabs));
        i = j;
      } else {
        out.push(nodes[i]);
        i++;
      }
    }
    tree.children = out;
  };
}
