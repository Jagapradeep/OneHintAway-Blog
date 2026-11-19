# 9 · Docker

> ⏱ 75 min · 🧰 Docker Desktop running · Stop the API from chapter 5 first (the stack also uses port 8080)

## 📖 The story

The first build of the API image took **1 minute 37 seconds**. After a one-line code change, the
next build took **18 seconds**. Nothing clever happened in between: the Dockerfile was written so
Docker could reuse almost everything it had already done.

The other half of the story you lived in chapter 6: a database container that kept an old
password because its **volume** outlived every change to its settings. Images are rebuilt from
scratch; volumes are not. Those two facts are most of what you need to know about Docker.

## 💡 The idea in 2 minutes

- **An image** is the app plus everything it needs to run (a Java runtime, the jar, settings),
  frozen into **layers**. Each line of a Dockerfile adds a layer. Docker caches layers and reuses
  them until something they depend on changes.
- **A container** is a running copy of an image. Throw it away and start another: same result.
- **A volume** is storage that lives outside containers. Delete the container, the data stays.
- **Compose** starts several containers on a private network where they find each other by name.

**The API's Dockerfile, in three stages:**

```text
Stage 1  build    eclipse-temurin:21-jdk     copy pom.xml + mvnw → download dependencies   ← cached until pom.xml changes
                                             copy src/ → mvn package                       ← reruns on any code change
Stage 2  layers   eclipse-temurin:21-jre-alpine   split the jar into: dependencies, loader, snapshot deps, app classes
Stage 3  runtime  eclipse-temurin:21-jre-alpine   copy the four layers; user 10001; HEALTHCHECK
                                                  ← no JDK, no Maven, no source code in the final image
```

The order is the whole trick. Dependencies change rarely, so they're downloaded *before* the
source is copied. A code change only reruns the steps after `COPY src`. In the final image, the
libraries layer (60 MB) is separate from your classes (53 kB), so a new version ships 53 kB of
change, not 128 MB.

**Measured on this project:** API image 128 MB compressed (the JRE is most of it); site build
image 161 MB (mostly slides and videos); Umami's image 1.32 GB.

## 📂 Where it lives

| File | What to look for |
| --- | --- |
| `api/Dockerfile` | the three stages; a comment on every choice; `USER 10001:10001`; `HEALTHCHECK` on `/actuator/health/readiness` |
| `api/.dockerignore` | an **allowlist**: everything is refused except `.mvn/`, `mvnw`, `pom.xml`, `src/` |
| `site/Dockerfile` | builds the site; the last stage is `FROM scratch` holding only `out/` (build-only, never run) |
| `api/compose.yaml` | the database alone, for running the API from your IDE |
| `deploy/compose/docker-compose.yml` | the whole stack: Postgres + API + Umami on one network |
| `deploy/compose/postgres-init/01-umami.sh` | runs **once, on an empty volume**: creates Umami's own database and user |
| `deploy/compose/.env` | the stack's own passwords (git-ignored; `.env.example` beside it) |

## 🛠 Try it (40 min)

**1. Build it and look inside.**

```bash
docker build -t ohw-api:learn api                    # first build: a minute or two
docker image ls ohw-api                              # size
docker history ohw-api:learn | head -12              # the layers, newest first, with sizes
docker run --rm --entrypoint id ohw-api:learn        # uid=10001: not root
docker run --rm --entrypoint ls ohw-api:learn /app   # the layered jar; no source, no JDK
```

**2. Watch the cache work.** Change a string in any `.java` file (a real change; a comment-only
change gives an identical jar, so Docker reuses even the app layer) and build again. The output
says `CACHED` for the dependency step and finishes in seconds. Now add a blank line to `pom.xml`
and build: everything after `COPY pom.xml` reruns. Undo both edits.

**3. The whole stack.**

```bash
cd deploy/compose
docker compose up -d --wait        # builds the API, starts Postgres + API + Umami, waits for "healthy"
docker compose ps                  # the STATUS column says (healthy)
curl -s localhost:8080/actuator/health/readiness; echo
docker compose exec api nslookup postgres   # the service name resolves: Docker's built-in DNS
docker compose port postgres 5432  # nothing: the database isn't published to your machine at all
(cd ../../site && npm run sync-posts:compose)   # load the posts (uses deploy/compose/.env's token)
```

Umami is at http://localhost:3001 (first login `admin` / `umami`; change it).

## 💥 Break it (25 min)

1. **Running is not healthy.** `docker compose stop postgres`, then watch `docker compose ps`
   for a minute: the API container is still *running* but turns *unhealthy* (its readiness check
   asks the database). `docker compose start postgres`: it recovers by itself.
2. **Restart policy.** `docker compose kill api`, then `docker compose ps`:
   `restart: unless-stopped` brings it back.
3. **Volumes outlive containers.** `docker compose down`, then `up -d --wait`: your data is still
   there. `down -v` would delete the volume. Don't, unless you mean it.
4. **The init script runs once.** Read `postgres-init/01-umami.sh`, then answer: if you change
   `UMAMI_DB_PASSWORD` in `.env` and run `up` again, what breaks, and why? (It's the chapter 6
   password story again. Check your answer below.)

Finish with `docker compose down` (no `-v`), and remove the test image:
`docker image rm ohw-api:learn`.

## 🧠 Explain it

<details>
<summary>1. Why copy pom.xml and download dependencies before copying src/?</summary>

Layers are cached in order, and a layer is rebuilt when anything it depends on changes. The
dependency download depends only on `pom.xml`, so it stays cached through every code change.
Copy `src/` first and every code change would re-download all dependencies.
</details>

<details>
<summary>2. What do the three stages buy you?</summary>

The final image has only a JRE and the app, no JDK, Maven or source: smaller (128 MB vs over
400), faster to pull, and less for an attacker to use. The layered jar lets a new version reuse
the 60 MB libraries layer and ship only the changed classes.
</details>

<details>
<summary>3. Why run as user 10001 and not root? Why a number?</summary>

If the app is ever compromised, the attacker isn't root inside the container. The Dockerfile
creates a user `app` with UID 10001, but `USER 10001:10001` uses the number: Kubernetes'
`runAsNonRoot` check can only verify a numeric user, and a high number never clashes with a
user on the host.
</details>

<details>
<summary>4. "Running" vs "healthy": what's the difference?</summary>

Running means the process is alive. Healthy means the `HEALTHCHECK` passes: here, the readiness
endpoint, which also checks the database. An app can be alive but unable to serve.
</details>

<details>
<summary>5. You change UMAMI_DB_PASSWORD and run up again. What breaks?</summary>

Umami can't log in to Postgres. The init script that created its user ran only when the volume
was empty, so the database still has the old password. Fix with `ALTER ROLE umami PASSWORD …`
or `down -v` (losing the data).
</details>

<details>
<summary>6. Why does api/.dockerignore refuse everything by default?</summary>

The build context is sent to Docker in full. An allowlist means `.env` files, `target/`, IDE
folders and anything added later can never slip into an image by accident.
</details>

## 🎤 Interview corner

> "How do you write a good Dockerfile for a Spring Boot app?" Multi-stage: build with the JDK,
> run on a slim JRE. Copy the build file and resolve dependencies before copying the source so
> the cache survives code changes. Use Spring Boot's layered jar so libraries and app classes are
> separate layers. Run as a non-root numeric user, add a health check on the readiness endpoint,
> pin base image versions, and use a `.dockerignore` allowlist to keep secrets out.

## ✅ You now know

- [ ] Image vs container vs volume
- [ ] Why the Dockerfile's order makes rebuilds fast
- [ ] What's in the final image and what isn't
- [ ] How Compose services find each other
- [ ] Why init scripts and passwords only apply to an empty volume

---

**Next →** [10 · Kubernetes](10-kubernetes.md)
