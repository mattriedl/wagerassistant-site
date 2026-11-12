#!/usr/bin/env python3
"""Point a domain at its Cloudflare Worker, or back at the web server (rollback).

Run from GitHub Actions (workflow "Cloudflare domain"). Needs secrets CLOUDFLARE_API_TOKEN
and CLOUDFLARE_ACCOUNT_ID. Environment: DOMAIN, WORKER, ACTION (status | switch | rollback),
ORIGIN_IP (rollback only: the web server's IP address).

switch:   removes the domain's DNS record that points at the web server, attaches the
          domain to the Worker (Cloudflare creates the DNS record and certificate), and adds
          a 301 redirect rule www.DOMAIN -> https://DOMAIN. If attaching fails, the old DNS
          record is put back straight away.
rollback: detaches the domain from the Worker, recreates a proxied A record to ORIGIN_IP
          and removes the www redirect rule this script added.
"""
import json, os, sys, time, urllib.request, urllib.error

TOKEN, ACCOUNT = os.environ["CLOUDFLARE_API_TOKEN"], os.environ["CLOUDFLARE_ACCOUNT_ID"]
DOMAIN, WORKER, ACTION = os.environ["DOMAIN"], os.environ["WORKER"], os.environ.get("ACTION", "status")
RULE_REF = f"www-to-apex-{DOMAIN}"
API = "https://api.cloudflare.com/client/v4"

def api(method, path, body=None, ok404=False):
    req = urllib.request.Request(API + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        data = e.read().decode(errors="replace")
        if ok404 and e.code == 404:
            return None
        sys.exit(f"::error::{method} {path.split('?')[0]} -> HTTP {e.code}: {data[:600]}")

def mask(v):
    print(f"::add-mask::{v}")
    return v

zone = (api("GET", f"/zones?name={DOMAIN}")["result"] or [None])[0]
if not zone:
    sys.exit(f"::error::Zone {DOMAIN} not found (check the token's zone access).")
ZONE = zone["id"]

def records(name):
    return [r for r in api("GET", f"/zones/{ZONE}/dns_records?name={name}&per_page=100")["result"]
            if r["type"] in ("A", "AAAA", "CNAME")]

def worker_domains():
    return [d for d in api("GET", f"/accounts/{ACCOUNT}/workers/domains?zone_id={ZONE}")["result"]
            if d["hostname"] in (DOMAIN, f"www.{DOMAIN}")]

def redirect_ruleset():
    rs = api("GET", f"/zones/{ZONE}/rulesets/phases/http_request_dynamic_redirect/entrypoint", ok404=True)
    return rs["result"] if rs else None

def show():
    for name in (DOMAIN, f"www.{DOMAIN}"):
        for r in records(name):
            target = "Worker" if r.get("meta", {}).get("read_only") or r["content"] in ("100::",) else mask(r["content"])
            print(f"DNS  {r['name']:<28} {r['type']:<5} proxied={r['proxied']}  -> {target}")
    for d in worker_domains():
        print(f"Worker domain  {d['hostname']} -> {d['service']}")
    rs = redirect_ruleset()
    for rule in (rs or {}).get("rules", []):
        print(f"Redirect rule  {rule.get('ref') or rule.get('description')}: {rule.get('expression')}")

def set_www_redirect(enable):
    rs = redirect_ruleset()
    rules = [r for r in (rs or {}).get("rules", []) if r.get("ref") != RULE_REF]
    keep = [{k: v for k, v in r.items() if k in ("ref", "description", "expression", "action", "action_parameters", "enabled")} for r in rules]
    if enable:
        keep.append({"ref": RULE_REF, "description": f"www.{DOMAIN} -> {DOMAIN}", "enabled": True,
                     "expression": f'(http.host eq "www.{DOMAIN}")', "action": "redirect",
                     "action_parameters": {"from_value": {"status_code": 301, "preserve_query_string": True,
                         "target_url": {"expression": f'concat("https://{DOMAIN}", http.request.uri.path)'}}}})
    api("PUT", f"/zones/{ZONE}/rulesets/phases/http_request_dynamic_redirect/entrypoint", {"rules": keep})
    print(("Added" if enable else "Removed") + f" redirect rule www.{DOMAIN} -> https://{DOMAIN}")

print(f"== {DOMAIN}: before"); show()

if ACTION == "switch":
    if any(d["hostname"] == DOMAIN for d in worker_domains()):
        print(f"{DOMAIN} is already attached to a Worker.")
    else:
        old = records(DOMAIN)
        for r in old:
            mask(r["content"])
            api("DELETE", f"/zones/{ZONE}/dns_records/{r['id']}")
            print(f"Removed DNS {r['type']} record for {DOMAIN} (pointed at the web server)")
        res = None
        try:
            res = api("PUT", f"/accounts/{ACCOUNT}/workers/domains",
                      {"environment": "production", "hostname": DOMAIN, "service": WORKER, "zone_id": ZONE})
        except SystemExit as e:
            print(str(e))
        if not res or not res.get("success"):
            for r in old:
                api("POST", f"/zones/{ZONE}/dns_records", {k: r[k] for k in ("type", "name", "content", "proxied", "ttl")})
            sys.exit("::error::Attaching the Worker failed; the old DNS record was restored. Nothing changed.")
        print(f"Attached {DOMAIN} to Worker '{WORKER}'")
    set_www_redirect(True)
elif ACTION == "rollback":
    ip = mask(os.environ.get("ORIGIN_IP", "").strip())
    if not ip:
        sys.exit("::error::Enter the web server's IP address (origin_ip) to roll back.")
    for d in worker_domains():
        if d["hostname"] == DOMAIN:
            api("DELETE", f"/accounts/{ACCOUNT}/workers/domains/{d['id']}")
            print(f"Detached {DOMAIN} from Worker '{d['service']}'")
    time.sleep(3)
    if not records(DOMAIN):
        api("POST", f"/zones/{ZONE}/dns_records", {"type": "A", "name": DOMAIN, "content": ip, "proxied": True, "ttl": 1})
        print(f"Recreated proxied A record for {DOMAIN} -> web server")
    set_www_redirect(False)

if ACTION != "status":
    time.sleep(2)
    print(f"== {DOMAIN}: after"); show()
