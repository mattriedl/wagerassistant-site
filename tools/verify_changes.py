#!/usr/bin/env python3
"""Headless verification of footer-link fix, nav subtitles and GA tag."""
from playwright.sync_api import sync_playwright
import re

BASE = "http://localhost:4100"

def lin(c):
    c = c / 255.0
    return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
def L(r,g,b):
    return 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b)
def ratio(fg, bg):
    l1, l2 = L(*fg), L(*bg)
    hi, lo = max(l1,l2), min(l1,l2)
    return (hi+0.05)/(lo+0.05)
def parse_rgb(s):
    m = re.findall(r'[\d.]+', s)
    return tuple(int(float(x)) for x in m[:3])

results = {}
with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---- 1. Console-error scan on key pages ----
    pages = ["index.html", "betting_calculator.html", "parlay_calculator.html", "embed-calculators.html"]
    console_report = {}
    for page_name in pages:
        ctx = browser.new_context(viewport={"width":1440,"height":900})
        pg = ctx.new_page()
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: "+str(e)))
        pg.goto(f"{BASE}/{page_name}", wait_until="networkidle")
        console_report[page_name] = list(errs)
        ctx.close()
    results["console_errors"] = console_report

    # ---- 2. Footer link contrast (rendered) on index.html ----
    ctx = browser.new_context(viewport={"width":1440,"height":900})
    pg = ctx.new_page()
    pg.goto(f"{BASE}/index.html", wait_until="networkidle")
    link = pg.query_selector(".site-footer a")
    color = pg.evaluate("el => getComputedStyle(el).color", link)
    # footer background = nearest non-transparent ancestor bg (body)
    bg = pg.evaluate("""() => {
        let el = document.querySelector('.site-footer');
        while (el) { const c = getComputedStyle(el).backgroundColor;
            if (c && c!=='rgba(0, 0, 0, 0)' && c!=='transparent') return c;
            el = el.parentElement; }
        return getComputedStyle(document.body).backgroundColor; }""")
    fg_rgb, bg_rgb = parse_rgb(color), parse_rgb(bg)
    results["footer_link"] = {"color":color, "bg":bg, "ratio":round(ratio(fg_rgb,bg_rgb),2)}
    pg.evaluate("document.querySelector('.site-footer').scrollIntoView({block:'center'})")
    pg.wait_for_timeout(300)
    pg.screenshot(path="/home/ubuntu/footer_link_fix.png",
                  clip=pg.query_selector(".site-footer").bounding_box())

    # ---- 3. Home grid subtitles screenshot ----
    pg.evaluate("document.querySelector('.calc-grid').scrollIntoView()")
    pg.screenshot(path="/home/ubuntu/home_grid_subtitles.png")

    # ---- 4. Desktop menu subtitles (open 'Basic' dropdown via hover) ----
    btns = pg.query_selector_all(".wa-dd-btn")
    pg.hover(".wa-dd:first-of-type .wa-dd-btn")
    pg.wait_for_timeout(400)
    sub_desktop = pg.query_selector(".wa-dd-menu .wa-dd-sub")
    sub_txt = sub_desktop.inner_text() if sub_desktop else None
    sub_visible = sub_desktop.is_visible() if sub_desktop else False
    results["desktop_subtitle_sample"] = {"text":sub_txt, "visible":sub_visible,
                                          "count":len(pg.query_selector_all('.wa-dd-sub'))}
    pg.screenshot(path="/home/ubuntu/menu_subtitles_desktop.png")
    ctx.close()

    # ---- 5. Mobile menu subtitles (390px, open hamburger) ----
    ctx = browser.new_context(viewport={"width":390,"height":800})
    pg = ctx.new_page()
    pg.goto(f"{BASE}/index.html", wait_until="networkidle")
    pg.evaluate("document.querySelector('#wa-nav-toggle').checked = true")
    pg.wait_for_timeout(400)
    msub = pg.query_selector(".wa-dd-menu .wa-dd-sub")
    results["mobile_subtitle_sample"] = {"text": msub.inner_text() if msub else None,
                                         "visible": msub.is_visible() if msub else False}
    pg.screenshot(path="/home/ubuntu/menu_subtitles_mobile.png", full_page=True)
    ctx.close()

    # ---- 6. GA presence ----
    ctx = browser.new_context()
    pg = ctx.new_page()
    pg.goto(f"{BASE}/index.html", wait_until="networkidle")
    results["ga_on_index"] = pg.evaluate("() => typeof window.gtag === 'function' && Array.isArray(window.dataLayer)")
    pg.goto(f"{BASE}/embed/betting_calculator.html", wait_until="networkidle")
    results["ga_on_embed"] = pg.evaluate("() => typeof window.gtag === 'function'")
    ctx.close()
    browser.close()

import json
print(json.dumps(results, indent=2))
