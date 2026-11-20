# 13 · Operations

> ⏱ 75 min · 🧰 the production kubeconfig, helm, a browser · Writes in production: switching Grafana on and off again, and a scratch restore that never touches the real database

## 📖 The story

Prometheus on the cluster has two alerts: `ApiDown` and `DiskFillingUp`. Both work. Both fire. And
both go… nowhere. Alertmanager, the part that sends alerts to email or a phone, is switched off to
save memory on a 4 GB server. Worse: if the server itself dies, so does Prometheus, and a dead
monitor can't tell you it's dead.

So on 16 November a second, outside watcher was added: a GitHub Actions workflow that asks the
site, the API and Umami every 15 minutes, from GitHub's computers, and emails you when one
doesn't answer. **Monitoring from inside tells you why; monitoring from outside tells you that.**
You need both. That's operations: knowing it's up, finding out why it isn't, going back, and
getting the data back.

## 💡 The idea in 2 minutes

| Question | Tool here | Where |
| --- | --- | --- |
| Is it up, from a reader's point of view? | Uptime workflow (every 15 min, emails on failure) | GitHub Actions |
| Why is it slow or failing? | Logs (`kubectl logs`), resource use (`kubectl top`) | the cluster |
| What's been happening over time? | Prometheus metrics; alerts `ApiDown`, `DiskFillingUp`; Grafana dashboards (off until you switch it on) | Prometheus via `port-forward`, `grafana.onehintaway.com` |
| Where did the memory go? | `kubectl top`, `free -m`, `vmstat`, Prometheus's own series count | the cluster and the server (see "The memory diet") |
| How many readers? | Umami (privacy-friendly analytics, no cookies) | `stats.onehintaway.com` |
| Can I go back? | `helm rollback` (about a minute) | runbook "Roll back" |
| Can I get the data back? | nightly `pg_dump` CronJob → Cloudflare R2, kept 14 days | runbook "Backups" |

**A backup you've never restored is a guess.** The runbook's scratch restore downloads last
night's dump and restores it into a throwaway `restore_test` database. The first time, it
restored 31 posts with 0 errors.

## 📂 Where it lives

| File | What to look for |
| --- | --- |
| `deploy/README.md` | the runbook: "Everyday", "Roll back", "Backups" → "Restore", "When something is wrong", "Rebuild the server from nothing" |
| `deploy/server/monitoring-values.yaml` | kube-prometheus-stack trimmed: `alertmanager.enabled: false`, `grafana.replicas: 0`, the control-plane metrics dropped, 7-day retention, the two alert rules |
| `deploy/helm/onehintaway/values-production.yaml` | `api.replicas: 1`, and why deploys still have no gap |
| `deploy/helm/onehintaway/templates/backup.yaml` | the `pg-backup` CronJob and the API's ServiceMonitor (what Prometheus scrapes) |
| `.github/workflows/uptime.yml` | the outside check; its header names two limits |

## 🛠 Try it (45 min)

Point this terminal at production for this chapter only (close it afterwards):

```bash
export KUBECONFIG=~/.kube/onehintaway-prod.yaml
```

**1. Logs and resources (10 min).**

```bash
kubectl -n onehintaway get pods
kubectl -n onehintaway logs deploy/api --tail 50
kubectl top pods -A --sort-by=memory | head        # who uses the 4 GB?
kubectl top nodes
```

**2. Metrics and alerts (20 min).** Grafana is off to save memory, so switch it on first (from the
repo root, about a minute):

```bash
HELM_MON="helm upgrade monitoring prometheus-community/kube-prometheus-stack --version 93.3.0 -n monitoring -f deploy/server/monitoring-values.yaml --wait"
$HELM_MON --set grafana.replicas=1          # on
```

Open https://grafana.onehintaway.com and sign in (the admin password is in the cluster: see the
runbook's Secrets table). Dashboards → "Kubernetes / Compute Resources / Namespace (Pods)" →
`onehintaway`: memory and CPU per pod. Then **Alerting → Alert rules**: find `ApiDown` and
`DiskFillingUp` and read their `expr` in `monitoring-values.yaml`. Translate each into plain
English. (Answers below.) **When you're done, switch it off again:** `$HELM_MON` (the file says 0).

No Grafana needed for a quick look: Prometheus has its own page.
`kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090`, then
http://localhost:9090 → **Alerts** shows both rules, and **Graph** runs any query.

**3. Uptime from outside (5 min).** GitHub → Actions → **Uptime**: a run every ~15 minutes. Read
`uptime.yml`'s header for its two limits.

**4. Backups, proven (15 min).**

```bash
kubectl -n onehintaway get cronjob,jobs          # did last night's backup run?
```

Then do the **scratch restore** from the runbook's "Backups → Restore" section once, exactly as
written: download last night's dump from R2, restore it into `restore_test`, count the posts, drop
the database. It doesn't touch the real database.

**5. Rollback, rehearsed.** Do it on k3d (chapter 10), not here: `helm history`,
`helm rollback <REVISION>`, `helm history` again. In production it's the same two commands
(runbook, "Roll back").

Finally: `unset KUBECONFIG`, or close the terminal.

## 🩺 The memory diet (20 November)

The server has 4 GB. On 20 November it was at **86 %**, with 350 MB free and 630 MB pushed out
to swap. A blog shouldn't need that, so it was measured before anything was changed.

**Step 1: who uses it?** (all read-only)

```bash
kubectl top nodes                                   # the total: 3380Mi, 86 %
kubectl top pods -A --sort-by=memory | head -12     # per pod
ssh root@<server> 'free -m; ps aux --sort=-rss | head -12'   # k3s itself isn't a pod: only ps shows it
ssh root@<server> 'vmstat 1 5'                      # si/so columns near 0 = swap is parked, not thrashing
```

What it showed: k3s about 1,000 MB, Prometheus 570, Grafana 435, the two API pods 600, Umami 245,
Postgres 90. **The app itself (API + database) was a fifth of it.** The static site uses none:
it's on Cloudflare.

**Step 2: why is Prometheus so big?** Its memory is the last ~2 hours of every *series* (one
metric with one set of labels), so count them. In Prometheus's page (port-forward above):

```promql
prometheus_tsdb_head_series                        # 123,816
sort_desc(count by (job)({__name__=~".+"}))        # kubelet 64k, apiserver 48k, everything else ~11k
topk(10, count by (__name__, job)({__name__=~".+"}))
```

The answer was surprising. k3s runs the whole Kubernetes control plane in one process, so the
kubelet's metrics page carries the API server's and etcd's metrics too, and the separate API
server scrape collected the **same metrics a second time**. About 107k of the 124k series were
Kubernetes timing its own internals (`etcd_request_duration_seconds_bucket` alone: 9k), and no
dashboard or alert here uses them.

**Step 3: the fix, all in Git:**

| Change | File | Saves |
| --- | --- | --- |
| Drop the control-plane metrics from the kubelet scrape; stop scraping the API server and the stock rules built on it | `monitoring-values.yaml` | ~107k series |
| Grafana to 0 pods; on only while you use it (step 2 above) | `monitoring-values.yaml` | ~400 MB |
| One API pod in production (the laptop keeps two) | `values-production.yaml` | ~300 MB |

Why one API pod is safe: with `maxSurge: 1` and `maxUnavailable: 0`, a deploy starts the new pod,
waits until it's ready, and only then stops the old one, so there's still no gap (once the
`preStop` pause below was added). What you give
up is a spare: if the one pod crashes, the API is down for the 30–60 s it takes to restart. On a
single server, the second pod never protected against much more than that.

**The result, measured** (minutes after the change):

| | Before | After |
| --- | --- | --- |
| Node memory (`kubectl top nodes`) | 3,278 Mi, 83 % | 2,978 Mi, 76 % |
| Available (`free -m`) | 468 MB | 958 MB |
| Series scraped by Prometheus | ~124,000 | ~11,600 |
| Pods | Grafana 449 Mi, API 2 × 252 Mi | Grafana 0, API 1 × 258 Mi |

Prometheus's own memory doesn't fall at once: series it already holds stay in its in-memory block
until that is written to disk, every two hours. Check `kubectl top pods -n monitoring` a few hours
later to see its share of the saving.

**One surprise, and the fix.** Right after the one-pod deploy, a health check answered **502**.
"No gap" had a hole: when the old pod is told to stop, Traefik hears a moment later that it should
stop sending it traffic, and with only one pod *every* request in that moment hits the closing
pod. Reproduced on k3d with a request every 20 ms through three restarts: 108 failures, ~2 s per
restart. Fix: a 5-second `preStop` pause in `templates/api.yaml`, so the pod keeps serving until
routing has caught up. Same test after: 8,401 requests, all 200. (Chapter 10 explains the race.)
Lesson two: test the claim you're relying on, under load, before you trust it.

**What was not done, and why:** shorter retention (that's disk, not memory); JVM flags (small
gains, real risk of an out-of-memory crash); a bigger server (the simplest fix, kept for when
readers grow).

**Lesson:** measure before you cut. The obvious suspects (Java, Postgres) were fine; the
biggest waste was a duplicate nobody knew about, found with one query.

## 🧠 Explain it

<details>
<summary>1. What do ApiDown and DiskFillingUp say, in plain English?</summary>

`ApiDown`: fewer than one API target is up, or Prometheus can't find any at all (`absent`), so
no pod is serving metrics. `DiskFillingUp`: the root disk has less than 15 % free.
</details>

<details>
<summary>2. The API is slow but up. Where do you look first, second, third?</summary>

1. `kubectl get pods` (restarts? not ready?) and `kubectl top` (memory or CPU at the limit?).
2. `kubectl logs deploy/api` (errors, slow queries, database connection problems).
3. Metrics over the last hours, in Prometheus or Grafana (when did it start? did a deploy happen
   then?), and the database
   (`kubectl exec postgres-0 -- psql …`, e.g. `select * from pg_stat_activity`).
</details>

<details>
<summary>3. Why have both the Uptime workflow and the ApiDown alert?</summary>

`ApiDown` sees inside (pods, metrics) but lives on the same server: if the server dies, it dies
too, and with Alertmanager off it notifies no one anyway. The Uptime workflow is outside and
emails you, but only knows "up or down", not why.
</details>

<details>
<summary>4. Why restore into a scratch database first?</summary>

To prove the backup works without risking the live data. A restore over the real database would
replace everything since the dump; you only do that in a real disaster, after checking the dump.
</details>

<details>
<summary>5. After `helm rollback`, why must you also revert the commit?</summary>

`main` still contains the bad change. The next push to `api/` builds and deploys it again. The
rollback buys time; the revert (or a fix) makes it permanent.
</details>

<details>
<summary>6. Why didn't shortening Prometheus's retention help with memory?</summary>

Retention is how long old data stays *on disk*. Memory holds the recent ~2 hours of every live
series, so memory follows the number of series, not the number of days. Fewer series is the
lever; that's why the duplicate control-plane metrics were dropped.
</details>

<details>
<summary>7. The server shows 600 MB of swap in use. Is that a problem?</summary>

Not by itself. Linux moves memory nobody is touching to swap. It's a problem when it keeps moving
pages in and out: `vmstat 1 5` and look at `si` and `so`. Near zero means it's parked; steady
non-zero numbers mean the server is short of memory and everything slows down.
</details>

## 🎤 Interview corner

> "How do you know your service is healthy, and what do you do when it isn't?" An outside uptime
> check for "is it up", metrics and alerts inside for "why", logs for detail. A one-command
> rollback for bad deploys, and nightly off-site backups that are actually restore-tested into a
> scratch database. And knowing the gaps: here alerts aren't delivered, because Alertmanager is off
> to save memory.
>
> "Tell me about a time you fixed a resource problem." The server was at 86 % memory. I measured
> before changing anything: per-pod and per-process memory, then Prometheus's series count by job.
> 86 % of the series were Kubernetes' own metrics, half of them scraped twice because k3s exposes
> the control plane through the kubelet. Dropping them, running Grafana only on demand, and one
> API pod with surge-first rolling updates freed about a gigabyte without losing any metric we used.

## ✅ You now know

- [ ] How to find out where a server's memory goes
- [ ] The difference between inside and outside monitoring
- [ ] Where to look, in order, when the API misbehaves
- [ ] How to prove a backup works
- [ ] Why rollback is followed by a revert

---

**Next →** [14 · The final boss](14-final.md)
