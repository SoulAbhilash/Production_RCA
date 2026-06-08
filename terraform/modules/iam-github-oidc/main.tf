locals {
  # e.g. repo:myorg/myrepo:ref:refs/heads/main
  branch_subjects = [
    for b in var.github_branch_names : "repo:${var.github_repository}:ref:refs/heads/${b}"
  ]
}

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  # GitHub Actions OIDC — see AWS docs; rotate if issuer TLS chain changes
  thumbprint_list = var.github_thumbprints
}

data "aws_iam_policy_document" "assume_github" {
  statement {
    effect = "Allow"
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    actions = ["sts:AssumeRoleWithWebIdentity"]
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = local.branch_subjects
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.assume_github.json
}

data "aws_iam_policy_document" "ci_inline" {
  statement {
    sid    = "EcrAuth"
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "EcrPush"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]
    resources = var.ecr_repository_arns
  }

  statement {
    sid    = "EksDescribe"
    effect = "Allow"
    actions = [
      "eks:DescribeCluster",
    ]
    resources = length(var.eks_cluster_arns) > 0 ? var.eks_cluster_arns : ["*"]
  }

  statement {
    sid       = "Sts"
    effect    = "Allow"
    actions   = ["sts:GetCallerIdentity"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "github_actions_inline" {
  name   = "${var.role_name}-inline"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.ci_inline.json
}
