provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  name    = var.project_name
  azs     = slice(sort(data.aws_availability_zones.available.names), 0, min(2, length(data.aws_availability_zones.available.names)))
  cluster = "${var.project_name}-eks"
}

module "vpc" {
  source = "../../modules/vpc"

  name         = local.name
  vpc_cidr     = var.vpc_cidr
  azs          = local.azs
  cluster_name = local.cluster
}

module "ecr" {
  source = "../../modules/ecr"
}

module "eks" {
  source = "../../modules/eks"

  cluster_name       = local.cluster
  cluster_version    = var.cluster_version
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnets
  tags = {
    Project = var.project_name
  }
}

module "iam_github_oidc" {
  count  = var.create_github_oidc ? 1 : 0
  source = "../../modules/iam-github-oidc"

  github_repository   = var.github_repository
  github_branch_names = var.github_branch_names
  ecr_repository_arns = module.ecr.repository_arns
  eks_cluster_arns    = [module.eks.cluster_arn]
}
