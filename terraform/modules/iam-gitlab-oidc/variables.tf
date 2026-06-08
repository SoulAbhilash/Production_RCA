variable "gitlab_project_path" {
  type        = string
  description = "GitLab project path like mygroup/myproject (no leading slash)"
}

variable "role_name" {
  type    = string
  default = "gitlab-ci-poc-rca"
}

variable "gitlab_thumbprints" {
  type        = list(string)
  description = "TLS thumbprints for gitlab.com OIDC provider (rotate per AWS/GitLab docs)"
  default     = ["99b41f7e164e00d04f1b90dfb7e51a2f8d69ad56"]
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
