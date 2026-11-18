# Learning lab: One Hint Away from A to Z

The project was built fast, and the learning was postponed. This lab is that learning, done on
your own code: every part of the system, in the order a request travels through it. Each lab
explains the idea briefly, points at the real files, has you run it, then has you **break it on
purpose** and explain what you saw. Breaking things is where it sticks, and it is what interviews
ask about ("what happens when…").

About 12 hours in all. Do the labs in order the first time; after that, each one stands alone.

| Lab | What you learn | Time |
| --- | --- | --- |
| [0](#lab-0-the-map) | The whole system on one page | 15 min |
| [1](#lab-1-the-static-site-and-cloudflare) | Static export, build-time checks, Cloudflare | 1 h |
| [2](#lab-2-the-api-spring-boot-and-postgresql) | Spring Boot: settings, Flyway, counting, rate limits, CORS, CSRF, sign-in, tests | 2.5 h |
| [3](#lab-3-docker) | Images, layers, health checks, Compose | 1.5 h |
| [4](#lab-4-kubernetes-on-your-laptop) | Kubernetes and Helm on a local k3d cluster | 3 h |
| [5](#lab-5-cicd-from-push-to-production) | GitHub Actions, GHCR, Workers Builds, safe rollouts | 45 min |
| [6](#lab-6-the-edges-server-dns-https-email) | The server, DNS, HTTPS certificates, email authentication | 1 h |
| [7](#lab-7-operations) | Logs, metrics, alerts, uptime, backups, rollback | 1 h |
| [8](#lab-8-put-it-together) | Incident drills and the final check | 1 h |

## Before you start

- **Tools:** Docker Desktop (running), Node 22, JDK 21 or newer, Git Bash, `kubectl`, `helm`, `k3d`.
  Commands below are for **Git Bash**. In PowerShell, `NAME=value command` becomes
  `$env:NAME="value"; command`.
- **Local files you already have:** `api/.env` and `deploy/compose/.env` (both git-ignored).
- **Port 8080** is the API's default. If something of yours is already on it, stop it first or
  use another port where a lab says so.

**Rules for the whole lab**

1. **Break things only on your laptop.** Labs 1 to 4 are entirely local.
2. **Production is read-only** unless the runbook ([README.md](README.md)) says otherwise: `get`,
   `describe`, `logs`, `top`, `history`. Every production command carries
   `--kubeconfig ~/.kube/onehintaway-prod.yaml`, so you can never hit it by accident.
3. **Never print readers' email addresses from the production database**, into a terminal you
   will screenshot, a chat, or anywhere else. Count rows; don't list them.

Each lab ends with questions. Answer them out loud or in writing *before* reading the hints.
If you can't, redo the "break it" part. For interview-style practice afterwards, the
backend-engineer-learning skill can quiz you on any lab.

---

## Lab 0: the map

Two journeys explain everything. Keep this page open while you do the other labs.

**A reader opens a post.**

```text
browser ──► onehintaway.com (Cloudflare edge)           static HTML/CSS/JS from site/out/
   │           no server of ours involved: works even if everything below is down
   │
   └─(JS, after the page loads)──► api.onehintaway.com ──► server: k3s
                                       Traefik (HTTPS, cert-manager)
                                         └─► Service "api" ──► 2 API pods (Spring Boot)
                                                                  └─► postgres-0 (StatefulSet + disk)
                                                                         └─► nightly dump ──► Cloudflare R2
```

The page is complete without the API. The API only adds extras: view counts, search, newsletter
sign-up, accounts and progress, and sign-in for the visualizer. If it fails, the extras quietly
disappear.

**You push a commit.**

```text
git push ──► GitHub
   ├─► Cloudflare Workers Builds (always): npm run build in site/ ──► new site version
   ├─► Actions "API" (if api/ or deploy/helm/ changed): test ──► image to GHCR ──► helm upgrade
   └─► Actions "Sync posts" (if posts changed): PUT the post list to the API (search)
Actions "Uptime" runs every 15 minutes, whatever you push.
```

| Piece | Where it lives | Lab |
| --- | --- | --- |
| Site | `site/` (Next.js 16, static export) | 1 |
| API | `api/` (Spring Boot 4.1, Java 21, PostgreSQL 16) | 2 |
| Images and the laptop stack | `api/Dockerfile`, `site/Dockerfile`, `deploy/compose/` | 3 |
| Cluster objects | `deploy/helm/onehintaway/` | 4 |
| Pipelines | `.github/workflows/`, Cloudflare Workers Builds | 5 |
| Server, certificates, monitoring | `deploy/server/` | 6, 7 |
| Day-to-day commands | `deploy/README.md` (the runbook) | 7 |

---

## Lab 1: the static site and Cloudflare

**The idea.** `next build` with `output: "export"` turns every page into a plain file in `out/`.
Nothing runs on a server when a reader visits: Cloudflare hands out files from its edge. That is
why the site is fast, free to host, and can't be taken down by the API.

**Read:** `site/next.config.ts` (`output: "export"`, `trailingSlash`), `site/wrangler.jsonc`
(files only, no Worker code), `site/lib/api.ts` (how the site calls the API).

**Do (20 min)**

```bash
cd site
npm run build                 # runs check-posts and check-viz first (prebuild), then builds out/
ls out out/posts | head       # one folder per page, each with an index.html
python -m http.server 8765 -d out
```

Open http://localhost:8765/posts/kadane/ and use **View page source**: the whole post (text,
coloured code, tables) is already in the HTML. In DevTools, turn JavaScript off and reload: the
post still reads fine. Only the extras (tabs, slides, search) need scripts.

Now look at the real site:

```bash
curl -sI https://onehintaway.com/ | grep -i "server\|cf-ray\|content-type"   # Cloudflare answers
curl -sI https://onehintaway.com/about | head -3                              # what happens without the slash?
```

**Break it (20 min)**

1. **A bad post fails the build.** In `content/posts/00-start-here.mdx` change `slides: 7` to
   `slides: 6`, then `npm run check-posts`. Read the error. Put it back
   (`git checkout -- content/posts/00-start-here.mdx`). This is why a broken post can never reach
   the live site: Workers Builds runs the same `prebuild`.
2. **The API is optional.** `lib/api.ts` gives up after 4 seconds and returns `null` instead of
   throwing. You will see this live at the end of Lab 2.

**Explain**

1. Why can't the site go down when the server goes down?
2. What does "build time" vs "request time" mean here, and which one does Shiki's code colouring
   use? What does that save the reader?
3. Why is `NEXT_PUBLIC_API_URL` baked in at build time, and what must you do after changing it in
   Cloudflare?
4. What does the `prebuild` script protect against?

---

## Lab 2: the API (Spring Boot and PostgreSQL)

**The idea.** A small, boring, well-tested API: settings from environment variables, the schema
owned by Flyway migrations, counting done by the database, rate limits, and accounts without
passwords. Read the "API" section of the root README first (15 minutes); this lab makes each of
its rules happen in front of you.

**Start it** (two terminals, from `api/`):

```bash
docker compose up -d --wait          # terminal 1: PostgreSQL 16 on 127.0.0.1:5432 (api/compose.yaml)
./mvnw spring-boot:run               # terminal 1: the API on http://localhost:8080 (keep this log visible)
(cd ../site && npm run sync-posts)   # terminal 2: copy the posts into the API (uses ADMIN_TOKEN from api/.env)
curl -s localhost:8080/actuator/health/readiness     # {"status":"UP",...}
```

A shortcut for the database, used below:

```bash
db() { docker exec -i api-postgres-1 psql -U onehintaway -d onehintaway -c "$1"; }
```

### 2a. Settings, and failing fast (15 min)

**Read:** `src/main/resources/application.properties` (every value comes from an env var with a
default) and `config/AppProperties.java` (a validated record).

**Break it.** Stop the API, then start it with an empty salt:

```bash
VISITOR_SALT= ./mvnw spring-boot:run
```

It refuses to start and says which value is missing. That is the point: a bad config fails
loudly at startup, not quietly on the first reader. Start it normally again.

### 2b. Flyway owns the schema (25 min)

**Read:** `src/main/resources/db/migration/V1__init.sql`, `V2__accounts.sql`, `V3__sign_in_codes.sql`.
`spring.jpa.hibernate.ddl-auto=validate`: Hibernate never changes the schema, it only checks it.

```bash
db "select version, description, checksum, success from flyway_schema_history order by installed_rank"
db "\dt"
```

**Break it (local only).**

1. Add a comment line at the end of `V3__sign_in_codes.sql` and restart the API. It refuses:
   *checksum mismatch*. An applied migration is history; you never edit it. Undo with
   `git checkout -- src/main/resources/db/migration/V3__sign_in_codes.sql`.
2. The right way to change the schema: create `V4__learn.sql` with
   `alter table posts add column learn_note text;`, restart, and look at
   `flyway_schema_history` again. Then clean up, in this order: delete the file,
   `db "alter table posts drop column learn_note"`,
   `db "delete from flyway_schema_history where version = '4'"`, restart.
   (If you only delete the file, Flyway refuses: a migration it applied no longer exists.)

### 2c. Let the database count (20 min)

**Read:** `stats/StatsController.java`, `visitor/VisitorHasher.java`.

```bash
curl -i -X POST localhost:8080/api/v1/posts/kadane/views     # 204
curl -i -X POST localhost:8080/api/v1/posts/kadane/views     # 204 again...
curl -s localhost:8080/api/v1/posts/kadane/stats             # ...but views is 1
db "select * from post_views limit 3"                        # no address anywhere, only a hash
curl -i -X POST localhost:8080/api/v1/posts/not-a-post/views # 404: only synced posts are counted
```

The second view hit the primary key `(post, day, visitor)` and `ON CONFLICT DO NOTHING` skipped
it. No read-then-write, so two requests at the same instant can't double-count.

### 2d. Rate limits (15 min)

**Read:** `visitor/RateLimitInterceptor.java`: one token bucket per caller per group.

```bash
for i in $(seq 1 65); do curl -s -o /dev/null -w "%{http_code} " "localhost:8080/api/v1/search?q=sum"; done; echo
curl -si "localhost:8080/api/v1/search?q=sum" | grep -i "HTTP/\|retry-after"
```

You get sixty `200`s, then `429` with `Retry-After`. Restart the API and the count resets: the
buckets live in memory. Keep that in mind for Lab 4 (two pods = two separate counts).

### 2e. CORS and CSRF (20 min)

**Read:** `config/WebConfig.java`, `accounts/CsrfInterceptor.java`.

```bash
# CORS is a browser rule: the server only *says* who may read its answers.
curl -si -H "Origin: http://localhost:3000"   "localhost:8080/api/v1/search?q=sum" | grep -i access-control-allow-origin
curl -si -H "Origin: https://evil.example"    "localhost:8080/api/v1/search?q=sum" | grep -i access-control-allow-origin   # nothing
# CSRF: a change to an account path needs the site's Origin AND the custom header.
curl -si -X POST localhost:8080/api/v1/auth/sign-out | head -1                                                   # 403
curl -si -X POST -H "Origin: http://localhost:3000" -H "X-OHW-CSRF: 1" localhost:8080/api/v1/auth/sign-out | head -1   # 204
```

Notice that curl got the search results even with the "evil" origin. CORS doesn't protect the
server from curl; it stops *another website's page* from reading answers in a reader's browser.
CSRF is the other direction: another site *sending* a request with the reader's cookie.

### 2f. Sign-in by code, and sessions (30 min)

**Read:** `accounts/AccountService.java` (`sendCode`, `exchange`), `accounts/SessionCookie.java`.

```bash
H='-H Origin:http://localhost:3000 -H X-OHW-CSRF:1 -H Content-Type:application/json'
curl -si $H -d '{"email":"me@example.com"}' localhost:8080/api/v1/auth/code | head -1     # 202
# copy the code from the API log line "Sign-in code for me@example.com: ......"
curl -si $H -c jar -d '{"email":"me@example.com","code":"PUT-IT-HERE"}' localhost:8080/api/v1/auth/session
grep -i host jar                                     # the cookie: __Host- prefix, HttpOnly, Secure
curl -s -b jar localhost:8080/api/v1/auth/me         # who am I
db "select purpose, attempts, used_at is not null as used from login_tokens"
db "select left(token_hash, 12) as hash, expires_at from sessions"     # only hashes are stored
```

**Break it.**

1. Ask for a new code, then send a wrong code five times, then the right one: `410` every time.
   Five wrong tries kill every live code for that address.
2. Use the same right code twice: the second is `410` (one use only).
3. `curl -s $H -b jar -X POST localhost:8080/api/v1/auth/sign-out`, then `/me` with the same jar:
   `401`. Signing out deletes the session row, so a copied cookie dies too.

Clean up: `db "delete from users where email = 'me@example.com'"` and
`db "delete from login_tokens where email = 'me@example.com'"`.

### 2g. The site against your API (15 min)

```bash
cd ../site
NEXT_PUBLIC_API_URL=http://localhost:8080 NEXT_PUBLIC_ACCOUNTS=on npm run dev
```

Open http://localhost:3000/posts/kadane/: a view count appears, search works, Sign in works
(code from the API log). Now **stop the API** and reload: the count disappears, search says it
isn't available, posts read normally, and the visualizer plays (it fails open). Nothing errors.
That is `lib/api.ts` doing its job.

### 2h. Tests with real PostgreSQL (20 min)

```bash
cd ../api
./mvnw verify            # in another terminal while it runs: docker ps  (a throwaway postgres appears)
```

Read one test end to end in `src/test/java/.../AccountIntegrationTests.java`
(`aCodeDiesAfterFiveWrongTries` is a good one), then `TestcontainersConfiguration.java`.
The tests use the real migrations against a real Postgres, not an in-memory imitation.

**Explain**

1. Why does a missing setting stop the app at startup instead of failing later?
2. Why must you never edit an applied migration? How do you undo a bad one in production?
3. How does the API count one view per visitor per day without storing who the visitor is?
4. Why is the rate limit keyed on the address and not the browser name?
5. What is the difference between CORS and CSRF? Which one does curl ignore, and why is that fine?
6. Why are sessions in Postgres and not in the pod's memory?
7. A 6-digit code is guessable. What makes guessing useless here?
8. Why do the tests use Testcontainers instead of H2?

---

## Lab 3: Docker

**The idea.** An image is the app plus everything it needs, frozen, built in layers that are
cached. A container is a running copy. Compose starts several containers on a private network.
Read the "Docker" section of the root README first.

**Read:** `api/Dockerfile` (three stages, with comments on every choice), `api/.dockerignore`,
`deploy/compose/docker-compose.yml`.

### 3a. Build it and look inside (30 min)

```bash
docker build -t ohw-api:learn api                    # first build: a few minutes
docker image ls ohw-api                              # size
docker history ohw-api:learn | head -12              # the layers, newest first
docker run --rm --entrypoint id ohw-api:learn        # uid=10001: not root
docker run --rm --entrypoint ls ohw-api:learn /app   # the layered jar, no source, no JDK
```

**Layer caching.** Add a comment to any `.java` file and build again. Watch the output: the step
that downloads dependencies says `CACHED`, and the build is several times faster. Change
`pom.xml` (add a blank line) and build again: now everything after it reruns. Undo both edits.

### 3b. The whole stack with Compose (30 min)

Stop the API from Lab 2 first (it uses port 8080).

```bash
cd deploy/compose
docker compose up -d --wait        # builds the API, starts API + Postgres + Umami, waits for "healthy"
docker compose ps                  # look at the STATUS column
curl -s localhost:8080/actuator/health/readiness
docker compose exec api nslookup postgres   # the service name resolves: Docker's DNS
docker compose port postgres 5432  # nothing: the database is not published to your machine
```

**Break it.**

1. `docker compose stop postgres`, then watch `docker compose ps` for a minute: the API is still
   running but turns `unhealthy` (readiness checks the database). `docker compose start postgres`
   and it recovers by itself.
2. `docker compose kill api`, then `docker compose ps`: `restart: unless-stopped` brings it back.
3. `docker compose down`, then `up -d --wait` again: your data is still there (named volume).
   `down -v` would delete it. Don't, unless you mean it.

Finish with `docker compose down`.

**Explain**

1. Why copy `pom.xml` and download dependencies *before* copying `src/`?
2. What do the three stages buy you? What is in the final image, and what isn't?
3. Why run as user 10001 and not root? Why a number and not a name?
4. "Running" vs "healthy": what is the difference, and which endpoint decides it?
5. How does the API find the database without an IP address?
6. Why does `api/.dockerignore` refuse everything by default?

---

## Lab 4: Kubernetes on your laptop

**The idea.** Kubernetes keeps a *desired state* (two API pods, one database with a disk, a
route from a hostname) and works continuously to make reality match it. Helm writes that desired
state from templates and values. Everything here runs on the **local k3d cluster**, so nothing can
hurt the live site. Read the "Kubernetes and production" section of the root README first.

Create or start the cluster (from the repo root, Docker Desktop running). The first time, follow
"The same chart on the laptop" at the end of [README.md](README.md); after that:

```bash
k3d cluster start onehintaway
kubectl config use-context k3d-onehintaway
kubectl config set-context --current --namespace onehintaway     # saves typing -n onehintaway
kubectl get pods
```

### 4a. From Compose to Kubernetes: the same ideas, new names

| In `docker-compose.yml` | In the chart | File |
| --- | --- | --- |
| A service with one container | A **Pod**: one or more containers sharing a network address | |
| `restart: unless-stopped`, and "run 2 of these" | A **Deployment**: keeps N identical pods alive and replaces them on a new version | `templates/api.yaml` |
| The service name `postgres` resolving on the network | A **Service**: a stable name and address in front of pods that come and go | `templates/api.yaml`, `postgres.yaml` |
| A named volume | A **PersistentVolumeClaim**, owned by a **StatefulSet** (a pod with a fixed name and its own disk) | `templates/postgres.yaml` |
| `environment:` | A **ConfigMap** for plain settings, a **Secret** for sensitive ones | `templates/api.yaml` |
| `ports: 127.0.0.1:8080:8080` | An **Ingress**: host and path rules handled by Traefik | `templates/ingress.yaml` |
| `depends_on: service_healthy` | An **init container** that waits, plus probes | `templates/_helpers.tpl` |
| `HEALTHCHECK` | **startup, liveness and readiness probes** | `templates/api.yaml` |
| `.env` + `${VAR}` | **Helm values**: one chart, different `values-*.yaml` per place | `values*.yaml` |

Read `templates/api.yaml` top to bottom once with this table beside it.

### 4b. Look around (20 min)

```bash
kubectl get all                              # everything the chart created
kubectl get deploy api -o wide               # 2/2 ready, which image
kubectl get rs                               # the ReplicaSet the Deployment made
kubectl describe pod -l app.kubernetes.io/name=api | less    # events at the bottom tell the story
kubectl get endpoints api                    # the pod addresses behind the Service
kubectl exec deploy/api -- nslookup postgres # cluster DNS, like Docker's
kubectl exec -it postgres-0 -- psql -U onehintaway -d onehintaway -c "\dt"
kubectl get pvc                              # the database's disk
helm get manifest onehintaway | less         # the YAML Helm rendered from the templates
```

Questions to answer: Which object decides there are two API pods? What would you change to
have three? Where does the API get its database password from?

### 4c. Break things on purpose (60 min)

Keep a second terminal running `kubectl get pods -w` while you do these.

**a. Delete a pod.** `kubectl delete pod -l app.kubernetes.io/name=api --wait=false`
A replacement appears within seconds: the ReplicaSet noticed the count dropped below 2.
Now `kubectl delete pod postgres-0`: it comes back with the *same name and the same data*.

**b. Roll out a bad image.**
```bash
kubectl set image deploy/api api=onehintaway-api:nope
kubectl rollout status deploy/api --timeout=60s      # it never finishes
kubectl get pods                                     # one ErrImagePull, the two old pods still Running
curl -H "Host: api.localhost" http://localhost:8081/actuator/health/readiness    # still 200
kubectl rollout undo deploy/api
```
`maxUnavailable: 0` is why the old pods stayed. This is what saved production in the drill.

**c. Run out of memory.**
```bash
kubectl set resources deploy/api --limits=memory=96Mi
kubectl get pods                                     # OOMKilled, then CrashLoopBackOff
kubectl describe pod <one of them> | grep -A4 "Last State"
kubectl rollout undo deploy/api
```

**d. Fail readiness without crashing.** Scale Postgres away: `kubectl scale sts postgres --replicas=0`
Within half a minute the API pods show `0/1` but are *not restarted*: readiness only takes a
pod out of the Service. Liveness would restart it. Bring the database back with `--replicas=1`.

**e. Break the config.** `kubectl edit configmap api-config`, change `DB_URL` to a wrong host,
then `kubectl rollout restart deploy/api`. The new pods never become ready, the old ones keep
serving. Fix it with `helm upgrade` (below), which puts the chart's value back.

**f. Two pods, two rate limits.** Repeat the search loop from Lab 2d through the ingress
(`-H "Host: api.localhost" http://localhost:8081/...`) with 130 requests. You get more than 60
`200`s: each pod counts on its own. That is the "in memory, per replica" note in the README.

After any of these, return to the known state:
```bash
helm upgrade onehintaway deploy/helm/onehintaway -n onehintaway -f deploy/helm/onehintaway/values-local.yaml --wait
```

### 4d. Helm (30 min)

```bash
helm template t deploy/helm/onehintaway -f deploy/helm/onehintaway/values-local.yaml | less
helm template t deploy/helm/onehintaway -f deploy/helm/onehintaway/values-production.yaml | grep -A12 "kind: Ingress"
helm upgrade onehintaway deploy/helm/onehintaway -n onehintaway -f deploy/helm/onehintaway/values-local.yaml --set api.replicas=3 --wait
helm history onehintaway -n onehintaway
helm rollback onehintaway 1 -n onehintaway --wait
```

Compare the two `helm template` outputs: the production one has TLS, the redirect middleware
and the backup CronJob; the local one doesn't. Same templates, different values.

When you're done: `k3d cluster stop onehintaway` frees the memory.

**Explain**

1. A pod is `Running` but `0/1`. What does that mean, and which probe decides it?
2. Why is Postgres a StatefulSet and the API a Deployment?
3. Startup, liveness, readiness: what question does each answer, and what happens when each fails?
4. Why did the bad image never take the API down?
5. Two replicas each keep rate-limit counters in memory. What does a reader's real limit become,
   and why are sign-in codes per email counted in Postgres instead?
6. What does Helm add on top of plain YAML files?

---

## Lab 5: CI/CD, from push to production

**The idea.** Nobody deploys by hand. A push runs the same tests you ran, builds an image named
after the commit, and rolls it out with an automatic rollback if the new pods never become ready.

**Read:** `.github/workflows/api.yml` (three jobs: `test`, `image`, `deploy`), `sync-posts.yml`,
`uptime.yml`, and `deploy/server/cluster.yaml` (the limited account CI deploys with).

**Do (30 min, read-only)**

1. GitHub → **Actions** → the latest **API** run. Open each job and match every step to a line in
   `api.yml`. Find the image tag: it is the commit SHA.
2. GitHub → your profile → **Packages** → `onehintaway-api`: one tag per deployed commit.
3. In production, check which image is running and which Helm revision put it there:
   ```bash
   kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml -n onehintaway get deploy api -o jsonpath="{.spec.template.spec.containers[0].image}"; echo
   helm --kubeconfig ~/.kube/onehintaway-prod.yaml -n onehintaway history onehintaway --max 5
   ```
   The tag should be the SHA of the last commit that touched `api/`.
4. Cloudflare dashboard → Workers & Pages → `onehintaway` → **Deployments**: one per push, each
   built from `site/` with the build variables (`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_ACCOUNTS`, …).

**Think it through (15 min).** Trace a broken commit: the tests fail, so `image` never runs and
production is untouched. Now a commit whose tests pass but whose pods crash at startup: `helm
upgrade --wait --rollback-on-failure` waits up to six minutes, sees the new pods never become
ready, puts the previous release back, and the job turns red. You rehearsed exactly that in Lab
4c(b).

**Explain**

1. Why tag images with the commit SHA and never `latest`?
2. What stops two pushes from deploying at the same time?
3. Why does a pull request run the tests but never deploy?
4. The deploy account can't touch the `monitoring` namespace. Why limit it, and how (RBAC)?
5. Which pipeline deploys the site, which deploys the API, and what happens to each when you
   change only a post?

---

## Lab 6: the edges (server, DNS, HTTPS, email)

**The idea.** Everything that sits between the internet and your pods: a hardened server, DNS
records pointing at it, certificates that renew themselves, and email that Gmail trusts.

### 6a. The server (15 min, read-only)

Read `deploy/server/01-harden.sh` and `02-k3s.sh`: SSH keys only, automatic security updates, a
firewall that leaves only SSH, web and the Kubernetes API open, then k3s. Then:

```bash
kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml get nodes -o wide
kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml top nodes
```

### 6b. DNS and HTTPS (20 min)

```bash
nslookup onehintaway.com            # Cloudflare's addresses (the site)
nslookup api.onehintaway.com        # your server's address
curl -sv https://api.onehintaway.com/actuator/health/readiness 2>&1 | grep -i "issuer\|expire\|subject:"
kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml get certificate -A
kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml -n onehintaway describe certificate api-tls | tail -15
```

The site and the API resolve to different places: the site to Cloudflare, the API straight to
your server (no orange-cloud proxy, so cert-manager's Let's Encrypt check can reach it). The
certificate's issuer is Let's Encrypt, and cert-manager renews it a month before it expires.

### 6c. Email that lands in the inbox (25 min)

```bash
nslookup -type=TXT _dmarc.onehintaway.com              # DMARC policy: p=reject
nslookup -type=TXT resend._domainkey.onehintaway.com   # DKIM public key (Resend signs with the private one)
nslookup -type=TXT send.onehintaway.com                # SPF: who may send for this domain
```

Then sign in on the live site, open the code email in Gmail on a computer, **⋮ → Show original**:
SPF, DKIM and DMARC should all say `PASS`. That is why it isn't in spam.

Two lessons this project learned the hard way, worth knowing in any email job:

- Gmail's dark mode on Android inverts any image up to 64 px wide, so the email header is one
  180 px image (logo and name). Preview every email with
  `./mvnw -q test -Dtest=MailPreviewTests` (see `api/README.md`).
- The sign-in email carries a code, not a link: company mail filters open links (some even run the
  page's script), which would use a one-time link up before the reader gets to it.

**Explain**

1. What are SPF, DKIM and DMARC, in one sentence each? What does `p=reject` do to a forged email?
2. How does cert-manager prove to Let's Encrypt that you own `api.onehintaway.com`?
3. Why is the API not behind Cloudflare's proxy while the site is?
4. What does the firewall leave open, and why is the Kubernetes API port safe to expose?

---

## Lab 7: operations

**The idea.** Running it is more than deploying it: knowing it's up, finding out why it isn't,
going back to a good version, and getting the data back. The runbook ([README.md](README.md)) has
every command; this lab has you use them once while nothing is on fire.

Set the production kubeconfig for this lab only, then close the terminal afterwards:

```bash
export KUBECONFIG=~/.kube/onehintaway-prod.yaml
```

### 7a. Logs and resources (10 min)

```bash
kubectl -n onehintaway get pods
kubectl -n onehintaway logs deploy/api --tail 50
kubectl top pods -A --sort-by=memory | head
```

### 7b. Metrics and alerts (20 min)

Open `grafana.onehintaway.com` and sign in (the admin password is in the runbook's Secrets
table). Dashboards → "Kubernetes / Compute Resources / Namespace (Pods)" → `onehintaway`: memory
and CPU per pod. Then **Alerting → Alert rules**: find `ApiDown` and `DiskFillingUp`, and read
their rules in `deploy/server/monitoring-values.yaml`. Read the `alertmanager` section of the same
file to see where an alert goes.

### 7c. Uptime from outside (5 min)

GitHub → Actions → **Uptime**: a run every 15 minutes that asks the site, the API and Umami from
outside. Read `uptime.yml`'s header for its two limits (late runs, and schedules switched off after
60 days without a commit).

### 7d. Backups, and proving they work (20 min)

```bash
kubectl -n onehintaway get cronjob,jobs          # did last night's backup run?
```

Then do the **scratch restore** from the runbook's Backups section once: download last night's
dump from R2, restore it into a `restore_test` database, count the posts, drop the database. This
is the one write you make in production in this lab; it doesn't touch the real database. A backup
that has never been restored is a guess.

### 7e. Rollback drill (on your laptop)

Do it on k3d (Lab 4), so production stays untouched: `helm history`, `helm rollback <REVISION>`,
`helm history` again. In production it is the same two commands (runbook, "Roll back"), followed
by reverting the bad commit, or the next push deploys it again.

**Explain**

1. The API is slow but up. Where do you look first, second and third?
2. What is the difference between the Uptime workflow and the `ApiDown` alert? Why have both?
3. Why does a restore go into a scratch database first?
4. After `helm rollback`, why must you also revert the commit?

---

## Lab 8: put it together

### 8a. Incident drills (40 min)

For each, write down: what the reader sees, what you'd check (exact commands), and the fix. Then
check your answer against the runbook's "When something is wrong" table and the labs above.
Do (1) to (3) for real on k3d.

1. The API image for the latest commit crashes at startup.
2. Postgres's disk is full.
3. Someone changes `CORS_ORIGINS` to a wrong value and deploys.
4. Resend's API key was revoked.
5. The server is unreachable.
6. A reader says their sign-in code "didn't work".
7. The site shows no view counts and no search, but posts load.
8. A backup was leaked: sign every reader out at once.

### 8b. The final check

Without notes, explain end to end, as you would in an interview:

1. **A reader opens a post and signs in.** From typing the address to the session cookie: DNS,
   Cloudflare, static HTML, the browser calling the API, CORS, Traefik, the Service, a pod, the
   CSRF check, the code, the session row, the cookie's flags.
2. **You push a change to the API.** From `git push` to every pod running the new version:
   tests, image, tag, GHCR, Helm, the rolling update, readiness, rollback if it fails.
3. **The server burns down.** What is lost, what isn't, and how you get back (runbook,
   "Rebuild the server from nothing", and the R2 backups).
4. **Why each choice?** Static site vs server rendering; k3s vs a managed cluster; sessions in
   Postgres; codes instead of passwords and instead of links; two replicas; SHA tags.

### 8c. Progress

- [ ] Lab 0: the map
- [ ] Lab 1: static site and Cloudflare
- [ ] Lab 2: the API
- [ ] Lab 3: Docker
- [ ] Lab 4: Kubernetes on the laptop
- [ ] Lab 5: CI/CD
- [ ] Lab 6: server, DNS, HTTPS, email
- [ ] Lab 7: operations (including one scratch restore)
- [ ] Lab 8: drills and the final check
