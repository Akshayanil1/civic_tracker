# Contributing to Civic SLA Engine

First off, thank you for considering contributing to the Civic SLA Engine! It's people like you that make open-source GovTech such a powerful tool for social change.

## How Can I Contribute?

### 1. "Good First Issue"
If you are a junior developer or new to open-source, look for issues tagged with the `good first issue` label. These are typically small bugs, CSS fixes on the landing page, or simple Frappe doctype configuration tweaks designed to get you familiar with our workflow.

### 2. Reporting Bugs
Please use the provided Bug Report template in the `.github/ISSUE_TEMPLATE` directory to ensure we have all the information needed to replicate and fix the issue.

### 3. Feature Requests
Have an idea to improve the AI Triage layer or the Mobile App? Open an issue using the Feature Request template. We are particularly interested in extending our multi-tenant capabilities and IoT sensor integrations.

## Local Development Setup
1. Fork the repository.
2. Ensure you have Frappe Bench installed locally.
3. Fetch the app: `bench get-app civic_tracker https://github.com/YOUR_USERNAME/civic_tracker`
4. Install on your local site: `bench --site your-site.local install-app civic_tracker`

## Pull Request Process
1. Ensure your code follows Frappe's Python styling conventions (PEP 8).
2. Document any changes to the REST API endpoints in the `README.md`.
3. Keep PRs small and focused on a single issue.
4. I will personally review all PRs, and once approved, they will be merged into the `master` branch.

Welcome to the community! Let's fix our cities with code.
