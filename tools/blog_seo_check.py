#!/usr/bin/env python3
"""SEO + quality gate for WagerAssistant blog posts (Python 3 stdlib only).

Run it on the post JSON BEFORE publishing, then on the rendered page AFTER
`blog_generator.py add`. Anything listed under PROBLEMS must be fixed; the run
ends with "Problems: 0" only when the post is ready to publish.

Usage:
  python3 tools/blog_seo_check.py post.json        # check a draft (before add)
  python3 tools/blog_seo_check.py --html <slug>    # check the rendered blog/<slug>.html
  python3 tools/blog_seo_check.py --all            # report on every published post (info only)

House rules enforced here are explained in blog/WRITING-GUIDE.md.
"""
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(ROOT, "blog")
SITE = "https://wagerassistant.com"

TITLE_MIN, TITLE_MAX = 35, 60
META_MIN, META_MAX = 140, 160
WORDS_MIN, WORDS_MAX = 1500, 3200
YEAR = re.compile(r"\b(19|20)\d{2}\b")
STOP = {"a", "an", "the", "in", "on", "of", "to", "for", "and", "or", "is", "what", "does", "do",
        "how", "it", "mean", "means", "vs", "with", "your", "you", "are", "betting", "bet", "bets"}
BANNED = [  # phrases that make promises we can't keep, or leak drafting artifacts
    r"\bguaranteed (win|wins|profit|profits|money)\b", r"\bcan'?t lose\b", r"\bsure thing\b",
    r"\block of the (day|week)\b", r"\bget rich\b", r"\bas an ai\b", r"\blorem ipsum\b",
    r"\bTODO\b", r"\[(insert|citation|source)[^\]]*\]", r"\*\*", r"(?m)^#{1,6} ", r"\bin today'?s (fast-paced|digital)\b",
    r"\bdelve\b", r"\bunlock the secrets\b", r"\bgame[- ]changer\b",
]


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.ids, self.h2, self.h1, self.links, self.imgs = [], [], [], [], [], []
        self.tables, self.wrapped_tables, self.figcaptions = 0, 0, 0
        self.quick_answer = False
        self._stack, self._cur_h = [], None
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._stack.append((tag, a))
        if tag in ("script", "style"):
            self._skip += 1
        if a.get("id"):
            self.ids.append(a["id"])
        if tag in ("h1", "h2"):
            self._cur_h = [tag, a.get("id"), ""]
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "img":
            self.imgs.append(a)
        if tag == "table":
            self.tables += 1
            if any(t == "div" and "table-wrap" in (x.get("class") or "") for t, x in self._stack[:-1]):
                self.wrapped_tables += 1
        if tag == "figcaption":
            self.figcaptions += 1
        if "quick-answer" in (a.get("class") or ""):
            self.quick_answer = True

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        if self._cur_h and tag == self._cur_h[0]:
            (self.h1 if tag == "h1" else self.h2).append((self._cur_h[1], self._cur_h[2].strip()))
            self._cur_h = None
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                del self._stack[i:]
                break

    def handle_data(self, data):
        if self._skip:
            return
        self.text.append(data)
        if self._cur_h:
            self._cur_h[2] += data


def parse(fragment):
    c = Collector()
    c.feed(fragment)
    c.close()
    return c


def words(s):
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'%.+-]*", s)


def core(kw):
    return [w for w in re.findall(r"[a-z0-9.+-]+", kw.lower()) if w not in STOP] or kw.lower().split()


def load_posts():
    p = os.path.join(BLOG, "posts.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []


def internal_target_exists(href, new_slug):
    path = href.split("#")[0].split("?")[0]
    if path in ("", "/"):
        return True
    if path.startswith(SITE):
        path = path[len(SITE):]
    if not path.startswith("/"):
        return True  # relative or anchor-only; not checked here
    if new_slug and path == f"/blog/{new_slug}.html":
        return True
    local = os.path.join(ROOT, path.lstrip("/"))
    if path.endswith("/"):
        local = os.path.join(local, "index.html")
    return os.path.exists(local)


class Report:
    def __init__(self):
        self.problems, self.warnings = [], []

    def p(self, msg):
        self.problems.append(msg)

    def w(self, msg):
        self.warnings.append(msg)

    def show(self, header):
        print(header)
        for m in self.problems:
            print("  PROBLEM:", m)
        for m in self.warnings:
            print("  warning:", m)
        print(f"Problems: {len(self.problems)}  Warnings: {len(self.warnings)}")
        return len(self.problems)


def check_draft(path):
    r = Report()
    post = json.load(open(path, encoding="utf-8"))
    need = ["title", "slug", "meta_description", "primary_keyword", "secondary_keywords", "category",
            "read_time", "toc", "takeaways", "body_html", "faq", "related_calculators", "sources"]
    for k in need:
        if not post.get(k):
            r.p(f"missing or empty field: {k}")
    if r.problems:
        return r.show(f"Draft {path}")

    title, h1, meta = post["title"], post.get("h1", post["title"]), post["meta_description"]
    slug, pk = post["slug"], post["primary_keyword"].strip()
    sk = post["secondary_keywords"]

    # ---- slug, title, description
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug) or len(slug) > 70:
        r.p(f"slug must be lowercase words joined by hyphens, <=70 chars: {slug!r}")
    if not TITLE_MIN <= len(title) <= TITLE_MAX:
        r.p(f"title is {len(title)} chars; must be {TITLE_MIN}-{TITLE_MAX} (the generator would truncate it)")
    if len(h1) > 90:
        r.p(f"h1 is {len(h1)} chars; keep it under 90")
    if not META_MIN <= len(meta) <= META_MAX:
        r.p(f"meta_description is {len(meta)} chars; must be {META_MIN}-{META_MAX}")
    for label, val in [("title", title), ("h1", h1), ("meta_description", meta), ("slug", slug),
                       ("primary_keyword", pk)] + [("secondary keyword", k) for k in sk]:
        if YEAR.search(val):
            r.p(f"{label} contains a year ({YEAR.search(val).group(0)}); content must be evergreen")
    pk_core = core(pk)
    for label, val in (("title", title), ("meta_description", meta)):
        missing = [w for w in pk_core if w not in val.lower()]
        if missing:
            r.p(f"{label} is missing primary-keyword words {missing}")
    if pk.lower() not in title.lower() and pk.lower() not in h1.lower():
        r.w("exact primary keyword is in neither the title nor the H1 (fine only if it reads unnaturally)")
    if not 4 <= len(sk) <= 10:
        r.p(f"secondary_keywords has {len(sk)}; use 4-10")
    if pk.lower() in [k.lower() for k in sk]:
        r.p("primary keyword is repeated in secondary_keywords")

    # ---- duplicates against published posts
    for p in load_posts():
        if p["slug"] == slug:
            r.p(f"slug {slug} is already published")
        if p.get("primary_keyword", "").strip().lower() == pk.lower():
            r.p(f"primary keyword already used by /blog/{p['slug']}.html")
        if p.get("title", "").strip().lower() == title.strip().lower():
            r.p(f"title already used by /blog/{p['slug']}.html")

    # ---- body
    body = post["body_html"]
    c = parse(body)
    text = " ".join(c.text)
    n = len(words(text))
    if not WORDS_MIN <= n <= WORDS_MAX:
        r.p(f"body is {n} words; must be {WORDS_MIN}-{WORDS_MAX}")
    first100 = " ".join(words(text)[:100]).lower()
    if not all(w in first100 for w in pk_core):
        r.p("primary keyword (its main words) must appear in the first 100 words")
    if c.h1:
        r.p("body_html must not contain an <h1> (the generator adds it)")
    if not c.quick_answer:
        r.p('add a <div class="quick-answer"> right after the intro that answers the search in 2-4 sentences')
    if len(c.h2) < 5:
        r.p(f"only {len(c.h2)} <h2> sections; use 5-12")
    if len(c.h2) > 14:
        r.w(f"{len(c.h2)} <h2> sections is a lot; consider merging")
    if not any(all(w in t.lower() for w in pk_core) for _, t in c.h2):
        r.p("no <h2> contains the primary keyword's main words")
    q_h2 = sum(1 for _, t in c.h2 if t.strip().endswith("?"))
    if q_h2 < 2:
        r.w("use question-style H2s for at least 2 sections (they win People Also Ask / AI answers)")
    for hid, t in c.h2:
        if not hid:
            r.p(f'<h2> without an id: "{t[:50]}"')
    toc_ids = [sid for _, sid in post["toc"]]
    if len(toc_ids) < 5:
        r.p("table of contents needs at least 5 entries")
    for sid in toc_ids:
        if sid not in c.ids:
            r.p(f"toc links to #{sid} but no element has that id")
    for hid, t in c.h2:
        if hid and hid not in toc_ids:
            r.p(f'<h2 id="{hid}"> is not in the toc')
    if len(set(c.ids)) != len(c.ids):
        r.p("duplicate id attributes in body_html")
    if c.tables < 1:
        r.p("include at least one comparison or worked-example <table>")
    if c.wrapped_tables < c.tables:
        r.p('wrap every <table> in <div class="table-wrap"> so it scrolls on phones')

    # ---- links
    internal = [h for h in c.links if h.startswith("/") or h.startswith(SITE)]
    external = [h for h in c.links if h.startswith("http") and not h.startswith(SITE)]
    if len(internal) < 6:
        r.p(f"{len(internal)} internal links in the body; need at least 6")
    calc = {h for h in internal if re.search(r"_(calculator|converter)\.html", h)}
    if len(calc) < 2:
        r.p(f"link at least 2 different calculator pages in the body (found {len(calc)})")
    blog_links = {h for h in internal if "/blog/" in h and h.rstrip("/") != "/blog"}
    if not blog_links:
        r.p("link at least one related /blog/ article in the body")
    for h in internal:
        if not internal_target_exists(h, slug):
            r.p(f"internal link points to a page that doesn't exist: {h}")
    for h in c.links:
        if h.startswith("http://"):
            r.p(f"use https links only: {h}")
    for name, href in post["related_calculators"]:
        if not internal_target_exists(href, slug):
            r.p(f"related_calculators link doesn't exist: {href}")
    if len(post["related_calculators"]) < 2:
        r.p("related_calculators needs at least 2 entries")

    srcs = post["sources"]
    if len(srcs) < 3:
        r.p(f"sources has {len(srcs)}; cite at least 3 reputable external sources")
    for t, u in srcs:
        if not u.startswith("https://") or "wagerassistant.com" in u:
            r.p(f"source must be an external https URL: {u}")
    if len(external) < 2:
        r.w("cite at least 2 sources inline in the body as well as in the Sources list")

    # ---- images
    hero = post.get("hero_image")
    if not hero:
        r.w("no hero_image: house style wants a Wikimedia Commons photo with credit (allowed only if Commons was unreachable or nothing relevant had a clear license)")
    else:
        for k in ("src", "alt", "credit_html", "width", "height", "file_page"):
            if not hero.get(k):
                r.p(f"hero_image.{k} is missing")
        if hero.get("src") and not hero["src"].startswith("https://upload.wikimedia.org/"):
            r.p("hero_image.src must be an https://upload.wikimedia.org/ URL")
        cr = hero.get("credit_html", "")
        if "commons.wikimedia.org" not in cr or not re.search(r"CC|public domain|Public domain|PD|GFDL", cr):
            r.p("hero_image.credit_html must name the author, the license (e.g. CC BY-SA 4.0) and link the Commons file page")
        if re.search(r"\bNC\b|NoDerivs|\bND\b|fair use", cr):
            r.p("hero image license must allow commercial reuse (no NC/ND/fair-use)")
    for im in c.imgs:
        if not im.get("alt"):
            r.p(f"in-article image without alt text: {im.get('src', '')[:60]}")
        if not (im.get("width") and im.get("height")):
            r.p(f"in-article image needs width and height attributes: {im.get('src', '')[:60]}")
        if im.get("loading") != "lazy":
            r.p(f'in-article image needs loading="lazy": {im.get("src", "")[:60]}')
    if c.imgs and c.figcaptions < len(c.imgs):
        r.p("every in-article image needs a <figure> with a <figcaption> credit")

    # ---- FAQ, takeaways
    faq = post["faq"]
    if not 4 <= len(faq) <= 8:
        r.p(f"faq has {len(faq)} questions; use 4-8")
    qs = [q.strip().lower() for q, _ in faq]
    if len(set(qs)) != len(qs):
        r.p("duplicate FAQ questions")
    for q, a in faq:
        if not q.strip().endswith("?"):
            r.p(f"FAQ question must end with '?': {q[:60]}")
        if len(words(re.sub("<[^>]+>", " ", a))) < 20:
            r.p(f"FAQ answer too thin (<20 words): {q[:60]}")
    if not 3 <= len(post["takeaways"]) <= 6:
        r.p("takeaways: use 3-6 bullets")
    if not str(post["read_time"]).isdigit():
        r.p("read_time must be a whole number of minutes as a string, e.g. \"9\"")
    elif abs(int(post["read_time"]) - round(n / 230)) > 2:
        r.w(f"read_time {post['read_time']} looks off for {n} words (~{round(n / 230)} min)")

    # ---- banned phrases and artifacts
    blob = " ".join([title, h1, meta, text] + [q + " " + a for q, a in faq] + post["takeaways"])
    for pat in BANNED:
        m = re.search(pat, blob, flags=re.I)
        if m:
            r.p(f"remove banned phrase/artifact: {m.group(0)!r}")
    if "1-800-gambler" in blob.lower():
        r.w("the page footer already carries the 1-800-MY-RESET helpline; don't add a different number unless sourced")

    print(f"words={n}  h2={len(c.h2)}  internal_links={len(internal)}  calculators={len(calc)}  "
          f"external_inline={len(external)}  sources={len(srcs)}  faq={len(faq)}  images={len(c.imgs) + (1 if hero else 0)}")
    return r.show(f"Draft {path}")


def check_html(slug, quiet=False):
    r = Report()
    path = os.path.join(BLOG, f"{slug}.html")
    if not os.path.exists(path):
        r.p(f"{path} not found")
        return r.show(f"Page /blog/{slug}.html")
    doc = open(path, encoding="utf-8").read()
    c = parse(doc)
    m = re.search(r"<title>(.*?)</title>", doc, re.S)
    t = html.unescape(m.group(1)) if m else ""
    if not TITLE_MIN <= len(t) <= TITLE_MAX:
        r.p(f"<title> is {len(t)} chars: {t!r}")
    d = re.search(r'<meta name="description" content="([^"]*)"', doc)
    dl = len(html.unescape(d.group(1))) if d else 0
    if not META_MIN <= dl <= META_MAX:
        r.p(f"meta description is {dl} chars")
    if len(c.h1) != 1:
        r.p(f"page has {len(c.h1)} <h1> elements; must be exactly 1")
    if f'<link rel="canonical" href="{SITE}/blog/{slug}.html">' not in doc:
        r.p("canonical link missing or wrong")
    for block in re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', doc, re.S):
        try:
            json.loads(block)
        except ValueError as e:
            r.p(f"invalid JSON-LD: {e}")
    types = re.findall(r'"@type": "(BlogPosting|BreadcrumbList|FAQPage)"', doc)
    for need in ("BlogPosting", "BreadcrumbList", "FAQPage"):
        if need not in types:
            r.p(f"{need} structured data missing")
    for im in c.imgs:
        if not im.get("alt"):
            r.p(f"image without alt: {im.get('src', '')[:60]}")
    for h in set(c.links):
        if (h.startswith("/") or h.startswith(SITE)) and not internal_target_exists(h, slug):
            r.p(f"broken internal link: {h}")
    if not any(p["slug"] == slug for p in load_posts()):
        r.p("post is not in blog/posts.json")
    sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    if f"<loc>{SITE}/blog/{slug}.html</loc>" not in sm:
        r.p("post is not in sitemap.xml")
    if f"/blog/{slug}.html" not in open(os.path.join(BLOG, "index.html"), encoding="utf-8").read():
        r.p("post is not on the blog hub page")
    if f"{SITE}/blog/{slug}.html" not in open(os.path.join(BLOG, "feed.xml"), encoding="utf-8").read():
        r.p("post is not in the RSS feed")
    if quiet:
        return r
    return r.show(f"Page /blog/{slug}.html")


def check_all():
    total = 0
    for p in load_posts():
        r = check_html(p["slug"], quiet=True)
        if r.problems:
            total += len(r.problems)
            print(f"/blog/{p['slug']}.html")
            for m in r.problems:
                print("   ", m)
    print(f"All published posts: {total} issue(s) (informational; older posts predate these rules)")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    if a[0] == "--all":
        sys.exit(check_all())
    if a[0] == "--html" and len(a) > 1:
        sys.exit(1 if check_html(a[1]) else 0)
    sys.exit(1 if check_draft(a[0]) else 0)
