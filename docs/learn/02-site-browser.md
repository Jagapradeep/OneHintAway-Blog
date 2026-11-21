# 2 · The site in the browser

> ⏱ 75 min · 🧰 the API and `npm run dev` running (course setup), Chrome or Edge DevTools

## 📖 The story

On 17 November the email confirmation pages got a nice three-step design, styled with a class
called `.steps`. It looked perfect on those pages. Then someone opened the **home page** in
production: its "how it works" section, which also used `.steps`, was broken. Two pages, one
class name, one global stylesheet.

A day later came a second puzzle: readers who were signed in saw **"Sign in"** flash in the
header on every page load, and on a phone, tapping it in the first seconds did nothing at all.

Both stories are about the same thing: what happens in the browser **after** the static HTML
arrives. That's this chapter.

## 💡 The idea in 2 minutes

The HTML from chapter 1 is already complete. Then three things happen in the browser:

1. **Tiny scripts in `<head>` run before the first paint.** They set the theme
   (`data-theme="light"` or `"dark"`) and a `data-acct` flag (this browser has signed in before),
   so the page never flashes the wrong colours or the wrong header.
2. **Hydration.** React loads, walks the existing HTML and attaches event handlers to it. Until
   that finishes, buttons look ready but do nothing. (In dev mode on your laptop that once took
   27 seconds.)
3. **Client components fetch the extras** from the API: view counts, "who am I?", progress. Each
   one gives up quietly if the API is slow or down.

**Server components vs client components.** In the App Router every component is a *server
component* by default: it runs only in the build and sends **no JavaScript** to readers. A file
that starts with `"use client"` is a *client component*: it's in the build's HTML **and** its code
ships to the browser so it can respond to clicks.

```text
Server only (no JS shipped)              Client ("use client": JS shipped)
───────────────────────────              ─────────────────────────────────
app/layout.tsx, app/page.tsx             ThemeToggle, NavLinks, BackButton
app/posts/[slug]/page.tsx                CodeTabs (tabs + copy), SlideGallery
components/PostList.tsx, BrandMark       SearchBox, PostViews (the view count)
components/Visualizer.tsx (colours the   AccountMenu, SignInForm, MarkDone
  pseudocode at build time)              VisualizerSlot → Gate / Player (lazy)
```

The rule this site follows: **keep the client part as small as possible**. Less JavaScript means
faster pages, especially on phones.

## 📂 Where it lives

| File | What to look for |
| --- | --- |
| `site/lib/theme.ts` | the before-paint theme script: saved choice, else the device setting |
| `site/lib/site.ts` | `ACCOUNTS_ON`, `ACCOUNT_SCRIPT` (sets `data-acct` before paint) |
| `site/app/globals.css` | the top: every colour as a **token** (`--gold`, `--text-2`, …), then `:root[data-theme="light"]` redefines them all |
| `site/lib/api.ts` | `apiGet` / `apiPost`: 4-second timeout, return `null`/`false`, never throw |
| `site/lib/account.ts` | one store for "who is signed in" shared by every component (`useSyncExternalStore`) |
| `site/lib/sign-in-draft.ts` | the sign-in step (email sent? code typed?) kept in `sessionStorage` |
| `site/components/AccountMenu.tsx` | the header button and panel; a plain `<form action="/sign-in/">` around it |
| `site/components/VisualizerSlot.tsx` | `React.lazy`: the visualizer's code loads only on pages that show one |

### Four techniques worth stealing

**1. Design tokens.** No colour is written twice. Components say `color: var(--text-2)`; the
token blocks say what `--text-2` is in each theme. Adding light mode was one block of overrides,
and every text colour is checked for WCAG AA contrast (4.5:1) in both themes.

**2. Fail quietly.** Every call to the API is wrapped so a failure becomes "show nothing":

```ts
// site/lib/api.ts
export async function apiGet<T>(path: string): Promise<T | null> {
  if (!API_URL) return null;                 // built without an API: every extra is off
  try {
    const res = await fetch(API_URL + path, { signal: AbortSignal.timeout(4000) });
    return res.ok ? ((await res.json()) as T) : null;
  } catch {
    return null;                             // down, slow, offline: same answer
  }
}
```

**3. One store, many components.** The header, the "Mark as done" button and the ticks on the
home page all need to know who's signed in. Instead of each one calling the API,
`lib/account.ts` keeps one module-level `state` and a set of listeners. React's
`useSyncExternalStore` subscribes each component to it. When `state` changes, every subscriber
re-renders. A `storage` event listener makes **other tabs** follow a sign-in or sign-out.
Another *browser or device* gets no such event, and a static site can't be pushed to, so a
signed-in page asks `/auth/me` again whenever the reader comes back to it (`focus`,
`visibilitychange`, `pageshow`) and every 30 seconds while it is on screen. That is how
"Sign out everywhere" on your phone signs out the laptop without a reload. This is **polling**:
simple and good enough here; the alternative, a server push (SSE or WebSocket), would need a
connection held open to the cluster from every reader.

**4. Work before JavaScript arrives.** The account button sits inside
`<form action="/sign-in/" method="get">`. Before hydration, a tap submits the form and opens the
sign-in page (plain HTML, works). After hydration, `onSubmit` calls `preventDefault()` and opens
the panel instead. This is called **progressive enhancement**.

## 🛠 Try it (25 min)

Open http://localhost:3000 in Chrome or Edge with DevTools open.

1. **Tokens.** Elements → `<html>`: see `data-theme`. Press the theme switch and watch it flip.
   In Styles, click `:root` and change `--gold` to `red`: every gold thing on the page changes.
2. **Storage.** Application → Local Storage: `ohw.theme` (your choice), and after you sign in,
   `ohw.account` (a timestamp, *not* the session). The session itself is a cookie your scripts
   can't read: Application → Cookies → `localhost:8080` → `ohw_session` or `__Host-ohw_session`,
   with **HttpOnly** ticked.
3. **Network.** Filter by `Fetch/XHR` and reload a post: `/views` (count), `/auth/me` (who am I),
   `/progress`. Filter by `JS` and open `/posts/two-pointers/`: the visualizer chunks arrive. Now
   open `/about/`: they don't.
4. **Two tabs.** Open the site in two tabs. Sign in in one (the code is in the API's log). Switch
   to the other: its header shows your initial without a reload. That's the `storage` event.
   Now sign in in a second browser too (or a private window), and use **Sign out everywhere** in
   the first. Click back into the second: it signs out at once. Leave it untouched instead and it
   signs out within 30 seconds (watch `/auth/me` answer 401 in the Network tab).
5. **Slow network.** Network → throttling → "Slow 4G", reload a post, and tap the account button
   immediately. Even before React loads, the form opens `/sign-in/`.

## 💥 Break it (20 min)

**1. Re-live the `.steps` bug.** Add this line to the end of `app/globals.css`:

```css
.steps { display: block; }
```

Look at the home page's "how it works" section: four columns collapse into one. Every class in
`globals.css` is global, which is why this project's rule is: **grep for a class name before
adding one**, and prefix whole areas (`acct-`, `vz-`). Remove the line.

**2. Lose the before-paint script.** In `app/layout.tsx`, comment out the line with
`themeScript`. Set the theme to light, then reload a few times: the page starts dark and
jumps. Put it back.

**3. Kill the API.** Stop the API (Ctrl+C in its terminal) and reload a post: no view count,
search says "not available", the header looks signed out, posts read normally, and **the
visualizer plays** (its sign-in gate fails open). DevTools Console: no red errors. Start the
API again.

## 🧠 Explain it

<details>
<summary>1. What's the difference between a server component and a client component here?</summary>

A server component runs only during `next build` and ships no JavaScript: its output is just
HTML. A client component (`"use client"`) is also rendered into the HTML at build time, but its
code ships to the browser so it can handle clicks, state and effects after hydration.
</details>

<details>
<summary>2. What is hydration, and why could a tap "do nothing" before it finished?</summary>

React downloads the JavaScript, re-runs the client components and attaches event handlers to the
HTML that's already on screen. Until then, buttons are only HTML. A button that needs JavaScript
does nothing; a real `<form>` or `<a>` still works. That's why the account button is in a form.
</details>

<details>
<summary>3. Why must the theme script be inline in &lt;head&gt; and not in a React component?</summary>

React components run after the page has painted (or after hydration). By then the reader has
already seen the default theme, so they'd see a flash. An inline script in `<head>` runs before
the body is drawn.
</details>

<details>
<summary>4. Why is `ohw.account` in localStorage safe, when the session isn't kept there?</summary>

`ohw.account` is only a hint ("this browser has signed in before, so ask the API"). It grants
nothing. The session token lives in an `HttpOnly` cookie, which scripts can't read, so an
injected script can't steal it. A reader who never signed in makes no account request at all.
</details>

<details>
<summary>5. What does `useSyncExternalStore` give you that `useState` in each component wouldn't?</summary>

One source of truth outside React. Every component reads the same snapshot, so the header and
the ticks can never disagree, and there's one `/auth/me` call per page, not one per component.
It's also safe with concurrent rendering (no torn reads).
</details>

<details>
<summary>6. Why load the visualizer with `React.lazy`?</summary>

Most pages don't show a player. With `React.lazy(() => import(...))` its code is a separate
chunk, fetched only where it's used. The shared post chunk went from 14,054 to 7,809 bytes when
this was done.
</details>

## 🎤 Interview corner

> "How do you keep a mostly-static site fast and still personalised?" Pre-render everything,
> ship JavaScript only for interactive islands, load heavy parts lazily, and fetch per-user data
> from an API after load with short timeouts and quiet failure. Use before-paint scripts for
> things that must be right on the first frame, like the theme.

## ✅ You now know

- [ ] Which components ship JavaScript and why most don't
- [ ] What happens between "HTML arrives" and "buttons work"
- [ ] How tokens give two themes with one set of components
- [ ] How the account store keeps every component and every tab in step
- [ ] Why a failing API never shows an error to readers

---

**Next →** [3 · The visualizer](03-visualizer.md)
