# CloudForge Service Unavailable Runbook

## Purpose

Use this runbook when the `CloudForgeUnavailable` alert fires or the `/healthz` endpoint stops responding. The objective is to restore service without hiding evidence needed for root-cause analysis.

## Triage

1. Confirm the alert and record its start time.
2. Check deployment health with `kubectl get deployment,pods -n cloudforge`.
3. Review recent events with `kubectl get events -n cloudforge --sort-by=.lastTimestamp`.
4. Inspect application logs with `kubectl logs -n cloudforge deployment/cloudforge --since=15m`.
5. Compare the active image and Argo CD revision with the last known healthy release.
6. Check node readiness and resource pressure before changing the application.

## Recovery

- If a new image is unhealthy, revert its Git reference or image parameter and allow Argo CD to synchronize the known-good state.
- If pods are resource constrained, preserve evidence and temporarily adjust requests only through the Helm values in Git.
- If a node is unhealthy, cordon and drain it only after verifying that disruption budgets and remaining capacity can sustain the workload.

Do not edit the live Deployment as a permanent fix. Argo CD self-healing will revert unmanaged changes.

## Verification

1. Verify all replicas are ready.
2. Verify `/healthz`, `/readyz`, and `/metrics` return HTTP 200.
3. Confirm the alert resolves and the error rate returns below five percent.
4. Record the cause, recovery action, detection gap, and preventive change in an incident report.

