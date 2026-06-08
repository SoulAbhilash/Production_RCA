output "vpc_id" {
  value = module.vpc.vpc_id
}

output "ecr_repository_urls" {
  value = module.ecr.repository_urls
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "eks_configure_kubeconfig" {
  value = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "gitlab_ci_role_arn" {
  value = try(module.iam_gitlab_oidc[0].role_arn, null)
}
