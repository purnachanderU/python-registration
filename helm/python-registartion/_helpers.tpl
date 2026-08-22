{{/*
Expand the name of the chart.
*/}}
{{- define "python-registration.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a fully qualified app name.
*/}}
{{- define "python-registration.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- include "python-registration.name" . }}
{{- end }}
{{- end }}

{{/*
Common labels.
*/}}
{{- define "python-registration.labels" -}}
app.kubernetes.io/name: {{ include "python-registration.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end }}

{{/*
Python application selector labels.
*/}}
{{- define "python-registration.pythonSelectorLabels" -}}
app: python-app
{{- end }}

{{/*
MySQL selector labels.
*/}}
{{- define "python-registration.mysqlSelectorLabels" -}}
app: mysql
{{- end }}
