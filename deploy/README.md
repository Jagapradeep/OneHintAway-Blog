# Deploy: runbook

How the backend runs in production and what to type when something needs doing.
The why behind each piece is in the [root README](../README.md#-kubernetes-and-production);
the course that teaches the whole project, top to bottom, is in [docs/learn/](../docs/learn/README.md).

| Folder | What it is |
| --- | --- |
| `compose/` | The whole stack in Docker Compose, for the laptop |
| `helm/onehintaway/` | The Helm chart: API, PostgreSQL, Umami, ingress, nightly backup. Used on the laptop (k3d) and on the server |
| `server/` | One-time server setup: hardening, k3s, cluster-level objects, monitoring values |
| `scripts/create-secret.sh` | Creates the chart's Secret from an env file (laptop) |

## What runs where

| Address | What | Where it runs |
| --- | --- | --- |
| `onehintaway.com` | The site | Cloudflare (does not depend on the server) |
| `api.onehintaway.com` | The API: only `/api` and `/actuator/health` are public | Server, namespace `onehintaway` |
| `stats.onehintaway.com` | Umami analytics | Server, namespace `onehintaway` |
| `grafana.onehintaway.com` | Dashboards and alerts; **off by default** (see "Grafana on and off") | Server, namespace `monitoring` |

One server (Ubuntu 24.04, 2 vCPU, 4 GB) runs k3s. Traefik takes ports 80 and 443 and
cert-manager keeps Let's Encrypt certificates renewed.

## Two kubeconfigs (both on the laptop, neither in Git)

| File | Can do | Used by |
| --- | --- | --- |
| `~/.kube/onehintaway-prod.yaml` | Everything (cluster admin) | You, for the commands below |
| `~/.kube/onehintaway-deployer.yaml` | Change the `onehintaway` namespace only | GitHub Actions (secret `KUBE_CONFIG`) |

Every command below is for production and assumes this, in PowerShell:

```powershell
$env:KUBECONFIG = "$HOME\.kube\onehintaway-prod.yaml"
```

Close the terminal (or `Remove-Item Env:KUBECONFIG`) to go back to the local cluster.

## Everyday

```bash
kubectl -n onehintaway get pods                    # is everything Running?
kubectl -n onehintaway logs deploy/api --tail 100  # API logs (add -f to follow)
kubectl top nodes; kubectl top pods -A             # memory and CPU
helm -n onehintaway history onehintaway            # what was deployed, when
```

### Grafana on and off

Grafana runs 0 pods to save ~400 MB of the server's 4 GB. Its disk, login, address and
certificate stay. From the repo root:

```bash
helm upgrade monitoring prometheus-community/kube-prometheus-stack --version 93.3.0 -n monitoring \
  -f deploy/server/monitoring-values.yaml --wait --set grafana.replicas=1    # on
# ...use https://grafana.onehintaway.com...
helm upgrade monitoring prometheus-community/kube-prometheus-stack --version 93.3.0 -n monitoring \
  -f deploy/server/monitoring-values.yaml --wait                            # off again
```

For a quick look without Grafana: `kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090`
and open http://localhost:9090 (alerts, and any query).

## Deploy

Push to `main`. If `api/` or `deploy/helm/` changed, the **API** workflow tests, builds
`ghcr.io/jagapradeep/onehintaway-api:<commit>`, and runs `helm upgrade`. If the new pods
don't become ready within six minutes, Helm puts the previous version back and the workflow
fails. Old pods are only removed after new ones are ready, so readers never see a broken one.

A change under `site/content/posts/` also runs **Sync posts**, which refreshes search.
Start it by hand under Actions → Sync posts → Run workflow.

## Roll back (about a minute)

```bash
helm -n onehintaway history onehintaway            # pick the last good REVISION
helm -n onehintaway rollback onehintaway <REVISION> --wait
```

Then revert the bad commit, or the next push deploys it again.

## Backups

Every night at 02:00 India time the `pg-backup` CronJob dumps both databases and copies them
to the R2 bucket under `postgres/`, keeping 14 days.

```bash
kubectl -n onehintaway get cronjob,jobs                                   # did last night's run succeed?
kubectl -n onehintaway create job --from=cronjob/pg-backup pg-backup-manual   # take one now
kubectl -n onehintaway logs job/pg-backup-manual --all-containers
```

### Restore

Download the dump from R2 (dashboard → the bucket → `postgres/`), then:

```bash
# into a scratch database first, to look before you overwrite anything
kubectl -n onehintaway exec -i postgres-0 -- psql -U onehintaway -d onehintaway -c "CREATE DATABASE restore_test"
gunzip -c onehintaway-<stamp>.sql.gz | kubectl -n onehintaway exec -i postgres-0 -- psql -U onehintaway -d restore_test
kubectl -n onehintaway exec -i postgres-0 -- psql -U onehintaway -d restore_test -c "select count(*) from posts"
kubectl -n onehintaway exec -i postgres-0 -- psql -U onehintaway -d onehintaway -c "DROP DATABASE restore_test"
```

For a real restore, scale the API to 0 (`kubectl -n onehintaway scale deploy/api --replicas=0`),
load the dump into an emptied `onehintaway` database the same way, then scale back to 2.
Do the scratch restore once a month: a backup that has never been restored is a guess.

## Accounts

Nothing new runs on the server: accounts are four tables in the same Postgres
(`users`, `login_tokens`, `sessions`, `progress`; migration V2 runs by itself at deploy)
and code inside the API pods. They are in the nightly backup like everything else.

| Setting | Where | Value in production |
| --- | --- | --- |
| `CORS_ORIGINS` (`api.corsOrigins`) | `values-production.yaml` | `https://onehintaway.com`, exactly. It is also the only origin allowed to change account data |
| `SITE_URL` (`api.siteUrl`) | `values-production.yaml` | `https://onehintaway.com`: where the confirm and unsubscribe links land |
| `SESSION_COOKIE_SECURE` (`api.sessionCookieSecure`) | `values.yaml` | `true`. Never false here |
| `RESEND_API_KEY` | `/root/onehintaway.env` | Already set. Without it sign-in codes would go to the log, with the reader's address |
| `NEXT_PUBLIC_ACCOUNTS=on` | Cloudflare, Workers Builds variables | Set (accounts are live). It also makes the visualizer play only for signed-in readers. Remove it and rebuild to hide accounts and open the visualizer to everyone again; the data stays |

Look without printing anyone's address:

```bash
kubectl -n onehintaway exec -i postgres-0 -- psql -U onehintaway -d onehintaway -c   "select (select count(*) from users) users, (select count(*) from sessions where expires_at > now()) sessions, (select count(*) from progress) progress"
```

Remove a user who asks by email and can't sign in (deleting the `users` row takes their
sessions and progress with it). Type the address yourself; never paste query output that
holds other readers' addresses anywhere:

```bash
kubectl -n onehintaway exec -i postgres-0 -- psql -U onehintaway -d onehintaway   -c "delete from login_tokens where email = lower('reader@example.com')"   -c "delete from users where email = lower('reader@example.com')"
```

`DELETE 1` on the second line means the account is gone. Copies stay in the R2 backups
for up to 14 days. The newsletter list is separate: `delete from subscribers where email = …`.

Sign every reader out at once (a leaked backup, a bug): `truncate table sessions`. Everyone
signs in again with a new link; nothing else is lost.

## Secrets

| Secret | Where the values live | Change it |
| --- | --- | --- |
| `onehintaway-secrets` (database, salt, tokens, Resend key) | `/root/onehintaway.env` on the server | Edit the file, run `deploy/server/02-k3s.sh` again, then `kubectl -n onehintaway rollout restart deploy/api` |
| `onehintaway-backup` (R2 key) | `deploy/.env.r2` on the laptop (git-ignored) | `kubectl -n onehintaway create secret generic onehintaway-backup --from-env-file=deploy/.env.r2 --dry-run=client -o yaml \| kubectl apply -f -` |
| `grafana-admin` (namespace `monitoring`) | Only in the cluster | Read it: `kubectl -n monitoring get secret grafana-admin -o jsonpath="{.data.admin-password}"`, then base64-decode |

Changing `POSTGRES_PASSWORD` or `UMAMI_DB_PASSWORD` in the file does not change the
database: those are read once, when the data volume is first created. Use `ALTER ROLE` too.

## When something is wrong

| Symptom | Look at | Usual cause |
| --- | --- | --- |
| Sign-in says "not available right now" | `kubectl -n onehintaway logs deploy/api --tail 100` | `Resend did not accept a sign-in email`: the Resend key or domain; otherwise the API is down |
| Reader says the sign-in code "didn't work" | Nothing to fix | A code works once, for 15 minutes, only the newest few are live, and five wrong tries kill it: ask for a new one |
| Site fine, no view counts or search | `curl https://api.onehintaway.com/actuator/health/readiness` | API or server down; the site hides the extras by design |
| Pod `CrashLoopBackOff` | `kubectl -n onehintaway logs <pod> --previous` | Bad config or a failed migration |
| Pod `ImagePullBackOff` | `kubectl -n onehintaway describe pod <pod>` | The GHCR package is private, or the tag doesn't exist |
| Pod `OOMKilled` | `kubectl -n onehintaway describe pod <pod>`, `kubectl top pods -A` | Memory limit too low in `values.yaml` |
| Pod `Pending` | `kubectl -n onehintaway describe pod <pod>` | Server out of memory |
| Certificate warning | `kubectl get certificate -A`, `kubectl -n cert-manager logs deploy/cert-manager --tail 50` | DNS no longer points at the server, or the proxy (orange cloud) is on |
| Server unreachable | The provider's console | Reboot it there; k3s and every pod start by themselves |

## Rebuild the server from nothing

```bash
ssh root@<ip> 'bash -s' < deploy/server/01-harden.sh
ssh root@<ip> 'bash -s' < deploy/server/02-k3s.sh          # also creates the app's secrets
scp root@<ip>:/etc/rancher/k3s/k3s.yaml ~/.kube/onehintaway-prod.yaml   # then change 127.0.0.1 to <ip>

helm repo add jetstack https://charts.jetstack.io
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install cert-manager jetstack/cert-manager -n cert-manager --create-namespace --set crds.enabled=true --wait
kubectl apply -f deploy/server/cluster.yaml
kubectl create namespace monitoring
kubectl -n monitoring create secret generic grafana-admin --from-literal=admin-user=admin --from-literal=admin-password="$(openssl rand -hex 16)"
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version 93.3.0 -n monitoring -f deploy/server/monitoring-values.yaml --wait
```

Then point the three DNS records at the new address, update the `KUBE_CONFIG` secret, restore
the latest backup, and re-run the API workflow. Versions in use on 16 November 2026:
k3s 1.37.2, cert-manager 1.21.3, kube-prometheus-stack 93.3.0, Helm 4.3.2.

## The same chart on the laptop

```bash
k3d cluster create onehintaway --agents 1 -p "8081:80@loadbalancer"
docker build -t onehintaway-api:dev api
k3d image import onehintaway-api:dev -c onehintaway          # slow: several minutes
sh deploy/scripts/create-secret.sh deploy/compose/.env
helm upgrade --install onehintaway deploy/helm/onehintaway -n onehintaway \
  -f deploy/helm/onehintaway/values-local.yaml --wait

curl -H "Host: api.localhost" http://localhost:8081/actuator/health/readiness
```

`k3d cluster stop onehintaway` frees the memory; `k3d cluster start onehintaway` brings it back.
