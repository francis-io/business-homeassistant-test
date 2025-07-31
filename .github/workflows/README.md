# GitHub Actions Workflows

## E2E Tests Workflow

The `e2e-tests.yml` workflow automatically runs end-to-end tests for pull requests and pushes to the main branch.

### Features

- **Automatic Execution**: Runs on every PR and push to main/master
- **Test Results Upload**: Saves test reports as artifacts for 30 days
- **Error Logs**: Captures logs on failure for debugging
- **PR Comments**: Automatically comments on PRs with test results
- **Manual Trigger**: Can be run manually via workflow_dispatch

### Required Branch Protection

To ensure E2E tests pass before merging, configure branch protection rules:

1. Go to Settings → Branches
2. Add/Edit rule for your main branch
3. Enable "Require status checks to pass before merging"
4. Select "e2e-tests" from the status checks list
5. Enable "Require branches to be up to date before merging"

### Workflow Details

- **Timeout**: 10 minutes (tests typically complete in ~40 seconds)
- **Runner**: Ubuntu latest
- **Artifacts**: Test results are saved even if tests fail
- **PR Integration**: Comments with pass/fail status and report filename

### Local Testing

Before pushing, you can run the same tests locally:

```bash
make test:e2e
```

Test reports will be saved in the `reports/` directory.