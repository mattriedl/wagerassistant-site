# WagerAssistant blog — writing and publishing guide

This is the rulebook for every new article on https://wagerassistant.com/blog/, including the
scheduled task that publishes one article every 3 days. Follow it exactly. When in doubt, choose
accuracy over length and leave out anything you can't verify.

The site: 32 free betting calculators plus a blog. Readers are US sports bettors (21+) from beginner
to intermediate, with some UK readers for system bets. Every article should answer one search fully
and send the reader to the calculator that does the math.

Pipeline at a glance:

1. Pick the keyword (OpenSEO + web search) → 2. Verify facts and do the math → 3. Write the post JSON →
4. `python3 tools/blog_seo_check.py post.json` until "Problems: 0" → 5. `python3 tools/blog_generator.py add post.json` →
6. `python3 tools/blog_seo_check.py --html <slug>` + browser check → 7. commit and push to main (this deploys) →
8. confirm live, submit to IndexNow, log in OpenSEO, update `blog/topics.md`.

---

## 1. Pick the keyword

Read first: `blog/topics.md` (published list + researched backlog) and the `primary_keyword` /
`secondary_keywords` of every entry in `blog/posts.json`. Never repeat a primary keyword or a search
intent that an existing post already serves. A "what is X" explainer and an "X strategy" post are
different intents and can coexist, but the explainer must link to the strategy post as the next step and
must not re-teach its strategy content.

Default: the top unused Backlog row. Choose another row only when:
- a Seasonal row's publish window is open now (check the real event date with a web search), or
- the fresh data below shows a clearly better opportunity (more volume at similar or lower KD, or a query
  where the site already sits on page 2).

OpenSEO (project "wagerassistant.com", projectId `c4cc47e5-a942-4d0d-a467-2e5d41786fa2`, US market).
Budget about 150-400 credits per article; never more than 1,000 without Matt's OK.
- `get_project_context` (free): read the research log so you don't re-buy research.
- `get_search_console_performance` (free) for the last 28 days, positions 5-30: queries where we are close.
  If an existing post already gets impressions for your candidate, pick a different keyword.
- `research_keywords` (about 54 credits per seed): 1-3 seeds to find long-tail variants and questions.
  Wildcards work well: `"what does * mean in betting"`, `"how does a * bet work"`.
- `get_keyword_metrics` on your shortlist (cheap): volume, KD, intent.
- `get_serp_results` for the final primary keyword (about 5 credits): who ranks, how deep their pages
  are, which questions they skip, whether a calculator/tool would beat them.

Selection rules:
- Primary keyword: informational intent, real demand (ideally 200+/month), KD under 30 (under 20 is best
  while the site is new), and a page one that isn't wall-to-wall major media.
- 4-10 secondary keywords: close variants, People-Also-Ask style questions, and long-tails from
  `research_keywords`. Each one must be answered somewhere in the article (a section, a table row or an FAQ).
- No years in the keyword, title, H1, description or slug (house rule: evergreen). Avoid sportsbook-brand
  keywords ("round robin fanduel") as primary keywords; mentioning that most US books offer the bet type
  is fine.
- Trending: also run 2-4 web searches for what bettors are searching right now (current NFL/NBA/NHL/MLB/
  college calendar, playoffs, Super Bowl, March Madness, new state launches, rule changes). Use trends to
  pick between candidates and to choose timely examples, never to put dates in titles.

## 2. Research and verify

- Use primary or authoritative sources: league rulebooks (NFL, NBA, MLB, NHL, NCAA), state gaming
  regulators (for example NJ DGE, PA PGCB, Nevada Gaming Control Board), the American Gaming Association,
  the National Council on Problem Gambling, sportsbook house-rules / help pages for settlement rules,
  academic papers, Investopedia-level references for math terms. Avoid thin affiliate sites as sources.
- Cite at least 3 sources in `sources`, and at least 2 of them inline in the body where the claim is made.
  Every link must be https and must load.
- Never invent statistics, quotes, studies, rulings, sportsbook policies, payout tables or personal
  experiences ("we tested", "in our experience"). If a fact can't be verified, leave it out or say it
  varies by sportsbook and state.
- Do every number in Python before writing it: payouts, implied probabilities, vig, combinations, EV.
  Round consistently (2 decimals for money, 1 for percentages). Use American odds first, with decimal in
  brackets where useful. Re-run the math after edits.
- Settlement rules differ between books (pushes in parlays, voids, overtime). Say so and describe the
  common rule rather than presenting one book's rule as universal.

## 3. Article structure (what every post contains)

Length: 1,500-3,000 words (the checker enforces 1,500-3,200). Long enough to fully answer, no filler.

In this order inside `body_html`:
1. **Intro (2-3 short paragraphs).** Answer the search in the first 2 sentences. Put the primary keyword
   (its main words, naturally) in the first 100 words. Say what the reader will be able to do afterwards.
2. **Quick answer box:** `<div class="quick-answer"><p><strong>Quick answer:</strong> ...</p></div>`,
   40-60 words, a self-contained definition. This is what Google's featured snippet and AI answers lift.
3. **5-12 `<h2 id="...">` sections**, most phrased as the questions people search ("How does a round robin
   bet work?", "How much does a round robin pay?"). At least one H2 contains the primary keyword's main
   words. Use `<h3>` for sub-points. Keep paragraphs to 2-4 sentences.
4. **At least one worked example with real numbers** and **at least one table**, every table wrapped:
   `<div class="table-wrap"><table>...</table></div>` with a `<thead>`.
5. **A calculator call-to-action** where the math appears:
   `<div class="calc-cta"><p>Run your own numbers with the free <a href="/round_robin_calculator.html">Round Robin Calculator</a> ...</p></div>`.
6. **Lists for steps** (`<ol>`) and for options (`<ul>`): these win list snippets.
7. **A "mistakes to avoid" or "pros and cons" section** when it fits the intent.
8. Optional extra photos as `<figure><img src="https://upload.wikimedia.org/..." alt="..." width="..." height="..." loading="lazy"><figcaption>credit</figcaption></figure>`.
9. End with a short wrap-up paragraph that points to the next step (a calculator or a related guide).
   Don't add a responsible-gambling section: the generator appends the disclaimer automatically.

The generator adds the H1, byline, hero photo, table of contents, key takeaways box, Sources list, FAQ
accordion, related links, structured data (BlogPosting, BreadcrumbList, FAQPage) and the disclaimer.

Links (counted in `body_html` only):
- 6+ internal links, root-relative (`/parlay_calculator.html`, `/blog/parlay-betting-tips.html`).
- 2+ different calculator pages and 1+ related blog post. Link the most relevant calculator in the first
  third of the article. Use descriptive anchor text, never "click here".
- Every internal link must point to a file that exists in the repo (the checker verifies).
- External links: https, `target="_blank" rel="noopener"`. No sportsbook affiliate links, no promo codes,
  no links to offshore/unlicensed books.

FAQ: 4-8 real questions taken from People Also Ask, `research_keywords` questions and the secondary
keywords. Answers 40-90 words, self-contained, may include a link. No "is gambling legal" style FAQ
unless the article is about it, and no responsible-gambling FAQ (the disclaimer covers it).

Takeaways: 3-6 short bullets that summarise the article (shown above the body).

## 4. On-page SEO rules

- `title` (the `<title>` tag): 35-60 characters, primary keyword near the start, no year, no brand suffix
  (the generator does not add one and the checker counts the title as written). Make it specific and
  click-worthy, e.g. "What Is a Round Robin Bet? Payouts and Examples".
- `h1`: may be slightly longer or more natural than the title (under 90 characters), also no year.
- `meta_description`: 140-160 characters, contains the primary keyword's main words, states the
  benefit, reads like a sentence a person would click. No year.
- `slug`: the primary keyword in lowercase-hyphens, short, no year, no stop-word padding
  (`what-is-a-round-robin-bet`).
- `category`: one of Guide, Strategy, Odds, Glossary, Casino.
- `read_time`: words / 230, rounded, as a string.
- Write for people first: plain US English, second person, short sentences, define every term the first
  time. Use the entity vocabulary page one uses (for example: legs, combinations, stake per bet, total
  stake, push, void) so Google sees full topical coverage.
- E-E-A-T: show the math, cite sources, explain where rules vary, and never overstate. No hype words and no
  promises ("guaranteed", "can't lose", "lock"). The checker blocks these.
- Images: one hero image (section 5) with descriptive alt text that includes the topic naturally.

## 5. Photos (Wikimedia Commons)

House rule: use Wikimedia Commons photos with credits. One hero image per post; extra in-article
photos are optional.

1. Search Commons for a relevant, good-quality photo (a sportsbook, stadium, betting slips, chips,
   scoreboard, the sport in question). Prefer photos without identifiable private people, logos dominating
   the frame, or minors.
2. Confirm the license on the file page: CC0, public domain, CC BY or CC BY-SA only (commercial reuse
   allowed). Reject NC, ND, fair-use and "no known copyright restrictions" without a clear tag.
3. Get the author, the license short name, the file page URL, a thumbnail URL on
   `upload.wikimedia.org` about 1200px wide, and its width and height.
   - Commons API (send a User-Agent such as `WagerAssistantBlog/1.0 (contact@wagerassistant.com)`):
     `https://commons.wikimedia.org/w/api.php?action=query&titles=File:NAME&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1200&format=json`
   - The API sometimes rate-limits this environment. If it does, wait 30 seconds and try once more, then
     use WebFetch on the file page (`https://commons.wikimedia.org/wiki/File:NAME`) to read the license,
     author and dimensions; build the thumbnail URL from the original URL
     (`.../commons/X/XY/Name.jpg` → `.../commons/thumb/X/XY/Name.jpg/1200px-Name.jpg`) and compute the
     height from the aspect ratio.
   - If you still can't verify a license, publish without a photo and say so in the report. Never guess a
     license.
4. In the post JSON:

```json
"hero_image": {
  "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/.../1200px-Name.jpg",
  "width": 1200, "height": 800,
  "alt": "Betting odds board at a Las Vegas sportsbook",
  "file_page": "https://commons.wikimedia.org/wiki/File:Name.jpg",
  "credit_html": "Photo: <a href=\"https://commons.wikimedia.org/wiki/File:Name.jpg\" target=\"_blank\" rel=\"noopener\">Author Name</a>, <a href=\"https://creativecommons.org/licenses/by-sa/4.0/\" target=\"_blank\" rel=\"noopener\">CC BY-SA 4.0</a>, via Wikimedia Commons"
}
```

Images are hotlinked from upload.wikimedia.org (allowed by Wikimedia). The hero is also used as the
social/OG image and the BlogPosting image.

## 6. Post JSON

Write the draft to a scratch file outside the repo (e.g. `/tmp/<slug>.json`), never into `blog/`.
The full schema is in `tools/README_BLOG_AUTOMATION.md`. Fields used for every post:

```json
{
  "title": "...", "h1": "...", "slug": "...", "category": "Guide", "read_time": "9",
  "meta_description": "...", "primary_keyword": "...", "secondary_keywords": ["...", "..."],
  "date": "YYYY-MM-DD (today, America/Los_Angeles)",
  "hero_image": { "...": "see section 5" },
  "toc": [["Section label", "section-id"]],
  "takeaways": ["..."],
  "body_html": "<p>...</p><div class=\"quick-answer\">...</div><h2 id=\"section-id\">...</h2>...",
  "sources": [["Source title (publisher)", "https://..."]],
  "faq": [["Question?", "Answer, may contain <a href=\"/...\">links</a>."]],
  "related_calculators": [["Round Robin Calculator", "/round_robin_calculator.html"]]
}
```

- `toc` lists every `<h2 id>` in `body_html`, in order (the generator adds FAQ and Sources itself; don't
  put them in `toc` or `body_html`).
- Build the JSON with Python (`json.dump(..., ensure_ascii=False, indent=2)`) so quotes in HTML are
  escaped correctly.

## 7. Responsible gambling and compliance

- Audience is 21+ in the US (18+ in some places). Never target or depict minors.
- Informational only: no picks, no "bet this", no guaranteed outcomes, no claims that a system beats the
  house long-term unless the math shows a positive edge and you explain the conditions.
- Legality varies by state: say so wherever it matters; never encourage offshore or unlicensed books.
- No sportsbook promo codes, bonus offers or affiliate language. Neutral mentions of how major US books
  label a feature are fine.
- Casino posts: always state the house edge plainly.
- The generator appends the responsible-gambling disclaimer with the 1-800-MY-RESET helpline.

## 8. Checks (all must pass before you push)

```bash
python3 tools/blog_seo_check.py /tmp/<slug>.json      # must end "Problems: 0"; fix warnings where reasonable
python3 tools/blog_generator.py add /tmp/<slug>.json    # renders the page, updates hub/home/sitemaps/feed/posts.json
python3 tools/blog_seo_check.py --html <slug>           # must end "Problems: 0"
python3 tools/blog_seo_check.py --all                   # no new problems in other posts
git diff --stat                                         # only expected files changed
```

The generator prints `[SEO] WARNING ... truncated` if a title or description was too long: that must
never happen (the draft check prevents it). If it does, `git checkout -- .`, fix the JSON and re-run.

Browser check: serve the repo (`python3 -m http.server 8765` in the background) and load
`http://localhost:8765/blog/<slug>.html` with Playwright at 390px and 1440px wide. Confirm: no sideways
scrolling (`document.documentElement.scrollWidth <= innerWidth`), the hero photo loads (or note that the
workspace can't reach Wikimedia), the TOC links jump to their sections, tables scroll inside their wrapper,
and the FAQ opens. Screenshot both widths and look at them.

Editor pass: re-read the whole article once. Check every number against your Python output, every fact
against its source, every link target, tone (helpful, plain, no hype) and that each secondary keyword is
answered.

## 9. Publish

- Commit only the files the generator changed plus `blog/topics.md`: `blog/<slug>.html`, `blog/index.html`,
  `blog/feed.xml`, `blog/posts.json`, `index.html`, `sitemap.xml`, `sitemap.html`, `blog/topics.md`.
- Commit message `Blog: <title>`, a blank line, then the co-author and session trailers. Author:
  `git -c user.name="Matt Riedl" -c user.email="mattriedl@users.noreply.github.com"`.
- `git pull --rebase origin main`, then `git push origin main`. Pushing to main deploys: the server pulls
  new commits every 15 minutes (`site-autosync`). Never push a post that failed any check.
- Wait for it to go live: poll `https://wagerassistant.com/blog/<slug>.html?v=<timestamp>` every 2 minutes
  for up to 25 minutes until it returns 200 and contains the title. Also confirm `sitemap.xml` lists it.
- IndexNow: OpenSEO `submit_indexnow_urls` with the article URL, `https://wagerassistant.com/blog/` and
  `https://wagerassistant.com/` (OpenSEO's key file `c1405303997646469b7fa65ab6601f7f.txt` is at the site
  root). If that fails, run `python3 -c "import sys; sys.path.insert(0,'tools'); import blog_generator as g; g.ping_indexnow([...])"`.
- OpenSEO `update_project_context` with `appendResearchLog`: "Blog post <date>: /blog/<slug>.html — primary
  '<keyword>' (vol/KD), secondaries ..., credits used N."
- In `blog/topics.md`: add the post to the Published table, delete its Backlog row, and append any good new
  keyword ideas you found (with volume and KD) to the Backlog. Commit that with the post (same commit).

## 10. If something goes wrong

- A check fails and you can't fix it within the run: don't push; leave the draft in /tmp and report.
- The push is rejected because main moved: `git pull --rebase origin main`, re-run
  `python3 tools/blog_generator.py rebuild` if hub/sitemap files conflicted, re-run the checks, push again.
- The page isn't live after 25 minutes: report it (the server's autosync may be down; status file
  `/var/log/site-autosync.status` on the server). Don't push again.
- OpenSEO unavailable: use web search for page-one checks and the backlog's numbers, and say so in the
  report.
