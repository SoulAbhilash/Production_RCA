resource "aws_iam_openid_connect_provider" "gitlab" {
  url             = "https://gitlab.com"
  client_id_list  = ["https://gitlab.com", "sts.amazonaws.com"]
  thumbprint_list = var.gitlab_thumbprints
}

data "aws_iam_policy_document" "assume_gitlab" {
  statement {
    effect = "Allow"
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.gitlab.arn]
    }
    actions = ["sts:AssumeRoleWithWebIdentity"]
    condition {
      test     = "StringEquals"
      variable = "gitlab.com:aud"
      values   = ["https://gitlab.com"]
    }
    condition {
      test     = "StringLike"
      variable = "gitlab.com:sub"
      values   = ["project_path:${var.gitlab_project_path}:ref_type:branch:ref:*"]
    }
  }
}

resource "aws_iam_role" "gitlab_ci" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.assume_gitlab.json
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

resource "aws_iam_role_policy" "gitlab_ci_inline" {
  name   = "${var.role_name}-inline"
  role   = aws_iam_role.gitlab_ci.id
  policy = data.aws_iam_policy_document.ci_inline.json
}
