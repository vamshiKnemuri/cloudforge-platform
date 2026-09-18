# Security Policy

## Reporting

Do not open a public issue containing credentials or exploitable account information. Remove the affected resource and rotate credentials before documenting the incident.

## Repository controls

- No AWS access keys are stored in GitHub.
- Deployment uses a repository- and environment-scoped OIDC trust policy.
- Images are immutable and scanned before deployment.
- The application container runs without root, writable root storage, added capabilities or a Kubernetes service-account token.
- AWS resources are tagged for identification and automated cleanup.

## Demonstration limitations

This repository keeps the EKS API endpoint reachable because GitHub-hosted runners operate outside the demo VPC. The deploy workflow discovers its current public IP and restricts access to that single `/32` address; private endpoint access also remains enabled and authentication is IAM-controlled. Trivy finding `AVD-AWS-0040` is narrowly suppressed for this documented, temporary architecture. A production implementation should use only a private endpoint and a controlled runner inside the network boundary.

The exception is reviewed before each demo and expires operationally on 2026-12-31. The gated destroy workflow removes the short-lived cluster after evidence is captured.
