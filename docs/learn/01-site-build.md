# 1 · The site at build time

> ⏱ 75 min · 🧰 Node 22, `site/` installed (`npm install`) · No API needed

## 📖 The story

Early on, a post's table had a cell that said `{3:0}` (a hash map: key 3, value 0). The build
died with a JavaScript error, on a page that has no JavaScript in it. Why? Because a post isn't
Markdown, it's **MDX**: Markdown where `{ }` means "run this JavaScript expression". `3:0` isn't
valid JavaScript, so the build stopped. That's also the good news: the mistake never reached a
reader, because **the whole site is built before anyone sees it**. This chapter is about that
build.

## 💡 The idea in 2 minutes

Most web apps render a page **when a reader asks for it** (request time). This site renders every
page **once, when you push** (build time), and writes the results as plain files:

```text
next build  ──►  site/out/
                   index.html
                   posts/kadane/index.html      ← the whole post: text, coloured code, tables
                   posts/two-pointers/index.html
                   _next/static/...              ← the JS and CSS the pages share
                   404.html
```

Cloudflare stores `out/` in data centres around the world and hands out files. No server of ours
runs per visit, so it's fast, free to host, and nothing on our side can take it down.

Three things make this work:

1. **`output: "export"`** in `next.config.ts` tells Next.js to write files instead of running a
   server.
2. **`generateStaticParams()`** in `app/posts/[slug]/page.tsx` lists every post, so Next knows
   which pages to build. `dynamicParams = false` makes any other address a 404.
3. **Everything that needs computing happens in the build**: reading MDX files, colouring code
   (Shiki), building the sitemap. Readers download the result, not the work.

## 📂 Where it lives

| File | What to look for |
| --- | --- |
| `site/next.config.ts` | `output: "export"`, `trailingSlash: true`, the MDX plugins, Shiki's two themes |
| `site/app/layout.tsx` | the frame of every page: fonts, header, footer, the scripts in `<head>` |
| `site/app/page.tsx` | the home page: posts grouped by roadmap section |
| `site/app/posts/[slug]/page.tsx` | one post: `generateStaticParams`, `generateMetadata` (title, preview image), the page |
| `site/lib/posts.ts` | reads every `.mdx` file's frontmatter (`gray-matter`), sorts and groups them |
| `site/lib/remark-code-tabs.mjs` | our own MDX plugin: four `## Java/Python/C++/JavaScript` sections become one tab block |
| `site/scripts/check-posts.mjs` | checks every post against the content contract before every build |
| `site/wrangler.jsonc` | Cloudflare: "serve `out/` as files"; no `main`, so no Worker code |

**How the App Router maps folders to addresses.** Each folder under `app/` is a path; the
`page.tsx` inside it is the page. `[slug]` is a placeholder filled from `generateStaticParams`.

```text
app/page.tsx                    →  /
app/patterns/page.tsx           →  /patterns/
app/posts/[slug]/page.tsx       →  /posts/kadane/, /posts/two-pointers/, …
app/visualize/[pattern]/page.tsx→  /visualize/two-pointers/, …
app/not-found.tsx               →  out/404.html
```

**How a post becomes HTML.** One `.mdx` file goes through a chain of plugins:

```text
NN-slug.mdx
  └► remark-frontmatter   strip the YAML header (lib/posts.ts reads it separately)
  └► remark-gfm           tables, strikethrough
  └► remark-code-tabs     the four language sections → one <CodeTabs> block; drop a leading # title
  └► @shikijs/rehype      colour every code block with VS Code's grammars, two themes at once
  └► React components     page.tsx puts it between the slides and the practice links
```

Shiki writes the colours into the HTML as inline styles, with the light theme's colours in a CSS
variable (`--shiki-light`). Switching themes is pure CSS. A reader never downloads a syntax
highlighter.

## 🛠 Try it (25 min)

```bash
cd site
npm run build                 # prebuild runs check-posts and check-viz first, then next build
ls out out/posts | head       # one folder per page, each with an index.html
find out -type f | wc -l      # Cloudflare's free plan allows 20,000 files per version
python -m http.server 8765 -d out
```

Open http://localhost:8765/posts/kadane/ and:

1. **View page source.** The whole post (text, coloured code, tables) is already in the HTML.
2. **DevTools → Settings → Disable JavaScript**, reload. The post still reads fine. Only the
   extras (tabs, slides, menus) need scripts. Turn JavaScript back on.
3. Find `<title>` and `og:image` in the source. That's `generateMetadata`: the title Google
   shows and the preview image WhatsApp shows.

Then look at the real thing:

```bash
curl -sI https://onehintaway.com/ | grep -i "server\|cf-ray\|content-type"   # Cloudflare answers
curl -sI https://onehintaway.com/about | head -3                              # no slash? a redirect
```

Stop the server with Ctrl+C. **Don't run it from inside `out/`**: a process sitting in that folder
locks it on Windows, and the next build fails with `EBUSY`.

## 💥 Break it (25 min)

**1. A bad post fails the build.** In `content/posts/00-start-here.mdx` change `slides: 7` to
`slides: 6`, then:

```bash
npm run check-posts
```

Read the error: it names the file and the rule. Put it back with
`git checkout -- content/posts/00-start-here.mdx`. Workers Builds runs the same `prebuild`, so
a broken post can never reach the live site.

**2. Re-live the `{3:0}` story.** Add this line to the end of any post's walk-through section
(outside a code block):

```text
The map starts as {3:0}.
```

Run `npm run build` and read the error. Fix it the way the contract says: `\{3:0\}` or
`` `{3:0}` ``. Rebuild to see it pass, then undo with `git checkout`.

**3. Build-time settings are frozen in.** Look in `site/.env.local` (from the course setup).
Build once with the API address and once without, and compare the header:

```bash
npm run build && grep -c "acct-btn" out/index.html              # 1: the Sign in button is there
mv .env.local .env.local.off && npm run build && grep -c "acct-btn" out/index.html   # 0
mv .env.local.off .env.local
```

`NEXT_PUBLIC_*` values are **pasted into the code at build time**. Changing one in Cloudflare
does nothing until the next build. That's also why a missing `.env.local` made the Sign in
button vanish on your laptop.

## 🧠 Explain it

<details>
<summary>1. Build time vs request time: which does this site use, and what does it save?</summary>

Build time. Every page is rendered once per push. Readers get finished files from a CDN: no
server cost per visit, no cold starts, nothing to crash, and pages work with JavaScript off.
The trade-off: anything that changes per reader (view counts, sign-in) has to be added in the
browser afterwards (chapter 2).
</details>

<details>
<summary>2. Why is Shiki run in the build and not in the browser?</summary>

Colouring code needs grammars and themes, hundreds of KB of JavaScript. Running it once in the
build means readers download only the coloured HTML. It also means the colours are there before
any script runs, so there's no flash of plain code.
</details>

<details>
<summary>3. What does `trailingSlash: true` do, and why does a static host need it?</summary>

Next writes `/posts/kadane/` as `posts/kadane/index.html`. Every static host serves a folder's
`index.html` for the address with a slash. `wrangler.jsonc`'s `auto-trailing-slash` then
redirects `/posts/kadane` to `/posts/kadane/`, so there's one address per page.
</details>

<details>
<summary>4. What happens to an address that isn't a post, like /posts/nope/?</summary>

`dynamicParams = false` means only the slugs from `generateStaticParams` exist, so there's no
file for it. Cloudflare's `not_found_handling: "404-page"` serves `out/404.html` with status 404.
</details>

<details>
<summary>5. You change NEXT_PUBLIC_API_URL in Cloudflare. When does the live site use it?</summary>

After the next build. The value is inlined into the JavaScript bundle while building. Trigger a
rebuild (push a commit, or "Retry deployment" in the dashboard).
</details>

## 🎤 Interview corner

> "Why a static site rather than server-side rendering?" Content changes only when a post is
> published, so rendering per request would just redo the same work. Pre-rendering gives CDN
> speed, almost no hosting cost and no runtime to fail. Per-reader features come from a separate
> API called in the browser, designed to fail quietly.

## ✅ You now know

- [ ] What `output: "export"` produces and who serves it
- [ ] How a folder under `app/` becomes an address
- [ ] The MDX plugin chain, and why `{ }` is special in a post
- [ ] Why a broken post can't reach production
- [ ] Why `NEXT_PUBLIC_*` changes need a rebuild

---

**Next →** [2 · The site in the browser](02-site-browser.md)
