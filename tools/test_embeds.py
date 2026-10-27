#!/usr/bin/env python3
"""Headless Playwright test for all embed widgets + the gallery page.
Checks: no console errors / page errors, and correct outputs for a known input."""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8099"

# (page, setup_fn_js_steps as list of (selector, value, kind), [(selector, expected_substring)])
def t_input(sel, val):   return ("input", sel, val)
def t_range(sel, val):   return ("range", sel, val)
def t_select(sel, val):  return ("select", sel, val)
def t_click(sel):        return ("click", sel, None)

TESTS = [
    {
        "url": f"{BASE}/embed/betting_calculator.html",
        "steps": [t_input("#stake", "100"), t_input("#odds", "-110")],
        "expect": [("#res-decimal", "1.9091"), ("#res-payout", "$190.91"),
                   ("#res-profit", "+$90.91"), ("#res-prob", "52.38%")],
    },
    {
        "url": f"{BASE}/embed/parlay_calculator.html",
        # inits with 2 legs; fill stake + both legs
        "steps": [t_input("#stake", "100"),
                  ("legodds", "0", "-110"), ("legodds", "1", "+150")],
        "expect": [("#res-odds", "4.7727"), ("#res-payout", "$477.27"),
                   ("#res-profit", "+$377.27")],
    },
    {
        "url": f"{BASE}/embed/odds_converter.html",
        "steps": [t_input("#american", "-110")],
        # these outputs are <input> fields -> read .value (marked with val: prefix)
        "expect": [("val:#decimal", "1.9091"), ("val:#probability", "52.38"), ("val:#fractional", "10/11")],
    },
    {
        "url": f"{BASE}/embed/arbitrage_calculator.html",
        "steps": [t_input("#odds1", "+120"), t_input("#odds2", "+110"), t_input("#stake1", "100")],
        "expect": [("#res-roi", "%"), ("#res-profit", "$")],
    },
    {
        "url": f"{BASE}/embed/kelly_criterion_calculator.html",
        "steps": [t_input("#bankroll", "1000"), t_input("#odds", "+150"),
                  t_range("#prob", "60"), t_select("#strategy", "1")],
        "expect": [("#res-pct", "33.3"), ("#res-stake", "$333.33")],
    },
    {
        "url": f"{BASE}/embed/hedging_calculator.html",
        "steps": [t_input("#origStake", "100"), t_input("#origOdds", "+300"),
                  t_input("#hedgeOdds", "-150")],
        "expect": [("#res-hedgeStake", "$240.00"), ("#res-guaranteed", "60.00")],
    },
    {
        "url": f"{BASE}/embed/expected_value_calculator.html",
        "steps": [t_input("#stake", "100"), t_input("#odds", "+150"), t_range("#prob", "60")],
        "expect": [("#res-ev", "$50.00"), ("#res-roi", "50")],
    },
    {
        "url": f"{BASE}/embed/implied_probability_calculator.html",
        "steps": [t_select("#inputType", "american"), t_input("#inputVal", "-110")],
        "expect": [("#s-decimal", "1.9091"), ("#s-probability", "52.38")],
    },
    {
        "url": f"{BASE}/embed-calculators.html",
        "steps": [],
        "expect": [],  # just load + no console errors; iframes load embeds
    },
]

def run():
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for tc in TESTS:
            page = browser.new_page()
            errors = []
            page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type in ("error",) else None)
            page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
            page.goto(tc["url"], wait_until="networkidle")
            page.wait_for_timeout(300)
            for step in tc["steps"]:
                kind, sel, val = step
                if kind == "input":
                    page.fill(sel, "")
                    page.fill(sel, val)
                elif kind == "legodds":
                    # sel is index into .leg-odds
                    idx = int(sel)
                    page.eval_on_selector_all(
                        ".leg-odds",
                        """(els, [i, v]) => { els[i].value = v; els[i].dispatchEvent(new Event('input', {bubbles:true})); }""",
                        [idx, val],
                    )
                elif kind == "range":
                    page.eval_on_selector(
                        sel,
                        """(el, v) => { el.value = v; el.dispatchEvent(new Event('input', {bubbles:true})); }""",
                        val,
                    )
                elif kind == "select":
                    page.select_option(sel, val)
                elif kind == "click":
                    page.click(sel)
            page.wait_for_timeout(300)
            name = tc["url"].split("/")[-1]
            for sel, exp in tc["expect"]:
                try:
                    if sel.startswith("val:"):
                        got = page.input_value(sel[4:])
                    else:
                        got = page.inner_text(sel)
                except Exception as e:
                    failures.append(f"[{name}] {sel}: could not read ({e})")
                    continue
                if exp not in got:
                    failures.append(f"[{name}] {sel}: expected '{exp}' in '{got}'")
                else:
                    print(f"  OK [{name}] {sel} = '{got}' (contains '{exp}')")
            if errors:
                failures.append(f"[{name}] JS errors: {errors}")
            else:
                print(f"  OK [{name}] no console/page errors")
            page.close()
        browser.close()
    print("\n" + ("=" * 50))
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print("  ✗ " + f)
        sys.exit(1)
    print("ALL EMBED TESTS PASSED")

if __name__ == "__main__":
    run()
