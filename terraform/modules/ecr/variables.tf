variable "names" {
  type        = list(string)
  description = "ECR repository names"
  default     = ["demo-app", "rca-agent"]
}

variable "image_tag_mutability" {
  type    = string
  default = "MUTABLE"
}

variable "force_delete" {
  type        = bool
  default     = false
  description = "If true, delete ECR repositories even when they contain images (enables non-empty destroy)."
}
