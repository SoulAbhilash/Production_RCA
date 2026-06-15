variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type        = string
  default     = "rca-poc"
  description = "Prefix for VPC/EKS naming"
}

variable "vpc_cidr" {
  type    = string
  default = "10.42.0.0/16"
}

variable "cluster_version" {
  type        = string
  default     = "1.30"
  description = "EKS control plane + node group version; use a version Amazon still ships AMIs for (upgrade one minor at a time from an existing older cluster)."
}

variable "create_github_oidc" {
  type        = bool
  default     = false
  description = "If true, creates GitHub Actions OIDC provider + CI role (skip if provider already exists in account)"
}

variable "github_repository" {
  type        = string
  default     = "myorg/myrepo"
  description = "GitHub repo org/name — must match workflows and IAM trust (sub claim). Used when create_github_oidc=true"
}

variable "github_branch_names" {
  type        = list(string)
  default     = ["main"]
  description = "Branch names allowed to assume the CI role via OIDC (refs/heads/<name>)"
}
