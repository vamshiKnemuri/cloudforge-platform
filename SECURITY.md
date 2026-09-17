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

This repository intentionally exposes the EKS API endpoint publicly so GitHub-hosted runners can reach it. Authentication remains IAM-controlled. A production implementation should use a private endpoint and a controlled runner inside the network boundary.

