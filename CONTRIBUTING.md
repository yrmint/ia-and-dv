# Git Workflow & Contribution Guidelines

## Overview

This project uses a feature-branch workflow with Pull Requests to ensure code quality and maintainability.

All changes must go through a Pull Request (PR) before being merged into the main branch.

---

## Branching Strategy

### Main Branch

* `main` — stable code
* Direct commits to `main` are **not allowed**

### Feature Branches

All new work must be done in separate branches

---

## Workflow

1. Make sure your branch is up to date:

   ```
    git pull origin main
   ```
2. Create a branch from `main`:

   ```
   git checkout -b feature/your-feature-name
   ```
3. Implement your changes
4. Commit using clear messages
5. Push your branch:

   ```
   git push origin feature/your-feature-name
   ```
6. Open a Pull Request in GitHub
7. Merge right away if you're sure or wait for a review

---

## Synchronization

Before opening a PR, make sure your branch is up to date:

```
git pull origin main
```

Resolve any merge conflicts locally before submitting the PR.

---

## CI Requirements

All Pull Requests must pass automated checks:

* Linting (ruff)

PRs with failing checks must not be merged.

---

## Best Practices

* Write modular and readable code
* Add tests for new functionality
* Avoid committing large data files
* Keep branches short-lived
