# LinkedIn Launch Post

I built CloudForge, a working AWS DevOps portfolio project that takes a small service through the full delivery lifecycle.

The platform uses Terraform to provision a two-AZ VPC, Amazon EKS and ECR. GitHub Actions runs application tests, Terraform and Helm validation, container and infrastructure scanning, and authenticates to AWS using OIDC instead of stored access keys. Argo CD handles GitOps deployment, while Prometheus, Grafana and Kyverno provide monitoring and workload policy enforcement.

I also tested operational behavior by generating load, deleting pods, introducing drift and verifying recovery through Kubernetes and Argo CD. After recording the demonstration, I destroyed the AWS environment through a gated cleanup workflow.

Repository: ADD_GITHUB_URL
Demo: ADD_VIDEO_URL

#DevOps #AWS #Terraform #Kubernetes #GitOps #GitHubActions #PlatformEngineering

