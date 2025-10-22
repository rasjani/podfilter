---
name: 🐛 Bug Report
about: Report a bug or issue in Podfilter
title: "fix: dashboard route ignores authenticated user"
labels: ["bug"]
assignees: ""
---

## 🐛 Bug Description
After a user signs in through the login form, the app redirects back to `/` but the view renders the public landing page instead of the authenticated dashboard. The handler in `podfilter/routes/web.py` never enters the branch starting at line 50 where it loads feeds and filter rules for the logged-in user.

## 🔄 Steps to Reproduce
1. Start the dev server with `python run.py`.
2. Navigate to `http://localhost:8000/login`.
3. Submit valid credentials for an existing user.
4. Observe the redirected `/` response.

## ✅ Expected Behavior
The request to `/` should detect the authenticated session, enter the dashboard branch in `podfilter/routes/web.py`, and render `dashboard.html` populated with the user's feeds and filter rules.

## ❌ Actual Behavior
Despite a successful login response, the subsequent GET `/` still resolves to the anonymous landing page (`index.html`). The handler treats the request as unauthenticated, so the dashboard branch at line 50 never executes.

## 🖥️ Environment
- **Backend**: `main` (current HEAD) via `python run.py`
- **Frontend**: Local dev UI served from `http://localhost:8000/`
- **Browser**: Chrome 126 on macOS 14.5
