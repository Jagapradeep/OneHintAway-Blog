# Learn it afterwards: a Kubernetes lab on your own project

Production was built quickly on 16 November 2026. This lab is the learning that was
postponed. Everything here runs on the **local k3d cluster**, so nothing can hurt the live
site. About three hours in all; each part stands alone.

Start the cluster (from the repo root, with Docker Desktop running):

```bash
k3d cluster start onehintaway          # or create it: see deploy/README.md, last section
kubectl config use-context k3d-onehintaway
kubectl -n onehintaway get pods
```

Tip: `kubectl config set-context --current --namespace onehintaway` saves typing `-n onehintaway`.

## 1. From Compose to Kubernetes: the same ideas, new names

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

## 2. Look around (20 minutes)

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

## 3. Break things on purpose (60 minutes)

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

After any of these, return to the known state:
```bash
helm upgrade onehintaway deploy/helm/onehintaway -n onehintaway -f deploy/helm/onehintaway/values-local.yaml --wait
```

## 4. Helm (30 minutes)

```bash
helm template t deploy/helm/onehintaway -f deploy/helm/onehintaway/values-local.yaml | less
helm template t deploy/helm/onehintaway -f deploy/helm/onehintaway/values-production.yaml | grep -A12 "kind: Ingress"
helm upgrade onehintaway deploy/helm/onehintaway -n onehintaway -f deploy/helm/onehintaway/values-local.yaml --set api.replicas=3 --wait
helm history onehintaway -n onehintaway
helm rollback onehintaway 1 -n onehintaway --wait
```

Compare the two `helm template` outputs: the production one has TLS, the redirect middleware
and the backup CronJob; the local one doesn't. Same templates, different values.

## 5. Read the production pieces (45 minutes, read-only)

Use the production kubeconfig for looking only (`get`, `describe`, `logs`):

- `deploy/server/01-harden.sh`, `02-k3s.sh`: what was done to the bare server, and why.
- `deploy/server/cluster.yaml`: the Let's Encrypt issuer, and the limited account CI uses
  (ServiceAccount + Role + RoleBinding: RBAC).
- `kubectl get certificate -A`: one per host; `kubectl describe certificate api-tls -n onehintaway`
  shows how cert-manager got it.
- `.github/workflows/api.yml`: test → image → deploy, and where the commit SHA becomes the tag.
- Grafana → Dashboards → "Kubernetes / Compute Resources / Namespace (Pods)" → `onehintaway`.

## 6. Check yourself

1. A pod is `Running` but `0/1`. What does that mean, and which probe decides it?
2. Why is Postgres a StatefulSet and the API a Deployment?
3. What exactly happens, step by step, between `git push` and readers getting the new API?
4. The API is `OOMKilled` in production. What two commands do you run first, and what do you change?
5. Why can CI's kubeconfig not delete the monitoring stack?
6. Two replicas each keep rate-limit counters in memory. What does a reader's real limit become?

For interview-style practice on these, the backend-engineer-learning skill can quiz you.
