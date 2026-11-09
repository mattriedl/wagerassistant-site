#!/usr/bin/env python3
"""Generate advertise-with-us.html — the 'Advertise with Us / Link to Us' page.

Shows all 8 WagerAssistant banner ads (animated GIF by default, with a toggle to
the static PNG), a copy-to-clipboard embed-code box per banner, download links
(GIF, PNG, PNG @2x, HTML5 zip), a plain text-link snippet, a download-all button,
usage guidelines and an advertising-inquiry section.

Run from repo root:  python3 tools/build_advertise.py
"""
import os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = "20261027"
GA = "G-TJL7RNVKJY"
SITE = "https://wagerassistant.com"

# Banner catalogue — order: most popular / largest first. (w, h, IAB name)
BANNERS = [
    (728, 90,  "Leaderboard"),
    (300, 250, "Medium Rectangle"),
    (336, 280, "Large Rectangle"),
    (300, 600, "Half Page"),
    (160, 600, "Wide Skyscraper"),
    (468, 60,  "Banner"),
    (320, 50,  "Mobile Leaderboard"),
    (250, 250, "Square"),
]

TITLE = "Advertise with Us — Free Banners to Link to WagerAssistant"
DESC = ("Grab free WagerAssistant banner ads in 8 standard sizes — animated GIF or "
        "static PNG. Copy the embed code and link to our 32 free betting calculators.")
CANON = f"{SITE}/advertise-with-us.html"

with open(os.path.join(ROOT, "tools", "_nav.html"), "r", encoding="utf-8") as f:
    NAV = f.read().strip()

ALT = "WagerAssistant – 32 Free Betting Calculators"


def embed_snippet(w, h, ext):
    return (f'<a href="{SITE}/" target="_blank" rel="noopener">'
            f'<img src="{SITE}/banners/wagerassistant_{w}x{h}.{ext}" '
            f'width="{w}" height="{h}" alt="{ALT}"></a>')


def card(w, h, name):
    slug = f"{w}x{h}"
    gif_code = embed_snippet(w, h, "gif")
    png_code = embed_snippet(w, h, "png")
    return f'''      <div class="ban-card" data-slug="{slug}">
        <div class="ban-head">
          <h2>{name} &mdash; {w}&times;{h}</h2>
        </div>
        <div class="ban-preview">
          <img class="ban-img" id="img-{slug}" src="banners/wagerassistant_{slug}.gif?v=20261105"
               width="{w}" height="{h}" alt="{ALT} ({name}, {w}x{h})" loading="lazy"
               data-gif="banners/wagerassistant_{slug}.gif?v=20261105"
               data-png="banners/wagerassistant_{slug}.png?v=20261105">
        </div>
        <div class="ban-controls">
          <div class="ban-toggle" role="group" aria-label="Choose banner version for {name}">
            <button type="button" class="ver-btn active" data-slug="{slug}" data-ver="gif" aria-pressed="true">Animated GIF</button>
            <button type="button" class="ver-btn" data-slug="{slug}" data-ver="png" aria-pressed="false">Static PNG</button>
          </div>
          <textarea class="code-box" id="code-{slug}" readonly rows="3"
                    data-gif="{html.escape(gif_code, quote=True)}"
                    data-png="{html.escape(png_code, quote=True)}">{html.escape(gif_code)}</textarea>
          <button type="button" class="copy-btn" data-target="code-{slug}">Copy code</button>
          <div class="ban-dl">
            <span class="ban-dl-label">Download:</span>
            <a href="banners/wagerassistant_{slug}.gif" download>GIF</a>
            <a href="banners/wagerassistant_{slug}.png" download>PNG</a>
            <a href="banners/wagerassistant_{slug}@2x.png" download>PNG @2x</a>
            <a href="banners/wagerassistant_{slug}_html5.zip" download>HTML5 .zip</a>
          </div>
        </div>
      </div>'''


CARDS = "\n".join(card(w, h, n) for (w, h, n) in BANNERS)

TEXT_LINK = f'<a href="{SITE}/">WagerAssistant – Free Betting Calculators</a>'

HEAD = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA}');
</script>
<title>{html.escape(TITLE)}</title>
<meta name="description" content="{html.escape(DESC, quote=True)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="author" content="Wager Assistant">
<link rel="canonical" href="{CANON}">
<meta property="og:title" content="{html.escape(TITLE)}">
<meta property="og:description" content="{html.escape(DESC, quote=True)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{CANON}">
<meta property="og:site_name" content="Wager Assistant">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(TITLE)}">
<meta name="twitter:description" content="{html.escape(DESC, quote=True)}">
<meta name="twitter:image" content="{SITE}/og-image.png">
<meta name="theme-color" content="#0d0f1a">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap">
<link rel="stylesheet" href="styles.css?v=20261108">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="application/rss+xml" title="Wager Assistant Blog" href="/blog/feed.xml">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"WebPage","name":"{html.escape(TITLE)}","description":"{html.escape(DESC, quote=True)}","url":"{CANON}","publisher":{{"@type":"Organization","name":"Wager Assistant","url":"{SITE}"}}}}
</script>

<style>
.adv-hero{{max-width:860px;margin:0 auto 6px;padding:28px 20px 6px;text-align:center}}
.adv-hero h1{{font-size:30px;font-weight:800;letter-spacing:-.5px;margin-bottom:12px;line-height:1.15}}
.adv-hero p{{color:var(--muted,#8892b0);font-size:16px;line-height:1.6;max-width:680px;margin:0 auto}}
.adv-actions{{max-width:900px;margin:18px auto 4px;padding:0 16px;text-align:center}}
.btn-download-all{{display:inline-block;background:linear-gradient(135deg,#4f6ef7,#7c3aed);color:#fff;text-decoration:none;font-weight:700;font-size:15px;padding:13px 26px;border-radius:11px}}
.btn-download-all:hover{{filter:brightness(1.08)}}
.ban-grid{{max-width:900px;margin:0 auto;padding:18px 16px 10px;display:grid;grid-template-columns:repeat(2,1fr);gap:22px}}
@media(max-width:760px){{.ban-grid{{grid-template-columns:1fr}}}}
.ban-card{{background:var(--surface,#141728);border:1px solid var(--border,#2a2f52);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}}
.ban-head{{padding:15px 18px;border-bottom:1px solid var(--border,#2a2f52)}}
.ban-head h2{{font-size:16px;font-weight:700}}
.ban-preview{{padding:16px;display:flex;align-items:center;justify-content:center;background:var(--bg,#0d0f1a);min-height:120px;overflow:auto}}
.ban-img{{max-width:100%;height:auto;display:block;border-radius:6px;box-shadow:0 2px 10px rgba(0,0,0,.35)}}
.ban-controls{{padding:16px 18px 18px;display:flex;flex-direction:column;gap:10px}}
.ban-toggle{{display:inline-flex;gap:0;border:1px solid var(--border,#2a2f52);border-radius:9px;overflow:hidden;align-self:flex-start}}
.ver-btn{{background:transparent;color:var(--muted,#8892b0);border:0;padding:7px 14px;font-family:inherit;font-size:13px;font-weight:600;cursor:pointer}}
.ver-btn.active{{background:var(--accent,#4f6ef7);color:#fff}}
.code-box{{width:100%;background:var(--bg,#0d0f1a);color:#c7d0f5;border:1px solid var(--border,#2a2f52);border-radius:9px;padding:10px 12px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;line-height:1.5;resize:vertical}}
.copy-btn{{background:var(--accent,#4f6ef7);color:#fff;border:0;border-radius:9px;padding:10px 18px;font-weight:600;font-size:14px;cursor:pointer;font-family:inherit;align-self:flex-start}}
.copy-btn:hover{{filter:brightness(1.08)}}
.copy-btn.done{{background:var(--green,#10b981)}}
.ban-dl{{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;font-size:13px}}
.ban-dl-label{{color:var(--muted,#8892b0);font-weight:600}}
.ban-dl a{{color:var(--accent-text,#a5b4fc);text-decoration:none;font-weight:600}}
.ban-dl a:hover{{text-decoration:underline}}
.adv-panel{{max-width:900px;margin:22px auto;padding:20px 22px;background:var(--surface,#141728);border:1px solid var(--border,#2a2f52);border-radius:14px}}
.adv-panel h2{{font-size:19px;margin-bottom:10px}}
.adv-panel p{{color:var(--muted,#8892b0);font-size:14.5px;line-height:1.7;margin-bottom:10px}}
.adv-panel ul{{margin:6px 0 0 20px;color:var(--muted,#8892b0);line-height:1.8;font-size:14.5px}}
.adv-textlink{{margin:10px 0}}
.adv-textlink textarea{{width:100%;background:var(--bg,#0d0f1a);color:#c7d0f5;border:1px solid var(--border,#2a2f52);border-radius:9px;padding:10px 12px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;line-height:1.5;resize:vertical}}
</style>
</head>
<body>

{NAV}

<div class="page-content">
  <div class="adv-hero">
    <h1>Advertise with Us &mdash; Link to WagerAssistant</h1>
    <p>Run a blog, tipster service, forum or betting site? Use our free, ready-made banner ads to link back to WagerAssistant and give your readers instant access to our <strong>32 free betting calculators</strong>. Pick a size, copy the code, done &mdash; no sign-up, no cost.</p>
  </div>

  <div class="adv-actions">
    <a class="btn-download-all" href="banners/wagerassistant_banners.zip" download>&#11015; Download all banners (.zip)</a>
  </div>

  <!-- AD ZONE: Leaderboard 728x90 - READY FOR INTEGRATION -->
  <div class="ad-zone ad-leaderboard ad-live" role="complementary" aria-label="Advertisement"><div class="ad-slot ad-slot-desktop" data-gb-spot="leaderboard"></div><div class="ad-slot ad-slot-mobile" data-gb-spot="mobile-banner"></div></div>

  <section class="ban-grid" aria-label="WagerAssistant banner ads by size">
{CARDS}
  </section>

  <div class="adv-panel">
    <h2>Prefer a simple text link?</h2>
    <p>Paste this anywhere a banner won&rsquo;t fit &mdash; sidebars, resource lists or forum signatures:</p>
    <div class="adv-textlink">
      <textarea id="code-textlink" readonly rows="2">{html.escape(TEXT_LINK)}</textarea>
    </div>
    <button type="button" class="copy-btn" data-target="code-textlink">Copy code</button>
  </div>

  <div class="adv-panel">
    <h2>Usage guidelines</h2>
    <ul>
      <li>The link must point to <strong>wagerassistant.com</strong> (keep the <code>href</code> as provided).</li>
      <li>Please don&rsquo;t alter, recolour, crop or overlay the banners &mdash; use them as supplied.</li>
      <li>Free to use on any site. No adult, illegal or spam placements, please.</li>
      <li>Banners are responsive: the <code>max-width:100%; height:auto</code> in our styles lets wide units shrink on mobile.</li>
    </ul>
  </div>

  <div class="adv-panel">
    <h2>Want to advertise on WagerAssistant?</h2>
    <p>Interested in sponsorship, a partnership or placing your own ad on WagerAssistant? We&rsquo;re open to relevant, responsible advertising from sportsbooks, tools and betting-adjacent brands.</p>
    <p>We don&rsquo;t currently list a public contact address. The quickest way to reach us is through the contact or social channels linked from our site; a dedicated advertising inbox is coming soon.</p>
  </div>
</div>

<footer class="site-footer">
  <p>&copy; 2026 WagerAssistant.com - All Rights Reserved. Free tools for informational purposes only. Please gamble responsibly.</p>
  <p><a href="embed-calculators.html">Embed our free calculators on your site</a> &middot; <a href="advertise-with-us.html">Advertise with Us</a> &middot; <a href="sitemap.html">Sitemap</a></p>
</footer>

<script defer src="nav.js?v={VER}"></script>
<script>
document.addEventListener('click', function(e){{
  // version toggle (GIF <-> PNG)
  var vb = e.target.closest('.ver-btn');
  if(vb){{
    var slug = vb.getAttribute('data-slug');
    var ver = vb.getAttribute('data-ver');
    var img = document.getElementById('img-'+slug);
    var code = document.getElementById('code-'+slug);
    if(img){{ img.src = img.getAttribute('data-'+ver); }}
    if(code){{ code.value = code.getAttribute('data-'+ver); }}
    var grp = vb.parentNode.querySelectorAll('.ver-btn');
    for(var i=0;i<grp.length;i++){{
      var on = grp[i]===vb;
      grp[i].classList.toggle('active', on);
      grp[i].setAttribute('aria-pressed', on ? 'true':'false');
    }}
    return;
  }}
  // copy to clipboard
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
<script src="https://bannerpromote.com/embed.js.php" async></script>
</body>
</html>
'''

out = os.path.join(ROOT, "advertise-with-us.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(HEAD)
print("Wrote", out, "(%d bytes)" % len(HEAD))
print("Meta description length:", len(DESC))
