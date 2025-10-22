# fix: register page responds with 404

Fixes #3.

## Summary
- wire the Litestar app to use the routers defined in `podfilter/routes` instead of ad-hoc handlers in `podfilter/app.py`.
- configure the Jinja template engine and static files so template based pages render correctly.
- update the base template to use static asset paths that align with Litestar's static router, fixing 500s from missing globals.

## Testing
- `python -m compileall podfilter/app.py`
- Manual QA: `python run.py`, navigate to `/`, `/register`, and `/login` to confirm pages render.
