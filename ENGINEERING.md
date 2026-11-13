# Engineering reliability foundation (ADF)

This branch adds **static validation**, unit tests, GitHub Actions checks and a **Terraform starter** for an ADF resource. It does not deploy the existing ADF pipeline JSON, provision ADLS, or prove cloud runtime success.

## Local checks
```bash
python scripts/validate_adf.py
python -m unittest discover -s tests -v
terraform -chdir=infrastructure fmt -check
terraform -chdir=infrastructure init -backend=false
terraform -chdir=infrastructure validate
```

## Deployment
Terraform requires Azure authentication plus `TF_VAR_subscription_id` and `TF_VAR_data_factory_name`. Review costs and naming before `plan`/`apply`. ADF pipeline/dataset/linked-service deployment and secrets are intentionally **not** automated here.

## Monitoring and recovery design
Monitor ADF pipeline/activity failures and duration in Azure Monitor. Add alert rules and diagnostic settings after selecting a destination Log Analytics workspace. Rerun failed copy operations only after verifying sink overwrite behavior to avoid duplicate outputs.

## Next steps
Implement credential-free ADF deployment via managed identity, externalize storage endpoints, add integration tests with a test ADLS container, and configure alerts. The current sink path is spelled `igestion` and must be coordinated with Databricks before changing.
