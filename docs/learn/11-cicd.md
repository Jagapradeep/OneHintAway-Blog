# 11 · CI/CD: from push to production

> ⏱ 45 min · 🧰 a browser (GitHub, Cloudflare), the production kubeconfig for two read-only commands

## 📖 The story

Earlier today you asked for a commit to be pushed, and a couple of minutes later the new account
menu was on onehintaway.com. Nobody ran a build, copied files or logged in to a server. And had
that commit broken a post, the live site wouldn't have changed at all.

That's the deal CI/CD makes: **every change goes through the same checks, in the same order, every
time**, and only a change that passes them reaches readers. This chapter traces both pipelines,
step by step, from `git push`.

## 💡 The idea in 2 minutes

**CI** (continuous integration): every push is built and tested automatically.
**CD** (continuous delivery/deployment): what passes is released automatically.

There are two pipelines, one per half of the system:

```text
git push to main
 │
 ├─ Cloudflare Workers Builds (every push)          root directory: site/
 │    npm ci → prebuild (check-posts, check-viz) → next build → postbuild (write out/_headers)
 │      → wrangler deploy (upload out/; Cloudflare applies _headers)
 │    a failing check = a failed build = the live site stays on the last good version
 │
 ├─ GitHub Actions "API" (only if api/**, deploy/helm/** or the workflow changed)
 │    test   ./mvnw verify (50 tests, Testcontainers)                      on pushes AND pull requests
 │    image  docker build → ghcr.io/jagapradeep/onehintaway-api:<commit SHA>   main only, needs: test
 │    deploy helm upgrade --set api.image.tag=<SHA> --wait --rollback-on-failure
 │           then curl https://api.onehintaway.com/actuator/health/readiness   needs: image
 │           concurrency: deploy-production (one deploy at a time, none cancelled)
 │
 └─ GitHub Actions "Sync posts" (only if site/content/posts/** changed)
      export the posts as text → PUT /api/v1/admin/posts with the ADMIN_TOKEN secret

GitHub Actions "Uptime": every 15 minutes, whatever you push.
```

**Three habits that make it safe:**

1. **Tag images with the commit SHA, never `latest`.** You always know exactly which code is
   running, and rolling back means pointing at an older tag that still exists.
2. **Least privilege.** The workflow's default permission is `contents: read`. Only the `image`
   job gets `packages: write`. The deploy job uses a kubeconfig for a ServiceAccount that can only
   touch the `onehintaway` namespace (`deploy/server/cluster.yaml`), not the monitoring stack, not
   the cluster.
3. **Pull requests test but never deploy** (`if: github.event_name != 'pull_request'`), so
   anyone's PR can be checked without risking production.

## 📂 Where it lives

| File / place | What to look for |
| --- | --- |
| `.github/workflows/api.yml` | `on.paths`, the three jobs, `needs:`, `if:`, `permissions:`, `concurrency:` |
| `.github/workflows/sync-posts.yml` | triggered by post changes, or by hand |
| `.github/workflows/uptime.yml` | the 15-minute schedule; its header lists two limits |
| `deploy/server/cluster.yaml` | ServiceAccount `deployer`, a Role limited to one namespace, its token |
| GitHub → Settings → Secrets | `KUBE_CONFIG` (the deployer kubeconfig), `ADMIN_TOKEN` |
| Cloudflare → Workers & Pages → `onehintaway` → Settings → Build | root directory, build command, the `NEXT_PUBLIC_*` variables |

## 🛠 Try it (30 min, read-only)

1. **GitHub → Actions → the latest "API" run.** Open each job and match every step to a line of
   `api.yml`. Find the image tag in the `image` job's log: it's the commit SHA.
2. **GitHub → your profile → Packages → `onehintaway-api`**: one tag per deployed commit.
3. **What's running in production, and which Helm revision put it there:**
   ```bash
   kubectl --kubeconfig ~/.kube/onehintaway-prod.yaml -n onehintaway get deploy api \
     -o jsonpath="{.spec.template.spec.containers[0].image}"; echo
   helm --kubeconfig ~/.kube/onehintaway-prod.yaml -n onehintaway history onehintaway --max 5
   ```
   The tag should be the SHA of the last commit that touched `api/`
   (`git log -1 --format=%H -- api deploy/helm`).
4. **Cloudflare → Workers & Pages → `onehintaway` → Deployments**: one per push. Open the latest
   build log and find `check-posts`, `check-visualizer: 35 pattern(s)…` and the Wrangler upload.
5. **GitHub → Actions → "Uptime"**: green runs every ~15 minutes (sometimes late).

## 🧩 Think it through (15 min)

Trace each of these before opening the answer:

<details>
<summary>A. A commit makes an API test fail.</summary>

`test` goes red. `image` has `needs: test`, so it never runs; neither does `deploy`. Production
is untouched. GitHub emails you about the failed run.
</details>

<details>
<summary>B. The tests pass, but the new version crashes at startup in the cluster.</summary>

`image` pushes the tag; `deploy` runs `helm upgrade --wait --rollback-on-failure`. The new pods
never become ready; thanks to `maxUnavailable: 0` the old pods keep serving. Helm gives up after
its timeout, puts the previous release back, and the job turns red. You did exactly this in
chapter 10, step 10c(b). Then fix or revert the commit, or the next push deploys it again.
</details>

<details>
<summary>C. You push a change to one post only.</summary>

Workers Builds rebuilds the site (every push). "Sync posts" runs (the post folder changed) so
search sees it. "API" doesn't run (no `api/` or chart change).
</details>

<details>
<summary>D. You push two API commits 30 seconds apart.</summary>

Both test and build in parallel, but `concurrency: deploy-production` with
`cancel-in-progress: false` makes the second deploy wait for the first to finish. They never run
at the same time, and neither is cancelled halfway.
</details>

<details>
<summary>E. You change NEXT_PUBLIC_API_URL in Cloudflare's dashboard.</summary>

Nothing changes until the next build: the value is pasted into the bundle at build time
(chapter 1). Push a commit or press "Retry deployment".
</details>

## 🧠 Explain it

<details>
<summary>1. Why tag images with the commit SHA and never `latest`?</summary>

`latest` moves, so two pods could run different code under the same name, and you can't tell
what's deployed or roll back to a known version. A SHA is immutable and links the running image
straight to its commit.
</details>

<details>
<summary>2. Why can't the deploy job touch the monitoring namespace?</summary>

Its kubeconfig belongs to a ServiceAccount bound to a Role in the `onehintaway` namespace only
(RBAC). If the GitHub secret leaked, the damage would be limited to the app, not the cluster.
</details>

<details>
<summary>3. Why does the deploy job run a curl after Helm?</summary>

Helm checks that pods are ready *inside* the cluster. The curl checks the whole public path
(DNS, HTTPS certificate, Traefik, the Service), the way a reader reaches it.
</details>

## 🎤 Interview corner

> "Describe your deployment pipeline." Push to main: the site is built and deployed by Cloudflare
> after content and visualizer checks. The API workflow runs integration tests, builds an image
> tagged with the commit SHA, pushes it to GHCR, then a least-privilege deploy account runs
> `helm upgrade --wait --rollback-on-failure` with one deploy at a time, followed by a public
> health check. Pull requests run the tests only.

## ✅ You now know

- [ ] Both pipelines, step by step
- [ ] What each kind of failure does (and doesn't) do to production
- [ ] Why SHA tags, least privilege and PR-only tests
- [ ] Why dashboard variables need a rebuild

---

**Next →** [12 · Production edges](12-production.md)
