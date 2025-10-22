---
name: 🚀 Feature Request
about: Request a new feature or enhancement for Podfilter
title: "ci: run robot acceptance tests on pull requests"
labels: ["enhancement", "ci"]
assignees: ""
---

## 🎯 Feature Description
Update the CI pipeline so that every pull request targeting `main` runs the Robot Framework acceptance suite. If the suite fails, the workflow must fail and block the merge.

## ✅ Acceptance Criteria
- [ ] Given a PR targets `main`, When the workflow runs, Then it executes `robot` against the acceptance suites headlessly.
- [ ] Given any acceptance test fails, When the workflow completes, Then the GitHub check reports a failure so the PR cannot merge.

## 🔧 Technical Requirements
- [ ] Frontend changes needed
- [ ] Backend changes needed
- [ ] Database changes needed
- [x] Infrastructure changes needed
- [x] Tooling changes needed
