import type { MDXComponents } from "mdx/types";
import { CodeTab, CodeTabs } from "@/components/CodeTabs";

// Components MDX can use without importing them. CodeTabs/CodeTab are inserted
// by lib/remark-code-tabs.mjs around the Java/Python/C++/JavaScript sections.
const components: MDXComponents = {
  CodeTabs,
  CodeTab,
  a: (props) => <a {...props} target={props.href?.startsWith("http") ? "_blank" : undefined} rel="noopener" />,
};

export function useMDXComponents(): MDXComponents {
  return components;
}
