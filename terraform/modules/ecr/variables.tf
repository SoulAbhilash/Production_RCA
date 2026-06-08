variable "names" {
  type        = list(string)
  description = "ECR repository names"
  default     = ["demo-app", "rca-agent"]
}

variable "image_tag_mutability" {
  type    = string
  default = "MUTABLE"
}
