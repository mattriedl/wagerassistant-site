# wagerassistant-site

Deployable static site for **wagerassistant.com** — 32 betting calculators, a blog section, and supporting SEO assets. The site is plain HTML/CSS/JS with no build step.

## Deploying

The site is served by **Cloudflare Workers** (static assets), straight from Cloudflare's network.
Cloudflare rebuilds and publishes it automatically on every push to `main` (Workers Builds),
usually within a minute or two. Nothing runs on a server.

- `wrangler.jsonc`: Cloudflare settings. `.html` addresses are kept as they are (`html_handling: none`).
- `_redirects`: `/` and `/blog/` serve their `index.html`; `/blog` redirects to `/blog/`.
- `_headers`: response headers for every file.
- `.assetsignore`: repository files that are not published (tools, Markdown, this README).

When you add a new folder with an `index.html`, add a matching line to `_redirects`.

The old copy on the web server (updated by a cron `git pull`) is kept as a fallback only.

## Structure

- `*.html` — calculator pages, homepage, 404
- `blog/` — blog hub, articles, `feed.xml`, `posts.json`
- `tools/` — blog automation (`blog_generator.py`, `seed_articles.py`); see `tools/README_BLOG_AUTOMATION.md`
- `styles.css`, `nav.js` — shared styling and utilities
- `sitemap.xml`, `sitemap.html`, `robots.txt`, `site.webmanifest`, favicons, `og-image.png` — SEO / PWA assets

## Automated blog updates

A Claude scheduled task researches (OpenSEO), writes and publishes one new article every 3 days directly
in this repo and pushes to `main`. The rules it follows are in `blog/WRITING-GUIDE.md`, the keyword plan is
`blog/topics.md`, and `tools/blog_seo_check.py` is the quality gate every post must pass.
