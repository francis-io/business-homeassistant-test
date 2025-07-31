terraform {
  required_version = ">= 1.0"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

# Configure the GitHub Provider using token from gh cli
provider "github" {
  token = data.external.gh_token.result.token
  owner = "francis-io"
}

# Get GitHub token from gh cli
data "external" "gh_token" {
  program = ["bash", "-c", "echo '{\"token\":\"'$(gh auth token)'\"}'"]
}

# Create the repository
resource "github_repository" "business_homeassistant_test" {
  name        = "business-homeassistant-test"
  description = "Business Home Assistant Test Repository"
  visibility  = "public"  # Change to "private" if you want a private repo

  # Initialize with README
  auto_init = true

  # Enable features
  has_issues   = true
  has_projects = true
  has_wiki     = true

  # Branch protection can be added later if needed
  # vulnerability_alerts = true

  # License
  license_template = "mit"  # Change or remove as needed

  # Topics/tags
  topics = ["home-assistant", "testing", "automation"]
}

# Output the repository URLs
output "repository_url" {
  value = github_repository.business_homeassistant_test.html_url
}

output "clone_url_ssh" {
  value = github_repository.business_homeassistant_test.ssh_clone_url
}

output "clone_url_https" {
  value = github_repository.business_homeassistant_test.http_clone_url
}
