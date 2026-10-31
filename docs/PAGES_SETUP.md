# Publish the 100 portfolio via GitHub Pages

The production-ready static site lives in `docs/` on the `main` branch.
No Node, Jekyll theme, external scripts, tokens, backend, or build step is needed
at request time. The `.nojekyll` marker preserves the static files as written.

## One-time Pages activation

With repository admin access:

1. Go to [repository Settings → Pages](https://github.com/Svyable/100/settings/pages).
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Choose branch **main** and folder **/docs**, then **Save**.
4. After the Pages deployment succeeds, visit **https://svyable.github.io/100/**.

If the site is not yet configured, the address may return 404. Merely committing
`docs/index.html` does **not** activate Pages settings automatically.
The linked account's current GitHub connector cannot modify repository Pages settings.
See [GitHub's official guide](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Update pipeline

The canonical list is `data/problems.json`. Every substantive edit should carry
a dated source and reason. After an edit, run:

```sh
python3 scripts/rank.py
python3 scripts/build_site.py
python3 scripts/rank.py --check
python3 scripts/build_site.py --check
python3 -m unittest discover -s tests -v
```

Commit `RANKED.md` and `docs/data/portfolio.json` with the source data.
The existing validation workflow fails on a stale generated artifact.

The standalone [Next 100](https://svyable.github.io/100/next/) explorer uses\n`docs/next/` and the generated `docs/data/next.json` snapshot. Refresh it with\n`python3 scripts/next.py`; CI validates its snapshot and JavaScript.\n\n## Features and boundaries

- Full 100-entry client-side explorer: search, field/evidence filter, ranking sort,
  detailed open questions, score breakdown, source links, and deep links by ID.
- Featured four research campaigns with GitHub-source dossiers and transparent
  evidence labels.
- Mobile and keyboard-friendly layout, reduced-motion support, no tracking.
- A **portfolio rank** measures editorial priorities, never the probability a claim is true.
- `official_open` refers to a specific official listing; `needs_review` and
  `claim_needs_review` must not be displayed as independently verified.
- The dashboard only refreshes when this generated snapshot is rebuilt and committed;
  it does not fetch live papers, issues, or external mathematical news.
- The GitHub Pages domain is specific to this repository; for a custom domain,
  use GitHub Pages Settings and update canonical/Open Graph URLs.

## Local preview

Serve the repository's `docs/` folder rather than opening `index.html` directly
with a `file://` URL, since browsers block local `fetch` in many configurations.

```sh
python3 -m http.server --directory docs 8000
# open http://localhost:8000
```
