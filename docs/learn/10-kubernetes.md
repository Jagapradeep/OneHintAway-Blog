# 10 · Kubernetes

> ⏱ 3 h (do it in three sittings: 10a–10b, 10c, 10d) · 🧰 Docker Desktop, `kubectl`, `helm`, `k3d` ·
> Everything runs on the **local k3d cluster**; nothing here can touch the live site.

## 📖 The story

On 16 November, on the production cluster, an API release was deployed **on purpose with an image
tag that didn't exist**. Then everyone watched. The new pods couldn't pull their image. The
public address `https://api.onehintaway.com` kept answering `200` the whole time. And 79 seconds
later, the deploy rolled itself back with nobody touching anything.

Nothing magical happened: a handful of settings in the Helm chart, each one simple. By the end of
this chapter you'll have done the same drill on your laptop and you'll know which line saved it.

## 💡 The idea in 2 minutes

Kubernetes keeps a **desired state** ("two API pods of this image, one database with a disk, a
route from this hostname") and works continuously to make reality match it. You never start a
container yourself; you change the desired state, and controllers do the rest.

**From Compose to Kubernetes: same ideas, new names.**

| In `docker-compose.yml` | In the chart | File |
| --- | --- | --- |
| A service with one container | A **Pod**: one or more containers sharing a network address | |
| `restart: unless-stopped`, and "run 2 of these" | A **Deployment** → **ReplicaSet** → pods: keeps N identical pods alive, replaces them on a new version | `templates/api.yaml` |
| The name `postgres` resolving on the network | A **Service**: a stable name and address in front of pods that come and go | `templates/api.yaml`, `postgres.yaml` |
| A named volume | A **PersistentVolumeClaim**, owned by a **StatefulSet** (a pod with a fixed name and its own disk) | `templates/postgres.yaml` |
| `environment:` | A **ConfigMap** for plain settings, a **Secret** for sensitive ones | `templates/api.yaml` |
| `ports: 127.0.0.1:8080:8080` | An **Ingress**: host and path rules, handled by Traefik | `templates/ingress.yaml` |
| `depends_on: service_healthy` | an **init container** that waits, plus probes | `templates/_helpers.tpl` |
| `HEALTHCHECK` | **startup, liveness and readiness probes** | `templates/api.yaml` |
| `.env` + `${VAR}` | **Helm values**: one chart, a `values-*.yaml` per place | `values*.yaml` |

**The three probes, as questions:**

| Probe | Question | When it fails |
| --- | --- | --- |
| startup | "Has it finished starting?" | the other two wait; too long → restart |
| liveness | "Is it stuck?" | Kubernetes **restarts** the container |
| readiness | "Can it serve right now?" | the pod is **taken out of the Service** (no traffic), not restarted |

**The settings that saved production:** two replicas; a rolling update with `maxUnavailable: 0`
(never remove an old pod before a new one is ready); a readiness probe; and
`helm upgrade --wait --rollback-on-failure` in CI.

## 🧰 Set up the cluster

**The first time** (from the repo root; about 15 minutes, most of it the image import). It's the
same as "The same chart on the laptop" in the [runbook](../../deploy/README.md):

```bash
k3d cluster create onehintaway --agents 1 -p "8081:80@loadbalancer"   # a k3s cluster inside Docker
docker build -t onehintaway-api:dev api
k3d image import onehintaway-api:dev -c onehintaway                  # copy the image into the cluster: slow
sh deploy/scripts/create-secret.sh deploy/compose/.env               # namespace + the chart's Secret, from the compose .env
helm upgrade --install onehintaway deploy/helm/onehintaway -n onehintaway \
  -f deploy/helm/onehintaway/values-local.yaml --wait
curl -H "Host: api.localhost" http://localhost:8081/actuator/health/readiness
```

**After that:**

```bash
k3d cluster start onehintaway
kubectl config use-context k3d-onehintaway
kubectl config set-context --current --namespace onehintaway     # saves typing -n onehintaway
kubectl get pods
```

> **Git Bash can't find `k3d` or `helm`?** winget installs them where Git Bash doesn't look. Add
> their folders under `~/AppData/Local/Microsoft/WinGet/Packages/` (`k3d.k3d_…` and
> `Helm.Helm_…/windows-amd64`) to `PATH` in `~/.bashrc`.

Read `deploy/helm/onehintaway/templates/api.yaml` top to bottom once with the table above beside it.

## 🛠 10b · Look around (20 min)

```bash
kubectl get all                              # everything the chart created
kubectl get deploy api -o wide               # 2/2 ready, which image
kubectl get rs                               # the ReplicaSet the Deployment made
kubectl describe pod -l app.kubernetes.io/name=api | less    # the Events at the bottom tell the story
kubectl get endpoints api                    # the pod addresses behind the Service
kubectl exec deploy/api -- nslookup postgres # cluster DNS, like Docker's
kubectl exec -it postgres-0 -- psql -U onehintaway -d onehintaway -c "\dt"
kubectl get pvc                              # the database's disk
helm get manifest onehintaway | less         # the YAML Helm rendered from the templates
```

Answer before moving on: Which object decides there are two API pods? What would you change to
have three? Where does the API get its database password from?

## 💥 10c · Break things on purpose (60 min)

Keep a second terminal running `kubectl get pods -w` while you do these.

**a. Delete a pod.**

```bash
kubectl delete pod -l app.kubernetes.io/name=api --wait=false
```

Replacements appear within seconds: the ReplicaSet noticed the count dropped below 2. Now
`kubectl delete pod postgres-0`: it comes back with the *same name and the same data*.

**b. The production drill: a bad image.**

```bash
kubectl set image deploy/api api=onehintaway-api:nope
kubectl rollout status deploy/api --timeout=60s      # never finishes
kubectl get pods                                     # one ErrImagePull, the two old pods still Running
curl -H "Host: api.localhost" http://localhost:8081/actuator/health/readiness    # still 200
kubectl rollout undo deploy/api
```

`maxUnavailable: 0` is why the old pods stayed: the rollout can't remove one until a new one is
ready, and the new one never is.

**c. Run out of memory.**

```bash
kubectl set resources deploy/api --limits=memory=96Mi
kubectl get pods                                     # OOMKilled, then CrashLoopBackOff
kubectl describe pod <one of them> | grep -A4 "Last State"
kubectl rollout undo deploy/api
```

**d. Not ready, but not restarted.** Take the database away:
`kubectl scale sts postgres --replicas=0`. Within half a minute the API pods show `0/1` but are
*not restarted*: readiness only takes a pod out of the Service; liveness would restart it. Bring
the database back with `--replicas=1`.

**e. Break the config.** `kubectl edit configmap api-config`, change `DB_URL` to a wrong host,
then `kubectl rollout restart deploy/api`. The new pods never become ready; the old ones keep
serving. The fix is below (`helm upgrade` puts the chart's value back).

**f. Two pods, two rate limits.** Send 160 view counts through the ingress:

```bash
for i in $(seq 1 160); do curl -s -o /dev/null -w "%{http_code}\n" -X POST -H "Host: api.localhost" http://localhost:8081/api/v1/posts/kadane/views; done | sort | uniq -c
```

On one API (chapter 5) about 70 got through. Here you'll see far more, up to about double: the
Service spreads requests across both pods, and each pod counts in its own memory. That's the
"in memory, per replica" trade-off written in the README. (The posts must be synced into the k3d
database for this to return `204` rather than `404`; both prove the point, since 404s are counted
too.)

**Back to a known state** after any of these:

```bash
helm upgrade onehintaway deploy/helm/onehintaway -n onehintaway -f deploy/helm/onehintaway/values-local.yaml --wait
```

## ⎈ 10d · Helm (30 min)

```bash
helm template t deploy/helm/onehintaway -f deploy/helm/onehintaway/values-local.yaml | less
helm template t deploy/helm/onehintaway -f deploy/helm/onehintaway/values-production.yaml | grep -A12 "kind: Ingress"
helm upgrade onehintaway deploy/helm/onehintaway -n onehintaway -f deploy/helm/onehintaway/values-local.yaml --set api.replicas=3 --wait
helm history onehintaway -n onehintaway
helm rollback onehintaway 1 -n onehintaway --wait
```

Compare the two `helm template` outputs: production has TLS, the https-redirect middleware and the
backup CronJob; local doesn't. Same templates, different values.

When you're done: `k3d cluster stop onehintaway` gives your memory back.

## 🧠 Explain it

<details>
<summary>1. A pod is Running but 0/1. What does that mean, and which probe decides it?</summary>

The container is alive but not ready: the readiness probe is failing (here, usually because the
database can't be reached). The pod gets no traffic from the Service until it passes again. It
isn't restarted.
</details>

<details>
<summary>2. Why is Postgres a StatefulSet and the API a Deployment?</summary>

API pods are interchangeable: any of them can serve any request, so they can be replaced freely.
The database needs a stable identity (`postgres-0`) and its own disk that follows it across
restarts: that's what a StatefulSet with a volume claim gives.
</details>

<details>
<summary>3. Startup, liveness, readiness: what happens when each fails?</summary>

Startup: the other probes wait, and too long means a restart (protects slow starts). Liveness:
restart the container (it's stuck). Readiness: remove it from the Service (it can't serve right
now), no restart.
</details>

<details>
<summary>4. Why did the bad image never take the API down?</summary>

Rolling update with `maxUnavailable: 0`: old pods are removed only after new ones are ready. The
new pod never became ready, so both old pods kept serving. In CI, `--rollback-on-failure` then
restored the previous release automatically.
</details>

<details>
<summary>5. With two replicas, what's a caller's real rate limit, and why are per-email code limits in Postgres?</summary>

Up to about double (each pod has its own buckets). Limits that matter for security, like three
codes per email per hour, are counted in the database, which both pods share.
</details>

<details>
<summary>6. What does Helm add on top of plain YAML?</summary>

Templates with values (one chart for laptop and server), a release history with one-command
rollback, and an upgrade that can wait for readiness and roll back on failure.
</details>

## 🎤 Interview corner

> "How do you deploy with zero downtime on Kubernetes?" At least two replicas, a readiness probe
> that reflects real ability to serve, a rolling update with `maxUnavailable: 0` so capacity never
> drops, and a deploy that waits for readiness and rolls back on failure. I've drilled it: a bad
> image tag in production kept serving 200s throughout and rolled back automatically in 79
> seconds.

## ✅ You now know

- [ ] The Compose → Kubernetes mapping
- [ ] What each probe does when it fails
- [ ] Why a bad deploy doesn't take the API down
- [ ] Why rate limits double with two pods
- [ ] How Helm values make one chart serve two places

---

**Next →** [11 · CI/CD](11-cicd.md)
