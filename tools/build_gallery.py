#!/usr/bin/env python3
"""Builds /embed-calculators.html gallery page from tools/_widgets.json.
Shows a live iframe preview of each embed plus a copy-to-clipboard embed snippet
(iframe + an outer plain-HTML attribution backlink)."""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDGETS = json.load(open(os.path.join(ROOT, "tools", "_widgets.json")))

# Recommended iframe heights per widget (px) to fit content without scroll.
HEIGHTS = {
    "betting_calculator": 520,
    "parlay_calculator": 620,
    "odds_converter": 470,
    "arbitrage_calculator": 560,
    "kelly_criterion_calculator": 560,
    "hedging_calculator": 560,
    "expected_value_calculator": 600,
    "implied_probability_calculator": 470,
}

NAV = '''<header class="wa-nav">
  <div class="wa-nav-inner">
    <a href="index.html" class="wa-brand"><span class="wa-brand-icon">&spades;</span><span class="wa-brand-text">Wager<b>Assistant</b></span></a>
    <input type="checkbox" id="wa-nav-toggle" class="wa-nav-toggle" aria-label="Toggle navigation menu">
    <nav class="wa-menu" aria-label="Main navigation">
      <a href="index.html" class="wa-link">Home</a>
      <div class="wa-dd">
        <button type="button" class="wa-dd-btn" aria-haspopup="true">Basic <svg width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        <div class="wa-dd-menu">
          <a href="betting_calculator.html" class=""><span class="wa-dd-t">Betting Calculator</span><span class="wa-dd-sub">Payouts & profit for single bets</span></a>
          <a href="moneyline_calculator.html" class=""><span class="wa-dd-t">Moneyline Calculator</span><span class="wa-dd-sub">American odds payout and profit</span></a>
          <a href="spread_calculator.html" class=""><span class="wa-dd-t">Spread Calculator</span><span class="wa-dd-sub">Point spread bets and payouts</span></a>
          <a href="over_under_calculator.html" class=""><span class="wa-dd-t">Over/Under Calculator</span><span class="wa-dd-sub">Totals betting — over or under</span></a>
          <a href="parlay_calculator.html" class=""><span class="wa-dd-t">Parlay Calculator</span><span class="wa-dd-sub">Combine legs, see total odds & payout</span></a>
          <a href="odds_converter.html" class=""><span class="wa-dd-t">Odds Converter</span><span class="wa-dd-sub">Convert American, decimal & fractional odds</span></a>
        </div>
      </div>
      <div class="wa-dd">
        <button type="button" class="wa-dd-btn" aria-haspopup="true">Advanced <svg width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        <div class="wa-dd-menu">
          <a href="arbitrage_calculator.html" class=""><span class="wa-dd-t">Arbitrage Calculator</span><span class="wa-dd-sub">Guaranteed profit across bookmakers</span></a>
          <a href="hedging_calculator.html" class=""><span class="wa-dd-t">Hedging Calculator</span><span class="wa-dd-sub">Lock in profit on existing bets</span></a>
          <a href="dutching_calculator.html" class=""><span class="wa-dd-t">Dutching Calculator</span><span class="wa-dd-sub">Split stakes for equal profit</span></a>
          <a href="kelly_criterion_calculator.html" class=""><span class="wa-dd-t">Kelly Criterion</span><span class="wa-dd-sub">Optimal stake size from your edge</span></a>
          <a href="expected_value_calculator.html" class=""><span class="wa-dd-t">Expected Value (EV)</span><span class="wa-dd-sub">Find positive expected value bets</span></a>
          <a href="no_vig_calculator.html" class=""><span class="wa-dd-t">No-Vig / True Odds</span><span class="wa-dd-sub">Strip the vig for true odds</span></a>
          <a href="margin_calculator.html" class=""><span class="wa-dd-t">Margin Calculator</span><span class="wa-dd-sub">Reveal the bookmaker's built-in margin</span></a>
        </div>
      </div>
      <div class="wa-dd">
        <button type="button" class="wa-dd-btn" aria-haspopup="true">System <svg width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        <div class="wa-dd-menu">
          <a href="accumulator_calculator.html" class=""><span class="wa-dd-t">Accumulator</span><span class="wa-dd-sub">Multi-selection acca odds & payout</span></a>
          <a href="round_robin_calculator.html" class=""><span class="wa-dd-t">Round Robin</span><span class="wa-dd-sub">All parlay combinations from selections</span></a>
          <a href="yankee_calculator.html" class=""><span class="wa-dd-t">Yankee</span><span class="wa-dd-sub">11 bets from four selections</span></a>
          <a href="trixie_calculator.html" class=""><span class="wa-dd-t">Trixie</span><span class="wa-dd-sub">Four bets from three selections</span></a>
          <a href="patent_calculator.html" class=""><span class="wa-dd-t">Patent</span><span class="wa-dd-sub">Seven bets with singles included</span></a>
          <a href="lucky_15_calculator.html" class=""><span class="wa-dd-t">Lucky 15</span><span class="wa-dd-sub">15 bets from four selections</span></a>
          <a href="lucky_31_calculator.html" class=""><span class="wa-dd-t">Lucky 31</span><span class="wa-dd-sub">31 bets from five selections</span></a>
          <a href="lucky_63_calculator.html" class=""><span class="wa-dd-t">Lucky 63</span><span class="wa-dd-sub">63 bets from six selections</span></a>
          <a href="goliath_calculator.html" class=""><span class="wa-dd-t">Goliath</span><span class="wa-dd-sub">247 bets from eight selections</span></a>
        </div>
      </div>
      <div class="wa-dd">
        <button type="button" class="wa-dd-btn" aria-haspopup="true">Specialty <svg width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        <div class="wa-dd-menu">
          <a href="asian_handicap_calculator.html" class=""><span class="wa-dd-t">Asian Handicap</span><span class="wa-dd-sub">Settle Asian handicap & goal lines</span></a>
          <a href="teaser_calculator.html" class=""><span class="wa-dd-t">Teaser Calculator</span><span class="wa-dd-sub">Adjust spreads across multiple games</span></a>
          <a href="each_way_calculator.html" class=""><span class="wa-dd-t">Each-Way</span><span class="wa-dd-sub">Win and place bet returns</span></a>
          <a href="matched_betting_calculator.html" class=""><span class="wa-dd-t">Matched Betting</span><span class="wa-dd-sub">Back and lay stake calculations</span></a>
          <a href="bonus_bet_converter.html" class=""><span class="wa-dd-t">Bonus Bet Converter</span><span class="wa-dd-sub">Convert free bets to cash value</span></a>
          <a href="poisson_calculator.html" class=""><span class="wa-dd-t">Poisson Distribution</span><span class="wa-dd-sub">Score probabilities from expected goals</span></a>
          <a href="half_point_calculator.html" class=""><span class="wa-dd-t">Half-Point</span><span class="wa-dd-sub">Value of buying or selling points</span></a>
        </div>
      </div>
      <div class="wa-dd">
        <button type="button" class="wa-dd-btn" aria-haspopup="true">Tracking <svg width="10" height="6" viewBox="0 0 10 6" fill="none" aria-hidden="true"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        <div class="wa-dd-menu">
          <a href="roi_calculator.html" class=""><span class="wa-dd-t">ROI Calculator</span><span class="wa-dd-sub">Track betting ROI and yield</span></a>
          <a href="progression_bet_calculator.html" class=""><span class="wa-dd-t">Bet Progression</span><span class="wa-dd-sub">Plan staking to recover losses</span></a>
          <a href="implied_probability_calculator.html" class=""><span class="wa-dd-t">Implied Probability</span><span class="wa-dd-sub">Convert odds to implied probability</span></a>
        </div>
      </div>
      <a href="blog/index.html" class="wa-link">Blog</a>
    </nav>
    <label for="wa-nav-toggle" class="wa-burger" aria-label="Open menu"><span></span><span></span><span></span></label>
  </div>
</header>'''

FOOTER = '''<footer class="site-footer">
  <p>&copy; 2026 WagerAssistant.com - All Rights Reserved. Free tools for informational purposes only. Please gamble responsibly.</p>
  <p><a href="embed-calculators.html">Embed our free calculators on your site</a> &middot; <a href="sitemap.html">Sitemap</a></p>
</footer>'''

PAGE_CSS = '''
<style>
.embed-hero{max-width:860px;margin:0 auto 10px;padding:28px 20px 6px;text-align:center}
.embed-hero h1{font-size:30px;font-weight:800;letter-spacing:-.5px;margin-bottom:12px;line-height:1.15}
.embed-hero p{color:var(--muted,#8892b0);font-size:16px;line-height:1.6;max-width:680px;margin:0 auto}
.embed-intro{max-width:860px;margin:18px auto;padding:18px 22px;background:var(--surface,#141728);border:1px solid var(--border,#2a2f52);border-radius:14px}
.embed-intro h2{font-size:18px;margin-bottom:8px}
.embed-intro ol{margin:8px 0 0 20px;color:var(--muted,#8892b0);line-height:1.8;font-size:14.5px}
.widget-list{max-width:900px;margin:0 auto;padding:10px 16px 40px;display:flex;flex-direction:column;gap:34px}
.widget-block{background:var(--surface,#141728);border:1px solid var(--border,#2a2f52);border-radius:16px;overflow:hidden}
.widget-head{padding:18px 20px;border-bottom:1px solid var(--border,#2a2f52);display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.widget-head .wic{font-size:24px}
.widget-head h2{font-size:19px;font-weight:700}
.widget-head .wlink{margin-left:auto;font-size:13px;color:var(--accent,#4f6ef7);text-decoration:none;font-weight:600}
.widget-head .wlink:hover{text-decoration:underline}
.widget-body{padding:20px;display:grid;grid-template-columns:1fr 1fr;gap:22px;align-items:start}
@media(max-width:760px){.widget-body{grid-template-columns:1fr}}
.preview-wrap{background:var(--bg,#0d0f1a);border:1px solid var(--border,#2a2f52);border-radius:12px;padding:6px}
.preview-wrap iframe{width:100%;border:0;border-radius:8px;display:block;background:var(--bg,#0d0f1a)}
.snippet-col label{display:block;font-size:12px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted,#8892b0);margin-bottom:6px;font-weight:600}
.snippet-box{position:relative}
.snippet-box textarea{width:100%;height:150px;resize:vertical;background:var(--bg,#0d0f1a);color:var(--text,#e8eaf6);border:1px solid var(--border,#2a2f52);border-radius:10px;padding:12px 12px 12px 12px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;line-height:1.5}
.copy-btn{margin-top:10px;background:var(--accent,#4f6ef7);color:#fff;border:0;border-radius:9px;padding:10px 18px;font-weight:600;font-size:14px;cursor:pointer;font-family:inherit}
.copy-btn:hover{filter:brightness(1.08)}
.copy-btn.done{background:var(--green,#10b981)}
.size-note{margin-top:10px;font-size:12.5px;color:var(--muted,#8892b0);line-height:1.6}
.size-note code{background:var(--surface2,#1c2038);padding:1px 6px;border-radius:5px;font-size:12px}
.embed-foot-note{max-width:860px;margin:0 auto 46px;padding:18px 22px;background:var(--surface,#141728);border:1px solid var(--border,#2a2f52);border-radius:14px;color:var(--muted,#8892b0);font-size:14px;line-height:1.7}
.embed-foot-note strong{color:var(--text,#e8eaf6)}
</style>'''

def snippet(slug, h):
    """The embed code users paste. iframe + an outer plain attribution backlink."""
    return (
        f'<iframe src="https://wagerassistant.com/embed/{slug}.html"\n'
        f'        width="100%" height="{h}" style="max-width:480px;border:0;"\n'
        f'        loading="lazy" title="WagerAssistant Calculator"></iframe>\n'
        f'<p style="font-size:12px;">Calculator by '
        f'<a href="https://wagerassistant.com/{[w["full"] for w in WIDGETS if w["slug"]==slug][0]}" '
        f'target="_blank" rel="noopener">WagerAssistant.com</a></p>'
    )

blocks = []
for w in WIDGETS:
    slug = w["slug"]; h = HEIGHTS.get(slug, 540)
    code = snippet(slug, h)
    code_esc = html.escape(code)
    blocks.append(f'''  <section class="widget-block">
    <div class="widget-head">
      <span class="wic">{w["icon"]}</span>
      <h2>{w["name"]}</h2>
      <a class="wlink" href="{w["full"]}" target="_blank" rel="noopener">View full calculator &rarr;</a>
    </div>
    <div class="widget-body">
      <div class="preview-col">
        <label style="display:block;font-size:12px;text-transform:uppercase;letter-spacing:.5px;color:var(--muted,#8892b0);margin-bottom:6px;font-weight:600">Live preview</label>
        <div class="preview-wrap">
          <iframe src="embed/{slug}.html" height="{h}" loading="lazy" title="{w["name"]} preview"></iframe>
        </div>
      </div>
      <div class="snippet-col">
        <label for="code-{slug}">Copy this embed code</label>
        <div class="snippet-box">
          <textarea id="code-{slug}" readonly spellcheck="false">{code_esc}</textarea>
        </div>
        <button type="button" class="copy-btn" data-target="code-{slug}">Copy code</button>
        <p class="size-note">Recommended size: width <code>100%</code> (max <code>480px</code>), height <code>{h}px</code>. The calculator is responsive &mdash; adjust the height if your layout needs it. Keep the attribution link so your readers can reach the full tool.</p>
      </div>
    </div>
  </section>''')

body = "\n".join(blocks)

DESC = "Add free, responsive betting calculator widgets to your website. Copy-paste embed code for parlay, arbitrage, Kelly, odds converter and more."
assert 140 <= len(DESC) <= 160, f"meta desc len={len(DESC)}"
TITLE = "Free Betting Calculator Widgets to Embed | WagerAssistant"
assert len(TITLE) <= 60, f"title len={len(TITLE)}"

doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TJL7RNVKJY"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-TJL7RNVKJY');
</script>
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Wager Assistant">
<link rel="canonical" href="https://wagerassistant.com/embed-calculators.html">
<meta property="og:title" content="Free Betting Calculator Widgets for Your Website">
<meta property="og:description" content="{DESC}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://wagerassistant.com/embed-calculators.html">
<meta property="og:site_name" content="Wager Assistant">
<meta property="og:image" content="https://wagerassistant.com/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Free Betting Calculator Widgets for Your Website">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="https://wagerassistant.com/og-image.png">
<meta name="theme-color" content="#0d0f1a">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap">
<link rel="stylesheet" href="styles.css?v=20261027">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="application/rss+xml" title="Wager Assistant Blog" href="/blog/feed.xml">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"WebPage","name":"Free Betting Calculator Widgets","description":"{DESC}","url":"https://wagerassistant.com/embed-calculators.html","publisher":{{"@type":"Organization","name":"Wager Assistant","url":"https://wagerassistant.com"}}}}
</script>
{PAGE_CSS}
</head>
<body>
{NAV}

<div class="page-content">
  <div class="embed-hero">
    <h1>Free Betting Calculator Widgets for Your Website</h1>
    <p>Embed any of our free betting calculators on your own blog, forum or tipster site in seconds. Each widget is lightweight, mobile-friendly and completely free &mdash; just copy the code below.</p>
  </div>

  <div class="embed-intro">
    <h2>How to embed a calculator</h2>
    <ol>
      <li>Pick a calculator below and press <strong>Copy code</strong>.</li>
      <li>Paste the code into your website&rsquo;s HTML where you want the calculator to appear.</li>
      <li>That&rsquo;s it &mdash; the calculator loads instantly. Please keep the attribution link so your visitors can reach the full tool.</li>
    </ol>
  </div>

  <div class="widget-list">
{body}
  </div>

  <div class="embed-foot-note">
    <p><strong>Free to use, no catch.</strong> These widgets are offered free for personal and commercial websites. They do not set tracking cookies or run ads. The only requirement is that you keep the visible &ldquo;Powered by WagerAssistant.com&rdquo; attribution link intact. Questions or need a custom size? Visit <a href="index.html">WagerAssistant.com</a>.</p>
  </div>
</div>

{FOOTER}

<script defer src="nav.js?v=20261027"></script>
<script>
document.addEventListener('click', function(e){{
  var btn = e.target.closest('.copy-btn');
  if(!btn) return;
  var ta = document.getElementById(btn.getAttribute('data-target'));
  if(!ta) return;
  ta.select(); ta.setSelectionRange(0, 99999);
  var ok = function(){{
    var old = btn.textContent;
    btn.textContent = 'Copied!'; btn.classList.add('done');
    setTimeout(function(){{ btn.textContent = old; btn.classList.remove('done'); }}, 1800);
  }};
  if(navigator.clipboard && navigator.clipboard.writeText){{
    navigator.clipboard.writeText(ta.value).then(ok, function(){{ try{{document.execCommand('copy');ok();}}catch(_){{}} }});
  }} else {{ try{{document.execCommand('copy');ok();}}catch(_){{}} }}
}});
</script>
</body>
</html>'''

out = os.path.join(ROOT, "embed-calculators.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(doc)
print(f"wrote {out} ({len(doc)} bytes), title={len(TITLE)}ch desc={len(DESC)}ch")
