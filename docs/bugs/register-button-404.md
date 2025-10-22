---
name: 🐛 Bug Report
about: Report a bug or issue in Podfilter
title: "fix: register page link returns 404"
labels: ["bug"]
assignees: ""
---

## 🐛 Bug Description
Clicking the **Register** button on the landing page navigates to `/register` but the request returns a `404 Not Found`. The template route exists in `podfilter/routes/web.py`, but it is not wired into the Litestar application, so the page never resolves.

## 🔄 Steps to Reproduce
1. Start the dev server with `python run.py`.
2. Open `http://localhost:8000/` in a browser.
3. Click the **Register** button on the hero section.

## ✅ Expected Behavior
The `/register` route should render the registration form so that a new user can create an account.

## ❌ Actual Behavior
The browser receives a `404 Not Found` response and the registration form never renders. The Litestar logs show the request falling through because the handler is not registered with the app.

## 🖥️ Environment
- **Frontend**: Local dev UI served from `http://localhost:8000/`
- **Backend**: `main` (current HEAD) via `python run.py`
- **Browser**: Chrome 126 on macOS 14.5
