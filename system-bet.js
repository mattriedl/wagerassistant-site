/* Wager Assistant — UK system bet settler (Trixie, Patent, Yankee, Lucky 15/31/63, Goliath).
 * Win or each-way, per-selection result (won / placed / lost / non-runner), place terms,
 * Rule 4 deductions and optional Lucky bonuses. Runs entirely in the browser. */
(function () {
  'use strict';

  var BETS = {
    trixie:  { name: 'Trixie',   n: 3, minK: 2 },
    patent:  { name: 'Patent',   n: 3, minK: 1 },
    yankee:  { name: 'Yankee',   n: 4, minK: 2 },
    lucky15: { name: 'Lucky 15', n: 4, minK: 1, bonus: true },
    lucky31: { name: 'Lucky 31', n: 5, minK: 1, bonus: true },
    lucky63: { name: 'Lucky 63', n: 6, minK: 1, bonus: true },
    goliath: { name: 'Goliath',  n: 8, minK: 2 }
  };
  var KNAMES = ['', 'Singles', 'Doubles', 'Trebles', 'Fourfolds', 'Fivefolds', 'Sixfolds', 'Sevenfolds', 'Eightfold'];
  var PLACE_TERMS = [['0.25', '1/4 odds'], ['0.2', '1/5 odds'], ['1/3', '1/3 odds'], ['0.5', '1/2 odds'], ['0.1666666667', '1/6 odds']];
  var RESULTS = [['won', 'Won'], ['placed', 'Placed'], ['lost', 'Lost'], ['nr', 'Non-runner / void']];

  var root = document.getElementById('sb-app');
  if (!root) return;
  var cfg = BETS[root.getAttribute('data-bet')];
  if (!cfg) return;

  var state = { format: 'fractional', cur: '£' };

  // ---------- odds parsing ----------
  function parseOdds(v, fmt) {
    v = (v || '').trim().toLowerCase();
    if (!v) return null;
    if (fmt === 'fractional') {
      if (v === 'evs' || v === 'evens' || v === 'ev' || v === 'even') return 2;
      var m = v.match(/^(\d+(?:\.\d+)?)\s*[\/\-]\s*(\d+(?:\.\d+)?)$/);
      if (m) { var a = parseFloat(m[1]), b = parseFloat(m[2]); return b > 0 && a > 0 ? 1 + a / b : null; }
      if (/^\d+(\.\d+)?$/.test(v)) { var w = parseFloat(v); return w > 0 ? 1 + w : null; }
      return null;
    }
    var n = parseFloat(v);
    if (isNaN(n)) return null;
    if (fmt === 'decimal') return n > 1 ? n : null;
    if (n >= 100) return 1 + n / 100;
    if (n <= -100) return 1 + 100 / -n;
    return null;
  }
  function parseFrac(s) { if (s.indexOf('/') > 0) { var p = s.split('/'); return parseFloat(p[0]) / parseFloat(p[1]); } return parseFloat(s); }
  function money(x) { return (x < 0 ? '-' : '') + state.cur + Math.abs(x).toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function signed(x) { return (x > 0.0049 ? '+' : '') + money(x); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function opts(list, sel) { return list.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === sel ? ' selected' : '') + '>' + o[1] + '</option>'; }).join(''); }
  function r4opts() { var a = []; for (var p = 0; p <= 90; p += 5) a.push([String(p), p === 0 ? 'No R4' : 'R4 ' + p + 'p']); return a; }

  function combos(arr, k) {
    var out = [];
    (function rec(start, acc) {
      if (acc.length === k) { out.push(acc.slice()); return; }
      for (var i = start; i < arr.length; i++) { acc.push(arr[i]); rec(i + 1, acc); acc.pop(); }
    })(0, []);
    return out;
  }
  var totalBets = 0;
  for (var kk = cfg.minK; kk <= cfg.n; kk++) totalBets += combos(new Array(cfg.n).fill(0).map(function (_, i) { return i; }), kk).length;

  // ---------- markup ----------
  var ph = { fractional: 'e.g. 5/2', decimal: 'e.g. 3.50', american: 'e.g. +250' };
  var rows = '';
  for (var i = 0; i < cfg.n; i++) {
    rows += '<div class="sb-row" data-i="' + i + '">' +
      '<div class="sb-num">#' + (i + 1) + '</div>' +
      '<input type="text" class="sb-odds" inputmode="decimal" autocomplete="off" aria-label="Odds for selection ' + (i + 1) + '" placeholder="' + ph.fractional + '">' +
      '<select class="sb-result" aria-label="Result for selection ' + (i + 1) + '">' + opts(RESULTS, 'won') + '</select>' +
      '<select class="sb-terms sb-ew-only" aria-label="Place terms for selection ' + (i + 1) + '">' + opts(PLACE_TERMS, '0.2') + '</select>' +
      '<select class="sb-r4" aria-label="Rule 4 deduction for selection ' + (i + 1) + '">' + opts(r4opts(), '0') + '</select>' +
      '</div>';
  }
  var bonusHTML = cfg.bonus ?
    '<div class="form-row sb-bonus">' +
      '<div class="form-group"><label for="sb-one">One-winner bonus</label><select id="sb-one">' +
        opts([['1', 'None'], ['2', 'Double odds on the single'], ['3', 'Treble odds on the single'], ['4', 'Quadruple odds on the single']], '1') + '</select></div>' +
      '<div class="form-group"><label for="sb-all">All-winners bonus (%)</label><input type="number" id="sb-all" min="0" max="100" step="any" value="0" inputmode="decimal"></div>' +
    '</div>' +
    '<p class="sb-note">Bonuses vary by bookmaker. Here they apply to the win part only: the one-winner bonus multiplies the odds of the single when exactly one selection wins, and the all-winners bonus adds a percentage of the win returns when every selection wins.</p>' : '';

  root.innerHTML =
    '<div class="odds-toggle"><label>Odds Format:</label><div class="toggle-group" role="group" aria-label="Odds format">' +
      '<button type="button" data-fmt="fractional" class="active">Fractional</button>' +
      '<button type="button" data-fmt="decimal">Decimal</button>' +
      '<button type="button" data-fmt="american">American</button></div></div>' +
    '<div class="form-row">' +
      '<div class="form-group"><label for="sb-stake">Unit stake</label><div class="sb-stake-wrap">' +
        '<select id="sb-cur" aria-label="Currency"><option value="£">£</option><option value="$">$</option><option value="€">€</option></select>' +
        '<input type="number" id="sb-stake" min="0" step="any" value="1" inputmode="decimal"></div></div>' +
      '<div class="form-group"><label for="sb-type">Bet type</label><select id="sb-type"><option value="win">Win only</option><option value="ew">Each way</option></select></div>' +
      '<div class="form-group sb-ew-only"><label for="sb-terms-all">Place terms (all)</label><select id="sb-terms-all">' + opts(PLACE_TERMS, '0.2') + '</select></div>' +
    '</div>' + bonusHTML +
    '<div class="sb-head"><span>#</span><span>Odds</span><span>Result</span><span class="sb-ew-only">Place terms</span><span>Rule 4</span></div>' +
    '<div class="sb-rows">' + rows + '</div>' +
    '<div class="sb-quick"><span>Set all to:</span>' +
      '<button type="button" class="btn-secondary" data-all="won">Won</button>' +
      '<button type="button" class="btn-secondary sb-ew-only" data-all="placed">Placed</button>' +
      '<button type="button" class="btn-secondary" data-all="lost">Lost</button>' +
      '<button type="button" class="btn-secondary" data-reset="1">↻ Reset</button></div>' +
    '<p class="sb-msg" id="sb-msg" role="status" aria-live="polite"></p>' +
    '<hr class="divider">' +
    '<section class="summary" aria-label="' + esc(cfg.name) + ' result">' +
      '<div class="summary-card"><div class="s-label">Bets</div><div class="s-value accent" id="sb-bets">' + totalBets + '</div></div>' +
      '<div class="summary-card"><div class="s-label">Total stake</div><div class="s-value" id="sb-total-stake">—</div></div>' +
      '<div class="summary-card"><div class="s-label">Total return</div><div class="s-value green" id="sb-return">—</div></div>' +
      '<div class="summary-card"><div class="s-label">Profit / loss</div><div class="s-value" id="sb-profit">—</div></div>' +
    '</section>' +
    '<div id="sb-out"></div>';

  var $ = function (s) { return root.querySelector(s); };
  var $$ = function (s) { return Array.prototype.slice.call(root.querySelectorAll(s)); };

  function isEW() { return $('#sb-type').value === 'ew'; }
  function syncEW() { root.classList.toggle('sb-is-ew', isEW()); }

  // ---------- settlement ----------
  function calculate() {
    syncEW();
    state.cur = $('#sb-cur').value;
    var stake = parseFloat($('#sb-stake').value);
    var ew = isEW();
    var sels = [], missing = [];
    $$('.sb-row').forEach(function (row, i) {
      var res = row.querySelector('.sb-result').value;
      var dec = parseOdds(row.querySelector('.sb-odds').value, state.format);
      var r4 = parseInt(row.querySelector('.sb-r4').value, 10) / 100;
      var frac = parseFrac(row.querySelector('.sb-terms').value);
      row.classList.toggle('sb-invalid', res !== 'nr' && !dec && row.querySelector('.sb-odds').value.trim() !== '');
      if (res !== 'nr' && !dec) missing.push(i + 1);
      var net = dec ? (dec - 1) * (1 - r4) : 0;
      sels.push({
        i: i, res: res, dec: dec, net: net,
        win: res === 'nr' ? 1 : (res === 'won' ? 1 + net : 0),
        place: res === 'nr' ? 1 : ((res === 'won' || res === 'placed') ? 1 + net * frac : 0)
      });
    });
    var msg = $('#sb-msg');
    if (isNaN(stake) || stake <= 0) { msg.textContent = 'Enter a unit stake.'; return clear(); }
    if (missing.length) { msg.textContent = 'Enter odds for selection' + (missing.length > 1 ? 's #' : ' #') + missing.join(', #') + ' (or mark it as a non-runner).'; return clear(); }
    msg.textContent = '';

    var winners = sels.filter(function (s) { return s.res === 'won'; });
    var oneMult = cfg.bonus ? parseFloat($('#sb-one').value) || 1 : 1;
    var allPct = cfg.bonus ? Math.max(0, parseFloat($('#sb-all').value) || 0) : 0;
    var oneBonusOn = cfg.bonus && oneMult > 1 && winners.length === 1;
    var allBonusOn = cfg.bonus && allPct > 0 && winners.length === cfg.n;

    var groups = [], detail = '', totW = 0, totP = 0, oneExtra = 0;
    for (var k = cfg.minK; k <= cfg.n; k++) {
      var list = combos(sels, k), gW = 0, gP = 0, gWon = 0;
      list.forEach(function (c) {
        var w = stake, p = stake;
        c.forEach(function (s) { w *= s.win; p *= s.place; });
        if (oneBonusOn && k === 1 && c[0].res === 'won') {
          var boosted = stake * (1 + c[0].net * oneMult);
          oneExtra = boosted - w; w = boosted;
        }
        gW += w; if (ew) gP += p;
        if (w > 0 || (ew && p > 0)) gWon++;
        detail += '<tr><td>' + KNAMES[k].replace(/s$/, '') + '</td><td>' + c.map(function (s) { return '#' + (s.i + 1); }).join(' × ') + '</td>' +
          '<td class="' + (w > 0 ? 'win-cell' : 'sb-zero') + '">' + money(w) + '</td>' +
          (ew ? '<td class="' + (p > 0 ? 'win-cell' : 'sb-zero') + '">' + money(p) + '</td>' : '') + '</tr>';
      });
      totW += gW; totP += gP;
      groups.push({ name: KNAMES[k], count: list.length, won: gWon, w: gW, p: gP });
    }
    var allExtra = allBonusOn ? totW * allPct / 100 : 0;
    var totalStake = stake * totalBets * (ew ? 2 : 1);
    var totalReturn = totW + totP + allExtra;
    var profit = totalReturn - totalStake;

    $('#sb-bets').textContent = ew ? (totalBets * 2) + ' (' + totalBets + ' EW)' : totalBets;
    $('#sb-total-stake').textContent = money(totalStake);
    $('#sb-return').textContent = money(totalReturn);
    var pe = $('#sb-profit'); pe.textContent = signed(profit);
    pe.className = 's-value ' + (profit > 0.0049 ? 'green' : profit < -0.0049 ? 'red' : '');

    var h = '<div class="table-wrap"><table class="seo-table sb-table"><thead><tr><th>Bet type</th><th>Bets</th><th>Paying</th><th>Win return</th>' +
      (ew ? '<th>Place return</th>' : '') + '<th>Total</th></tr></thead><tbody>';
    groups.forEach(function (g) {
      h += '<tr><td>' + g.name + '</td><td>' + g.count + (ew ? ' × 2' : '') + '</td><td>' + g.won + '</td><td>' + money(g.w) + '</td>' +
        (ew ? '<td>' + money(g.p) + '</td>' : '') + '<td>' + money(g.w + g.p) + '</td></tr>';
    });
    if (oneExtra > 0) h += '<tr><td colspan="' + (ew ? 5 : 4) + '">One-winner bonus (' + $('#sb-one').selectedOptions[0].text.toLowerCase() + ')</td><td>+' + money(oneExtra) + '</td></tr>';
    if (allExtra > 0) h += '<tr><td colspan="' + (ew ? 5 : 4) + '">All-winners bonus (' + allPct + '% of win returns)</td><td>+' + money(allExtra) + '</td></tr>';
    h += '<tr class="sb-total"><td>Total</td><td>' + (totalBets * (ew ? 2 : 1)) + '</td><td></td><td>' + money(totW + (oneExtra ? 0 : 0)) + '</td>' +
      (ew ? '<td>' + money(totP) + '</td>' : '') + '<td>' + money(totalReturn) + '</td></tr></tbody></table></div>';
    h += '<details class="sb-details"><summary>Show all ' + totalBets + ' bets</summary><div class="table-wrap"><table class="seo-table sb-table"><thead><tr><th>Bet</th><th>Selections</th><th>Win return</th>' +
      (ew ? '<th>Place return</th>' : '') + '</tr></thead><tbody>' + detail + '</tbody></table></div></details>';
    if (!ew && sels.some(function (s) { return s.res === 'placed'; }))
      h += '<p class="sb-note">A selection marked <strong>Placed</strong> loses in a win-only bet. Switch the bet type to <strong>Each way</strong> to settle the place part.</p>';
    $('#sb-out').innerHTML = h;
  }

  function clear() {
    ['#sb-total-stake', '#sb-return', '#sb-profit'].forEach(function (s) { $(s).textContent = '—'; });
    $('#sb-profit').className = 's-value';
    $('#sb-out').innerHTML = '';
  }

  // ---------- events ----------
  root.addEventListener('input', function (e) {
    if (e.target.id === 'sb-terms-all') return;
    calculate();
  });
  root.addEventListener('change', function (e) {
    if (e.target.id === 'sb-terms-all') $$('.sb-terms').forEach(function (s) { s.value = e.target.value; });
    calculate();
  });
  root.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    if (b.getAttribute('data-fmt')) {
      state.format = b.getAttribute('data-fmt');
      $$('.toggle-group button').forEach(function (x) { x.classList.toggle('active', x === b); });
      $$('.sb-odds').forEach(function (x) { x.placeholder = ph[state.format]; });
      calculate();
    } else if (b.getAttribute('data-all')) {
      $$('.sb-result').forEach(function (s) { s.value = b.getAttribute('data-all'); });
      calculate();
    } else if (b.getAttribute('data-reset')) {
      $$('.sb-odds').forEach(function (x) { x.value = ''; });
      $$('.sb-result').forEach(function (s) { s.value = 'won'; });
      $$('.sb-r4').forEach(function (s) { s.value = '0'; });
      $$('.sb-terms').forEach(function (s) { s.value = '0.2'; });
      $('#sb-terms-all').value = '0.2';
      $('#sb-type').value = 'win'; $('#sb-stake').value = '1';
      if (cfg.bonus) { $('#sb-one').value = '1'; $('#sb-all').value = '0'; }
      calculate();
    }
  });

  // expose for tests
  window.__sbCalculate = calculate;
  calculate();
})();
