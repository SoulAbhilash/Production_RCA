# Terraform (POC)

## Layout

- `modules/vpc` — VPC + single NAT (cost-aware default).
- `modules/ecr` — `demo-app` and `rca-agent` repositories + lifecycle policy.
- `modules/eks` — minimal managed node group (`t3.small`).
- `modules/iam-github-oidc` — optional GitHub Actions → AWS role for CI (enable only if no OIDC provider conflict).
- `environments/poc` — wires modules for a single environment.

## First-time init (local state / no backend)

```bash
cd terraform/environments/poc
terraform init -backend=false
terraform plan -var-file=terraform.tfvars.example
```

## Remote state (recommended)

1. Create S3 bucket + DynamoDB lock table (see playbook Phase C).
2. Copy `backend.hcl.example` → `backend.hcl` and edit bucket/table/region.
3. `terraform init -backend-config=backend.hcl`

## GitHub OIDC module

Set `create_github_oidc = true` and `github_repository = "yourorg/yourrepo"` **only** if your AWS account does not already have an OIDC provider for `https://token.actions.githubusercontent.com`. If one exists, import it or manage the role separately.

Match `github_repository` and `github_branch_names` to the IAM `sub` claims GitHub sends (see [AWS docs: GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)).

## EKS access for the CI role

Grant the GitHub Actions role cluster access (EKS access entries / console) after first apply — see playbook Phase E.
