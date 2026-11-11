# wagerassistant-site

Deployable static site for **wagerassistant.com** — 32 betting calculators, a blog section, and supporting SEO assets. The site is plain HTML/CSS/JS with no build step.

## Deploying

The production server runs a cron job that pulls this repo into the web root:

```bash
cd /path/to/webroot && git pull origin main
```

Since the repo is public, the server can `git pull` without credentials.

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
