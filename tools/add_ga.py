#!/usr/bin/env python3
"""Insert the GA4 gtag.js snippet into the <head> of all root + blog pages.
Deliberately EXCLUDES /embed/*.html (third-party iframes, no tracking).
Idempotent: skips any page that already has the tag."""
import glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GA_ID = 'G-TJL7RNVKJY'
ANCHOR = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
SNIPPET = (
    '\n<!-- Google tag (gtag.js) -->\n'
    f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
    '<script>\n'
    '  window.dataLayer = window.dataLayer || [];\n'
    '  function gtag(){dataLayer.push(arguments);}\n'
    "  gtag('js', new Date());\n"
    f"  gtag('config', '{GA_ID}');\n"
    '</script>'
)

def process(path):
    src = open(path, encoding='utf-8').read()
    if GA_ID in src:
        return False
    if ANCHOR not in src:
        print('  WARN no anchor:', os.path.relpath(path, ROOT))
        return False
    open(path, 'w', encoding='utf-8').write(src.replace(ANCHOR, ANCHOR + SNIPPET, 1))
    return True

def main():
    targets = sorted(glob.glob(os.path.join(ROOT, '*.html')) +
                     glob.glob(os.path.join(ROOT, 'blog', '*.html')))
    changed = sum(process(p) for p in targets)
    print(f'Done. {changed}/{len(targets)} files changed (embeds excluded).')

if __name__ == '__main__':
    main()
