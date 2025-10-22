# fix: dashboard route honors authenticated user

Fixes #12.

## Summary
- set an HTTP-only `access_token` cookie during login and clear it on logout so the server identifies returning users.
- ensure all authenticated fetch helpers include browser credentials when calling backend endpoints.
- document the bug report for future reference.

## Testing
- `python -m compileall podfilter/routes/auth.py podfilter/static/js/app.js`
