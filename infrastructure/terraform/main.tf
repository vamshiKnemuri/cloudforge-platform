data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

locals {
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 2)
  name               = "${var.project_name}-${var.environment}"
}

module "network" {
  source = "./modules/network"

  name               = local.name
  vpc_cidr           = var.vpc_cidr
  availability_zones = local.availability_zones
  cluster_name       = local.name
}

module "eks" {
  source = "./modules/eks"

  name                = local.name
  kubernetes_version  = var.kubernetes_version
  private_subnet_ids  = module.network.private_subnet_ids
  public_access_cidrs = var.cluster_public_access_cidrs
  node_instance_types = var.node_instance_types
  node_desired_size   = var.node_desired_size
}

resource "aws_ecr_repository" "application" {
  name                 = "${local.name}-app"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true

  encryption_configuration {
    encryption_type = "AES256"
  }

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "application" {
  repository = aws_ecr_repository.application.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep the most recent ten demo images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = { type = "expire" }
    }]
  })
}
