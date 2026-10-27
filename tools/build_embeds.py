#!/usr/bin/env python3
"""build_embeds.py — Generate self-contained embeddable calculator widgets.

Each embed is a single, dependency-free HTML file sized for an iframe. It
carries <meta name="robots" content="noindex, follow"> and a canonical pointing
to the matching full calculator page so it never competes in search. A visible
attribution link ("Powered by WagerAssistant.com") points back to the full page.

Outputs:
  embed/<slug>.html          (8 widgets)
  embed-calculators.html     (public gallery with copy-to-clipboard snippets)

Run from repo root:  python3 tools/build_embeds.py
"""
import os, html, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBED_DIR = os.path.join(BASE, "embed")
os.makedirs(EMBED_DIR, exist_ok=True)
SITE = "https://wagerassistant.com"

# ---- shared odds utility JS (inlined, no external deps) ----
UTIL_JS = r"""
function americanToDecimal(a){if(a>=100)return a/100+1;if(a<=-100)return 100/Math.abs(a)+1;return null;}
function decimalToAmerican(d){if(d<=1)return null;if(d>=2)return '+'+Math.round((d-1)*100);return '-'+Math.round(100/(d-1));}
function fractionalToDecimal(f){var p=(f||'').split('/');if(p.length!==2)return null;var n=parseFloat(p[0]),de=parseFloat(p[1]);if(isNaN(n)||isNaN(de)||de===0)return null;return n/de+1;}
function decimalToFractional(d){if(d<=1)return null;var pr=d-1;for(var de=1;de<=100;de++){var n=pr*de;if(Math.abs(n-Math.round(n))<0.01)return Math.round(n)+'/'+de;}return pr.toFixed(2)+'/1';}
function parseOddsToDecimal(v,fmt){if(v===''||v==null)return null;if(fmt==='american'){var n=parseFloat(String(v).replace('+',''));if(isNaN(n)||(n<100&&n>-100))return null;return americanToDecimal(n);}if(fmt==='decimal'){var m=parseFloat(v);if(isNaN(m)||m<=1)return null;return m;}if(fmt==='fractional'){return fractionalToDecimal(String(v).trim());}return null;}
function decimalToImpliedProb(d){if(!d||d<=0)return null;return 1/d*100;}
function fmt$(n){if(n===null||isNaN(n))return '\u2014';return '$'+Math.abs(n).toFixed(2);}
function fmtSign$(n){if(n===null||isNaN(n))return '\u2014';return (n>=0?'+':'-')+'$'+Math.abs(n).toFixed(2);}
function fmtPct(n){if(n===null||isNaN(n))return '\u2014';return n.toFixed(2)+'%';}
"""

# ---- shared compact CSS matching site theme ----
CSS = r"""
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0d0f1a;--surface:#141728;--surface2:#1c2038;--border:#2a2f52;--accent:#4f6ef7;--accent2:#7c3aed;--green:#10b981;--red:#ef4444;--yellow:#f59e0b;--text:#e8eaf6;--muted:#8892b0}
html,body{background:var(--bg);color:var(--text);font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:460px;margin:0 auto;padding:14px}
.ttl{display:flex;align-items:center;gap:8px;margin-bottom:12px}
.ttl .ic{font-size:20px}
.ttl h1{font-size:17px;font-weight:700;letter-spacing:-.2px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px}
.tg{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap}
.tg button{flex:1;min-width:84px;font-family:inherit;font-size:12.5px;font-weight:600;color:var(--muted);background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:8px 6px;cursor:pointer;transition:all .15s}
.tg button.active{color:#fff;background:linear-gradient(135deg,var(--accent),var(--accent2));border-color:transparent}
.row{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px}
.fg{flex:1;min-width:120px}
label{display:block;font-size:12px;color:var(--muted);margin-bottom:5px;font-weight:500}
input[type=text],input[type=number],select{width:100%;font-family:inherit;font-size:15px;color:var(--text);background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:10px 11px;-webkit-appearance:none;appearance:none}
input[type=number]{-moz-appearance:textfield}
input::-webkit-outer-spin-button,input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}
input:focus,select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--glow,rgba(79,110,247,.25))}
input[readonly]{color:var(--muted);background:var(--surface2)}
.rng{width:100%;margin:6px 0}
.hr{height:1px;background:var(--border);border:0;margin:14px 0}
.sum{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.sc{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:11px}
.sl{font-size:11px;color:var(--muted);margin-bottom:4px}
.sv{font-size:18px;font-weight:700}
.sv.green{color:var(--green)}.sv.red{color:var(--red)}.sv.accent{color:#8ea2ff}
.status{text-align:center;font-weight:700;font-size:14px;margin-top:12px;display:none}
.btns{display:flex;gap:8px;margin-top:12px}
.btns button{flex:1;font-family:inherit;font-size:13px;font-weight:600;border-radius:8px;padding:10px;cursor:pointer;border:1px solid var(--border)}
.bp{color:#fff;background:linear-gradient(135deg,var(--accent),var(--accent2));border:none}
.bs{color:var(--muted);background:var(--surface2)}
.leg{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.leg .ln{font-size:12px;color:var(--muted);min-width:46px}
.leg input{flex:1}
.leg .rm{background:var(--surface2);border:1px solid var(--border);color:var(--red);border-radius:7px;width:34px;height:34px;cursor:pointer;flex-shrink:0}
.addbtn{width:100%;font-family:inherit;font-size:13px;font-weight:600;color:var(--accent);background:transparent;border:1px dashed var(--border);border-radius:8px;padding:9px;cursor:pointer;margin-bottom:4px}
.attr{text-align:center;margin-top:12px;font-size:12px;color:var(--muted)}
.attr a{color:#8ea2ff;text-decoration:none;font-weight:600}
.attr a:hover{text-decoration:underline}
.hint{font-size:11px;color:var(--muted);margin-top:4px}
"""

HEAD_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{canonical}">
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <div class="ttl"><span class="ic">{icon}</span><h1>{h1}</h1></div>
  <div class="card">
{body}
  </div>
  <div class="attr">Powered by <a href="{attr_url}" target="_blank" rel="noopener">WagerAssistant.com &ndash; Free Betting Calculators</a></div>
</div>
<script>{util}
{script}
</script>
</body>
</html>
"""

def oddsformat_toggle():
    return """    <div class="tg" role="radiogroup" aria-label="Odds format">
      <button id="btn-us" class="active" onclick="setFormat('american')">American</button>
      <button id="btn-dec" onclick="setFormat('decimal')">Decimal</button>
      <button id="btn-frac" onclick="setFormat('fractional')">Fractional</button>
    </div>"""

SETFORMAT_JS = """
function setFormat(f){oddsFormat=f;document.getElementById('btn-us').classList.toggle('active',f==='american');document.getElementById('btn-dec').classList.toggle('active',f==='decimal');document.getElementById('btn-frac').classList.toggle('active',f==='fractional');%s;calculate();}
"""

# ============================ WIDGET DEFINITIONS ============================
WIDGETS = []

# 1. Betting / payout
WIDGETS.append(dict(
  slug="betting_calculator", full="betting_calculator.html", icon="\U0001F9EE",
  name="Betting Calculator", h1="Bet Payout Calculator",
  title="Bet Payout Calculator Widget | WagerAssistant.com",
  desc="Free embeddable bet payout calculator by WagerAssistant.com.",
  body=oddsformat_toggle()+"""
    <div class="row">
      <div class="fg"><label for="stake">Stake ($)</label><input type="number" id="stake" placeholder="e.g. 100" min="0" step="any" oninput="calculate()"></div>
      <div class="fg"><label for="odds">Odds</label><input type="text" id="odds" placeholder="e.g. -110" oninput="calculate()"></div>
    </div>
    <hr class="hr">
    <div class="sum">
      <div class="sc"><div class="sl">Potential Payout</div><div class="sv green" id="res-payout">\u2014</div></div>
      <div class="sc"><div class="sl">Profit</div><div class="sv green" id="res-profit">\u2014</div></div>
      <div class="sc"><div class="sl">Implied Probability</div><div class="sv accent" id="res-prob">\u2014</div></div>
      <div class="sc"><div class="sl">Decimal Odds</div><div class="sv" id="res-decimal">\u2014</div></div>
    </div>
    <div class="btns"><button class="bp" onclick="calculate()">Calculate</button><button class="bs" onclick="resetCalc()">\u21BB Reset</button></div>""",
  script="""
var oddsFormat='american';
""" + SETFORMAT_JS % "var ph=f==='american'?'e.g. -110':f==='decimal'?'e.g. 1.91':'e.g. 10/11';document.getElementById('odds').placeholder=ph" + """
function calculate(){var s=parseFloat(document.getElementById('stake').value);var o=document.getElementById('odds').value.trim();if(isNaN(s)||s<=0||!o){clr();return;}var d=parseOddsToDecimal(o,oddsFormat);if(!d){clr();return;}var pay=s*d;document.getElementById('res-payout').textContent=fmt$(pay);document.getElementById('res-profit').textContent=fmtSign$(pay-s);document.getElementById('res-prob').textContent=fmtPct(decimalToImpliedProb(d));document.getElementById('res-decimal').textContent=d.toFixed(4);}
function clr(){['res-payout','res-profit','res-prob','res-decimal'].forEach(function(i){document.getElementById(i).textContent='\u2014';});}
function resetCalc(){document.getElementById('stake').value='';document.getElementById('odds').value='';clr();}
"""))

# 2. Parlay
WIDGETS.append(dict(
  slug="parlay_calculator", full="parlay_calculator.html", icon="\U0001F517",
  name="Parlay Calculator", h1="Parlay Calculator",
  title="Parlay Calculator Widget | WagerAssistant.com",
  desc="Free embeddable parlay calculator by WagerAssistant.com.",
  body=oddsformat_toggle()+"""
    <div class="row"><div class="fg"><label for="stake">Total Stake ($)</label><input type="number" id="stake" placeholder="e.g. 50" min="0" step="any" oninput="calculate()"></div></div>
    <div id="legs"></div>
    <button class="addbtn" onclick="addLeg()">+ Add Leg</button>
    <hr class="hr">
    <div class="sum">
      <div class="sc"><div class="sl">Total Payout</div><div class="sv green" id="res-payout">\u2014</div></div>
      <div class="sc"><div class="sl">Profit</div><div class="sv green" id="res-profit">\u2014</div></div>
      <div class="sc"><div class="sl">Combined Decimal Odds</div><div class="sv accent" id="res-odds">\u2014</div></div>
      <div class="sc"><div class="sl">Implied Probability</div><div class="sv" id="res-prob">\u2014</div></div>
    </div>
    <div class="btns"><button class="bp" onclick="calculate()">Calculate</button><button class="bs" onclick="resetCalc()">\u21BB Reset</button></div>""",
  script="""
var oddsFormat='american';var legCount=0;
""" + SETFORMAT_JS % "var ph=f==='american'?'e.g. -110':f==='decimal'?'e.g. 1.91':'e.g. 10/11';document.querySelectorAll('.leg-odds').forEach(function(e){e.placeholder=ph;})" + """
function addLeg(){legCount++;var c=document.getElementById('legs');var ph=oddsFormat==='american'?'e.g. -110':oddsFormat==='decimal'?'e.g. 1.91':'e.g. 10/11';var r=document.createElement('div');r.className='leg';r.id='leg-'+legCount;r.innerHTML='<div class="ln">Leg '+legCount+'</div><input type="text" class="leg-odds" placeholder="'+ph+'" oninput="calculate()"><button class="rm" onclick="removeLeg('+legCount+')" aria-label="Remove">\u2715</button>';c.appendChild(r);calculate();}
function removeLeg(id){var e=document.getElementById('leg-'+id);if(e)e.remove();calculate();}
function calculate(){var s=parseFloat(document.getElementById('stake').value);var inp=document.querySelectorAll('.leg-odds');if(isNaN(s)||s<=0||inp.length===0){clr();return;}var cd=1,v=0;inp.forEach(function(i){var d=parseOddsToDecimal(i.value.trim(),oddsFormat);if(d){cd*=d;v++;}});if(v===0){clr();return;}var pay=s*cd;document.getElementById('res-payout').textContent=fmt$(pay);document.getElementById('res-profit').textContent=fmtSign$(pay-s);document.getElementById('res-odds').textContent=cd.toFixed(4);document.getElementById('res-prob').textContent=fmtPct(decimalToImpliedProb(cd));}
function clr(){['res-payout','res-profit','res-odds','res-prob'].forEach(function(i){document.getElementById(i).textContent='\u2014';});}
function resetCalc(){document.getElementById('stake').value='';document.getElementById('legs').innerHTML='';legCount=0;addLeg();addLeg();clr();}
addLeg();addLeg();
"""))

# 3. Odds converter
WIDGETS.append(dict(
  slug="odds_converter", full="odds_converter.html", icon="\U0001F504",
  name="Odds Converter", h1="Odds Converter",
  title="Odds Converter Widget | WagerAssistant.com",
  desc="Free embeddable odds converter (American, decimal, fractional, probability) by WagerAssistant.com.",
  body="""
    <div class="row"><div class="fg"><label for="american">American</label><input type="text" id="american" placeholder="e.g. -110" oninput="convert('american')"></div>
      <div class="fg"><label for="decimal">Decimal</label><input type="text" id="decimal" placeholder="e.g. 1.91" oninput="convert('decimal')"></div></div>
    <div class="row"><div class="fg"><label for="fractional">Fractional</label><input type="text" id="fractional" placeholder="e.g. 10/11" oninput="convert('fractional')"></div>
      <div class="fg"><label for="probability">Implied Prob (%)</label><input type="text" id="probability" placeholder="e.g. 52.38" oninput="convert('probability')"></div></div>
    <div class="hint">Type into any field \u2014 the others update automatically.</div>
    <div class="btns"><button class="bs" onclick="resetCalc()">\u21BB Reset</button></div>""",
  script="""
var isU=false;
function convert(src){if(isU)return;isU=true;var dec=null;
  if(src==='american'){var v=document.getElementById('american').value.trim().replace('+','');var n=parseFloat(v);if(!isNaN(n)&&(n>=100||n<=-100))dec=americanToDecimal(n);}
  else if(src==='decimal'){var m=parseFloat(document.getElementById('decimal').value);if(!isNaN(m)&&m>1)dec=m;}
  else if(src==='fractional'){dec=fractionalToDecimal(document.getElementById('fractional').value.trim());}
  else if(src==='probability'){var p=parseFloat(document.getElementById('probability').value);if(!isNaN(p)&&p>0&&p<100)dec=100/p;}
  if(dec&&dec>1){if(src!=='american')document.getElementById('american').value=decimalToAmerican(dec);if(src!=='decimal')document.getElementById('decimal').value=dec.toFixed(4);if(src!=='fractional')document.getElementById('fractional').value=decimalToFractional(dec);if(src!=='probability')document.getElementById('probability').value=(100/dec).toFixed(2);}
  else{['american','decimal','fractional','probability'].forEach(function(i){if(i!==src)document.getElementById(i).value='';});}
  isU=false;}
function resetCalc(){['american','decimal','fractional','probability'].forEach(function(i){document.getElementById(i).value='';});}
"""))

# 4. Arbitrage
WIDGETS.append(dict(
  slug="arbitrage_calculator", full="arbitrage_calculator.html", icon="\U0001F3AF",
  name="Arbitrage Calculator", h1="Arbitrage Calculator",
  title="Arbitrage Calculator Widget | WagerAssistant.com",
  desc="Free embeddable two-way arbitrage calculator by WagerAssistant.com.",
  body=oddsformat_toggle()+"""
    <div class="row"><div class="fg"><label for="odds1">Odds A</label><input type="text" id="odds1" placeholder="e.g. +120" oninput="calculate()"></div>
      <div class="fg"><label for="stake1">Stake A ($)</label><input type="number" id="stake1" placeholder="e.g. 100" min="0" step="any" oninput="calculate()"></div></div>
    <div class="row"><div class="fg"><label for="odds2">Odds B</label><input type="text" id="odds2" placeholder="e.g. +110" oninput="calculate()"></div>
      <div class="fg"><label for="stake2">Stake B ($)</label><input type="text" id="stake2" placeholder="auto" readonly></div></div>
    <hr class="hr">
    <div class="sum">
      <div class="sc"><div class="sl">Total Invested</div><div class="sv" id="res-invest">\u2014</div></div>
      <div class="sc"><div class="sl">Guaranteed Profit</div><div class="sv green" id="res-profit">\u2014</div></div>
      <div class="sc"><div class="sl">ROI</div><div class="sv accent" id="res-roi">\u2014</div></div>
      <div class="sc"><div class="sl">Market Margin</div><div class="sv" id="res-margin">\u2014</div></div>
    </div>
    <div class="status" id="st"></div>
    <div class="btns"><button class="bp" onclick="calculate()">Calculate</button><button class="bs" onclick="resetCalc()">\u21BB Reset</button></div>""",
  script="""
var oddsFormat='american';
""" + SETFORMAT_JS % "0" + """
function calculate(){var o1=document.getElementById('odds1').value.trim(),o2=document.getElementById('odds2').value.trim(),s1=parseFloat(document.getElementById('stake1').value);var d1=parseOddsToDecimal(o1,oddsFormat),d2=parseOddsToDecimal(o2,oddsFormat);if(!d1||!d2||isNaN(s1)||s1<=0){clr();return;}var m=1/d1+1/d2;var p1=s1*d1;var s2=p1/d2;var p2=s2*d2;var tot=s1+s2;var gp=Math.min(p1,p2)-tot;var roi=gp/tot*100;document.getElementById('stake2').value=s2.toFixed(2);document.getElementById('res-invest').textContent=fmt$(tot);var pe=document.getElementById('res-profit');pe.textContent=fmtSign$(gp);pe.className='sv '+(gp>=0?'green':'red');document.getElementById('res-roi').textContent=roi.toFixed(2)+'%';document.getElementById('res-margin').textContent=(m*100).toFixed(2)+'%';var st=document.getElementById('st');st.style.display='block';if(m<1){st.textContent='\u2713 ARBITRAGE FOUND';st.style.color='var(--green)';}else{st.textContent='\u2717 No Arbitrage';st.style.color='var(--red)';}}
function clr(){document.getElementById('stake2').value='';['res-invest','res-profit','res-roi','res-margin'].forEach(function(i){document.getElementById(i).textContent='\u2014';});document.getElementById('st').style.display='none';}
function resetCalc(){['odds1','odds2','stake1'].forEach(function(i){document.getElementById(i).value='';});document.getElementById('stake2').value='';clr();}
"""))

# 5. Kelly
WIDGETS.append(dict(
  slug="kelly_criterion_calculator", full="kelly_criterion_calculator.html", icon="\U0001F9E0",
  name="Kelly Criterion Calculator", h1="Kelly Criterion",
  title="Kelly Criterion Calculator Widget | WagerAssistant.com",
  desc="Free embeddable Kelly Criterion stake-sizing calculator by WagerAssistant.com.",
  body=oddsformat_toggle()+"""
    <div class="row"><div class="fg"><label for="bankroll">Bankroll ($)</label><input type="number" id="bankroll" placeholder="e.g. 1000" min="0" step="any" oninput="calculate()"></div>
      <div class="fg"><label for="odds">Odds</label><input type="text" id="odds" placeholder="e.g. +150" oninput="calculate()"></div></div>
    <div class="fg"><label for="prob">Your Win Probability: <span id="pv">50%</span></label><input type="range" id="prob" class="rng" min="1" max="99" value="50" oninput="upd()"></div>
    <div class="fg"><label for="strategy">Kelly Strategy</label><select id="strategy" onchange="calculate()"><option value="1">Full Kelly</option><option value="0.5">Half Kelly</option><option value="0.25">Quarter Kelly</option></select></div>
    <hr class="hr">
    <div class="sum">
      <div class="sc"><div class="sl">Recommended Stake</div><div class="sv green" id="res-stake">\u2014</div></div>
      <div class="sc"><div class="sl">% of Bankroll</div><div class="sv accent" id="res-pct">\u2014</div></div>
      <div class="sc"><div class="sl">Your Edge (EV)</div><div class="sv" id="res-edge">\u2014</div></div>
      <div class="sc"><div class="sl">Full Kelly Fraction</div><div class="sv" id="res-fraction">\u2014</div></div>
    </div>
    <div class="status" id="adv"></div>
    <div class="btns"><button class="bp" onclick="calculate()">Calculate</button><button class="bs" onclick="resetCalc()">\u21BB Reset</button></div>""",
  script="""
var oddsFormat='american';
""" + SETFORMAT_JS % "var ph=f==='american'?'e.g. +150':f==='decimal'?'e.g. 2.50':'e.g. 3/2';document.getElementById('odds').placeholder=ph" + """
function upd(){var v=document.getElementById('prob').value;document.getElementById('pv').textContent=v+'%';calculate();}
function calculate(){var bk=parseFloat(document.getElementById('bankroll').value);var o=document.getElementById('odds').value.trim();var p=parseFloat(document.getElementById('prob').value)/100;var strat=parseFloat(document.getElementById('strategy').value);if(isNaN(bk)||bk<=0||!o){clr();return;}var d=parseOddsToDecimal(o,oddsFormat);if(!d){clr();return;}var b=d-1,q=1-p;var kf=(b*p-q)/b;var ka=kf*strat;var ev=p*b-q;var stk=Math.max(0,ka*bk);var pct=Math.max(0,ka*100);document.getElementById('res-stake').textContent=fmt$(stk);document.getElementById('res-pct').textContent=pct.toFixed(2)+'%';document.getElementById('res-edge').textContent=(ev*100).toFixed(2)+'%';document.getElementById('res-fraction').textContent=kf.toFixed(4);var a=document.getElementById('adv');a.style.display='block';if(kf<=0){a.textContent='\u26A0 No Bet \u2014 Negative EV';a.style.color='var(--red)';}else if(kf>0.25){a.textContent='\U0001F525 Strong Edge \u2014 consider fractional Kelly';a.style.color='var(--yellow)';}else{a.textContent='\u2713 Positive Edge Detected';a.style.color='var(--green)';}}
function clr(){['res-stake','res-pct','res-edge','res-fraction'].forEach(function(i){document.getElementById(i).textContent='\u2014';});document.getElementById('adv').style.display='none';}
function resetCalc(){document.getElementById('bankroll').value='';document.getElementById('odds').value='';document.getElementById('prob').value=50;upd();clr();}
"""))

# 6. Hedging
WIDGETS.append(dict(
  slug="hedging_calculator", full="hedging_calculator.html", icon="\U0001F6E1\uFE0F",
  name="Hedging Calculator", h1="Hedging Calculator",
  title="Hedging Calculator Widget | WagerAssistant.com",
  desc="Free embeddable hedge-bet calculator by WagerAssistant.com.",
  body=oddsformat_toggle()+"""
    <div class="row"><div class="fg"><label for="origStake">Original Stake ($)</label><input type="number" id="origStake" placeholder="e.g. 100" min="0" step="any" oninput="calculate()"></div>
      <div class="fg"><label for="origOdds">Original Odds</label><input type="text" id="origOdds" placeholder="e.g. +300" oninput="calculate()"></div></div>
    <div class="row"><div class="fg"><label for="hedgeOdds">Hedge Odds</label><input type="text" id="hedgeOdds" placeholder="e.g. -150" oninput="calculate()"></div></div>
    <hr class="hr">
    <div class="sum">
      <div class="sc"><div class="sl">Hedge Stake</div><div class="sv accent" id="res-hedgeStake">\u2014</div></div>
      <div class="sc"><div class="sl">Total Invested</div><div class="sv" id="res-totalInvest">\u2014</div></div>
      <div class="sc"><div class="sl">If Original Wins</div><div class="sv green" id="res-profitOrig">\u2014</div></div>
      <div class="sc"><div class="sl">If Hedge Wins</div><div class="sv green" id="res-profitHedge">\u2014</div></div>
      <div class="sc"><div class="sl">Guaranteed Profit</div><div class="sv green" id="res-guaranteed">\u2014</div></div>
      <div class="sc"><div class="sl">Margin</div><div class="sv" id="res-margin">\u2014</div></div>
    </div>
    <div class="btns"><button class="bp" onclick="calculate()">Calculate</button><button class="bs" onclick="resetCalc()">\u21BB Reset</button></div>""",
  script="""
var oddsFormat='american';
""" + SETFORMAT_JS % "var p1=f==='american'?'e.g. +300':f==='decimal'?'e.g. 4.00':'e.g. 3/1';document.getElementById('origOdds').placeholder=p1;var p2=f==='american'?'e.g. -150':f==='decimal'?'e.g. 1.67':'e.g. 2/3';document.getElementById('hedgeOdds').placeholder=p2" + """
function calculate(){var os=parseFloat(document.getElementById('origStake').value);var oo=document.getElementById('origOdds').value.trim();var ho=document.getElementById('hedgeOdds').value.trim();if(isNaN(os)||os<=0||!oo||!ho){clr();return;}var od=parseOddsToDecimal(oo,oddsFormat);var hd=parseOddsToDecimal(ho,oddsFormat);if(!od||!hd){clr();return;}var op=os*od;var hs=op/hd;var tot=os+hs;var po=op-tot;var ph=hs*hd-tot;var g=Math.min(po,ph);document.getElementById('res-hedgeStake').textContent=fmt$(hs);document.getElementById('res-totalInvest').textContent=fmt$(tot);var eo=document.getElementById('res-profitOrig');eo.textContent=fmtSign$(po);eo.className='sv '+(po>=0?'green':'red');var eh=document.getElementById('res-profitHedge');eh.textContent=fmtSign$(ph);eh.className='sv '+(ph>=0?'green':'red');var eg=document.getElementById('res-guaranteed');eg.textContent=fmtSign$(g);eg.className='sv '+(g>=0?'green':'red');document.getElementById('res-margin').textContent=(g/tot*100).toFixed(2)+'%';}
function clr(){['res-hedgeStake','res-totalInvest','res-profitOrig','res-profitHedge','res-guaranteed','res-margin'].forEach(function(i){document.getElementById(i).textContent='\u2014';});}
function resetCalc(){['origStake','origOdds','hedgeOdds'].forEach(function(i){document.getElementById(i).value='';});clr();}
"""))

# 7. Expected Value
WIDGETS.append(dict(
  slug="expected_value_calculator", full="expected_value_calculator.html", icon="\U0001F4C8",
  name="Expected Value Calculator", h1="Expected Value (EV)",
  title="Expected Value Calculator Widget | WagerAssistant.com",
  desc="Free embeddable expected value (EV) betting calculator by WagerAssistant.com.",
  body=oddsformat_toggle()+"""
    <div class="row"><div class="fg"><label for="stake">Stake ($)</label><input type="number" id="stake" placeholder="e.g. 100" min="0" step="any" oninput="calculate()"></div>
      <div class="fg"><label for="odds">Odds</label><input type="text" id="odds" placeholder="e.g. +150" oninput="calculate()"></div></div>
    <div class="fg"><label for="prob">Your Win Probability: <span id="pv">50%</span></label><input type="range" id="prob" class="rng" min="1" max="99" value="50" oninput="upd()"></div>
    <hr class="hr">
    <div class="sc" style="margin-bottom:8px"><div class="sl">Expected Value (per bet)</div><div class="sv" id="res-ev">\u2014</div></div>
    <div class="status" id="tag"></div>
    <div class="sum">
      <div class="sc"><div class="sl">ROI per bet</div><div class="sv accent" id="res-roi">\u2014</div></div>
      <div class="sc"><div class="sl">Break-even Prob</div><div class="sv" id="res-breakeven">\u2014</div></div>
      <div class="sc"><div class="sl">Profit if Win</div><div class="sv green" id="res-profit">\u2014</div></div>
      <div class="sc"><div class="sl">Implied Prob</div><div class="sv" id="res-implied">\u2014</div></div>
    </div>
    <div class="btns"><button class="bp" onclick="calculate()">Calculate</button><button class="bs" onclick="resetCalc()">\u21BB Reset</button></div>""",
  script="""
var oddsFormat='american';
""" + SETFORMAT_JS % "var ph=f==='american'?'e.g. +150':f==='decimal'?'e.g. 2.50':'e.g. 3/2';document.getElementById('odds').placeholder=ph" + """
function upd(){document.getElementById('pv').textContent=document.getElementById('prob').value+'%';calculate();}
function calculate(){var s=parseFloat(document.getElementById('stake').value);var o=document.getElementById('odds').value.trim();var p=parseFloat(document.getElementById('prob').value)/100;if(isNaN(s)||s<=0||!o){clr();return;}var d=parseOddsToDecimal(o,oddsFormat);if(!d){clr();return;}var pw=s*(d-1);var ev=p*pw-(1-p)*s;var roi=ev/s*100;var be=1/d*100;var e=document.getElementById('res-ev');e.textContent=fmtSign$(ev);e.style.color=ev>=0?'var(--green)':'var(--red)';var t=document.getElementById('tag');t.style.display='block';if(ev>0){t.textContent='\u2713 POSITIVE EV';t.style.color='var(--green)';}else if(ev===0){t.textContent='\u2014 NEUTRAL EV';t.style.color='var(--yellow)';}else{t.textContent='\u2717 NEGATIVE EV';t.style.color='var(--red)';}document.getElementById('res-roi').textContent=roi.toFixed(2)+'%';document.getElementById('res-breakeven').textContent=be.toFixed(2)+'%';document.getElementById('res-profit').textContent=fmt$(pw);document.getElementById('res-implied').textContent=be.toFixed(2)+'%';}
function clr(){document.getElementById('tag').style.display='none';document.getElementById('res-ev').textContent='\u2014';['res-roi','res-breakeven','res-profit','res-implied'].forEach(function(i){document.getElementById(i).textContent='\u2014';});}
function resetCalc(){document.getElementById('stake').value='';document.getElementById('odds').value='';document.getElementById('prob').value=50;upd();clr();}
"""))

# 8. Implied probability
WIDGETS.append(dict(
  slug="implied_probability_calculator", full="implied_probability_calculator.html", icon="\U0001F4CA",
  name="Implied Probability Calculator", h1="Implied Probability",
  title="Implied Probability Calculator Widget | WagerAssistant.com",
  desc="Free embeddable implied probability calculator by WagerAssistant.com.",
  body="""
    <div class="fg"><label for="inputType">Input Format</label><select id="inputType" onchange="go()"><option value="american">American</option><option value="decimal">Decimal</option><option value="fractional">Fractional</option><option value="probability">Probability (%)</option></select></div>
    <div class="fg" style="margin-top:10px"><label for="inputVal">Odds / Probability</label><input type="text" id="inputVal" placeholder="e.g. -110" oninput="go()"></div>
    <hr class="hr">
    <div class="sum">
      <div class="sc"><div class="sl">Implied Probability</div><div class="sv green" id="s-probability">\u2014</div></div>
      <div class="sc"><div class="sl">Decimal</div><div class="sv accent" id="s-decimal">\u2014</div></div>
      <div class="sc"><div class="sl">American</div><div class="sv" id="s-american">\u2014</div></div>
      <div class="sc"><div class="sl">Fractional</div><div class="sv" id="s-fractional">\u2014</div></div>
    </div>
    <div class="btns"><button class="bs" onclick="resetCalc()">\u21BB Reset</button></div>""",
  script="""
function go(){var t=document.getElementById('inputType').value;var raw=document.getElementById('inputVal').value.trim();if(!raw){clr();return;}var dec=null;
  if(t==='american'){var v=parseFloat(raw.replace('+',''));if(isNaN(v)||(v<100&&v>-100)){clr();return;}dec=americanToDecimal(v);}
  else if(t==='decimal'){dec=parseFloat(raw);if(isNaN(dec)||dec<=1){clr();return;}}
  else if(t==='fractional'){dec=fractionalToDecimal(raw);if(!dec){clr();return;}}
  else if(t==='probability'){var p=parseFloat(raw);if(isNaN(p)||p<=0||p>=100){clr();return;}dec=100/p;}
  if(!dec||dec<=1){clr();return;}
  document.getElementById('s-probability').textContent=decimalToImpliedProb(dec).toFixed(2)+'%';document.getElementById('s-decimal').textContent=dec.toFixed(4);document.getElementById('s-american').textContent=decimalToAmerican(dec);document.getElementById('s-fractional').textContent=decimalToFractional(dec);}
function clr(){['s-probability','s-decimal','s-american','s-fractional'].forEach(function(i){document.getElementById(i).textContent='\u2014';});}
function resetCalc(){document.getElementById('inputVal').value='';clr();}
"""))

# ============================ BUILD EMBEDS ============================
for w in WIDGETS:
    canonical = SITE + "/" + w["full"]
    out = HEAD_TMPL.format(
        title=html.escape(w["title"]), canonical=canonical, desc=html.escape(w["desc"]),
        css=CSS, icon=w["icon"], h1=html.escape(w["h1"]), body=w["body"],
        attr_url=canonical, util=UTIL_JS, script=w["script"])
    with open(os.path.join(EMBED_DIR, w["slug"]+".html"), "w", encoding="utf-8") as f:
        f.write(out)
    print("wrote embed/"+w["slug"]+".html")

# save widget registry for gallery builder
with open(os.path.join(BASE, "tools", "_widgets.json"), "w", encoding="utf-8") as f:
    json.dump([{k: w[k] for k in ("slug","full","icon","name","desc")} for w in WIDGETS], f, indent=2)
print("DONE: %d embeds" % len(WIDGETS))
