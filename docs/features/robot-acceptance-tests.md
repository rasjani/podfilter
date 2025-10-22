---
name: 🚀 Feature Request
about: Request a new feature or enhancement for Podfilter
title: "feat: add acceptance tests with robotframework-browser"
labels: ["enhancement"]
assignees: ""
---

## 🎯 Feature Description
Introduce automated end-to-end acceptance tests using the `robotframework-browser` library. These tests should cover critical user flows (registration, login, feed management) and run in CI to prevent regressions in the web UI.

## ✅ Acceptance Criteria
- [ ] Given Robot test suites are added, When `robot` is executed locally, Then scenarios for landing page, registration, and login succeed against the dev server.
- [ ] Given the CI pipeline runs, When the acceptance suite executes headlessly, Then the pipeline reports pass/fail status and fails on regression.

## 🔧 Technical Requirements
- [x] Frontend changes needed
- [x] Backend changes needed
- [ ] Database changes needed
- [x] Infrastructure changes needed
- [x] Tooling changes needed
