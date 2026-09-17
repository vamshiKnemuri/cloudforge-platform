{{- define "cloudforge.name" -}}
cloudforge
{{- end }}

{{- define "cloudforge.labels" -}}
app.kubernetes.io/name: {{ include "cloudforge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}

{{- define "cloudforge.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cloudforge.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

