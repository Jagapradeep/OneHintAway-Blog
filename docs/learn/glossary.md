# Glossary

Every term in the course, one line each, with the chapter that explains it.

| Term | Meaning | Ch. |
| --- | --- | --- |
| **App Router** | Next.js routing where each folder under `app/` is an address and its `page.tsx` is the page | 1 |
| **Bucket (token bucket)** | a rate limit: N tokens, one spent per request, refilled over time; empty → 429 | 5 |
| **CDN** | servers around the world that keep copies of files and serve them from near the reader (Cloudflare) | 1 |
| **cert-manager** | Kubernetes add-on that gets and renews TLS certificates (here from Let's Encrypt) | 12 |
| **Client component** | a React component marked `"use client"`: its JavaScript ships to the browser | 2 |
| **ConfigMap / Secret** | Kubernetes objects holding plain settings / sensitive settings for pods | 10 |
| **Container** | a running copy of an image | 9 |
| **CORS** | browser rule: a page may read another origin's answer only if that origin allows it | 5 |
| **CronJob** | Kubernetes object that runs a pod on a schedule (the nightly backup) | 13 |
| **CSRF** | another site making the reader's browser send a request with the reader's cookie | 7 |
| **Deployment** | Kubernetes object that keeps N identical pods running and rolls out new versions | 10 |
| **DKIM / SPF / DMARC** | email signature / allowed senders / policy when checks fail (`p=reject`) | 12 |
| **Fail fast** | stop at startup on bad config rather than fail later on a user | 5 |
| **Fail quietly** | the site's rule: if the API fails, hide the extra, never show an error | 2 |
| **Fixture** | saved test data; here the brute-force answers for the visualizer, as JSON | 3 |
| **Flyway** | runs numbered SQL migrations once each, in order, and records them | 6 |
| **Generated column** | a column Postgres computes from others (`tsv`) | 6 |
| **Generator (`function*`)** | a function that pauses at each `yield`: the visualizer's step recorder | 3 |
| **GHCR** | GitHub Container Registry, where API images are stored | 11 |
| **GIN index** | Postgres index type for "contains" searches, used for full-text search | 6 |
| **Helm / chart / values / release** | Kubernetes templating: a chart is the templates, values fill them in, a release is one install with a history | 10 |
| **HTTP-01 challenge** | proving domain ownership by serving a token at a well-known URL | 12 |
| **HttpOnly / Secure / SameSite / `__Host-`** | cookie flags: no script access / HTTPS only / not on cross-site requests / locked to this host and path `/` | 7 |
| **Hydration** | React attaching event handlers to HTML that's already on screen | 2 |
| **Image / layer** | a frozen app plus its runtime, built in cached layers | 9 |
| **Ingress / Traefik** | rules routing a hostname and path to a Service / the program that does it and terminates HTTPS | 10, 12 |
| **Init script (Postgres)** | runs only when the data volume is empty; why `.env` changes don't change an existing password | 6, 9 |
| **Interceptor** | Spring MVC code that runs before controllers (CSRF, rate limits) | 5 |
| **JdbcClient / JPA** | plain SQL from Java / object mapping; each where it fits | 5 |
| **k3s / k3d** | a small Kubernetes / k3s running inside Docker on the laptop | 10 |
| **Lazy loading** | loading code only when it's needed (`React.lazy`) | 2 |
| **Liveness / readiness / startup probe** | stuck → restart / can't serve → no traffic / still starting → wait | 10 |
| **maxUnavailable: 0** | rolling-update rule: never drop below the wanted number of ready pods | 10 |
| **MDX** | Markdown where `{ }` and `<Tags>` are JavaScript/JSX | 1 |
| **`NEXT_PUBLIC_*`** | build-time settings pasted into the browser bundle; change → rebuild | 1 |
| **ON CONFLICT (upsert)** | insert, or do nothing / update when the key exists, in one atomic statement | 6 |
| **Pod** | one or more containers sharing a network address; the unit Kubernetes runs | 10 |
| **Progressive enhancement** | it works as plain HTML first; JavaScript makes it nicer | 2 |
| **PVC / StatefulSet** | a disk claim / pods with stable names that keep their own disks | 10 |
| **RBAC / ServiceAccount** | Kubernetes permissions / an identity for programs (the CI deployer) | 11 |
| **Rollback** | going back to the previous release (`helm rollback`, or automatically on a failed deploy) | 10, 13 |
| **SCRAM-SHA-256** | how Postgres stores passwords: a one-way hash, so they can't be read back | 6 |
| **Server component** | a React component that runs only at build time and ships no JavaScript | 2 |
| **Service** | a stable name and address in front of a changing set of pods | 10 |
| **SHA tag** | an image named after the git commit it was built from | 11 |
| **Shiki** | build-time syntax colouring with VS Code's grammars | 1 |
| **Static export** | `output: "export"`: Next.js writes every page as a file, no server needed | 1 |
| **Testcontainers** | starts real services (Postgres) in Docker for tests | 8 |
| **Token (design)** | a CSS variable like `--gold` that every component uses, redefined per theme | 2 |
| **tsvector / tsquery** | Postgres full-text: a document's word stems / a search's | 6 |
| **`useSyncExternalStore`** | React hook to subscribe components to a store outside React | 2 |
| **Volume** | storage that outlives containers | 9 |
| **Workers Builds** | Cloudflare's build service: builds `site/` on every push and deploys `out/` | 1, 11 |
| **XSS** | a script injected into our own pages; `HttpOnly` limits what it can steal | 7 |
