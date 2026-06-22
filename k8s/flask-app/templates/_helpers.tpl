{{- define "flask-ml-backend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "flask-ml-backend.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "flask-ml-backend.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
