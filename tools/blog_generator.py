#!/usr/bin/env python3
"""WagerAssistant Blog Generator (Python 3 stdlib only).

Renders SEO-compliant blog articles that match the seed structure, then wires the
new post into the blog hub, homepage latest-posts cards, sitemap.xml, sitemap.html,
blog/feed.xml and blog/posts.json. Idempotent: duplicate slugs are skipped.

Usage:
  python3 blog_generator.py add path/to/post.json [--ping]
  python3 blog_generator.py rebuild            # rebuild hub/feed/sitemaps from posts.json

Post JSON schema:
  {
    "title": "...",                 # <=60 chars recommended (incl. brand suffix added automatically off)
    "slug": "my-post",
    "meta_description": "...",       # ~140-160 chars
    "primary_keyword": "...",
    "secondary_keywords": ["...", "..."],
    "body_html": "<p>...</p>...",    # H2/H3 sections, already-formatted HTML
    "toc": [["Section label","section-id"], ...],
    "takeaways": ["...", "..."],
    "faq": [["Question?","Answer."], ...],
    "related_calculators": [["Parlay Calculator","/parlay_calculator.html"], ...],
    "date": "2026-10-12"            # optional; defaults today
  }
"""
import json, os, re, sys, html, datetime, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(ROOT, "blog")
POSTS_JSON = os.path.join(BLOG, "posts.json")
SITE = "https://wagerassistant.com"
BRAND = "Wager Assistant"
CACHE = "v=20261012"
INDEXNOW_KEY = "18151ece1492f341aafcb49eab497ebd"

# ── Shared nav + footer (root-relative; Blog active) ───────────────────────────
NAV = open(os.path.join(os.path.dirname(__file__), "_nav.html"), encoding="utf-8").read() \
    if os.path.exists(os.path.join(os.path.dirname(__file__), "_nav.html")) else ""

FOOTER = '''<footer class="site-footer">
  <p>&copy; 2026 WagerAssistant.com - All Rights Reserved. Free tools for informational purposes only. Please gamble responsibly.</p>
  <p style="margin-top:8px"><a href="/index.html" style="color:#8892b0;margin:0 8px">Calculators</a> &middot; <a href="/blog/index.html" style="color:#8892b0;margin:0 8px">Blog</a> &middot; <a href="/sitemap.html" style="color:#8892b0;margin:0 8px">Sitemap</a></p>
</footer>'''

DISCLAIMER = '''<div class="rg-disclaimer">
  <strong>Responsible gambling:</strong> You must be 21+ (or the legal age in your jurisdiction) to gamble.
  Betting involves risk &mdash; never wager more than you can afford to lose. These articles are for informational
  purposes only and are not betting advice. If gambling stops being fun, help is available 24/7 at
  <strong>1-800-GAMBLER</strong> or <a href="https://www.ncpgambling.org/" target="_blank" rel="noopener">ncpgambling.org</a>.
</div>'''


def esc(s):
    return html.escape(s, quote=True)


def head(post):
    url = f"{SITE}/blog/{post['slug']}.html"
    kw = ", ".join([post["primary_keyword"]] + post.get("secondary_keywords", []))
    faq_schema = ""
    if post.get("faq"):
        faq_schema = '<script type="application/ld+json">\n' + json.dumps({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in post["faq"]]
        }) + "\n</script>"
    blogposting = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": post["title"], "description": post["meta_description"],
        "image": f"{SITE}/og-image.png", "author": {"@type": "Organization", "name": "WagerAssistant Editorial Team"},
        "publisher": {"@type": "Organization", "name": BRAND,
                      "logo": {"@type": "ImageObject", "url": f"{SITE}/og-image.png"}},
        "datePublished": post["date"], "dateModified": post["date"],
        "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "keywords": kw
    })
    breadcrumb = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": post["title"], "item": url},
        ]})
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(post["title"])}</title>
<meta name="description" content="{esc(post["meta_description"])}">
<meta property="og:title" content="{esc(post["title"])}">
<meta property="og:description" content="{esc(post["meta_description"])}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(post["title"])}">
<meta name="twitter:description" content="{esc(post["meta_description"])}">
<meta name="twitter:image" content="{SITE}/og-image.png">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="WagerAssistant Editorial Team">
<meta name="theme-color" content="#0d0f1a">
<link rel="canonical" href="{url}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap">
<link rel="stylesheet" href="/styles.css?{CACHE}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="application/rss+xml" title="Wager Assistant Blog" href="/blog/feed.xml">
<script type="application/ld+json">
{blogposting}
</script>
<script type="application/ld+json">
{breadcrumb}
</script>
{faq_schema}
</head>
<body>'''


def render_article(post, all_posts):
    toc = "".join(f'<li><a href="#{sid}">{esc(label)}</a></li>' for label, sid in post.get("toc", []))
    takeaways = "".join(f"<li>{t}</li>" for t in post.get("takeaways", []))
    faq_html = ""
    if post.get("faq"):
        items = "".join(
            f'<div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)" aria-expanded="false">'
            f'<span>{esc(q)}</span><span class="faq-icon">+</span></button>'
            f'<div class="faq-a"><div class="faq-a-inner">{a}</div></div></div>'
            for q, a in post["faq"])
        faq_html = f'<section class="article-faq"><h2 id="faq">Frequently Asked Questions</h2>{items}</section>'
    # related calculators + related posts
    rel_calc = "".join(
        f'<a href="{href}">{esc(name)}<span>Free calculator</span></a>'
        for name, href in post.get("related_calculators", []))
    others = [p for p in all_posts if p["slug"] != post["slug"]][:3]
    rel_posts = "".join(
        f'<a href="/blog/{p["slug"]}.html">{esc(p["title"])}<span>Read guide</span></a>' for p in others)
    related = ""
    if rel_calc or rel_posts:
        related = '<section class="related-posts"><h2>Related Tools &amp; Guides</h2><div class="related-grid">' \
                  + rel_calc + rel_posts + "</div></section>"
    toc_block = f'<nav class="toc" aria-label="Table of contents"><h2>In this guide</h2><ol>{toc}</ol></nav>' if toc else ""
    take_block = f'<div class="takeaways"><h2>Key takeaways</h2><ul>{takeaways}</ul></div>' if takeaways else ""
    date_h = datetime.datetime.strptime(post["date"], "%Y-%m-%d").strftime("%B %-d, %Y")
    return head(post) + f'''
{NAV}
<div class="page-content">
  <nav class="breadcrumb-wrap" aria-label="Breadcrumb" style="max-width:820px;margin:16px auto 0;font-size:13px;color:#6f7c91">
    <a href="/index.html" style="color:#8892b0">Home</a> &rsaquo;
    <a href="/blog/index.html" style="color:#8892b0">Blog</a> &rsaquo;
    <span>{esc(post["title"])}</span>
  </nav>
  <article class="article-wrap">
    <div class="article-head">
      <span class="blog-tag">{esc(post.get("category", "Guide"))}</span>
      <h1>{esc(post["h1"])}</h1>
      <p class="article-meta">By <b>WagerAssistant Editorial Team</b> &middot; Published {date_h} &middot; {post.get("read_time", "7")} min read</p>
    </div>
    <div class="ad-zone ad-leaderboard" aria-hidden="true"><span>Advertisement</span></div>
    {toc_block}
    {take_block}
    <div class="article-body">
      {post["body_html"]}
    </div>
    {faq_html}
    {related}
    {DISCLAIMER}
  </article>
</div>
{FOOTER}
<script defer src="/nav.js?{CACHE}"></script>
<script>
function toggleFaq(b){{var e=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',!e);var a=b.nextElementSibling;a.style.maxHeight=e?null:a.scrollHeight+'px';b.querySelector('.faq-icon').textContent=e?'+':'\\u2212';}}
</script>
</body>
</html>'''


def load_posts():
    if os.path.exists(POSTS_JSON):
        return json.load(open(POSTS_JSON, encoding="utf-8"))
    return []


def save_posts(posts):
    json.dump(posts, open(POSTS_JSON, "w", encoding="utf-8"), indent=2)


def build_hub(posts):
    cards = ""
    for p in posts:
        date_h = datetime.datetime.strptime(p["date"], "%Y-%m-%d").strftime("%b %-d, %Y")
        cards += (f'<article class="blog-card"><span class="blog-tag">{esc(p.get("category","Guide"))}</span>'
                  f'<h2><a href="/blog/{p["slug"]}.html">{esc(p["title"])}</a></h2>'
                  f'<p>{esc(p["meta_description"])}</p>'
                  f'<div class="blog-meta">{date_h}</div>'
                  f'<a class="blog-read" href="/blog/{p["slug"]}.html">Read article &rarr;</a></article>')
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Blog", "name": f"{BRAND} Blog",
        "url": f"{SITE}/blog/", "description": "Betting strategy, odds and casino guides from Wager Assistant.",
        "blogPost": [{"@type": "BlogPosting", "headline": p["title"],
                      "url": f"{SITE}/blog/{p['slug']}.html", "datePublished": p["date"]} for p in posts]})
    doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Betting Blog - Strategy, Odds & Casino Guides | {BRAND}</title>
<meta name="description" content="Expert sports betting and casino strategy guides: odds, bankroll management, blackjack, roulette, craps, baccarat and more. Free, no signup.">
<meta property="og:title" content="Wager Assistant Blog - Betting &amp; Casino Guides">
<meta property="og:description" content="Expert sports betting and casino strategy guides from Wager Assistant.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:url" content="{SITE}/blog/">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Wager Assistant Blog">
<meta name="twitter:description" content="Expert betting and casino strategy guides.">
<meta name="twitter:image" content="{SITE}/og-image.png">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="WagerAssistant Editorial Team">
<meta name="theme-color" content="#0d0f1a">
<link rel="canonical" href="{SITE}/blog/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap">
<link rel="stylesheet" href="/styles.css?{CACHE}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="application/rss+xml" title="Wager Assistant Blog" href="/blog/feed.xml">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
{NAV}
<div class="page-content">
  <nav class="breadcrumb-wrap" aria-label="Breadcrumb" style="max-width:1100px;margin:16px auto 0;font-size:13px;color:#6f7c91">
    <a href="/index.html" style="color:#8892b0">Home</a> &rsaquo; <span>Blog</span>
  </nav>
  <header class="blog-hero">
    <h1>Betting &amp; Casino Strategy Blog</h1>
    <p>Practical, no-nonsense guides to sports betting and casino games &mdash; odds, bankroll management, and game strategy to help you bet smarter. Pair every guide with our free calculators.</p>
  </header>
  <div class="ad-zone ad-leaderboard" aria-hidden="true"><span>Advertisement</span></div>
  <section class="blog-grid">
    {cards}
  </section>
</div>
{FOOTER}
<script defer src="/nav.js?{CACHE}"></script>
</body>
</html>'''
    open(os.path.join(BLOG, "index.html"), "w", encoding="utf-8").write(doc)


def build_feed(posts):
    now = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = ""
    for p in posts:
        pub = datetime.datetime.strptime(p["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0000")
        items += f'''    <item>
      <title>{esc(p["title"])}</title>
      <link>{SITE}/blog/{p["slug"]}.html</link>
      <guid isPermaLink="true">{SITE}/blog/{p["slug"]}.html</guid>
      <description>{esc(p["meta_description"])}</description>
      <pubDate>{pub}</pubDate>
    </item>
'''
    feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Wager Assistant Blog</title>
    <link>{SITE}/blog/</link>
    <atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Sports betting and casino strategy guides from Wager Assistant.</description>
    <language>en-us</language>
    <lastBuildDate>{now}</lastBuildDate>
{items}  </channel>
</rss>
'''
    open(os.path.join(BLOG, "feed.xml"), "w", encoding="utf-8").write(feed)


def update_sitemap_xml(posts):
    path = os.path.join(ROOT, "sitemap.xml")
    s = open(path, encoding="utf-8").read()
    today = datetime.date.today().isoformat()
    # ensure blog hub + each post present
    def ensure(url):
        if f"<loc>{url}</loc>" in s:
            return ""
        return f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
    add = ensure(f"{SITE}/blog/")
    for p in posts:
        add += ensure(f"{SITE}/blog/{p['slug']}.html")
    if add:
        s = s.replace("</urlset>", add + "</urlset>")
        open(path, "w", encoding="utf-8").write(s)


def update_sitemap_html(posts):
    path = os.path.join(ROOT, "sitemap.html")
    s = open(path, encoding="utf-8").read()
    links = '<li><a href="/blog/index.html">Blog Home</a></li>\n' + "".join(
        f'        <li><a href="/blog/{p["slug"]}.html">{esc(p["title"])}</a></li>\n' for p in posts)
    block = f'    <!-- BLOG-SECTION -->\n    <section class="sitemap-section"><h2>Blog &amp; Guides</h2>\n      <ul>\n        {links}      </ul>\n    </section>\n    <!-- /BLOG-SECTION -->\n\n'
    s = re.sub(r'\s*<!-- BLOG-SECTION -->.*?<!-- /BLOG-SECTION -->\n\n', '', s, flags=re.DOTALL)
    # insert before the sitemap footer paragraph
    if '<p class="sitemap-foot">' in s:
        s = s.replace('    <p class="sitemap-foot">', block + '    <p class="sitemap-foot">', 1)
    elif "</footer>" in s:
        s = s.replace("<footer", block + "<footer", 1)
    open(path, "w", encoding="utf-8").write(s)


def update_homepage(posts):
    path = os.path.join(ROOT, "index.html")
    s = open(path, encoding="utf-8").read()
    latest = posts[:3]
    cards = ""
    for p in latest:
        cards += (f'<article class="hub-card"><span class="hub-tag">{esc(p.get("category","Guide"))}</span>'
                  f'<h3><a href="blog/{p["slug"]}.html" style="color:inherit;text-decoration:none">{esc(p["title"])}</a></h3>'
                  f'<p>{esc(p["meta_description"])}</p></article>')
    s = re.sub(r'(<div class="hub-grid">).*?(</div>\s*</div>\s*</section>)',
               r'\1' + cards + r'\2', s, count=1, flags=re.DOTALL)
    open(path, "w", encoding="utf-8").write(s)


def ping_indexnow(urls):
    try:
        payload = json.dumps({
            "host": "wagerassistant.com", "key": INDEXNOW_KEY,
            "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt", "urlList": urls}).encode()
        req = urllib.request.Request("https://api.indexnow.org/indexnow", data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            print("IndexNow:", r.status)
    except Exception as e:
        print("IndexNow ping failed:", e)


def add_post(json_path, ping=False):
    os.makedirs(BLOG, exist_ok=True)
    post = json.load(open(json_path, encoding="utf-8"))
    post.setdefault("date", datetime.date.today().isoformat())
    post.setdefault("h1", post["title"])
    posts = load_posts()
    if any(p["slug"] == post["slug"] for p in posts):
        print(f"Slug '{post['slug']}' already exists — skipping.")
        return
    # manifest entry (newest first)
    posts.insert(0, {"title": post["title"], "slug": post["slug"], "date": post["date"],
                     "meta_description": post["meta_description"], "category": post.get("category", "Guide"),
                     "primary_keyword": post["primary_keyword"],
                     "secondary_keywords": post.get("secondary_keywords", [])})
    full = [dict(p) for p in posts]
    # write article
    html_doc = render_article(post, posts)
    open(os.path.join(BLOG, f"{post['slug']}.html"), "w", encoding="utf-8").write(html_doc)
    save_posts(posts)
    rebuild(posts)
    print(f"Added post: {post['slug']}.html")
    if ping:
        ping_indexnow([f"{SITE}/blog/{post['slug']}.html", f"{SITE}/blog/", f"{SITE}/"])


def rebuild(posts=None):
    posts = posts or load_posts()
    os.makedirs(BLOG, exist_ok=True)
    build_hub(posts)
    build_feed(posts)
    update_sitemap_xml(posts)
    update_sitemap_html(posts)
    update_homepage(posts)
    print(f"Rebuilt hub/feed/sitemaps/homepage from {len(posts)} posts.")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "add":
        add_post(sys.argv[2], ping="--ping" in sys.argv)
    elif len(sys.argv) >= 2 and sys.argv[1] == "rebuild":
        rebuild()
    else:
        print(__doc__)
