output "role_arn" {
  value = aws_iam_role.gitlab_ci.arn
}

output "oidc_provider_arn" {
  value = aws_iam_openid_connect_provider.gitlab.arn
}
