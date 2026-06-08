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
  type    = string
  default = "1.29"
}

variable "create_gitlab_oidc" {
  type        = bool
  default     = false
  description = "If true, creates gitlab.com OIDC provider + CI role (skip if provider already exists in account)"
}

variable "gitlab_project_path" {
  type        = string
  default     = "example/group"
  description = "GitLab project path (group/project). Used when create_gitlab_oidc=true"
}
