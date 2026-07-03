# Cloudflare Access for Kesakisa

This Terraform config protects the static Kesakisa app before the app is uploaded.

It creates four Access applications:

- `jmyrberg.com/kesakisa`
- `jmyrberg.com/kesakisa/*`
- `jmyrberg.com/kesakisa/admin`
- `jmyrberg.com/kesakisa/admin/*`

The player paths allow both `player_emails` and `admin_emails`.
The admin paths allow only `admin_emails`.

## One-time setup

Keep the API token in your shell only.

```sh
export CLOUDFLARE_API_TOKEN="paste-token-here"
```

Create a private vars file:

```sh
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and add the invited player/admin emails.

## Plan

```sh
terraform init
terraform fmt
terraform validate
terraform plan
```

Stop after `terraform plan` and review the four resources before applying.

## Apply

Only run this after the plan looks right:

```sh
terraform apply
```

## Notes

- `jmyrberg.com` is already proxied through Cloudflare, which is required for Access to protect the path.
- Do not commit `terraform.tfvars`; it is intentionally local operator configuration.
- This creates Cloudflare Access configuration only. It does not create GCP resources.
