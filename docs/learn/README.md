# 🎓 Learn One Hint Away, top to bottom

You built this project fast and postponed the learning. This course is that learning, done on
**your own code**. By the end you can explain every part of the system, from the CSS in the
header to the certificate on the API, the way an interviewer wants to hear it.

**How it stays interesting**

- **Real stories first.** Each chapter opens with something that actually happened in this
  project: a lost database password, a CSS class that broke the home page in production, Gmail
  turning the logo inside out. You learn the idea by solving the mystery.
- **Short missions.** Every chapter is 30 to 90 minutes, split into 10 to 20 minute blocks.
  Stop after any block.
- **Break it on purpose.** You will crash the API, corrupt a migration, kill pods and feed bad
  images to Kubernetes, all on your laptop. Breaking things is where it sticks, and "what
  happens when…" is what interviews ask.
- **Answers are folded away.** Each chapter ends with questions. Say your answer out loud
  first, then open the answer and compare.

## 🗺️ The route

Do the chapters in order the first time; after that each one stands on its own.

| # | Chapter | You'll be able to explain | Time |
| --- | --- | --- | --- |
| 0 | [The map](00-map.md) | The whole system on one page, and two journeys through it | 20 min |
| **Frontend** | | | |
| 1 | [The site at build time](01-site-build.md) | Next.js App Router, static export, MDX, Shiki, build-time checks, Cloudflare | 75 min |
| 2 | [The site in the browser](02-site-browser.md) | Server vs client components, hydration, the theme script, CSS tokens, the account store, lazy loading, failing quietly | 75 min |
| 3 | [The visualizer](03-visualizer.md) | Generators as step recorders, a typed step schema, checking an algorithm against a brute force | 45 min |
| 4 | [How a post reaches the site](04-content-pipeline.md) | The content contract, `add-post`, `check-posts`, the post sync and search | 30 min |
| **Backend** | | | |
| 5 | [The API with Spring Boot](05-api.md) | Settings that fail fast, controllers, interceptors, rate limits, CORS, the mail interface | 75 min |
| 6 | [The database](06-database.md) | Schema design, migrations, upserts, full-text search, indexes, `EXPLAIN`, volumes | 75 min |
| 7 | [Accounts and security](07-accounts-security.md) | Sign-in by code, sessions, cookie flags, CSRF, hashing, the threat model | 60 min |
| 8 | [Testing and quality](08-testing.md) | Testcontainers, build-time checks, browser checks, what each layer catches | 40 min |
| **Infrastructure** | | | |
| 9 | [Docker](09-docker.md) | Images, layers, caching, non-root, health checks, Compose, volumes | 75 min |
| 10 | [Kubernetes](10-kubernetes.md) | Pods, Deployments, Services, StatefulSets, probes, limits, Helm, on k3d | 3 h |
| 11 | [CI/CD](11-cicd.md) | GitHub Actions, GHCR, SHA tags, Workers Builds, automatic rollback | 45 min |
| 12 | [Production edges](12-production.md) | The server, DNS, HTTPS certificates, email authentication | 60 min |
| 13 | [Operations](13-operations.md) | Logs, metrics, alerts, uptime, backups and restores, rollbacks | 60 min |
| 14 | [The final boss](14-final.md) | Incident drills, and the whole system explained without notes | 60 min |
| | [Glossary](glossary.md) | Every term in one line | |

About **15 hours** in all. At under 6 hours a week, that's three weeks of evenings.

## 🧰 Set up once (15 min)

**Tools:** Docker Desktop (running), Node 22, JDK 21 or newer, Git Bash. For chapter 10 also
`kubectl`, `helm` and `k3d`.

Commands are written for **Git Bash**. In PowerShell, `NAME=value command` becomes
`$env:NAME="value"; command`.

**Your local settings files** (all git-ignored; each has a committed `.example` beside it):

| File | Used by | Holds |
| --- | --- | --- |
| `api/.env` | the API and `api/compose.yaml`'s database | database password, visitor salt, admin token, CORS origin |
| `site/.env.local` | `npm run dev` and `npm run build` in `site/` | the API address and the accounts switch |
| `deploy/compose/.env` | the whole Docker stack (chapter 9) | its own database password and secrets |

Missing one? Copy its example: `cp api/.env.example api/.env` (fill in the blanks with
`openssl rand -hex 32`), `cp site/.env.example site/.env.local`.

**Start everything for chapters 1 to 8** (two terminals):

```bash
# terminal 1: database + API (keep this log visible: sign-in codes appear here)
cd api && docker compose up -d --wait && ./mvnw spring-boot:run

# terminal 2: posts into the API, then the site
cd site && npm run sync-posts && npm run dev          # http://localhost:3000
```

## 🧭 Rules for the whole course

1. **Break things only on your laptop.** Chapters 1 to 10 are entirely local.
2. **Production is read-only** unless the runbook ([deploy/README.md](../../deploy/README.md))
   says otherwise: `get`, `describe`, `logs`, `top`, `history`. Every production command carries
   `--kubeconfig ~/.kube/onehintaway-prod.yaml`, so you can't hit it by accident.
3. **Never print readers' email addresses from production.** Count rows; don't list them.
4. **Put things back.** Every "break it" says how to undo it. If you get lost:
   `git status`, then `git checkout -- <file>`.

## ✅ Progress

Tick these as you go (VS Code's Markdown preview and GitHub both show the boxes).

- [ ] 0 · The map
- [ ] 1 · The site at build time
- [ ] 2 · The site in the browser
- [ ] 3 · The visualizer
- [ ] 4 · How a post reaches the site
- [ ] 5 · The API
- [ ] 6 · The database
- [ ] 7 · Accounts and security
- [ ] 8 · Testing and quality
- [ ] 9 · Docker
- [ ] 10 · Kubernetes
- [ ] 11 · CI/CD
- [ ] 12 · Production edges
- [ ] 13 · Operations (including one scratch restore)
- [ ] 14 · The final boss

**Want to be quizzed?** After any chapter, ask Claude: "quiz me on chapter 6 of the One Hint
Away course" (the backend-engineer-learning skill does interview-style practice).
