# CloudForge Interview Guide

## Thirty-second explanation

I built CloudForge to demonstrate a complete platform lifecycle rather than an isolated Terraform or Kubernetes example. GitHub Actions tests and scans the service, authenticates to AWS with short-lived OIDC credentials, and provisions a two-AZ EKS environment using reusable Terraform modules. Argo CD pulls the desired Helm configuration from Git, while Prometheus, Grafana and Kyverno provide monitoring and policy enforcement. The environment is intentionally short-lived and has an automated destroy workflow.

## Design questions

**Why OIDC instead of GitHub secrets?**  
OIDC removes long-lived AWS keys from GitHub. The AWS trust policy also limits assumption to this repository and its protected `demo` environment.

**Why both CI and Argo CD?**  
CI builds, tests, scans and publishes an immutable artifact. Argo CD handles deployment by reconciling the Git state with the cluster, so the pipeline does not need to issue imperative application deployment commands.

**Why one NAT gateway?**  
This is a temporary demonstration environment. One NAT gateway keeps the design realistic while limiting short-lived cost. A production design would evaluate per-AZ NAT gateways or VPC endpoints against availability and traffic requirements.

**How is rollback handled?**  
Images use immutable commit-SHA tags. Rollback means returning the desired Git or Argo image value to a known-good SHA. Kubernetes performs a controlled rolling update, and readiness checks prevent an unhealthy replica from receiving traffic.

**What would you change for production?**  
I would use separate AWS accounts, private API access through a controlled runner, per-AZ egress, managed DNS and ingress, external secret management, stronger admission policies, backup and recovery testing, and SLO-based alert routing.

## Honest scope

CloudForge is a working portfolio environment built with AI assistance and validated through automated tests. It demonstrates engineering decisions and operational workflows; it does not represent customer production traffic.

