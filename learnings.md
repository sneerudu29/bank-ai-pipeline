> - What is Terraform?
Teraform is a blueprint. It provides cloud infrastructure using code instead of clicking buttons

> - What is Key Vault?
Keyvault is like a secret locker where we store sensitive information

> - Why do banks need secrets management?
Without secrets management, compliance audits fails immediately

→ What is CI/CD and why banks need it?
CI/CD (Continuous Integration / Continuous Deployment) is an automated process that builds, tests, and deploys code safely and consistently.
Banks need it because:
Manual deployments are risky and error-prone
Financial systems require strict audit trails
Releases must be repeatable and controlled
Security checks must run automatically before production
Without CI/CD, human mistakes increase operational risk — which banks cannot afford.

→ What is a service principal?
A service principal is a non-human identity used by applications, scripts, or pipelines to securely access Azure resources.

→ What is terraform import?
terraform import brings an existing cloud resource under Terraform management without recreating it.
Example:
If a storage account was created manually in Azure Portal,
you can import it into Terraform state so Terraform can manage it going forward.

→ What does workflow_dispatch do?
In GitHub Actions, workflow_dispatch allows you to manually trigger a workflow from the GitHub UI.
Instead of automatic triggers like:
push
pull_request
It lets you click “Run workflow"

→ What errors did you fix today?
AuthorizationPermissionMismatch
Service principal not found
RoleAssignmentExists conflict
Deprecated Terraform property
Lock file inconsistency
Nested CLI command failures