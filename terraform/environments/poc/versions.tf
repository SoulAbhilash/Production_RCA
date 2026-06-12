terraform {
  required_version = ">= 1.5.0"

  # Bucket, key, region, lock table, etc. supplied via backend.hcl:
  #   terraform init -backend-config=backend.hcl
  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }
}
