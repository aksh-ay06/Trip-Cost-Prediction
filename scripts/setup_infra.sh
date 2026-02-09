#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../terraform"

echo "==> Initializing Terraform..."
terraform init

echo "==> Planning infrastructure..."
terraform plan -var-file=terraform.tfvars -out=tfplan

echo "==> Applying infrastructure..."
terraform apply tfplan

echo "==> Done. Outputs:"
terraform output
