output "cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS API endpoint."
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "ecr_repository_url" {
  description = "ECR repository receiving immutable application images."
  value       = aws_ecr_repository.application.repository_url
}

output "aws_account_id" {
  description = "AWS account hosting the short-lived demo."
  value       = data.aws_caller_identity.current.account_id
}

output "vpc_id" {
  description = "Demo VPC ID."
  value       = module.network.vpc_id
}

