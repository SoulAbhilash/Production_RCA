variable "name" {
  type        = string
  description = "Name prefix for VPC resources"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.42.0.0/16"
  description = "VPC CIDR"
}

variable "azs" {
  type        = list(string)
  description = "Availability zone names (e.g. first two in region)"
}

variable "cluster_name" {
  type        = string
  default     = ""
  description = "If set, adds kubernetes.io/cluster tag for EKS subnet discovery"
}
