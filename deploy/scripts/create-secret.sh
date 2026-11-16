#!/bin/sh
# Creates (or replaces) the Kubernetes Secret the chart reads, from an env file that is
# never committed. Uses kubectl's current context.
#
#   deploy/scripts/create-secret.sh deploy/compose/.env        (laptop, k3d)
#
# The file needs: POSTGRES_PASSWORD, VISITOR_SALT, ADMIN_TOKEN, UMAMI_DB_PASSWORD,
# UMAMI_APP_SECRET, and optionally RESEND_API_KEY.
set -eu
file=${1:?usage: create-secret.sh <env file> [namespace]}
ns=${2:-onehintaway}

kubectl create namespace "$ns" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl -n "$ns" create secret generic onehintaway-secrets \
  --from-env-file="$file" --dry-run=client -o yaml | kubectl apply -f - >/dev/null
echo "secret onehintaway-secrets written to namespace $ns (values not shown)"
