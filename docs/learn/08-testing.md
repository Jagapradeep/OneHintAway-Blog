# 8 · Testing and quality

> ⏱ 40 min · 🧰 Docker running, JDK, `site/` installed

## 📖 The story

When the visualizer's loader was rewritten on 18 November (to make every post page lighter),
the risk was invisible: a page that *looks* the same but has a missing paragraph, or a changed
link, somewhere among 81 pages. Nobody can eyeball 81 pages. So the check was a script: build the
site before the change, build it after, and compare **every page's visible HTML**. 81 of 81
identical. Then the change shipped.

Good testing in this project is mostly that idea: **find the cheapest automatic check that would
catch the mistake you're worried about**, and make the build run it.

## 💡 The idea in 2 minutes

Each layer has its own net. Mistakes are caught as early and as cheaply as possible:

| Layer | Check | Runs | Catches |
| --- | --- | --- | --- |
| Post content | `post-kit/render.py --test`: every code block in 4 languages vs a brute force | when a post is made | wrong solutions |
| Post format | `npm run check-posts` | before every site build | broken frontmatter, missing sections, duplicate practice |
| Visualizer | `npm run check-viz` (chapter 3) | before every site build | wrong answers, lying steps, pseudocode drift |
| Types and lint | `next build` (TypeScript), `npm run lint` (ESLint) | every build / by hand | type errors, React mistakes |
| API | `./mvnw verify`: 45 tests, real PostgreSQL 16 via Testcontainers | every push touching `api/` (GitHub Actions) | wrong SQL, broken rules, security regressions |
| Emails | `MailPreviewTests` writes every email to `api/target/mail-preview/` | by hand | ugly or broken emails, before anyone gets one |
| Browser | Playwright scripts against the built site (run by Claude in a scratchpad, not in the repo) | for UI changes | layout at 360 to 1920 px, contrast, flows, sideways scroll |
| Deploy | `helm upgrade --wait --rollback-on-failure` | every API deploy | a version that never becomes healthy |
| Live | `uptime.yml` every 15 minutes | always | the site, API or stats being down |

**Why Testcontainers and not an in-memory database (H2)?** The API's correctness lives in
Postgres-specific SQL: `ON CONFLICT`, generated `tsvector` columns, `websearch_to_tsquery`,
`SELECT … FOR UPDATE` row locks, `INSERT … RETURNING`. H2 doesn't have most of these, or behaves differently. Testcontainers
starts a real `postgres:16-alpine` in Docker for the test run, Flyway applies the real
migrations, and the tests talk to it exactly as production does.

**Tests read like the rules.** Open `AccountIntegrationTests.java` and read only the method
names:

```text
aFirstCodeCreatesTheAccountAndSetsALockedDownCookie
aUsedExpiredOrWrongCodeIsRefusedTheSameWay
aCodeDiesAfterFiveWrongTries
aBurstOfGuessesSentAtOnceStillGetsOnlyFiveTries
theCodeIsEmailedWithNoDatabaseTransactionOpen
noCodeIsEmailedUnlessTheHumanCheckPasses
theAnswerIsTheSameForKnownAndUnknownAddresses
aCookieStolenBeforeSignOutIsUselessAfterIt
aChangeWithoutTheSitesOriginAndTheCustomHeaderIsRefused
deletingTheAccountNeedsAFreshCodeAndRemovesEverything
```

That list *is* the security spec from chapter 7. If a rule changes, a test name has to change too.

## 📂 Where it lives

| File | What to look for |
| --- | --- |
| `api/src/test/java/.../TestcontainersConfiguration.java` | one `@ServiceConnection` Postgres container shared by the tests |
| `api/src/test/java/.../ApiIntegrationTests.java` | every public endpoint with MockMvc |
| `api/src/test/java/.../AccountIntegrationTests.java` | sign-in, sessions, CSRF, progress, delete |
| `api/src/test/java/.../ResendMailSenderTests.java` | the email sender against a fake Resend server |
| `api/src/test/java/.../TurnstileVerifierTests.java` | the Turnstile check against a fake Cloudflare: what is sent, refused tokens, Cloudflare down |
| `site/scripts/check-posts.mjs`, `check-visualizer.mjs` | the build's own checks |
| `.github/workflows/api.yml` | job `test`: `./mvnw verify` on every push and pull request that touches `api/` |

## 🛠 Try it (25 min)

**1. Run the API tests and watch the database appear.**

```bash
cd api
./mvnw verify                      # 45 tests; in another terminal while it runs:
docker ps                          # a postgres:16-alpine you didn't start (plus Testcontainers' helper)
```

When it finishes, `docker ps` again: gone. Tests never touch your `api-postgres-1`.

**2. Read one test end to end.** `aCodeDiesAfterFiveWrongTries` in `AccountIntegrationTests.java`:
arrange (ask for a code), act (five wrong tries), assert (the right code is refused). Then find
how the test gets the code without email: `@MockitoBean private MailSender mail;` swaps the real
sender for a Mockito mock, and the test captures the code it was asked to send.

**3. See the emails without sending any.**

```bash
./mvnw -q test -Dtest=MailPreviewTests
ls target/mail-preview/            # open the .html files in a browser, in light and dark mode
```

**4. The site's checks.**

```bash
cd ../site
npm run check-posts && npm run check-viz -- --sample 50 && npm run lint
```

## 💥 Break it (10 min)

Make the API forget the five-try rule. In `AccountService.java`, change
`static final int MAX_ATTEMPTS = 5;` to `50`. Run only that test:

```bash
cd api
./mvnw -q test -Dtest='AccountIntegrationTests#aCodeDiesAfterFiveWrongTries'
```

It fails and tells you which assertion. That's the point of a test named after a rule: the
moment someone weakens the rule, the build goes red. Undo with
`git checkout -- src/main/java/com/onehintaway/api/accounts/AccountService.java`.

## 🧠 Explain it

<details>
<summary>1. Why use Testcontainers instead of H2?</summary>

The correctness is in Postgres-specific SQL (upserts, full-text search, `RETURNING`). H2 lacks
or fakes those, so tests could pass on H2 and fail in production. A real Postgres in Docker runs
the real migrations and the real SQL.
</details>

<details>
<summary>2. Which checks run in the cloud on every push, and which only on your machine?</summary>

Cloud: `check-posts`, `check-viz` and `next build` (Workers Builds); `./mvnw verify` (Actions,
when `api/` changes); the Helm rollout check; uptime. Local only: lint, the post kit's
four-language tests, mail previews, browser checks.
</details>

<details>
<summary>3. Why compare the built HTML before and after a refactor?</summary>

A refactor should change *how*, not *what*. Comparing all pages' visible output is a cheap,
complete regression test for "nothing a reader sees changed", far more thorough than looking.
</details>

<details>
<summary>4. Why are browser checks not part of the repo or CI?</summary>

They're slow, need a real browser, and are written per change. Here they're run by hand (by
Claude, in a scratchpad) for UI work. Adding a small permanent Playwright suite to CI is a good
next step if UI regressions start slipping through.
</details>

## 🎤 Interview corner

> "How do you test a Spring Boot API that depends on Postgres features?" Integration tests with
> Testcontainers: a real Postgres per test run, the real Flyway migrations, MockMvc through the
> whole stack including interceptors. Name tests after the business rule, so the test list reads
> like the spec, and inject a `Clock` and fake external services (email) so tests are fast and
> deterministic.

## ✅ You now know

- [ ] Which check catches which kind of mistake, and when it runs
- [ ] Why the tests use a real Postgres
- [ ] How to preview emails and run one test
- [ ] Why "compare the output" is a powerful regression test

---

**Next →** [9 · Docker](09-docker.md)
