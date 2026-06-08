variable "github_repository" {
  type        = string
  description = "GitHub repository in org/repo form (no https://, no .git)"
}

variable "github_branch_names" {
  type        = list(string)
  description = "Branch names allowed in OIDC sub claim (refs/heads/<name> matched in IAM trust)"
  default     = ["main"]
}

variable "role_name" {
  type    = string
  default = "github-actions-poc-rca"
}

variable "github_thumbprints" {
  type        = list(string)
  description = "TLS thumbprints for token.actions.githubusercontent.com OIDC provider"
  default     = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

variable "ecr_repository_arns" {
  type        = list(string)
  description = "ECR repository ARNs CI may push to"
}

variable "eks_cluster_arns" {
  type        = list(string)
  description = "EKS cluster ARNs for DescribeCluster"
  default     = []
}
