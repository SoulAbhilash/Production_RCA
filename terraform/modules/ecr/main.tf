resource "aws_ecr_repository" "this" {
  for_each             = toset(var.names)
  name                 = each.key
  image_tag_mutability = var.image_tag_mutability
  # Required for clean `terraform destroy` when images still exist (AWS otherwise returns RepositoryNotEmptyException).
  force_delete = var.force_delete

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "this" {
  for_each   = aws_ecr_repository.this
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
