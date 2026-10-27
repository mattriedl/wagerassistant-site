# Blog Automation — WagerAssistant.com

`blog_generator.py` is a **Python 3 stdlib-only** tool that publishes new blog posts and
keeps every related file in sync. It is designed to be driven by an automated job
(e.g. an every-3-days AI content task) or run by hand.

## What it does

Given one post described in a JSON file, it:

1. Renders a fully SEO-compliant article to `blog/<slug>.html` (canonical, Open Graph +
   Twitter cards, `BlogPosting` + `BreadcrumbList` + `FAQPage` JSON-LD, TOC, key-takeaways
   box, FAQ accordion, related tools/posts, responsible-gambling disclaimer, dark theme,
   root-relative asset + nav paths).
2. Inserts the post at the **top** of the blog hub (`blog/index.html`).
3. Refreshes the **homepage** "Betting Insights & Guides" cards with the 3 latest posts.
4. Adds the URL to `sitemap.xml` (with today's `lastmod`) and `sitemap.html`.
5. Prepends an entry to the RSS feed `blog/feed.xml`.
6. Records the post in the manifest `blog/posts.json`.
7. **Skips** the post if the slug already exists (safe to re-run / idempotent).
8. Optionally pings **IndexNow** so Bing/Yandex re-crawl immediately (`--ping`).

## Usage

```bash
# Publish one new post
python3 tools/blog_generator.py add path/to/post.json

# Publish AND notify search engines via IndexNow
python3 tools/blog_generator.py add path/to/post.json --ping

# Rebuild hub + feed + sitemaps + homepage from the existing manifest
python3 tools/blog_generator.py rebuild
```

## Post JSON schema

```json
{
  "title": "Keyword-Rich Title (<= 60 chars recommended)",
  "h1": "On-page H1 (optional; defaults to title)",
  "slug": "url-friendly-slug",
  "category": "Strategy",
  "read_time": "8",
  "meta_description": "Unique 140-160 character summary with the primary keyword.",
  "primary_keyword": "main keyword",
  "secondary_keywords": ["supporting keyword", "another"],
  "date": "2026-10-12",
  "toc": [["Section label", "section-id"]],
  "takeaways": ["Short takeaway bullet", "..."],
  "body_html": "<h2 id=\"section-id\">...</h2><p>...</p>",
  "faq": [["Question?", "Answer HTML."]],
  "related_calculators": [["Parlay Calculator", "/parlay_calculator.html"]]
}
```

- `body_html` is pre-formatted HTML. Use `<h2 id="...">`/`<h3>` for sections and make the
  `id`s match the second element of each `toc` row so the table of contents links work.
- Internal links to calculators and other articles should use **root-relative** paths
  (`/parlay_calculator.html`, `/blog/other-post.html`).

## Regenerating the 8 seed articles

`seed_articles.py` contains the original 8 posts and (re)builds them through the generator:

```bash
python3 tools/seed_articles.py
```

## Notes

- **IndexNow key:** `18151ece1492f341aafcb49eab497ebd` — served at
  `https://wagerassistant.com/18151ece1492f341aafcb49eab497ebd.txt`. Keep that file in the
  site root; the generator references it when pinging.
- **Cache-busting:** asset links use `?v=20261027`. Bump the `CACHE` constant in
  `blog_generator.py` whenever `styles.css`/`nav.js` change so browsers refetch.
- `tools/_nav.html` holds the shared navigation markup used on blog pages (Blog tab active,
  root-relative links). Update it if the main navigation changes.
- The tool writes only within the project; no third-party packages are required.
