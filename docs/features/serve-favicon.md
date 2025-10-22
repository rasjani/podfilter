---
name: 🚀 Feature Request
about: Request a new feature or enhancement for Podfilter
title: "feat: serve favicon for browser requests"
labels: ["enhancement"]
assignees: ""
---

## 🎯 Feature Description
Browsers request `/favicon.ico` on every page load, but PodFilter currently answers with a 404. Add a branded favicon and ensure it is served correctly so the browser no longer logs missing asset errors.

## ✅ Acceptance Criteria
- [ ] Given any page is opened in a browser, When the browser requests `/favicon.ico`, Then the server responds with the favicon image and the browser displays it without console errors.
- [ ] Given the favicon is updated, When assets are reloaded, Then the new icon is returned without requiring manual cache busting instructions.

## 🔧 Technical Requirements
- [x] Frontend changes needed
- [x] Backend changes needed
- [ ] Database changes needed
- [ ] Infrastructure changes needed
