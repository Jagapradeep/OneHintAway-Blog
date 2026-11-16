#!/bin/bash
# Installs k3s (one-node Kubernetes) and creates the app's secrets on the server.
# Safe to run again: existing secrets are kept.
#   ssh root@<server> 'bash -s' < deploy/server/02-k3s.sh
set -euo pipefail

PUBLIC_IP=$(curl -fsS -4 https://ifconfig.me || hostname -I | awk '{print $1}')

# Traefik keeps the reader's real address (needed for per-visitor counts and rate limits).
mkdir -p /var/lib/rancher/k3s/server/manifests
cat > /var/lib/rancher/k3s/server/manifests/traefik-config.yaml <<'EOF'
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    service:
      spec:
        externalTrafficPolicy: Local
EOF

if ! command -v k3s >/dev/null; then
  curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL=stable sh -s - \
    --tls-san "$PUBLIC_IP" --secrets-encryption --write-kubeconfig-mode 600 >/dev/null
fi
until k3s kubectl get nodes 2>/dev/null | grep -q ' Ready '; do sleep 3; done

# Secrets are born here and never leave, except the two that CI needs.
ENVF=/root/onehintaway.env
if [ ! -f "$ENVF" ]; then
  umask 077
  cat > "$ENVF" <<EOF
POSTGRES_PASSWORD=$(openssl rand -hex 24)
VISITOR_SALT=$(openssl rand -hex 32)
ADMIN_TOKEN=$(openssl rand -hex 32)
UMAMI_DB_PASSWORD=$(openssl rand -hex 24)
UMAMI_APP_SECRET=$(openssl rand -hex 32)
RESEND_API_KEY=
EOF
fi
k3s kubectl create namespace onehintaway --dry-run=client -o yaml | k3s kubectl apply -f - >/dev/null
k3s kubectl -n onehintaway create secret generic onehintaway-secrets \
  --from-env-file="$ENVF" --dry-run=client -o yaml | k3s kubectl apply -f - >/dev/null

echo "--- result"
k3s --version | head -1
k3s kubectl get nodes --no-headers
echo "secrets file: $ENVF ($(wc -l < "$ENVF") values, not shown)"
