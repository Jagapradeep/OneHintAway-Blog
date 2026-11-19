# 0 · The map

> ⏱ 20 min · 🧰 nothing to install · Keep this page open while you do the others.

## 📖 The story

On 2 November 2026 the site went live. On 16 November the API joined it on a real Kubernetes
cluster. Between those dates, readers never noticed a thing, and the site **still doesn't depend
on that cluster**. If the server burned down tonight, every post would still load tomorrow.
That one decision shapes everything else in this course. By the end of this page you'll know
why.

## 🧩 The whole system on one page

```text
                       ┌─────────────────────── Cloudflare ───────────────────────┐
 reader's browser ───► │ onehintaway.com: plain files (HTML, CSS, JS, slides)      │
        │              │ built by Workers Builds from site/ on every push          │
        │              └───────────────────────────────────────────────────────────┘
        │
        └── JavaScript, after the page loads ───► api.onehintaway.com
                                                     │  DigitalOcean server, k3s (Kubernetes)
                                                     ▼
                                          Traefik (HTTPS, certificates from cert-manager)
                                                     │
                                          Service "api" ──► 2 API pods (Spring Boot, Java 21)
                                                                   │
                                                     postgres-0 (PostgreSQL 16 + its own disk)
                                                                   │
                                                     nightly dump ──► Cloudflare R2 (backups)

 also on the cluster: Umami (stats.), Prometheus + Grafana (grafana.)
 email: the API ──► Resend ──► reader's inbox (sign-in codes, subscription confirmations)
```

**The page is complete without the API.** The API only adds extras: view counts, search,
sign-in, "Mark as done", the newsletter and the visualizer's sign-in gate. If the API fails,
the extras quietly disappear and the post reads normally.

## 🚶 Journey 1: a reader opens a post and signs in

1. The browser asks DNS for `onehintaway.com` and gets a **Cloudflare** address.
2. Cloudflare's nearest data centre returns `posts/kadane/index.html`, a file built days ago.
   No code of ours runs. (Chapter 1)
3. The browser shows the page, then **hydrates** it: React attaches to the HTML so the code tabs,
   slides and menus respond. (Chapter 2)
4. A small script asks `api.onehintaway.com` to count the view. DNS gives **our server's**
   address this time. (Chapter 12)
5. **Traefik** on the server takes the HTTPS connection and hands it to the **Service** `api`,
   which picks one of two **pods**. (Chapter 10)
6. Spring Boot checks the rate limit, hashes the visitor and adds a row with
   `ON CONFLICT DO NOTHING`. (Chapters 5 and 6)
7. The reader presses **Sign in**, types their email, gets a 6-digit code by email (Resend),
   types it, and receives an `HttpOnly` session cookie. (Chapter 7)

## 🚀 Journey 2: you push a commit

```text
git push ──► GitHub
   ├─► Cloudflare Workers Builds (every push): npm run build in site/ ──► new site version
   ├─► Actions "API" (api/ or deploy/helm/ changed): test ──► image to GHCR ──► helm upgrade
   └─► Actions "Sync posts" (a post changed): send the post list to the API (for search)
Actions "Uptime" runs every 15 minutes, whatever you push.
```

A broken post stops the site build. A failing test stops the API image. A new API version that
never becomes healthy is rolled back by itself. (Chapters 1, 8 and 11)

## 📂 Where each piece lives

| Piece | Folder | Chapter |
| --- | --- | --- |
| Pages, components, styles | `site/app/`, `site/components/`, `site/app/globals.css` | 1, 2 |
| The pattern visualizer | `site/visualizer/`, `site/components/Visualizer*.tsx` | 3 |
| Posts | `site/content/posts/`, `site/public/posts/`, `post-kit/` | 4 |
| The API | `api/src/main/java/com/onehintaway/api/` | 5, 7 |
| The database schema | `api/src/main/resources/db/migration/` | 6 |
| Tests | `api/src/test/`, `site/scripts/check-*.mjs` | 8 |
| Images and the laptop stack | `api/Dockerfile`, `site/Dockerfile`, `deploy/compose/` | 9 |
| Cluster objects | `deploy/helm/onehintaway/` | 10 |
| Pipelines | `.github/workflows/`, Cloudflare Workers Builds | 11 |
| The server and its setup | `deploy/server/` | 12, 13 |
| Day-to-day commands | `deploy/README.md` (the runbook) | 13 |

## 🧠 Explain it

<details>
<summary>1. Why does the site keep working when the server is down?</summary>

Every page is a file built in advance and served by Cloudflare. The API is only called from the
browser *after* the page has loaded, for extras. Every API call gives up quietly (4 seconds for
counts and search, 8 for accounts), so a dead API just means no extras.
</details>

<details>
<summary>2. Name the three things that run on every push, and what triggers each.</summary>

Workers Builds builds and deploys the site on every push to `main`. The "API" workflow runs
when `api/` or `deploy/helm/` changed: test, image, deploy. "Sync posts" runs when posts
changed and sends them to the API for search.
</details>

<details>
<summary>3. Why do onehintaway.com and api.onehintaway.com resolve to different places?</summary>

The site is files at Cloudflare's edge; the API is a program on our own server. DNS points each
name at whatever serves it. The API is not behind Cloudflare's proxy, so Let's Encrypt can
reach the server directly to issue its certificate (chapter 12).
</details>

## 🎤 Interview corner

Practise this 30-second answer until it's smooth:

> "It's a static Next.js site on Cloudflare with a Spring Boot API on a small k3s cluster. The
> key design choice is that readers never depend on the cluster: every page is pre-built, and
> the API only adds extras like search and sign-in, which fail quietly. Pushes deploy
> automatically: Cloudflare builds the site, and GitHub Actions tests the API, builds an image
> tagged with the commit and rolls it out with Helm, rolling back by itself if it never becomes
> healthy."

---

**Next →** [1 · The site at build time](01-site-build.md)
