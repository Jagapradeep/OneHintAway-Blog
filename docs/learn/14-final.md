# 14 · The final boss

> ⏱ 60 min · 🧰 k3d for drills 1 to 3 · No notes for part B

## 📖 The story

You've broken the build, a migration, the cookie, the pods, the image and the config, each one on
its own. Real incidents don't arrive labelled. They arrive as "the site's weird" from a friend at
11 pm. This chapter puts everything together: first eight incidents to work out, then the whole
system explained out loud, the way an interviewer will ask for it.

## A · Incident drills (40 min)

For each one, write down three things before opening the answer: **what the reader sees**, **what
you'd check** (exact commands), and **the fix**. Do 1 to 3 for real on k3d (chapter 10).

<details>
<summary>1. The API image for the latest commit crashes at startup.</summary>

**Reader sees:** nothing; the old pods keep serving (`maxUnavailable: 0`). **Check:** the API
workflow's deploy job is red; `helm history` shows a failed revision rolled back;
`kubectl logs <new pod> --previous` shows why. **Fix:** revert or fix the commit and push. The
next push deploys again only if it's healthy.
</details>

<details>
<summary>2. Postgres's disk is full.</summary>

**Reader sees:** posts fine (static); counts, sign-in and progress fail quietly, and new writes
fail. **Check:** the `DiskFillingUp` alert in Grafana, `kubectl top`, `df -h` inside `postgres-0`,
`kubectl get pvc`. **Fix:** free space (old login_tokens are cleaned automatically; check the
WAL and backups), or grow the PVC / the server's disk.
</details>

<details>
<summary>3. Someone sets CORS_ORIGINS to a wrong value and deploys.</summary>

**Reader sees:** the site works, but no view counts, search "not available", sign-in fails, all
quietly. The API itself is healthy, so no alert fires and the rollout succeeds. **Check:**
browser DevTools console: "blocked by CORS policy"; `curl -si -H "Origin: https://onehintaway.com"
https://api.onehintaway.com/api/v1/search?q=sum | grep -i access-control`. **Fix:** correct
`api.corsOrigins` in `values-production.yaml` and push. **Lesson:** healthy isn't the same as
working.
</details>

<details>
<summary>4. Resend's API key was revoked.</summary>

**Reader sees:** "Email me a code" fails with "not available right now" (the API answers 503 when
Resend refuses). Everything else works. **Check:** API logs (Resend 401/403). **Fix:** a new key
in `/root/onehintaway.env` on the server, recreate the Secret, restart the API (runbook,
Secrets).
</details>

<details>
<summary>5. The server is unreachable.</summary>

**Reader sees:** posts load normally (Cloudflare). No counts, search, sign-in or Umami. **Check:**
the Uptime workflow is red and emails you; `ssh`; the DigitalOcean console. **Fix:** reboot from
the console; if it's gone, the runbook's "Rebuild the server from nothing" plus last night's R2
backup.
</details>

<details>
<summary>6. A reader says their sign-in code "didn't work".</summary>

**Check, most likely first:** more than 15 minutes passed; the code was already used once; five
wrong tries killed every live code for that address; the email went to spam; or three codes were
already sent this hour, so no new one came (the answer is still 202, by design). The API log shows
the 410s. **Fix:** usually "ask for a new code and type it within 15 minutes".
</details>

<details>
<summary>7. The site shows no view counts and no search, but posts load.</summary>

That's the site failing quietly, which means the API isn't answering the browser. **Check, in
order:** API health from outside (`curl https://api.onehintaway.com/actuator/health/readiness`);
if healthy, CORS (incident 3); if not, pods and logs (chapter 13); also whether the last site build
had `NEXT_PUBLIC_API_URL` set.
</details>

<details>
<summary>8. A backup was leaked. Sign every reader out at once.</summary>

The dump holds only *hashes* of sessions, so it can't be used to sign in, but act anyway:
`delete from sessions;` in production (every reader is signed out and signs in again with a code).
Consider rotating `VISITOR_SALT` too. Emails *are* in the dump: that's a data breach to take
seriously.
</details>

## B · Explain it all, no notes (20 min)

Say each one out loud, or record yourself. Aim for two minutes each. Then check against the
chapters in brackets.

1. **A reader opens a post and signs in.** From typing the address to holding a session cookie:
   DNS, Cloudflare, static HTML, hydration, the browser calling the API, CORS, Traefik, the
   Service, a pod, the CSRF check, the code, the session row, the cookie's flags.
   *(0, 1, 2, 5, 7, 10, 12)*
2. **You push a change to the API.** From `git push` to every pod running the new version:
   tests, image, SHA tag, GHCR, Helm, the rolling update, readiness, rollback if it fails.
   *(8, 9, 10, 11)*
3. **The server burns down.** What's lost, what isn't, and how you get back: the static site
   unaffected, the R2 backups, "Rebuild the server from nothing". *(0, 12, 13)*
4. **Why each choice?** Be ready to defend each against the obvious alternative:

| Choice | Alternative | Why this one |
| --- | --- | --- |
| Static site | server rendering | content changes per post, not per request; CDN speed; can't go down |
| k3s on one server | a managed cluster | real Kubernetes at blog cost; managed control planes cost more than the whole server |
| Sessions in Postgres | in memory / JWT | two replicas; sign-out must really end a session (a JWT can't be revoked) |
| Codes | passwords / magic links | no passwords to leak; mail scanners use up links |
| Two replicas | one | zero-downtime deploys, survives a pod dying |
| SHA tags | `latest` | know what runs, roll back to an exact version |
| Testcontainers | H2 | the SQL is Postgres-specific |
| Flyway | Hibernate `ddl-auto=update` | reviewed, versioned, repeatable schema changes |

## 🏆 You've finished

Tick the last box in the [course home](README.md). Then:

- Ask Claude to **quiz you**: "interview me on the One Hint Away project, mixed topics, harder
  each time".
- Pick one thing to build next that this course made you notice: a permanent Playwright test in
  CI, Alertmanager sending to your email, rate-limit buckets in Postgres so two pods share them, or
  the paywall's server-side check. Each one is a good interview story too.
