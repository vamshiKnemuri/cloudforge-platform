#!/usr/bin/env bash
set -euo pipefail

cluster_name="cloudforge-local"

for command in docker kind kubectl helm; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Missing required command: $command" >&2
    exit 1
  fi
done

if ! kind get clusters | grep -qx "$cluster_name"; then
  kind create cluster --name "$cluster_name"
fi

docker build -t cloudforge:local .
kind load docker-image cloudforge:local --name "$cluster_name"

helm upgrade --install cloudforge platform/chart \
  --namespace cloudforge --create-namespace \
  --set image.repository=cloudforge \
  --set image.tag=local \
  --set image.pullPolicy=IfNotPresent \
  --set serviceMonitor.enabled=false \
  --set prometheusRule.enabled=false \
  --wait --timeout 5m

kubectl get pods,services,hpa --namespace cloudforge
echo "Run: kubectl port-forward service/cloudforge 8080:80 --namespace cloudforge"

