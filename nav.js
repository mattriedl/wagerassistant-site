/* ═══════════════════════════════════════════════════════════
   Wager Assistant — Professional Navigation System
   Categorized dropdown menus with responsive mobile support
   ═══════════════════════════════════════════════════════════ */

const NAV_CATEGORIES = [
  {
    label: 'Basic Calculators',
    icon: '🧮',
    items: [
      { href: 'betting_calculator.html',   label: 'Betting Calculator',   id: 'betting' },
      { href: 'moneyline_calculator.html',  label: 'Moneyline Calculator', id: 'moneyline' },
      { href: 'spread_calculator.html',     label: 'Spread Calculator',    id: 'spread' },
      { href: 'over_under_calculator.html', label: 'Over/Under Calculator',id: 'overunder' },
      { href: 'parlay_calculator.html',     label: 'Parlay Calculator',    id: 'parlay' },
      { href: 'odds_converter.html',        label: 'Odds Converter',       id: 'odds' }
    ]
  },
  {
    label: 'Advanced Strategy',
    icon: '🎯',
    items: [
      { href: 'arbitrage_calculator.html',        label: 'Arbitrage Calculator',       id: 'arbitrage' },
      { href: 'hedging_calculator.html',           label: 'Hedging Calculator',         id: 'hedging' },
      { href: 'dutching_calculator.html',          label: 'Dutching Calculator',        id: 'dutching' },
      { href: 'kelly_criterion_calculator.html',   label: 'Kelly Criterion',            id: 'kelly' },
      { href: 'expected_value_calculator.html',    label: 'Expected Value (EV)',        id: 'ev' },
      { href: 'no_vig_calculator.html',            label: 'No-Vig / True Odds',        id: 'novig' },
      { href: 'margin_calculator.html',            label: 'Margin Calculator',          id: 'margin' }
    ]
  },
  {
    label: 'System Bets',
    icon: '🔗',
    items: [
      { href: 'accumulator_calculator.html', label: 'Accumulator',  id: 'accumulator' },
      { href: 'round_robin_calculator.html', label: 'Round Robin',  id: 'roundrobin' },
      { href: 'yankee_calculator.html',      label: 'Yankee',       id: 'yankee' },
      { href: 'trixie_calculator.html',      label: 'Trixie',       id: 'trixie' },
      { href: 'patent_calculator.html',      label: 'Patent',       id: 'patent' },
      { href: 'lucky_15_calculator.html',    label: 'Lucky 15',     id: 'lucky15' },
      { href: 'lucky_31_calculator.html',    label: 'Lucky 31',     id: 'lucky31' },
      { href: 'lucky_63_calculator.html',    label: 'Lucky 63',     id: 'lucky63' },
      { href: 'goliath_calculator.html',     label: 'Goliath',      id: 'goliath' }
    ]
  },
  {
    label: 'Specialty Tools',
    icon: '⚡',
    items: [
      { href: 'asian_handicap_calculator.html',     label: 'Asian Handicap',      id: 'asian' },
      { href: 'teaser_calculator.html',             label: 'Teaser Calculator',   id: 'teaser' },
      { href: 'each_way_calculator.html',           label: 'Each-Way',            id: 'eachway' },
      { href: 'matched_betting_calculator.html',    label: 'Matched Betting',     id: 'matched' },
      { href: 'bonus_bet_converter.html',           label: 'Bonus Bet Converter', id: 'bonusbet' },
      { href: 'poisson_calculator.html',            label: 'Poisson Distribution',id: 'poisson' },
      { href: 'half_point_calculator.html',         label: 'Half-Point',          id: 'halfpoint' }
    ]
  },
  {
    label: 'Tracking & Analysis',
    icon: '📊',
    items: [
      { href: 'roi_calculator.html',                    label: 'ROI Calculator',          id: 'roi' },
      { href: 'progression_bet_calculator.html',        label: 'Bet Progression',         id: 'progression' },
      { href: 'implied_probability_calculator.html',    label: 'Implied Probability',     id: 'impliedprob' }
    ]
  }
];

/* Flat lookup of all IDs for backward compatibility */
const NAV_ITEMS = [{ href: 'index.html', label: 'Home', id: 'home' }];
NAV_CATEGORIES.forEach(cat => cat.items.forEach(item => NAV_ITEMS.push(item)));

/* ─── Build Navigation ─── */
function buildNav(activeId) {
  /* Find which category the active page belongs to */
  let activeCatIndex = -1;
  NAV_CATEGORIES.forEach((cat, i) => {
    cat.items.forEach(item => {
      if (item.id === activeId) activeCatIndex = i;
    });
  });

  /* Desktop dropdown categories */
  const desktopCats = NAV_CATEGORIES.map((cat, i) => {
    const hasActive = cat.items.some(item => item.id === activeId);
    const links = cat.items.map(item =>
      `<a href="${item.href}" class="dropdown-item${item.id === activeId ? ' active' : ''}">${item.label}</a>`
    ).join('');
    return `
      <div class="nav-dropdown${hasActive ? ' has-active' : ''}">
        <button class="nav-dropdown-btn" aria-expanded="false" aria-haspopup="true">
          <span class="dropdown-cat-icon">${cat.icon}</span>
          <span>${cat.label}</span>
          <svg class="dropdown-chevron" width="10" height="6" viewBox="0 0 10 6" fill="none">
            <path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div class="dropdown-menu">${links}</div>
      </div>`;
  }).join('');

  /* Mobile accordion categories */
  const mobileCats = NAV_CATEGORIES.map((cat, i) => {
    const hasActive = cat.items.some(item => item.id === activeId);
    const links = cat.items.map(item =>
      `<a href="${item.href}" class="mobile-dropdown-item${item.id === activeId ? ' active' : ''}">${item.label}</a>`
    ).join('');
    return `
      <div class="mobile-category${hasActive ? ' is-open' : ''}">
        <button class="mobile-category-btn" onclick="toggleMobileCategory(this)" aria-expanded="${hasActive}">
          <span><span class="dropdown-cat-icon">${cat.icon}</span> ${cat.label}</span>
          <svg class="mobile-chevron" width="12" height="7" viewBox="0 0 10 6" fill="none">
            <path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div class="mobile-category-links${hasActive ? ' is-open' : ''}">${links}</div>
      </div>`;
  }).join('');

  const navHTML = `
    <!-- ═══ SPORTS / ODDS TICKER — READY FOR INTEGRATION ═══
         Static placeholder strip. Wire up to a live scores / best-odds
         feed (API) later by replacing the .ticker-feed contents. -->
    <div class="ticker-bar" role="complementary" aria-label="Sports ticker (placeholder)">
      <div class="ticker-inner">
        <span class="ticker-tag">⚡ Live</span>
        <div class="ticker-feed">
          <span>NFL &middot; <strong>Best line feed ready for integration</strong></span>
          <span>NBA &middot; <strong>Odds ticker placeholder</strong></span>
          <span>MLB &middot; <strong>Scores feed placeholder</strong></span>
        </div>
      </div>
    </div>
    <nav class="top-nav" role="navigation" aria-label="Main navigation">
      <div class="nav-inner">
        <a href="index.html" class="nav-brand">
          <span class="brand-icon">♠</span>
          <span class="brand-text">Wager<span class="brand-highlight">Assistant</span></span>
        </a>
        <div class="nav-links">
          <a href="index.html" class="nav-home-link${activeId === 'home' ? ' active' : ''}">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            Home
          </a>
          ${desktopCats}
        </div>
        <button class="hamburger" id="hamburgerBtn" onclick="toggleMobile()" aria-label="Toggle navigation menu">
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
        </button>
      </div>
    </nav>
    <div class="mobile-menu" id="mobileMenu">
      <a href="index.html" class="mobile-home-link${activeId === 'home' ? ' active' : ''}">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        Home
      </a>
      ${mobileCats}
    </div>
    <div class="nav-backdrop" id="navBackdrop" onclick="closeMobile()"></div>
  `;
  document.body.insertAdjacentHTML('afterbegin', navHTML);

  /* Desktop: close dropdowns when clicking outside */
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.nav-dropdown')) {
      document.querySelectorAll('.nav-dropdown.is-open').forEach(d => d.classList.remove('is-open'));
    }
  });

  /* Desktop: dropdown click toggle (also works alongside hover) */
  document.querySelectorAll('.nav-dropdown-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      const parent = this.closest('.nav-dropdown');
      const wasOpen = parent.classList.contains('is-open');
      document.querySelectorAll('.nav-dropdown.is-open').forEach(d => d.classList.remove('is-open'));
      if (!wasOpen) parent.classList.add('is-open');
    });
  });
}

/* ─── Mobile Menu Toggles ─── */
function toggleMobile() {
  const menu = document.getElementById('mobileMenu');
  const btn = document.getElementById('hamburgerBtn');
  const backdrop = document.getElementById('navBackdrop');
  const isOpen = menu.classList.contains('open');
  menu.classList.toggle('open');
  btn.classList.toggle('is-open');
  backdrop.classList.toggle('visible');
  document.body.classList.toggle('nav-open');
}

function closeMobile() {
  document.getElementById('mobileMenu').classList.remove('open');
  document.getElementById('hamburgerBtn').classList.remove('is-open');
  document.getElementById('navBackdrop').classList.remove('visible');
  document.body.classList.remove('nav-open');
}

function toggleMobileCategory(btn) {
  const cat = btn.closest('.mobile-category');
  const links = cat.querySelector('.mobile-category-links');
  const isOpen = cat.classList.contains('is-open');
  cat.classList.toggle('is-open');
  links.classList.toggle('is-open');
  btn.setAttribute('aria-expanded', !isOpen);
}

/* ═══════════════════════════════════════════════════
   Shared odds conversion utilities (unchanged)
   ═══════════════════════════════════════════════════ */

function americanToDecimal(american) {
  if (american >= 100) return (american / 100) + 1;
  if (american <= -100) return (100 / Math.abs(american)) + 1;
  return null;
}

function decimalToAmerican(decimal) {
  if (decimal <= 1) return null;
  if (decimal >= 2) return '+' + Math.round((decimal - 1) * 100);
  return '-' + Math.round(100 / (decimal - 1));
}

function fractionalToDecimal(frac) {
  const parts = frac.split('/');
  if (parts.length !== 2) return null;
  const num = parseFloat(parts[0]);
  const den = parseFloat(parts[1]);
  if (isNaN(num) || isNaN(den) || den === 0) return null;
  return (num / den) + 1;
}

function decimalToFractional(decimal) {
  if (decimal <= 1) return null;
  const profit = decimal - 1;
  for (let den = 1; den <= 100; den++) {
    const num = profit * den;
    if (Math.abs(num - Math.round(num)) < 0.01) {
      return Math.round(num) + '/' + den;
    }
  }
  return profit.toFixed(2) + '/1';
}

function parseOddsToDecimal(value, format) {
  if (value === '' || value === null || value === undefined) return null;
  if (format === 'american') {
    const n = parseFloat(value);
    if (isNaN(n)) return null;
    return americanToDecimal(n);
  } else if (format === 'decimal') {
    const n = parseFloat(value);
    if (isNaN(n) || n <= 1) return null;
    return n;
  } else if (format === 'fractional') {
    return fractionalToDecimal(value.toString());
  }
  return null;
}

function decimalToImpliedProb(decimal) {
  if (!decimal || decimal <= 0) return null;
  return (1 / decimal) * 100;
}

function fmt$(n) {
  if (n === null || isNaN(n)) return '—';
  return '$' + Math.abs(n).toFixed(2);
}

function fmtSign$(n) {
  if (n === null || isNaN(n)) return '—';
  const sign = n >= 0 ? '+' : '-';
  return sign + '$' + Math.abs(n).toFixed(2);
}

function fmtPct(n) {
  if (n === null || isNaN(n)) return '—';
  return n.toFixed(2) + '%';
}



// ---- FAQ accordion toggle (SEO content) ----
function toggleFaq(btn) {
  var item = btn.closest('.faq-item');
  if (!item) return;
  var isOpen = item.classList.contains('open');
  // close siblings within the same list for a clean accordion feel
  var list = item.closest('.faq-list');
  if (list) {
    list.querySelectorAll('.faq-item.open').forEach(function (el) {
      if (el !== item) {
        el.classList.remove('open');
        var b = el.querySelector('.faq-q');
        if (b) b.setAttribute('aria-expanded', 'false');
      }
    });
  }
  item.classList.toggle('open');
  btn.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
}
