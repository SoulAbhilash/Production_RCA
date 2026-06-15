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

## Troubleshooting

### `ResourceAlreadyExistsException` — CloudWatch log group `/aws/eks/<cluster>/cluster`

**Cause:** The log group already exists in AWS (e.g. leftover from a partial apply, destroy, or state reset) but is **not** in the current Terraform state, so the EKS module tries to create it again.

**Fix A — import (keep the existing log group, let Terraform manage it):** from `terraform/environments/poc`, with the same backend and `var-file` you use for apply:

```bash
terraform import 'module.eks.module.eks.aws_cloudwatch_log_group.this[0]' /aws/eks/rca-poc-eks/cluster
```

If your `project_name` is not `rca-poc`, the name is `/aws/eks/<project_name>-eks/cluster`. Confirm in CloudWatch Logs → Log groups, or:

```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/eks/" --query "logGroups[].logGroupName" --output text
```

Then run `terraform plan` / `terraform apply` again.

**Fix B — delete (only if the group is truly orphaned):** in the AWS console (CloudWatch → Log groups), delete `/aws/eks/<cluster>/cluster`, then re-run `terraform apply`. Do **not** delete it if an existing production cluster still sends logs there.

### EKS: `InvalidParameterException: Requested AMI for this version X.XX is not supported`

**Cause:** Amazon stopped publishing EKS-optimized AMIs for that Kubernetes minor (common for older minors). Managed node groups cannot launch until the **control plane** and **`cluster_version`** use a supported minor.

**Fix:** In `terraform.tfvars`, set **`cluster_version`** to a [currently supported EKS version](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html). AWS only allows **one minor upgrade at a time** on the control plane (e.g. `1.29` → `1.30` → `1.31` …). After changing the version, run `terraform plan` / `terraform apply` again; repeat with the next minor if the API still rejects a multi-step jump.
