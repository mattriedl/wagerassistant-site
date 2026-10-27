#!/usr/bin/env python3
"""Inject descriptive subtitles into the static nav dropdown menus across all
pages. Scoped strictly to <div class="wa-dd-menu">...</div> blocks so the
homepage grid, sitemap and other links are never touched. Idempotent."""
import json, re, sys, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBS = json.load(open(os.path.join(ROOT, 'tools', '_nav_subtitles.json')))

MENU_BLOCK = re.compile(r'(<div class="wa-dd-menu">)(.*?)(</div>)', re.DOTALL)
# <a href="[/]betting_calculator.html" class="...">Label</a>  (label = no tags)
LINK = re.compile(r'(<a href="(/?)([a-z0-9_]+\.html)"([^>]*)>)([^<]+)(</a>)')

def transform_block(m):
    head, body, tail = m.group(1), m.group(2), m.group(3)
    def repl(lm):
        full_open, slash, base, attrs, label, close = lm.groups()
        if base not in SUBS:
            return lm.group(0)               # not a known calculator → leave
        if 'wa-dd-sub' in label:
            return lm.group(0)               # already processed
        sub = SUBS[base]
        inner = f'<span class="wa-dd-t">{label.strip()}</span><span class="wa-dd-sub">{sub}</span>'
        return f'{full_open}{inner}{close}'
    return head + LINK.sub(repl, body) + tail

def process(path):
    src = open(path, encoding='utf-8').read()
    new = MENU_BLOCK.sub(transform_block, src)
    if new != src:
        open(path, 'w', encoding='utf-8').write(new)
        return True
    return False

def main():
    targets = sorted(glob.glob(os.path.join(ROOT, '*.html')) +
                     glob.glob(os.path.join(ROOT, 'blog', '*.html')))
    changed = 0
    for p in targets:
        if process(p):
            changed += 1
            print('  updated', os.path.relpath(p, ROOT))
    print(f'Done. {changed}/{len(targets)} files changed.')

if __name__ == '__main__':
    main()
