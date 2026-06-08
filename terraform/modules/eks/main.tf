module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.31"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnet_ids

  enable_cluster_creator_admin_permissions = true

  eks_managed_node_groups = {
    default = {
      name           = "default"
      instance_types = ["t3.small"]
      min_size       = 1
      max_size       = 2
      desired_size   = 1
    }
  }

  tags = var.tags
}
