# Terraform Configuration for GitHub Repository

This Terraform configuration creates a GitHub repository for the Business Home Assistant Test project.

## Prerequisites

- Terraform installed (version >= 1.0)
- GitHub CLI (`gh`) installed and authenticated
- GitHub account with appropriate permissions

## Usage

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Review the planned changes:
   ```bash
   terraform plan
   ```

3. Apply the configuration:
   ```bash
   terraform apply
   ```

## Configuration

The configuration will create:
- Repository name: `business-homeassistant-test`
- Owner: `francis-io`
- Visibility: Public (change in `main.tf` if you want private)
- Features: Issues, Projects, Wiki enabled
- License: MIT (change or remove as needed)

## Authentication

This configuration uses the GitHub CLI token for authentication. Make sure you're logged in with:
```bash
gh auth status
```

## Outputs

After applying, you'll get:
- `repository_url`: The web URL of the repository
- `clone_url_ssh`: SSH clone URL
- `clone_url_https`: HTTPS clone URL