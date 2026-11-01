import { isValidElement, type ComponentProps } from "react";
import type { MDXComponents } from "mdx/types";
import { CodeTab, CodeTabs } from "@/components/CodeTabs";

// Pseudocode blocks get the slides' "PSEUDOCODE · any language" header as a bar above the
// code, outside the part that scrolls sideways, so it never moves and its underline always
// spans the whole box.
function Pre(props: ComponentProps<"pre">) {
  const child = props.children;
  const lang = isValidElement<{ className?: string }>(child) ? child.props.className : undefined;
  if (!lang?.includes("language-pseudo")) return <pre {...props} />;
  return (
    <div className="pseudo-block">
      <div className="pseudo-head">{"Pseudocode  ·  any language"}</div>
      <pre {...props} />
    </div>
  );
}

// Components MDX can use without importing them. CodeTabs/CodeTab are inserted
// by lib/remark-code-tabs.mjs around the Java/Python/C++/JavaScript sections.
const components: MDXComponents = {
  CodeTabs,
  CodeTab,
  pre: Pre,
  a: (props) => <a {...props} target={props.href?.startsWith("http") ? "_blank" : undefined} rel="noopener" />,
};

export function useMDXComponents(): MDXComponents {
  return components;
}
