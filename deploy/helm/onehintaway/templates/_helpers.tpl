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

{{/*
Ingress annotations. Every route gets the security headers; with TLS on, cert-manager makes a
certificate and http is sent to https. Call with (dict "root" . "extra" (list "api-headers"))
to add more of this chart's middlewares, by name, after those.
*/}}
{{- define "ohw.ingressAnnotations" -}}
{{- $root := .root -}}
{{- $ns := $root.Release.Namespace -}}
{{- $names := list -}}
{{- if $root.Values.ingress.tls.enabled }}{{ $names = append $names "https-redirect" }}{{ end -}}
{{- $names = append $names "security-headers" -}}
{{- range (.extra | default list) }}{{ $names = append $names . }}{{ end -}}
{{- $refs := list -}}
{{- range $names }}{{ $refs = append $refs (printf "%s-%s@kubernetescrd" $ns .) }}{{ end -}}
{{- if $root.Values.ingress.tls.enabled }}
cert-manager.io/cluster-issuer: {{ $root.Values.ingress.tls.clusterIssuer }}
{{- end }}
traefik.ingress.kubernetes.io/router.middlewares: {{ join "," $refs }}
{{- end }}
