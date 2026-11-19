# 5 · The API with Spring Boot

> ⏱ 75 min · 🧰 JDK 21+, Docker running, the database up (`cd api && docker compose up -d --wait`)

## 📖 The story

Type any email into the footer's newsletter form, a real one or a made-up one, and the API answers
the same thing every time: **202 Accepted**. Even for an address that's already subscribed. Even
for one it has never seen. Why would an API hide the truth from its own website?

Because a different answer for known and unknown addresses would let anyone test whether a person
is on the list, one request at a time. The sign-in code request does the same. This chapter is
full of choices like that: small, deliberate, and the kind interviewers ask about.

## 💡 The idea in 2 minutes

A small, boring, well-tested API. "Boring" is the compliment: every rule is enforced in one place.

**A request's path through the API:**

```text
HTTP request
  └► Tomcat (embedded web server, port 8080)
      └► Spring MVC DispatcherServlet  ── finds the controller method by path and verb
          ├► CORS rules (WebConfig)     ── which websites may read the answer in a browser
          ├► CsrfInterceptor            ── account paths only: right Origin + X-OHW-CSRF header, else 403
          ├► RateLimitInterceptor       ── a token bucket per caller per group, else 429 + Retry-After
          └► @RestController method     ── validates input, does one thing
              └► JdbcClient (plain SQL) or a JPA repository ──► PostgreSQL
```

**Packages by feature, not by layer.** Everything about stats is in `stats/`, everything about
sign-in in `accounts/`. You never hunt across `controllers/`, `services/` and `repositories/`
for one feature.

**Settings fail fast.** Every setting comes from an environment variable (with a default when a
safe one exists) and lands in one validated Java record, `AppProperties`. A missing
`VISITOR_SALT` stops the API **at startup** with a clear message, instead of failing quietly on
the first reader.

**Interfaces where the outside world is.** Email goes through a `MailSender` interface.
`MailConfig` picks `ResendMailSender` when `RESEND_API_KEY` is set and `LoggingMailSender`
otherwise. That's why your laptop prints sign-in codes in the log instead of emailing them.
Time comes from an injected `Clock` bean, so tests can move time forward to expire a code.

## 📂 Where it lives

All under `api/src/main/java/com/onehintaway/api/` unless stated.

| File | What to look for |
| --- | --- |
| `../../resources/application.properties` | every value as `${ENV_VAR:default}`; imports `api/.env` when present |
| `config/AppProperties.java` | `@Validated` record with `@NotBlank`, `@Min`: the fail-fast part |
| `config/WebConfig.java` | CORS for `/api/**`, the two interceptors and their paths |
| `visitor/RateLimitInterceptor.java` | Bucket4j buckets in a Caffeine cache, keyed on the hashed address |
| `visitor/VisitorHasher.java` | SHA-256 of salt + day + address + browser name: a visitor id that changes daily |
| `stats/StatsController.java` | `POST …/views`, `POST …/copies`, `GET …/stats` with single-statement SQL |
| `posts/SearchController.java` | full-text search (chapter 6) |
| `subscribers/` | `MailSender` + two implementations, `MailConfig`, the double opt-in flow |
| `accounts/` | sign-in, sessions, CSRF (chapter 7) |
| `ApiApplication.java` | the main class, and the `Clock` bean |

**JPA or plain SQL?** Both, each where it fits. Simple entities with no tricks (`Post`,
`Subscriber`) use JPA repositories. Anything where the SQL *is* the logic (counting with
`ON CONFLICT`, search ranking, spending a code with `UPDATE … RETURNING`) uses Spring's
`JdbcClient` with the SQL in a text block, where you can read it.

## 🛠 Try it (30 min)

Start it (from `api/`, keep this terminal's log visible):

```bash
docker compose up -d --wait          # PostgreSQL 16 on 127.0.0.1:5432
./mvnw spring-boot:run               # the API on http://localhost:8080
```

In a second terminal:

```bash
(cd site && npm run sync-posts)                          # the posts, for search and counts
curl -s localhost:8080/actuator/health/readiness; echo   # {"status":"UP",...}
```

**1. Count a view.**

```bash
curl -i -X POST localhost:8080/api/v1/posts/kadane/views      # 204
curl -i -X POST localhost:8080/api/v1/posts/kadane/views      # 204 again…
curl -s localhost:8080/api/v1/posts/kadane/stats; echo        # …but views is 1
curl -i -X POST localhost:8080/api/v1/posts/not-a-post/views  # 404: only synced posts count
```

Why only one? You're the same visitor (same address, same browser, same day), and chapter 6
shows the database line that makes the second one a no-op.

**2. Rate limits.**

```bash
for i in $(seq 1 80); do curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:8080/api/v1/posts/kadane/views; done | sort | uniq -c
curl -si -X POST localhost:8080/api/v1/posts/kadane/views | grep -i "HTTP/\|retry-after"
```

You get about seventy `204`s, then `429 Too Many Requests` with `Retry-After: 1`. Why seventy and
not sixty? The bucket holds 60 tokens and refills *greedily*, one token a second, so the ten
seconds your loop took earned about ten more. Restart the API and the count resets: the buckets
live in memory.

Now try the same loop with `curl -s "localhost:8080/api/v1/search?q=sum"`: never a 429. Read
`preHandle` in `RateLimitInterceptor.java`: **only POST, PUT and DELETE are limited**. Reads are
cheap and cacheable; writes are what spammers abuse.

**3. CORS: who may read the answer.**

```bash
curl -si -H "Origin: http://localhost:3000" "localhost:8080/api/v1/search?q=sum" | grep -i access-control-allow-origin
curl -si -H "Origin: https://evil.example"  "localhost:8080/api/v1/search?q=sum" | grep -i access-control-allow-origin   # nothing
```

Notice curl still got the results with the "evil" origin. CORS doesn't protect the server from
curl. It's a rule *browsers* follow: without that header, a page on evil.example can send the
request but can't read the answer.

**4. The 202 from the story.**

```bash
curl -si -H "Content-Type: application/json" -d '{"email":"someone@example.com"}' localhost:8080/api/v1/subscribers | head -1
curl -si -H "Content-Type: application/json" -d '{"email":"someone@example.com"}' localhost:8080/api/v1/subscribers | head -1
```

Both `202`. The API log shows what it actually did (a confirmation link the first time).

## 💥 Break it (15 min)

**1. Fail fast.** Stop the API, then start it with an empty salt:

```bash
VISITOR_SALT= ./mvnw spring-boot:run
```

It refuses to start and names the missing value. Start it normally again.

**2. Bad input.** Send an address with spaces around it:

```bash
curl -si -H "Content-Type: application/json" -d '{"email":" a@b.com "}' localhost:8080/api/v1/subscribers | head -1   # 400
```

`@Email` refuses surrounding spaces, so the site trims what readers type before sending it.
Validation at the edge means the code behind it never sees bad data.

## 🧠 Explain it

<details>
<summary>1. Why does a missing setting stop the app at startup instead of failing later?</summary>

A broken config found at startup fails the deploy, and Kubernetes keeps the old version running
(chapter 10). Found later, it fails on a reader, maybe days later, maybe silently. `@Validated`
on the properties record makes Spring check every value before the app accepts traffic.
</details>

<details>
<summary>2. Why is the rate limit keyed on the hashed address and not the browser name?</summary>

The caller chooses the browser name (`User-Agent`): a script could send a new one with every
request and get a fresh bucket each time. The address is much harder to change. It's hashed so
the raw IP is never stored, even in memory.
</details>

<details>
<summary>3. What's the difference between CORS and an interceptor that returns 403?</summary>

CORS is advice to browsers about who may *read* answers; the server still runs the request.
An interceptor actually refuses to run it. That's why the account paths have a CSRF interceptor
on top of CORS (chapter 7).
</details>

<details>
<summary>4. Why put email behind an interface?</summary>

Production sends through Resend; your laptop and the tests shouldn't send real email. With a
`MailSender` interface, one config class chooses the implementation and nothing else in the code
knows or cares. It also made Resend easy to fake in `ResendMailSenderTests`.
</details>

<details>
<summary>5. Why inject a `Clock` instead of calling `Instant.now()`?</summary>

Tests can use a fixed or moving clock: "issue a code, move time 16 minutes, the code is dead"
runs instantly and never flakes.
</details>

<details>
<summary>6. When do you pick JdbcClient over JPA?</summary>

When the SQL is the logic: upserts, ranking, `UPDATE … RETURNING`, counting. JPA is great for
loading and saving objects, but it hides the SQL, and here the exact SQL is what makes things
correct under concurrency.
</details>

## 🎤 Interview corner

> "Walk me through what happens when the site counts a view." The browser POSTs to
> `/api/v1/posts/{slug}/views` with no body (so no CORS preflight). The rate-limit interceptor
> takes a token from the caller's bucket (60, refilling one a second). The controller hashes salt, day, address and user
> agent into a visitor id and runs one `INSERT … ON CONFLICT DO NOTHING`. A repeat view hits the
> primary key and does nothing. No read-then-write, so two simultaneous requests can't
> double-count, and no raw IP is ever stored.

## ✅ You now know

- [ ] The path of a request through Tomcat, interceptors and a controller
- [ ] How settings are validated at startup
- [ ] What CORS does and doesn't do
- [ ] Why the API sometimes deliberately hides the truth (202)
- [ ] When to use JPA and when plain SQL

---

**Next →** [6 · The database](06-database.md)
