variable "aws_region" {
  description = "AWS region for the demo platform."
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Short project identifier used in resource names."
  type        = string
  default     = "cloudforge"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.project_name))
    error_message = "project_name must be 3-21 lowercase letters, digits, or hyphens."
  }
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "demo"
}

variable "github_repository" {
  description = "GitHub repository in owner/name format."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR used by the demo VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "kubernetes_version" {
  description = "EKS Kubernetes minor version under standard support."
  type        = string
  default     = "1.36"
}

variable "node_instance_types" {
  description = "EC2 instance types used by the managed node group."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_desired_size" {
  description = "Desired worker-node count. Keep low for the short-lived demo."
  type        = number
  default     = 2
}
