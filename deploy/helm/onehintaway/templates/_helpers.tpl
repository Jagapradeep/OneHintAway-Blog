{{- define "ohw.labels" -}}
app.kubernetes.io/part-of: onehintaway
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{/* Compose's "depends_on: service_healthy": hold the pod until Postgres answers. */}}
{{- define "ohw.waitForPostgres" -}}
- name: wait-for-postgres
  image: {{ .Values.postgres.image }}
  command: ["sh", "-c", "until pg_isready -h postgres -p 5432 -q; do sleep 2; done"]
  securityContext:
    runAsNonRoot: true
    runAsUser: 70
    allowPrivilegeEscalation: false
    capabilities: { drop: ["ALL"] }
  resources:
    requests: { cpu: 10m, memory: 16Mi }
    limits: { memory: 64Mi }
{{- end }}

{{/* Ingress annotations: with TLS on, ask cert-manager for a certificate and send http to https. */}}
{{- define "ohw.ingressAnnotations" -}}
{{- if .Values.ingress.tls.enabled }}
cert-manager.io/cluster-issuer: {{ .Values.ingress.tls.clusterIssuer }}
traefik.ingress.kubernetes.io/router.middlewares: {{ .Release.Namespace }}-https-redirect@kubernetescrd
{{- end }}
{{- end }}
