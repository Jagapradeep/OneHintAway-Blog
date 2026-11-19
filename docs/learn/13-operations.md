# 13 · Operations

> ⏱ 60 min · 🧰 the production kubeconfig, a browser · One write in production: a scratch restore that never touches the real database

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
| What's been happening over time? | Prometheus metrics + Grafana dashboards; alerts `ApiDown`, `DiskFillingUp` | `grafana.onehintaway.com` |
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
| `deploy/server/monitoring-values.yaml` | kube-prometheus-stack trimmed: `alertmanager.enabled: false`, 7-day retention, the two alert rules |
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

**2. Metrics and alerts (15 min).** Open https://grafana.onehintaway.com and sign in (the admin
password is in the cluster: see the runbook's Secrets table). Dashboards → "Kubernetes / Compute
Resources / Namespace (Pods)" → `onehintaway`: memory and CPU per pod. Then **Alerting → Alert
rules**: find `ApiDown` and `DiskFillingUp` and read their `expr` in `monitoring-values.yaml`.
Translate each into plain English. (Answers below.)

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
3. Grafana over the last hours (when did it start? did a deploy happen then?), and the database
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

## 🎤 Interview corner

> "How do you know your service is healthy, and what do you do when it isn't?" An outside uptime
> check for "is it up", metrics and alerts inside for "why", logs for detail. A one-command
> rollback for bad deploys, and nightly off-site backups that are actually restore-tested into a
> scratch database. And knowing the gaps: here alerts aren't delivered, because Alertmanager is off
> to save memory.

## ✅ You now know

- [ ] The difference between inside and outside monitoring
- [ ] Where to look, in order, when the API misbehaves
- [ ] How to prove a backup works
- [ ] Why rollback is followed by a revert

---

**Next →** [14 · The final boss](14-final.md)
