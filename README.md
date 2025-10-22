# podfilter
Service that imports podcast feeds, applies filters to what episode to hide from it and then exposes a new rss feed with filtered items removed

## Robot Framework Acceptance Tests
1. Install dev dependencies: `pip install -e .[dev]`.
2. Download Playwright browsers once: `rfbrowser init`.
3. Run the app in another terminal via `python run.py`.
4. Execute the suite: `robot -d acceptance/results acceptance/suites`.
   - Override the target with `BASE_URL=http://localhost:8000` if your server runs on a custom address.
5. Pull requests to `main` automatically run the acceptance suite via GitHub Actions; fix failing tests before merging.
