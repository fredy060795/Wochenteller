'use strict';
/* Wochenteller – Oberfläche. Alle Daten kommen vom eigenen Server (/api), nichts liegt nur im Browser. */

const app = document.getElementById('app');
let SES = null;          // Sitzung {authenticated, user, csrf, setup_required, registration}
let CAT = null;          // Katalog {ingredients, recipes, options}
let ST = null;           // Zustand {user, profile, subst, eligible, channels, ...}
let INGS = {}, RBY = {}, OPT = {}, ELIG = new Set();
let PLAN = {from: null, to: null, rows: [], by: {}, first: null, last: null};
let SHOP = null;
let route = {name: 'heute', arg: null, q: {}};
const ui = {planWeek: null, planMode: 'woche', planMonth: null, shopWeek: null, rFilter: 'fit', rCat: '', rQuery: '',
  portions: {}, open: new Set(), wizard: null, admin: null, contact: {}, authMode: 'login', sendLog: null};

/* ---------- kleine Helfer ---------- */
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const eur = n => (Math.round(n * 100) / 100).toFixed(2).replace('.', ',') + ' €';
const num = n => Math.round(n).toLocaleString('de-AT');
const DAYS = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'];
const DS = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
const MONTHS = ['Jänner', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
const SLOT_LABEL = {frueh: 'Frühstück', mittag: 'Mittagessen', abend: 'Abendessen'};
const SLOTS = ['frueh', 'mittag', 'abend'];
const pad = n => String(n).padStart(2, '0');
const iso = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const parseD = s => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };
const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const wd = d => (d.getDay() + 6) % 7;
const mondayOf = d => addDays(new Date(d.getFullYear(), d.getMonth(), d.getDate()), -wd(d));
const today = () => { const n = new Date(); return new Date(n.getFullYear(), n.getMonth(), n.getDate()); };
const todayS = () => iso(today());
function isoWeek(d) { const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())); const day = t.getUTCDay() || 7; t.setUTCDate(t.getUTCDate() + 4 - day); const y0 = new Date(Date.UTC(t.getUTCFullYear(), 0, 1)); return Math.ceil(((t - y0) / 86400000 + 1) / 7); }
const dshort = d => `${d.getDate()}.${d.getMonth() + 1}.`;
const P = () => ST.profile;
function frac(q) { const r = Math.round(q * 4) / 4 || 0.25; const w = Math.floor(r), f = r - w; const fs = {0: '', 0.25: '¼', 0.5: '½', 0.75: '¾'}[f]; return ((w ? w : '') + fs) || '0'; }
function fmtQty(q, u) {
  if (u === 'g' || u === 'ml') { if (q >= 1000) return String(Math.round(q / 100) / 10).replace('.', ',') + (u === 'g' ? ' kg' : ' l'); const v = q < 20 ? Math.round(q) : Math.round(q / 5) * 5; return v + ' ' + u; }
  if (u === 'kg' || u === 'l') return String(Math.round(q * 10) / 10).replace('.', ',') + ' ' + u;
  const lab = {Zehe: q > 1 ? 'Zehen' : 'Zehe'}[u] || u;
  return frac(q) + ' ' + lab;
}
const ingLabel = (g, q) => (g.unit === 'Stk' && q <= 1.001) ? g.one : g.name;
function qtyName(g, q) { return g.unit === 'Stk' ? `${frac(q)} ${ingLabel(g, q)}` : `${fmtQty(q, g.unit)} ${g.name}`; }
const plural = (n, a, b) => `${n} ${n === 1 ? a : b}`;
function greet() { const h = new Date().getHours(); return h < 11 ? 'Guten Morgen' : h < 17 ? 'Hallo' : 'Guten Abend'; }

const ICON = {
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></svg>',
  plan: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
  cart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.7 11.5a2 2 0 0 0 2 1.5h7.6a2 2 0 0 0 2-1.6L21 7H6"/></svg>',
  fridge: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M5 10h14M9 6v1M9 13v3"/></svg>',
  book: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/></svg>',
  play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>',
  left: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>',
  right: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>',
  x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>',
  mail: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
  wa: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21l1.7-5A8.5 8.5 0 1 1 8 19.4z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1.3-1.3-2-1-1 .8c-1-.5-1.8-1.3-2.3-2.3l.8-1-1-2z"/></svg>',
  share: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg>',
  shuffle: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5M4 20L21 3M21 16v5h-5M15 15l6 6M4 4l5 5"/></svg>',
  timer: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2M9 2h6"/></svg>',
};
const BRAND = `<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="14" fill="none" stroke="currentColor" stroke-width="2.5"/><circle cx="16" cy="16" r="8" fill="none" stroke="currentColor" stroke-width="2"/>${[0, 1, 2, 3, 4, 5, 6].map(i => { const a = i / 7 * Math.PI * 2 - Math.PI / 2; return `<circle cx="${(16 + 11 * Math.cos(a)).toFixed(2)}" cy="${(16 + 11 * Math.sin(a)).toFixed(2)}" r="1.4" fill="currentColor"/>`; }).join('')}</svg>Wochenteller`;

/* ---------- Hinweise ---------- */
function toast(msg, err = false, ms = 3800) {
  const box = document.getElementById('toasts');
  const t = document.createElement('div');
  t.className = 'toast' + (err ? ' err' : '');
  t.setAttribute('role', err ? 'alert' : 'status');
  t.textContent = msg;
  box.appendChild(t);
  setTimeout(() => t.remove(), ms);
}

/* ---------- Server ---------- */
class ApiErr extends Error { constructor(m, s, c) { super(m); this.status = s; this.code = c; } }
async function api(method, path, body) {
  const opt = {method, headers: {'Accept': 'application/json'}, credentials: 'same-origin'};
  if (body !== undefined) { opt.headers['Content-Type'] = 'application/json'; opt.body = JSON.stringify(body); }
  if (method !== 'GET' && SES && SES.csrf) opt.headers['X-CSRF-Token'] = SES.csrf;
  let r;
  try { r = await fetch('/api/' + path, opt); } catch (e) { throw new ApiErr('Keine Verbindung zum Wochenteller-Server.', 0); }
  let data = {};
  try { data = await r.json(); } catch (e) { /* leer */ }
  if (!r.ok) {
    if (r.status === 401 && data.code === 'auth') { SES = {authenticated: false, registration: SES?.registration}; renderAuth(); }
    else if (r.status === 403 && data.code === 'password_change_required') { SES.user.must_change_pw = true; renderPwChange(); }
    else if (r.status === 403 && data.code === 'csrf') { try { SES = await api('GET', 'session'); } catch (e) { /* egal */ } }
    throw new ApiErr(data.error || ('Fehler ' + r.status), r.status, data.code);
  }
  return data;
}
async function act(fn, okMsg) {
  try { const r = await fn(); if (okMsg) toast(okMsg); return r; }
  catch (e) { toast(e.message || String(e), true, 6000); throw e; }
}
const quiet = p => p.catch(() => {});

function indexCatalog() {
  INGS = CAT.ingredients; OPT = CAT.options;
  RBY = {}; CAT.recipes.forEach(r => { RBY[r.id] = r; });
}
function applyState(s) { ST = s; ELIG = new Set(s.eligible); }
async function refreshState() { applyState(await api('GET', 'state')); }

/* ---------- Rezeptlogik (spiegelt den Server) ---------- */
function effMap(r) {
  const m = {};
  for (let [id, q] of Object.entries(r.i)) {
    const orig = id; let note = null;
    const s = ST.subst[id];
    if (s) { note = INGS[id].name; id = s[0]; q = q * s[1]; }
    m[orig] = P().blocked.includes(id) ? null : {id, q, note};
  }
  return m;
}
const effIng = r => Object.values(effMap(r)).filter(Boolean);
const kcalOf = r => Math.round(effIng(r).reduce((a, e) => a + e.q * INGS[e.id].kcal, 0) / 10) * 10;
const haveIt = id => (P().fridge[id] || 0) > 0 || P().pantry.includes(id);
const isVeg = r => !Object.keys(r.i).some(id => INGS[id].tags.some(t => t === 'fleisch' || t === 'fisch' || t === 'schalentier'));
function stepHTML(s, r, f) {
  const m = effMap(r);
  return esc(s).replace(/\{([^}]+)\}/g, (all, tok) => {
    if (tok[0] === '=') {
      const mm = tok.slice(1).match(/^(\d+(?:[.,]\d+)?)\s*(\S+)$/);
      if (!mm) return '';
      return '<b>' + esc(fmtQty(parseFloat(mm[1].replace(',', '.')) * f, mm[2])) + '</b>';
    }
    const e = m[tok];
    if (!e) return `<span class="muted">(ohne ${esc(INGS[tok] ? INGS[tok].name : tok)})</span>`;
    return '<b>' + esc(qtyName(INGS[e.id], e.q * f)) + '</b>';
  });
}
const appl = r => r.need.split(' ').filter(Boolean).map(g => [...g].map(c => OPT.applianceCodes[c]).join(' oder ')).join(' + ') || 'kein Gerät nötig';
function cuisineLabel(r) { const s = OPT.styles.find(x => r.s.includes(x[0]) && ['oesterr', 'ital', 'medi', 'asia', 'mex', 'orient', 'indisch'].includes(x[0])); return s ? s[2] : ''; }
const inSeason = r => !r.season || (() => { const [a, b] = r.season.split('-').map(Number); const m = new Date().getMonth() + 1; return a <= b ? (m >= a && m <= b) : (m >= a || m <= b); })();

/* ---------- Plan-Daten ---------- */
async function ensurePlan(a, b, force = false) {
  if (!force && PLAN.from && a >= PLAN.from && b <= PLAN.to) return;
  const t = today();
  let from = [a, iso(addDays(t, -42))].sort()[0];
  let to = [b, iso(addDays(t, 200))].sort()[1];
  if ((parseD(to) - parseD(from)) / 864e5 > 395) to = iso(addDays(parseD(from), 395));
  if (b > to) { from = a; to = iso(addDays(parseD(a), 395)); }
  const res = await api('GET', `plan?from=${from}&to=${to}`);
  PLAN = {from, to, rows: res.rows, by: {}, first: res.first, last: res.last};
  res.rows.forEach(r => { (PLAN.by[r.date] = PLAN.by[r.date] || {})[r.slot] = r; });
}
const reloadPlan = () => ensurePlan(PLAN.from || todayS(), PLAN.to || todayS(), true);
const rowAt = (ds, slot) => (PLAN.by[ds] || {})[slot];
function needsFrom(fromS, toS) {
  const n = {};
  for (const row of PLAN.rows) {
    if (row.cooked || !row.cook_portions || row.date < fromS || row.date >= toS) continue;
    const r = RBY[row.recipe_id]; if (!r) continue;
    for (const e of effIng(r)) n[e.id] = (n[e.id] || 0) + e.q * row.cook_portions;
  }
  return n;
}

/* ---------- Grundgerüst ---------- */
const NAV = [['heute', 'Heute', ICON.home], ['plan', 'Plan', ICON.plan], ['einkauf', 'Einkauf', ICON.cart], ['vorrat', 'Vorrat', ICON.fridge], ['rezepte', 'Rezepte', ICON.book]];
function shell(inner, opts = {}) {
  const u = ST.user;
  const cur = route.name === 'rezept' ? 'rezepte' : route.name;
  return `<header class="top" id="top"><div class="top-in"><a class="brand" href="#/heute">${BRAND}</a><span class="spacer"></span>
  <a class="who" href="#/profil" aria-label="Profil von ${esc(u.display_name)}"><span class="av">${esc((u.display_name.trim()[0] || '?').toUpperCase())}</span><span class="nm">${esc(u.display_name)}</span></a></div></header>
  ${opts.nonav ? '' : `<nav class="nav" aria-label="Hauptnavigation"><div class="nav-in">${NAV.map(([k, l, ic]) => `<a href="#/${k}" ${cur === k ? 'aria-current="page"' : ''}>${ic}<span>${l}</span>${k === 'einkauf' && SHOP && SHOP.open ? `<span class="badge">${SHOP.open}</span>` : ''}</a>`).join('')}</div></nav>`}
  <main class="wrap ${opts.nonav ? 'nonav' : ''}" id="main">${inner}</main>`;
}
window.addEventListener('scroll', () => { const t = document.getElementById('top'); if (t) t.classList.toggle('scrolled', window.scrollY > 4); }, {passive: true});

function parseHash() {
  const h = location.hash.replace(/^#\/?/, '');
  const [path, qs] = h.split('?');
  const [name, arg] = path.split('/');
  const q = Object.fromEntries(new URLSearchParams(qs || ''));
  return {name: name || 'heute', arg: arg ? decodeURIComponent(arg) : null, q};
}
const VIEWS = {};
async function render(opts = {}) {
  if (!ST) return;
  if (!P().onboarded && route.name !== 'einstellungen' && route.name !== 'profil' && route.name !== 'verwaltung') { startWizard('onboarding'); }
  const v = VIEWS[route.name] || VIEWS.heute;
  try { if (v.load) await v.load(); }
  catch (e) { if (e.status === 401 || e.code === 'password_change_required') return; app.innerHTML = shell(`<div class="warn" role="alert">${esc(e.message)}</div>`); return; }
  paint(opts);
}
function paint(opts = {}) {
  const v = VIEWS[route.name] || VIEWS.heute;
  const y = window.scrollY;
  const focus = document.activeElement && document.activeElement.id;
  app.innerHTML = shell(v.html(), {nonav: v.nonav});
  if (opts.keepScroll) window.scrollTo(0, y); else if (opts.top !== false) window.scrollTo(0, 0);
  if (focus && opts.keepScroll) { const el = document.getElementById(focus); if (el) { el.focus(); if (el.setSelectionRange && el.value) el.setSelectionRange(el.value.length, el.value.length); } }
  if (v.after) v.after();
}
const repaint = () => paint({keepScroll: true});
window.addEventListener('hashchange', () => { route = parseHash(); render(); });

/* ---------- Anmeldung ---------- */
function renderAuth() {
  ST = null;
  const reg = SES && SES.registration;
  let mode = ui.authMode;
  if (SES && SES.setup_required) mode = 'setup';
  else if (mode === 'register' && !(reg === 'open' || reg === 'invite')) mode = 'login';
  const pwFields = `<label class="f"><span>Passwort</span><input class="in" id="a-pw" type="password" autocomplete="new-password" minlength="8" required></label>
    <label class="f"><span>Passwort wiederholen</span><input class="in" id="a-pw2" type="password" autocomplete="new-password" minlength="8" required></label>`;
  let body;
  if (mode === 'setup') {
    body = `<h1>Willkommen!</h1><p class="sub">Lege das erste Konto an. Es bekommt die Verwaltungsrechte (Benutzer, E-Mail-Server, WhatsApp).</p>
    <form data-form="setup"><label class="f"><span>Einrichtungscode</span><input class="in" id="a-code" autocomplete="off" required placeholder="steht im Server-Fenster"></label>
    <label class="f"><span>Dein Name</span><input class="in" id="a-name" autocomplete="name" maxlength="40" required></label>
    <label class="f"><span>Benutzername</span><input class="in" id="a-user" autocomplete="username" required pattern="[A-Za-z0-9ÄÖÜäöüß._\\-]{3,32}"></label>
    ${pwFields}<button class="btn primary block" type="submit">Konto anlegen</button></form>`;
  } else if (mode === 'register') {
    body = `<h1>Konto erstellen</h1><p class="sub">Dein Plan, deine Einkaufsliste und dein Vorrat sind nur für dich sichtbar.</p>
    <form data-form="register">${reg === 'invite' ? '<label class="f"><span>Einladungscode</span><input class="in" id="a-inv" autocomplete="off" required></label>' : ''}
    <label class="f"><span>Dein Name</span><input class="in" id="a-name" autocomplete="name" maxlength="40" required></label>
    <label class="f"><span>Benutzername</span><input class="in" id="a-user" autocomplete="username" required></label>
    ${pwFields}<button class="btn primary block" type="submit">Registrieren</button></form>
    <p class="small muted">Schon ein Konto? <button class="link" data-act="auth-mode" data-v="login">Anmelden</button></p>`;
  } else {
    body = `<h1>Anmelden</h1><p class="sub">Schön, dass du da bist.</p>
    <form data-form="login"><label class="f"><span>Benutzername</span><input class="in" id="a-user" autocomplete="username" required autofocus></label>
    <label class="f"><span>Passwort</span><input class="in" id="a-pw" type="password" autocomplete="current-password" required></label>
    <button class="btn primary block" type="submit">Anmelden</button></form>
    ${reg === 'open' || reg === 'invite' ? `<p class="small muted">Noch kein Konto? <button class="link" data-act="auth-mode" data-v="register">Registrieren</button></p>` : '<p class="small muted">Noch kein Konto? Die Person, die den Wochenteller betreibt, kann dir eines anlegen.</p>'}`;
  }
  app.innerHTML = `<div class="auth"><div class="auth-card"><div class="brand">${BRAND}</div><div class="card">${body}<p class="small muted" id="a-err" role="alert"></p></div></div></div>`;
}
async function submitAuth(kind) {
  const v = id => (document.getElementById(id) || {}).value || '';
  const err = document.getElementById('a-err');
  err.textContent = '';
  try {
    let res;
    if (kind === 'login') res = await api('POST', 'login', {username: v('a-user').trim(), password: v('a-pw')});
    else {
      if (v('a-pw') !== v('a-pw2')) { err.textContent = 'Die Passwörter stimmen nicht überein.'; return; }
      const body = {username: v('a-user').trim(), display_name: v('a-name').trim(), password: v('a-pw')};
      if (kind === 'setup') res = await api('POST', 'setup', Object.assign(body, {setup_code: v('a-code').trim()}));
      else res = await api('POST', 'register', Object.assign(body, {invite: v('a-inv').trim()}));
    }
    SES = Object.assign({}, SES, res, {setup_required: false});
    await afterLogin();
  } catch (e) { err.textContent = e.message; }
}
function renderPwChange() {
  ST = null;
  app.innerHTML = `<div class="auth"><div class="auth-card"><div class="brand">${BRAND}</div><div class="card">
  <h1>Neues Passwort</h1><p class="sub">Bitte vergib ein eigenes Passwort, das nur du kennst. Mindestens 8 Zeichen.</p>
  <form data-form="pwforce"><label class="f"><span>Bisheriges (vorläufiges) Passwort</span><input class="in" id="p-old" type="password" autocomplete="current-password" required></label>
  <label class="f"><span>Neues Passwort</span><input class="in" id="p-new" type="password" autocomplete="new-password" minlength="8" required></label>
  <label class="f"><span>Neues Passwort wiederholen</span><input class="in" id="p-new2" type="password" autocomplete="new-password" minlength="8" required></label>
  <button class="btn primary block" type="submit">Speichern</button></form>
  <p class="small muted" id="a-err" role="alert"></p><button class="link" data-act="logout">Abmelden</button></div></div></div>`;
}
async function afterLogin() {
  if (SES.user && SES.user.must_change_pw) { renderPwChange(); return; }
  app.innerHTML = '<p style="padding:40px;text-align:center" class="muted">Wird geladen …</p>';
  if (!CAT) { CAT = await api('GET', 'catalog'); indexCatalog(); }
  await refreshState();
  route = parseHash();
  render();
}

/* ---------- Gemeinsame Bausteine ---------- */
function tile(key, val, emoji, label, sub, multi, cls = '', src) {
  src = src || ui.wizard.d;
  const on = multi ? src[key].includes(val) : src[key] === val;
  return `<button class="tile ${cls}" aria-pressed="${on}" data-act="w-${multi ? 'toggle' : 'set'}" data-key="${key}" data-v="${esc(val)}">${emoji ? `<span class="e" aria-hidden="true">${emoji}</span>` : ''}<span class="l">${esc(label)}</span>${sub ? `<span class="s">${esc(sub)}</span>` : ''}</button>`;
}
function chip(key, val, label, cls = '') {
  return `<button class="chip ${cls}" aria-pressed="${ui.wizard.d[key].includes(val)}" data-act="w-toggle" data-key="${key}" data-v="${esc(val)}">${esc(label)}</button>`;
}
function weekNav(mon, act, extra = '') {
  const end = addDays(mon, 6);
  const isThis = iso(mon) === iso(mondayOf(today()));
  return `<div class="weeknav"><button class="ib" data-act="${act}" data-v="-1" aria-label="Vorherige Woche">${ICON.left}</button>
  <div class="t">KW ${isoWeek(mon)}${isThis ? ' · diese Woche' : ''}<small>${dshort(mon)} – ${dshort(end)}${end.getFullYear() !== today().getFullYear() ? end.getFullYear() : ''}</small></div>
  ${extra}<button class="ib" data-act="${act}" data-v="1" aria-label="Nächste Woche">${ICON.right}</button></div>`;
}
function ingsHTML(r, f) {
  return `<dl class="ings">${effIng(r).map(e => {
    const g = INGS[e.id];
    return `<dt>${esc(g.unit === 'Stk' ? frac(e.q * f) : fmtQty(e.q * f, g.unit))}</dt><dd>${esc(g.unit === 'Stk' ? ingLabel(g, e.q * f) : g.name)}${haveIt(e.id) ? '<span class="have">✓ da</span>' : ''}${e.note ? `<p class="sub">statt ${esc(e.note)}</p>` : ''}</dd>`;
  }).join('')}</dl>`;
}
function stepsHTML(r, f, withTimers = true) {
  return `<ol class="steps">${r.st.map((s, i) => `<li>${stepHTML(s, r, f)}${withTimers && r.timers[i] ? ` <button class="tbtn" data-act="timer-start" data-rid="${r.id}" data-i="${i}" data-sec="${r.timers[i]}">${ICON.timer} ${Math.round(r.timers[i] / 60)} Min</button>` : ''}</li>`).join('')}</ol>`;
}
function channelButtons(kind, extra = '') {
  const u = ST.user, ch = ST.channels;
  const btns = [];
  if (ch.whatsapp) btns.push(`<button class="btn ghost small" data-act="send" data-kind="${kind}" data-ch="whatsapp" ${extra} ${u.phone_verified ? '' : 'data-unverified="1"'}>${ICON.wa} WhatsApp</button>`);
  if (ch.email) btns.push(`<button class="btn ghost small" data-act="send" data-kind="${kind}" data-ch="email" ${extra} ${u.email_verified ? '' : 'data-unverified="1"'}>${ICON.mail} E-Mail</button>`);
  return btns.join('');
}

/* ---------- Heute ---------- */
VIEWS.heute = {
  async load() {
    const t = today();
    await ensurePlan(iso(addDays(t, -7)), iso(addDays(t, 14)));
    quiet(loadShopBadge());
  },
  html() {
    const t = today(), ts = iso(t), tm = iso(addDays(t, 1));
    const u = ST.user;
    let h = `<p class="hello">${greet()}, ${esc(u.display_name)}</p><h1>${DAYS[wd(t)]}, ${t.getDate()}. ${MONTHS[t.getMonth()]}</h1>`;
    const future = PLAN.last && PLAN.last >= ts;
    if (!future) {
      h += `<div class="card hl"><h2>Noch nichts geplant</h2><p class="sub">Erstelle einen Plan für eine Woche oder gleich für mehrere Monate. Gerichte wiederholen sich dabei nicht ständig, und die Einkaufsliste entsteht automatisch.</p><button class="btn primary" data-act="plan-dialog">Plan erstellen</button></div>`;
    }
    const todays = SLOTS.map(s => rowAt(ts, s)).filter(Boolean);
    if (todays.length) {
      h += `<h2>Heute</h2>` + todays.map(row => todayCard(row)).join('');
      if (ST.channels.whatsapp || ST.channels.email) h += `<div class="row small" style="margin:-2px 0 6px"><span class="muted">Tagesmenü schicken:</span>${channelButtons('today')}</div>`;
    } else if (future) {
      h += `<div class="empty"><span class="big">🍽️</span>Heute ist nichts geplant.<br><button class="link" data-act="go" data-v="#/plan">Zum Plan</button></div>`;
    }
    const tomorrow = SLOTS.map(s => rowAt(tm, s)).filter(Boolean);
    if (tomorrow.length) {
      h += `<h2>Morgen</h2>` + tomorrow.map(row => { const r = RBY[row.recipe_id]; return `<a class="meal" style="display:block;text-decoration:none;color:inherit" href="#/rezept/${r.id}?d=${row.date}&s=${row.slot}"><div style="display:flex;gap:12px;align-items:center;padding:10px 14px"><span class="em" aria-hidden="true">${r.e}</span><span class="mt"><span class="ml">${SLOT_LABEL[row.slot]}${row.leftover ? ', Reste' : ''}</span><span class="mn">${esc(r.n)}</span></span><span class="tm"><span>${r.t} Min</span></span></div></a>`; }).join('');
      const prep = tomorrow.filter(row => /über Nacht|am Vorabend|Vortag/i.test(RBY[row.recipe_id].st.join(' ')));
      if (prep.length) h += `<div class="tip">💡 Für morgen schon heute vorbereiten: ${prep.map(row => esc(RBY[row.recipe_id].n)).join(', ')}</div>`;
    }
    if (SHOP && SHOP.week) {
      const mon = parseD(SHOP.week);
      h += `<h2>Einkauf</h2><a class="card" href="#/einkauf" style="display:block;text-decoration:none;color:inherit"><div class="row between"><div><div class="muted small">KW ${isoWeek(mon)} · ${esc(storeName(SHOP.store))}</div><div class="stat">${SHOP.open ? plural(SHOP.open, 'Artikel', 'Artikel') + ' offen' : 'Alles erledigt'}</div></div><div style="text-align:right"><div class="muted small">ca.</div><div class="stat">${eur(SHOP.total)}</div></div></div></a>`;
    }
    const n = P().notify;
    if (!n.shopping.enabled && !n.daily.enabled && (ST.channels.whatsapp || ST.channels.email)) {
      h += `<div class="info small">📬 Tipp: Lass dir die Einkaufsliste am Einkaufstag und das Tagesmenü automatisch per ${[ST.channels.whatsapp ? 'WhatsApp' : '', ST.channels.email ? 'E-Mail' : ''].filter(Boolean).join(' oder ')} schicken. <a href="#/profil">Einrichten</a></div>`;
    }
    if (future && PLAN.last < iso(addDays(t, 10))) h += `<div class="info small">Dein Plan endet am ${dshort(parseD(PLAN.last))} <button class="link" data-act="plan-dialog" data-extend="1">Plan verlängern</button></div>`;
    return h;
  },
};
function todayCard(row) {
  const r = RBY[row.recipe_id];
  const f = row.cook_portions || row.portions;
  if (!r) return '';
  return `<div class="card today-meal-card"><div class="today-meal ${row.cooked ? 'done' : ''}"><span class="em" aria-hidden="true">${r.e}</span><div class="grow"><div class="ml">${SLOT_LABEL[row.slot]}${row.leftover ? ' · Reste vom Vortag' : ''}</div><div class="mn" style="font-size:1.12rem">${esc(r.n)}</div><div class="meta"><span>${row.leftover ? 'aufwärmen' : r.t + ' Min'}</span><span>${num(kcalOf(r))} kcal</span>${row.leftover ? '' : `<span>${plural(f, 'Portion', 'Portionen')}</span>`}</div></div></div>
  <div class="row" style="margin-top:12px">${row.leftover ? '' : `<button class="btn primary small" data-act="cook-open" data-rid="${r.id}" data-f="${f}" data-d="${row.date}" data-s="${row.slot}">${ICON.play} Kochen</button>`}<a class="btn ghost small" href="#/rezept/${r.id}?d=${row.date}&s=${row.slot}">Rezept</a><button class="btn ${row.cooked ? 'ok' : 'ghost'} small" data-act="cook-toggle" data-d="${row.date}" data-s="${row.slot}">${row.cooked ? ICON.check + ' Gekocht' : 'Als gekocht markieren'}</button></div></div>`;
}
const storeName = s => (OPT.stores.find(x => x[0] === s) || [s, s])[1];
async function loadShopBadge() {
  const t = today();
  const mon = wd(t) >= 5 && PLAN.rows.some(r => r.date >= iso(addDays(mondayOf(t), 7)) && r.date < iso(addDays(mondayOf(t), 14))) ? addDays(mondayOf(t), 7) : mondayOf(t);
  const s = await api('GET', 'shopping?week=' + iso(mon));
  setShop(s);
  if (route.name === 'heute') repaint();
}
function setShop(s) { SHOP = s; SHOP.open = s.items.filter(it => !s.checked[it.id]).length + s.custom.filter(x => !x.checked).length; }

/* ---------- Plan ---------- */
VIEWS.plan = {
  async load() {
    if (!ui.planWeek) {
      await ensurePlan(todayS(), iso(addDays(today(), 14)));
      const next = PLAN.rows.find(r => r.date >= todayS());   // auf der Woche mit der nächsten Mahlzeit öffnen
      ui.planWeek = iso(mondayOf(next ? parseD(next.date) : today()));
    }
    if (ui.planMode === 'monat') {
      const m = ui.planMonth ? parseD(ui.planMonth) : new Date(today().getFullYear(), today().getMonth(), 1);
      ui.planMonth = iso(m);
      const a = mondayOf(m), b = addDays(mondayOf(new Date(m.getFullYear(), m.getMonth() + 1, 0)), 7);
      await ensurePlan(iso(a), iso(b));
    } else {
      await ensurePlan(ui.planWeek, iso(addDays(parseD(ui.planWeek), 7)));
    }
  },
  html() {
    let h = `<div class="row between"><h1>Plan</h1><button class="btn primary small" data-act="plan-dialog">Planen …</button></div>
    <div class="seg" role="group" aria-label="Ansicht" style="margin-bottom:12px"><button data-act="plan-mode" data-v="woche" aria-pressed="${ui.planMode === 'woche'}">Woche</button><button data-act="plan-mode" data-v="monat" aria-pressed="${ui.planMode === 'monat'}">Monat</button></div>`;
    if (ui.planMode === 'monat') return h + monthHTML();
    const mon = parseD(ui.planWeek);
    h += weekNav(mon, 'plan-week');
    const ws = ui.planWeek, we = iso(addDays(mon, 7));
    const wrows = PLAN.rows.filter(r => r.date >= ws && r.date < we);
    if (!wrows.length) {
      h += `<div class="empty"><span class="big">🗓️</span>Für diese Woche ist noch nichts geplant.<br><br><button class="btn primary" data-act="plan-generate-week">Diese Woche planen</button></div>`;
      if (PLAN.first) h += `<p class="note" style="text-align:center">Dein Plan reicht vom ${dshort(parseD(PLAN.first))} bis ${dshort(parseD(PLAN.last))}.</p>`;
      return h;
    }
    const mt = OPT.mealSlots[P().meals];
    let kc = 0, nd = 0;
    for (let i = 0; i < 7; i++) {
      const d = addDays(mon, i), ds = iso(d);
      const rows = SLOTS.map(s => rowAt(ds, s)).filter(Boolean);
      const home = P().days.includes(i);
      const cls = ds === todayS() ? 'today' : ds < todayS() ? 'past' : '';
      if (!rows.length && !home) {
        h += `<section class="day ${cls}"><div class="day-head"><h2>${DAYS[i]} <span class="muted small">${dshort(d)}</span></h2></div><div class="offrow"><span>Nicht zuhause</span><button class="btn ghost small" data-act="pick" data-d="${ds}" data-s="${mt.includes('abend') ? 'abend' : mt[0]}">Gericht hinzufügen</button></div></section>`;
        continue;
      }
      let dk = 0;
      const cards = SLOTS.map(s => {
        const row = rowAt(ds, s);
        if (row) { dk += kcalOf(RBY[row.recipe_id]); return mealCard(row); }
        if (mt.includes(s) && home && ds >= todayS()) return `<button class="addslot" data-act="pick" data-d="${ds}" data-s="${s}">＋ ${SLOT_LABEL[s]} hinzufügen</button>`;
        return '';
      }).join('');
      kc += dk; nd++;
      const hi = P().kcal && dk > P().kcal * 1.05;
      h += `<section class="day ${cls}" id="day-${ds}"><div class="day-head"><h2>${DAYS[i]} <span class="muted small">${dshort(d)}</span></h2><span class="kcal ${hi ? 'hi' : ''}">${num(dk)}${P().kcal ? ` von ${num(P().kcal)}` : ''} kcal</span></div>${cards}</section>`;
    }
    h += `<div class="card"><div class="row between"><span class="muted small">Ø ${num(kc / Math.max(1, nd))} kcal pro Tag · ${plural(wrows.filter(r => r.slot !== 'frueh').length, 'Hauptmahlzeit', 'Hauptmahlzeiten')}</span></div>
    <div class="row" style="margin-top:10px">${we > todayS() ? `<button class="btn ghost small" data-act="plan-generate-week">${ICON.shuffle} Woche neu mischen</button>` : ''}<a class="btn ghost small" href="#/einkauf?week=${ws}">${ICON.cart} Einkaufsliste</a>${channelButtons('week', `data-week="${ws}"`)}</div></div>`;
    return h;
  },
  after() { if (route.q.day) { const el = document.getElementById('day-' + route.q.day); if (el) el.scrollIntoView({block: 'start'}); route.q = {}; } },
};
function mealCard(row) {
  const r = RBY[row.recipe_id];
  const key = row.date + '|' + row.slot;
  const f = row.cook_portions || row.portions;
  const past = row.date < todayS();
  if (row.leftover) {
    return `<details class="meal left ${row.cooked ? 'done' : ''}" data-key="${key}" ${ui.open.has(key) ? 'open' : ''}><summary><span class="em" aria-hidden="true">${r.e}</span><span class="mt"><span class="ml">${SLOT_LABEL[row.slot]} · Reste vom Vortag</span><span class="mn">${esc(r.n)}</span></span><span class="tm"><span>aufwärmen</span><span>${num(kcalOf(r))} kcal</span></span></summary>
    <div class="md"><p class="note">Das kochst du davor in doppelter Menge – einfach aufwärmen.</p><div class="btnrow row"><button class="btn ${row.cooked ? 'ok' : 'ghost'} small" data-act="cook-toggle" data-d="${row.date}" data-s="${row.slot}">${row.cooked ? ICON.check + ' Gegessen' : 'Als gegessen markieren'}</button><button class="btn ghost small" data-act="skip" data-d="${row.date}" data-s="${row.slot}">Auslassen</button></div></div></details>`;
  }
  return `<details class="meal ${row.cooked ? 'done' : ''}" data-key="${key}" ${ui.open.has(key) ? 'open' : ''}><summary><span class="em" aria-hidden="true">${r.e}</span><span class="mt"><span class="ml">${SLOT_LABEL[row.slot]}${row.cook_portions > row.portions ? ' · doppelte Menge' : ''}</span><span class="mn">${esc(r.n)}</span></span><span class="tm"><span>${r.t} Min</span><span>${num(kcalOf(r))} kcal</span></span></summary>
  <div class="md">${row.cook_portions > row.portions ? '<p class="note">Doppelte Menge kochen: Die Hälfte ist für die nächste Mahlzeit.</p>' : ''}
  <div class="row" style="margin:10px 0 4px">${row.cooked ? '' : `<button class="btn primary small" data-act="cook-open" data-rid="${r.id}" data-f="${f}" data-d="${row.date}" data-s="${row.slot}">${ICON.play} Kochmodus</button>`}<button class="btn ${row.cooked ? 'ok' : 'ghost'} small" data-act="cook-toggle" data-d="${row.date}" data-s="${row.slot}">${row.cooked ? ICON.check + ' Gekocht – rückgängig' : 'Als gekocht markieren'}</button></div>
  ${ingsHTML(r, f)}<p class="note">Für ${plural(f, 'Portion', 'Portionen')}, ca. ${num(kcalOf(r))} kcal pro Portion.</p>
  ${stepsHTML(r, f)}${r.tip ? `<div class="tip">💡 ${esc(r.tip)}</div>` : ''}
  ${row.cooked || past ? '' : `<div class="row"><button class="btn ghost small" data-act="swap" data-d="${row.date}" data-s="${row.slot}">${ICON.shuffle} Anderes Gericht</button><button class="btn ghost small" data-act="pick" data-d="${row.date}" data-s="${row.slot}">Selbst aussuchen</button><button class="btn ghost small" data-act="skip" data-d="${row.date}" data-s="${row.slot}">Auslassen</button></div>`}
  <div class="row" style="margin-top:6px"><a class="link" href="#/rezept/${r.id}?d=${row.date}&s=${row.slot}">Rezept groß öffnen</a></div></div></details>`;
}
function monthHTML() {
  const m = parseD(ui.planMonth);
  const first = mondayOf(m), last = new Date(m.getFullYear(), m.getMonth() + 1, 0);
  let h = `<div class="weeknav"><button class="ib" data-act="plan-month" data-v="-1" aria-label="Voriger Monat">${ICON.left}</button><div class="t">${MONTHS[m.getMonth()]} ${m.getFullYear()}</div><button class="ib" data-act="plan-month" data-v="1" aria-label="Nächster Monat">${ICON.right}</button></div>`;
  h += `<div class="month">${DS.map(d => `<div class="dh">${d}</div>`).join('')}`;
  for (let d = new Date(first); d <= last || wd(d) !== 0; d = addDays(d, 1)) {
    const ds = iso(d);
    const rows = SLOTS.map(s => rowAt(ds, s)).filter(Boolean);
    const out = d.getMonth() !== m.getMonth();
    h += `<button class="dc ${out ? 'out' : ''} ${ds === todayS() ? 'today' : ''} ${rows.length ? '' : 'empty-day'}" data-act="month-day" data-v="${ds}" aria-label="${DAYS[wd(d)]} ${dshort(d)}: ${rows.map(r => esc(RBY[r.recipe_id].n)).join(', ') || 'nichts geplant'}"><span class="n">${d.getDate()}</span><span class="es">${rows.map(r => RBY[r.recipe_id].e).join('')}</span></button>`;
  }
  h += '</div>';
  const mrows = PLAN.rows.filter(r => r.date.slice(0, 7) === ui.planMonth.slice(0, 7) && r.slot !== 'frueh' && !r.leftover);
  const distinct = new Set(mrows.map(r => r.recipe_id)).size;
  h += `<p class="note">${mrows.length ? `${plural(mrows.length, 'Hauptgericht', 'Hauptgerichte')} in diesem Monat, davon ${distinct} verschiedene.` : 'In diesem Monat ist noch nichts geplant.'} Tippe auf einen Tag, um die Woche zu öffnen.</p>`;
  return h;
}

function planDialog(extend) {
  const t = today();
  const last = PLAN.last ? parseD(PLAN.last) : null;
  const after = last && last >= t ? addDays(last, 1) : null;
  const nextMon = addDays(mondayOf(t), 7);
  const def = extend && after ? after : (after && wd(t) >= 4 ? nextMon : t);
  const starts = [['Ab heute', t], ['Ab Montag', wd(t) === 0 ? t : nextMon]];
  if (after) starts.push(['Anschließend', after]);
  const weeks = [[1, '1 Woche'], [2, '2 Wochen'], [4, '1 Monat'], [8, '2 Monate'], [13, '3 Monate'], [26, '6 Monate']];
  const curW = P().horizon || 4;
  openDialog('Plan erstellen', `<p class="sub">Gerichte wiederholen sich frühestens nach einigen Wochen – je mehr Rezepte zu deinen Einstellungen passen, desto länger. Bereits gekochte Mahlzeiten bleiben erhalten.</p>
  <h3>Ab wann?</h3><div class="chips" id="pd-starts">${starts.map(([l, d]) => `<button class="chip" data-act="pd-start" data-v="${iso(d)}" aria-pressed="${iso(d) === iso(def)}">${l} <span class="muted">${dshort(d)}</span></button>`).join('')}</div>
  <label class="f" style="margin-top:10px"><span>oder Datum wählen</span><input class="in" type="date" id="pd-date" value="${iso(def)}" min="${iso(addDays(t, -7))}"></label>
  <h3>Wie lange?</h3><div class="chips" id="pd-weeks">${weeks.map(([w, l]) => `<button class="chip" data-act="pd-weeks" data-v="${w}" aria-pressed="${w === (weeks.some(x => x[0] === curW) ? curW : 4)}">${l}</button>`).join('')}</div>
  <p class="note" id="pd-note"></p>
  <p class="small muted">Einstellungen wie Budget, Geräte oder Vorlieben änderst du unter <a href="#/einstellungen" data-act="dlg-close">Einstellungen</a>.</p>`,
  `<button class="btn ghost" data-act="dlg-close">Abbrechen</button><button class="btn primary" data-act="pd-go">Plan erstellen</button>`);
  pdNote();
}
function pdNote() {
  const s = document.getElementById('pd-date').value;
  const w = +(document.querySelector('#pd-weeks [aria-pressed="true"]') || {dataset: {v: 4}}).dataset.v;
  if (!s) return;
  const end = addDays(parseD(s), 7 * w - 1);
  const ex = PLAN.rows.filter(r => r.date >= s && r.date <= iso(end) && !r.cooked).length;
  document.getElementById('pd-note').textContent = `Zeitraum ${dshort(parseD(s))} – ${dshort(end)}${end.getFullYear() !== today().getFullYear() ? end.getFullYear() : ''}.` + (ex ? ` ${plural(ex, 'bereits geplante Mahlzeit wird', 'bereits geplante Mahlzeiten werden')} neu geplant.` : '');
}
async function generate(start, weeks, days) {
  const res = await act(() => api('POST', 'plan/generate', days ? {start, weeks, days} : {start, weeks}));
  await reloadPlan();
  await refreshState();
  SHOP = null;
  const i = res.info;
  let msg = days && days < 7 ? `${plural(days, 'Tag', 'Tage')} neu geplant.` : `${plural(weeks, 'Woche', 'Wochen')} geplant.`;
  if (i.cooldown) msg += ` Kein Gericht öfter als alle ${i.cooldown} Tage.`;
  toast(msg, false, 5000);
  if (i.few_recipes) toast(`Nur ${i.eligible} Gerichte passen zu deinen Einstellungen – deshalb wiederholen sie sich öfter.`, true, 7000);
  if (i.no_breakfast) toast('Für deine Einstellungen gibt es kein passendes Frühstück.', true, 6000);
  return res;
}

async function pickDialog(ds, slot) {
  const isBf = slot === 'frueh';
  let sugg = [];
  try { sugg = (await api('GET', `alternatives?date=${ds}&slot=${slot}`)).ids; } catch (e) { /* ohne Vorschläge */ }
  const d = parseD(ds);
  openDialog(`${SLOT_LABEL[slot]} am ${DS[wd(d)]} ${dshort(d)}`, `<input class="in" id="pick-q" type="search" placeholder="Rezept oder Zutat suchen" aria-label="Suchen" autocomplete="off">
  <div id="pick-list" class="rlist" style="margin-top:12px"></div>`, `<button class="btn ghost" data-act="dlg-close">Schließen</button>`);
  const list = document.getElementById('pick-list');
  const draw = () => {
    const q = document.getElementById('pick-q').value.trim().toLowerCase();
    let rs = CAT.recipes.filter(r => (r.type === 'f') === isBf && ELIG.has(r.id));
    if (q) rs = rs.filter(r => r.n.toLowerCase().includes(q) || Object.keys(r.i).some(id => INGS[id].name.toLowerCase().includes(q)));
    else { const s = sugg.map(id => RBY[id]).filter(Boolean); rs = s.concat(rs.filter(r => !sugg.includes(r.id)).sort((a, b) => a.n.localeCompare(b.n, 'de'))); }
    list.innerHTML = (q ? '' : sugg.length ? '<p class="note">Passende Vorschläge zuerst – lange nicht gekocht und gut fürs Budget:</p>' : '') + rs.slice(0, 80).map(r => recipeRow(r, `data-act="pick-set" data-d="${ds}" data-s="${slot}" data-rid="${r.id}"`)).join('') + (rs.length ? '' : '<div class="empty">Nichts gefunden.</div>');
  };
  document.getElementById('pick-q').addEventListener('input', draw);
  draw();
}
function recipeRow(r, attrs) {
  const fav = P().favorites.includes(r.id);
  const log = P().cooklog[r.id];
  return `<button class="meal" style="display:flex;width:100%;text-align:left;gap:12px;align-items:center;padding:10px 12px;cursor:pointer" ${attrs}><span class="em" aria-hidden="true">${r.e}</span><span class="mt"><span class="ml">${fav ? '♥ ' : ''}${r.type === 'f' ? 'Frühstück' : esc(cuisineLabel(r) || 'Hauptgericht')}${log ? ` · ${log.n}× gekocht` : ''}${r.season && inSeason(r) ? ' · Saison' : ''}</span><span class="mn">${esc(r.n)}</span></span><span class="tm"><span>${r.t} Min</span><span>${num(kcalOf(r))} kcal</span></span></button>`;
}

/* ---------- Einkauf ---------- */
VIEWS.einkauf = {
  async load() {
    if (route.q.week) { ui.shopWeek = iso(mondayOf(parseD(route.q.week))); route.q = {}; }
    if (!ui.shopWeek) {
      const t = today();
      await ensurePlan(iso(mondayOf(t)), iso(addDays(mondayOf(t), 14)));
      const nm = iso(addDays(mondayOf(t), 7));
      ui.shopWeek = wd(t) >= 5 && PLAN.rows.some(r => r.date >= nm && r.date < iso(addDays(mondayOf(t), 14))) ? nm : iso(mondayOf(t));
    }
    setShop(await api('GET', 'shopping?week=' + ui.shopWeek));
  },
  html() {
    const s = SHOP, mon = parseD(s.week);
    let h = `<h1>Einkauf</h1>` + weekNav(mon, 'shop-week');
    if (s.mode === 'past') h += `<div class="info small">Diese Woche ist vorbei. Die Liste zeigt, was dafür geplant war.</div>`;
    if (s.mode === 'future') h += `<div class="info small">Vorschau: Dein Vorrat wird zuerst für die früheren Wochen eingeplant, was übrig bleibt, wird hier abgezogen.</div>`;
    const over = s.total > s.budget, pct = Math.min(100, s.total / Math.max(1, s.budget) * 100);
    h += `<div class="card"><div class="row between"><span class="stat">${eur(s.total)}</span><span class="muted small">bei ${esc(storeName(s.store))} · Budget ${eur(s.budget)}</span></div>
    <div class="meter ${over ? 'over' : ''}"><span style="width:${pct}%"></span></div><p class="small" style="margin:0">${over ? `${eur(s.total - s.budget)} über dem Budget. Tausche ein teures Gericht oder vergleiche die Geschäfte.` : `Du bleibst ${eur(s.budget - s.total)} unter deinem Budget.`}</p></div>`;
    if (s.compare.length > 1) h += `<div class="stores" role="group" aria-label="Geschäft wählen">${s.compare.map(([k, t]) => `<button class="store" aria-pressed="${k === s.store}" data-act="shop-store" data-v="${k}"><strong>${esc(storeName(k))}</strong><small>${eur(t)}</small></button>`).join('')}</div>`;
    const done = s.items.filter(it => s.checked[it.id]).length;
    const groups = OPT.categoryOrder.map(c => [c, s.items.filter(it => INGS[it.id].cat === c).sort((a, b) => INGS[a.id].name.localeCompare(INGS[b.id].name, 'de'))]).filter(([, a]) => a.length);
    h += `<div class="receipt"><div class="rtitle">Einkaufsliste ${esc(storeName(s.store))}</div><div class="rsub" id="rsub">${done} von ${s.items.length} im Wagen</div>`;
    if (!s.items.length) h += `<p style="text-align:center;margin:18px 0">${PLAN.rows.length || s.have.length || s.fromFridge.length ? 'Alles da – für diese Woche musst du nichts einkaufen. 🎉' : 'Für diese Woche ist nichts geplant.'}</p>`;
    h += groups.map(([c, a]) => `<h3>${esc(c)}</h3>${a.map(it => {
      const g = INGS[it.id], chk = !!s.checked[it.id];
      const rest = it.rest > 0.05 * g.pack && !(g.unit === 'EL' || g.unit === 'TL') ? `, Rest ca. ${fmtQty(it.rest, g.unit)}` : '';
      return `<label class="item ${chk ? 'done' : ''}"><input type="checkbox" data-check="${it.id}" ${chk ? 'checked' : ''}><span class="rn">${esc(g.name)}<small>${it.packs}× ${esc(g.packLabel)}, du brauchst ${esc(fmtQty(it.need, g.unit))}${rest}</small></span><span class="rp">${eur(it.price)}</span></label>`;
    }).join('')}`).join('');
    h += `<h3>Sonstiges</h3>${s.custom.map(x => `<div class="item ${x.checked ? 'done' : ''}"><input type="checkbox" data-custom="${x.id}" ${x.checked ? 'checked' : ''} aria-label="${esc(x.text)} abhaken"><span class="rn">${esc(x.text)}</span><button class="del" data-act="custom-del" data-v="${x.id}" aria-label="${esc(x.text)} entfernen">✕</button></div>`).join('')}
    <form class="addrow" data-form="custom"><input id="custom-in" maxlength="120" placeholder="z. B. Klopapier, Kaffee …" aria-label="Eigenen Artikel hinzufügen"><button type="submit">＋</button></form>
    <div class="rtotal"><span>Summe</span><span>${eur(s.total)}</span></div><div class="rline"><span>Budget</span><span>${eur(s.budget)}</span></div>
    ${s.fromFridge.length ? `<div class="rhave">Schon im Vorrat: ${s.fromFridge.map(id => esc(INGS[id].name)).join(', ')}</div>` : ''}
    ${s.have.length ? `<div class="rhave">Immer zuhause: ${s.have.map(id => esc(INGS[id].name)).join(', ')}</div>` : ''}</div>`;
    h += `<button class="btn primary block" data-act="shop-finish" id="shop-finish" ${done ? '' : 'disabled'}>Eingekauft: Abgehakte Sachen in den Vorrat legen</button>
    <h2>Liste weitergeben</h2><div class="row">${channelButtons('shopping', `data-week="${s.week}"`)}<button class="btn ghost small" data-act="shop-share">${ICON.share} Teilen / Kopieren</button><button class="btn ghost small" data-act="print">Drucken</button></div>
    ${!ST.channels.whatsapp && !ST.channels.email ? '<p class="note">E-Mail- und WhatsApp-Versand richtet die Verwaltung ein.</p>' : ''}
    <p class="foot">Preise sind Schätzwerte (Hofer-Niveau, je Geschäft hochgerechnet) und können je nach Produkt, Filiale und Aktion abweichen.</p>`;
    return h;
  },
};
function shopText() {
  const s = SHOP, mon = parseD(s.week);
  const lines = [`🛒 Einkaufsliste KW ${isoWeek(mon)} (${dshort(mon)}–${dshort(addDays(mon, 6))}) · ${storeName(s.store)}`, ''];
  for (const c of OPT.categoryOrder) {
    const a = s.items.filter(it => INGS[it.id].cat === c && !s.checked[it.id]);
    if (!a.length) continue;
    lines.push(c);
    a.forEach(it => lines.push(`• ${it.packs}× ${INGS[it.id].name} (${INGS[it.id].packLabel})`));
    lines.push('');
  }
  const cu = s.custom.filter(x => !x.checked);
  if (cu.length) { lines.push('Sonstiges'); cu.forEach(x => lines.push('• ' + x.text)); lines.push(''); }
  lines.push(`Summe ca. ${eur(s.total)}`);
  return lines.join('\n');
}

/* ---------- Vorrat ---------- */
VIEWS.vorrat = {
  async load() { const t = today(); await ensurePlan(todayS(), iso(addDays(t, 14))); },
  html() {
    const fr = P().fridge;
    const ids = Object.keys(fr).filter(id => fr[id] > 0);
    const needs = needsFrom(todayS(), iso(addDays(today(), 14)));
    const opts = OPT.categoryOrder.filter(c => c !== 'Gewürze & Öle').map(c => `<optgroup label="${esc(c)}">${Object.values(INGS).filter(g => g.cat === c).sort((a, b) => a.name.localeCompare(b.name, 'de')).map(g => `<option value="${g.id}">${esc(g.name)}</option>`).join('')}</optgroup>`).join('');
    const first = Object.values(INGS).filter(g => g.cat === 'Obst & Gemüse').sort((a, b) => a.name.localeCompare(b.name, 'de'))[0];
    let h = `<h1>Vorrat</h1><p class="sub">Was du da hast, planen wir bevorzugt ein und ziehen es von der Einkaufsliste ab. Beim Kochen wird es automatisch abgebucht.</p>
    <form class="card fform" data-form="fadd"><label class="f full"><span>Lebensmittel</span><select class="in" id="fsel">${opts}</select></label><label class="f"><span>Menge (<span id="funit">${esc(first.unit)}</span>)</span><input class="in" id="famt" type="number" min="0" step="any" value="${first.pack}" inputmode="decimal"></label><button class="btn primary" type="submit">Hinzufügen</button></form>`;
    if (!ids.length) h += `<div class="empty"><span class="big">🧺</span>Dein Vorrat ist leer. Füge oben hinzu, was du da hast – oder hake beim Einkaufen ab und lege die Sachen mit einem Tipp hierher.</div>`;
    for (const c of OPT.categoryOrder) {
      const list = ids.filter(id => INGS[id].cat === c).sort((a, b) => INGS[a].name.localeCompare(INGS[b].name, 'de'));
      if (!list.length) continue;
      h += `<h3>${esc(c)}</h3>` + list.map(id => {
        const g = INGS[id], have = fr[id], need = needs[id] || 0;
        const st = !need ? '<small class="warn2">In den nächsten 2 Wochen nicht eingeplant – bald verbrauchen</small>' : have >= need - 1e-6 ? `<small>Reicht für den Plan (${esc(fmtQty(need, g.unit))} gebraucht)</small>` : `<small>Für den Plan fehlen ${esc(fmtQty(need - have, g.unit))}</small>`;
        return `<div class="fitem"><span class="fn">${esc(g.name)}${st}</span><button class="ib" data-act="f-step" data-v="${id}" data-dir="-1" aria-label="${esc(g.name)} weniger">−</button><span class="fq">${esc(fmtQty(have, g.unit))}</span><button class="ib" data-act="f-step" data-v="${id}" data-dir="1" aria-label="${esc(g.name)} mehr">＋</button><button class="ib" data-act="f-del" data-v="${id}" aria-label="${esc(g.name)} entfernen">${ICON.x}</button></div>`;
      }).join('');
    }
    const sug = CAT.recipes.filter(r => ELIG.has(r.id)).map(r => {
      const main = effIng(r).filter(e => !INGS[e.id].minor && !P().pantry.includes(e.id));
      const hasN = main.filter(e => fr[e.id] > 0).length;
      return {r, hasN, tot: main.length, miss: main.filter(e => !(fr[e.id] > 0)).map(e => INGS[e.id].name)};
    }).filter(x => x.hasN > 0).sort((a, b) => (b.hasN / b.tot) - (a.hasN / a.tot) || a.miss.length - b.miss.length).slice(0, 8);
    if (sug.length) h += `<h2>Das kannst du daraus kochen</h2>` + sug.map(x => `<a class="meal" style="display:flex;gap:12px;align-items:center;padding:10px 12px;text-decoration:none;color:inherit" href="#/rezept/${x.r.id}"><span class="em" aria-hidden="true">${x.r.e}</span><span class="mt"><span class="ml">${x.hasN} von ${x.tot} Zutaten da${x.miss.length ? ' · fehlt: ' + esc(x.miss.slice(0, 3).join(', ')) + (x.miss.length > 3 ? ' …' : '') : ''}</span><span class="mn">${esc(x.r.n)}</span></span><span class="tm"><span>${x.r.t} Min</span></span></a>`).join('');
    h += `<h2>Immer zuhause</h2><p class="sub">Grundvorrat wie Öl und Gewürze kommt nie auf die Einkaufsliste.</p><div class="chips">${OPT.pantryOrder.slice(0, 3).flatMap(c => Object.values(INGS).filter(g => g.cat === c && !g.id.endsWith('_gf')).sort((a, b) => a.name.localeCompare(b.name, 'de'))).map(g => `<button class="chip" aria-pressed="${P().pantry.includes(g.id)}" data-act="pantry" data-v="${g.id}">${esc(g.name)}</button>`).join('')}</div>`;
    return h;
  },
};
const fstep = g => (g.unit === 'g' || g.unit === 'ml') ? (g.pack >= 500 ? 50 : 25) : 1;
async function setFridge(id, qty) {
  const res = await act(() => api('PUT', 'fridge', {id, qty}));
  P().fridge = res.fridge; SHOP = null; repaint();
}

/* ---------- Rezepte ---------- */
const RCATS = [['', 'Alle Küchen'], ['f', '🌅 Frühstück'], ['oesterr', '🥨 Österreichisch'], ['ital', '🍝 Italienisch'], ['medi', '🫒 Mediterran'], ['asia', '🥢 Asiatisch'], ['indisch', '🍛 Indisch'], ['mex', '🌮 Mexikanisch'], ['orient', '🧆 Orientalisch'], ['schnell', '⏱️ Bis 25 Min'], ['veg', '🥕 Vegetarisch'], ['suess', '🥞 Süß'], ['saison', '🍂 Saison']];
VIEWS.rezepte = {
  html() {
    const F = [['fit', 'Passt zu mir'], ['fav', `Favoriten (${P().favorites.length})`], ['cooked', 'Schon gekocht'], ['all', 'Alle'], ['hidden', 'Ausgeblendet']];
    return `<h1>Rezepte</h1><p class="sub">${CAT.recipes.length} Rezepte mit Schritt-für-Schritt-Anleitung und Kochmodus.</p>
    <input class="in" id="rsearch" type="search" placeholder="Rezept oder Zutat suchen" value="${esc(ui.rQuery)}" aria-label="Rezepte durchsuchen" autocomplete="off">
    <div class="chips scroll" style="margin:12px 0 8px">${F.map(([k, l]) => `<button class="chip" aria-pressed="${ui.rFilter === k}" data-act="rfilter" data-v="${k}">${l}</button>`).join('')}</div>
    <div class="chips scroll" style="margin-bottom:14px">${RCATS.map(([k, l]) => `<button class="chip" aria-pressed="${ui.rCat === k}" data-act="rcat" data-v="${k}">${l}</button>`).join('')}</div>
    <div id="rlist" class="rlist">${recipeListHTML()}</div>`;
  },
};
function recipeListHTML() {
  const q = ui.rQuery.trim().toLowerCase();
  let list = CAT.recipes.slice();
  const p = P();
  if (ui.rFilter === 'fit') list = list.filter(r => ELIG.has(r.id));
  else if (ui.rFilter === 'fav') list = list.filter(r => p.favorites.includes(r.id));
  else if (ui.rFilter === 'cooked') list = list.filter(r => p.cooklog[r.id]).sort((a, b) => p.cooklog[b.id].n - p.cooklog[a.id].n);
  else if (ui.rFilter === 'hidden') list = list.filter(r => p.hidden.includes(r.id));
  const c = ui.rCat;
  if (c === 'f') list = list.filter(r => r.type === 'f');
  else if (c === 'schnell') list = list.filter(r => r.t <= 25);
  else if (c === 'veg') list = list.filter(isVeg);
  else if (c === 'saison') list = list.filter(r => r.season && inSeason(r));
  else if (c) list = list.filter(r => r.s.includes(c));
  if (q) list = list.filter(r => r.n.toLowerCase().includes(q) || Object.keys(r.i).some(id => INGS[id].name.toLowerCase().includes(q)));
  if (ui.rFilter !== 'cooked') list.sort((a, b) => (p.favorites.includes(b.id) - p.favorites.includes(a.id)) || a.n.localeCompare(b.n, 'de'));
  if (!list.length) return `<div class="empty">${ui.rFilter === 'fav' && !q ? 'Noch keine Favoriten. Tippe bei einem Rezept auf „♡ Favorit“ – Favoriten kommen doppelt so oft in den Plan.' : ui.rFilter === 'hidden' ? 'Keine ausgeblendeten Rezepte.' : 'Kein Rezept gefunden.'}</div>`;
  return `<p class="note">${plural(list.length, 'Rezept', 'Rezepte')}</p>` + list.map(r => recipeRow(r, `data-act="go" data-v="#/rezept/${r.id}"`)).join('');
}
VIEWS.rezept = {
  async load() {
    const q = route.q;
    if (q.d) await ensurePlan(q.d, iso(addDays(parseD(q.d), 1)));
  },
  html() {
    const r = RBY[route.arg];
    if (!r) return '<div class="empty">Rezept nicht gefunden.</div>';
    const q = route.q;
    const row = q.d && q.s ? rowAt(q.d, q.s) : null;
    const f = ui.portions[r.id] || (row ? (row.cook_portions || row.portions) : P().persons);
    const fav = P().favorites.includes(r.id), hid = P().hidden.includes(r.id);
    const log = P().cooklog[r.id];
    const subs = effIng(r).filter(e => e.note);
    let h = `<button class="link" data-act="back">← Zurück</button>
    <div class="hero"><span class="em" aria-hidden="true">${r.e}</span><div><h1 style="margin:0 0 6px">${esc(r.n)}</h1><div class="meta"><span>⏱ ${r.t} Min</span><span>🔥 ${num(kcalOf(r))} kcal/Portion</span><span>🍳 ${esc(appl(r))}</span></div></div></div>
    <div class="chips" style="margin-bottom:10px">${r.type === 'f' ? '<span class="tag">Frühstück</span>' : ''}${cuisineLabel(r) ? `<span class="tag">${esc(cuisineLabel(r))}</span>` : ''}${r.season ? `<span class="tag amber">${inSeason(r) ? 'Saison jetzt' : 'Saisonal'}</span>` : ''}${ELIG.has(r.id) ? '' : '<span class="tag beet">passt nicht zu deinen Einstellungen</span>'}${log ? `<span class="tag">${log.n}× gekocht</span>` : ''}</div>
    ${row ? `<div class="info small">Geplant: ${SLOT_LABEL[row.slot]} am ${DAYS[wd(parseD(row.date))]}, ${dshort(parseD(row.date))}${row.cooked ? ' · ✓ gekocht' : ''}</div>` : ''}
    <div class="row" style="margin:12px 0"><button class="btn primary" data-act="cook-open" data-rid="${r.id}" data-f="${f}" ${row ? `data-d="${row.date}" data-s="${row.slot}"` : ''}>${ICON.play} Kochmodus starten</button>
    <button class="btn ${fav ? 'ok' : 'ghost'} small" data-act="fav" data-v="${r.id}" aria-pressed="${fav}">${fav ? '♥ Favorit' : '♡ Favorit'}</button>
    <button class="btn ghost small" data-act="plan-recipe" data-v="${r.id}">Einplanen …</button>
    ${row && !row.cooked ? `<button class="btn ghost small" data-act="cook-toggle" data-d="${row.date}" data-s="${row.slot}">Als gekocht markieren</button>` : ''}</div>
    <div class="card"><div class="row between"><h2 style="margin:0">Zutaten</h2><div class="portion"><button class="ib" data-act="portions" data-v="${r.id}" data-dir="-1" aria-label="Weniger Portionen">−</button><output>${f}</output><button class="ib" data-act="portions" data-v="${r.id}" data-dir="1" aria-label="Mehr Portionen">＋</button><span class="small muted">${f === 1 ? 'Portion' : 'Portionen'}</span></div></div>
    ${ingsHTML(r, f)}<p class="note">Salz, Pfeffer und Wasser setzen wir voraus.${subs.length ? ' Für deine Ernährung angepasst.' : ''}</p></div>
    <div class="card"><h2 style="margin-top:0">Zubereitung</h2>${stepsHTML(r, f)}${r.tip ? `<div class="tip">💡 ${esc(r.tip)}</div>` : ''}</div>
    <div class="row"><button class="link ${hid ? '' : 'danger'}" data-act="hide" data-v="${r.id}">${hid ? 'Wieder vorschlagen' : 'Nicht mehr vorschlagen'}</button></div>`;
    return h;
  },
};
function planRecipeDialog(rid) {
  const r = RBY[rid];
  const t = today();
  const slots = r.type === 'f' ? ['frueh'] : ['mittag', 'abend'];
  openDialog(`„${esc(r.n)}“ einplanen`, `<label class="f"><span>Tag</span><input class="in" type="date" id="pr-date" value="${iso(t)}" min="${iso(t)}"></label>
  <div class="seg" role="group" aria-label="Mahlzeit" id="pr-slot">${slots.map((s, i) => `<button data-act="pr-slot" data-v="${s}" aria-pressed="${i === slots.length - 1}">${SLOT_LABEL[s]}</button>`).join('')}</div>
  <p class="note">Steht dort schon ein Gericht, wird es ersetzt.</p>`, `<button class="btn ghost" data-act="dlg-close">Abbrechen</button><button class="btn primary" data-act="pr-go" data-v="${rid}">Einplanen</button>`);
}

/* ---------- Kochmodus ---------- */
const TIMERS = {};
let COOK = null, wakeLock = null, audioCtx = null;
function openCook(rid, f, slot) {
  const r = RBY[rid];
  COOK = {r, f: +f || P().persons, step: 0, checked: new Set(), slot};
  const el = document.createElement('div');
  el.className = 'cook'; el.id = 'cook'; el.setAttribute('role', 'dialog'); el.setAttribute('aria-modal', 'true'); el.setAttribute('aria-label', 'Kochmodus ' + r.n);
  document.body.appendChild(el);
  document.body.style.overflow = 'hidden';
  drawCook();
  requestWake();
}
async function requestWake() { try { if ('wakeLock' in navigator) wakeLock = await navigator.wakeLock.request('screen'); } catch (e) { /* nicht verfügbar */ } }
document.addEventListener('visibilitychange', () => { if (COOK && document.visibilityState === 'visible') requestWake(); });
function closeCook() {
  COOK = null;
  const el = document.getElementById('cook'); if (el) el.remove();
  document.body.style.overflow = '';
  if (wakeLock) { wakeLock.release().catch(() => {}); wakeLock = null; }
  drawTimerDock();
}
function drawCook() {
  const el = document.getElementById('cook'); if (!el || !COOK) return;
  const {r, f, step} = COOK;
  const n = r.st.length, total = n + 2;
  let body;
  if (step === 0) {
    const ings = effIng(r);
    body = `<p class="cook-step-no">Vorbereitung</p><h2 class="big" style="margin:0 0 12px;font-size:1.6rem">Alles bereitstellen</h2>
    <p class="muted">Für ${plural(f, 'Portion', 'Portionen')}. Hake ab, was schon auf der Arbeitsfläche steht.</p>
    <ul class="ingcheck">${ings.map(e => { const g = INGS[e.id]; return `<li><label><input type="checkbox" data-act="cook-ing" data-v="${e.id}" ${COOK.checked.has(e.id) ? 'checked' : ''}><span class="q">${esc(g.unit === 'Stk' ? frac(e.q * f) : fmtQty(e.q * f, g.unit))}</span><span>${esc(g.unit === 'Stk' ? ingLabel(g, e.q * f) : g.name)}${e.note ? ` <small class="muted">(statt ${esc(e.note)})</small>` : ''}</span></label></li>`; }).join('')}</ul>
    <p class="note">Gerät: ${esc(appl(r))}</p>`;
  } else if (step <= n) {
    const i = step - 1, key = r.id + '-' + i;
    const tm = TIMERS[key];
    body = `<p class="cook-step-no">Schritt ${step} von ${n}</p><p class="cook-text">${stepHTML(r.st[i], r, f)}</p>`;
    if (r.timers[i]) {
      const sec = tm ? remaining(tm) : r.timers[i];
      body += `<div class="timer ${tm && tm.running ? 'run' : ''} ${tm && tm.ring ? 'ring' : ''}" data-timer="${key}"><span class="clock" data-clock="${key}">${clock(sec)}</span><span class="grow muted small">${tm && tm.ring ? 'Fertig!' : 'Timer für diesen Schritt'}</span>
      ${tm && tm.ring ? `<button class="btn primary small" data-act="timer-stop" data-v="${key}">OK</button>` : tm && tm.running ? `<button class="btn ghost small" data-act="timer-pause" data-v="${key}">Pause</button><button class="btn ghost small" data-act="timer-add" data-v="${key}">+1 Min</button>` : `<button class="btn primary small" data-act="timer-start" data-rid="${r.id}" data-i="${i}" data-sec="${tm ? remaining(tm) : r.timers[i]}">${ICON.timer} ${tm ? 'Weiter' : 'Start'}</button>${tm ? `<button class="btn ghost small" data-act="timer-stop" data-v="${key}">Zurücksetzen</button>` : ''}`}</div>`;
    }
    if (i === n - 1 && r.tip) body += `<div class="tip">💡 ${esc(r.tip)}</div>`;
  } else {
    body = `<div style="text-align:center;padding:30px 0"><div style="font-size:4rem">${r.e}</div><h2 class="big" style="font-size:1.8rem">Guten Appetit!</h2><p class="muted">${esc(r.n)} ist fertig.</p>
    ${COOK.slot && !(rowAt(COOK.slot.d, COOK.slot.s) || {}).cooked ? `<button class="btn primary" data-act="cook-finish">${ICON.check} Als gekocht markieren</button><p class="note">Die Zutaten werden aus deinem Vorrat abgebucht.</p>` : ''}</div>`;
  }
  el.innerHTML = `<div class="cook-top"><button class="ib" data-act="cook-close" aria-label="Kochmodus schließen">${ICON.x}</button><span class="t">${r.e} ${esc(r.n)}</span><div class="portion"><button class="ib" data-act="cook-f" data-dir="-1" aria-label="Weniger Portionen">−</button><output>${f}</output><button class="ib" data-act="cook-f" data-dir="1" aria-label="Mehr Portionen">＋</button></div></div>
  <div class="cook-dots" aria-hidden="true">${Array.from({length: total}, (_, k) => `<span class="${k <= step ? 'on' : ''}"></span>`).join('')}</div>
  <div class="timers-bar" id="cook-timers"></div>
  <div class="cook-body">${body}</div>
  <div class="cook-nav"><button class="btn ghost" data-act="cook-prev" ${step === 0 ? 'disabled' : ''}>${ICON.left} Zurück</button><button class="btn primary" data-act="cook-next" ${step >= total - 1 ? 'disabled' : ''}>${step === 0 ? 'Los geht’s' : step === n ? 'Fertig' : 'Weiter'} ${ICON.right}</button></div>`;
  drawTimerDock();
}
const remaining = t => Math.max(0, t.running ? Math.ceil((t.endAt - Date.now()) / 1000) : t.left);
const clock = s => `${Math.floor(s / 60)}:${pad(s % 60)}`;
function startTimer(rid, i, sec) {
  const key = rid + '-' + i, r = RBY[rid];
  TIMERS[key] = {key, label: `${r.e} Schritt ${+i + 1}`, running: true, endAt: Date.now() + sec * 1000, left: sec, ring: false};
  unlockAudio();
  if ('Notification' in window && Notification.permission === 'default') Notification.requestPermission().catch(() => {});
  refreshTimersUI();
}
function refreshTimersUI() { if (COOK) drawCook(); else drawTimerDock(); }
function drawTimerDock() {
  const list = Object.values(TIMERS);
  let dock = document.getElementById(COOK ? 'cook-timers' : 'timerdock');
  if (!COOK && !dock && list.length) { dock = document.createElement('div'); dock.id = 'timerdock'; dock.className = 'timers-bar'; dock.style.cssText = 'position:fixed;top:calc(64px + env(safe-area-inset-top,0px));left:0;right:0;z-index:25;justify-content:center'; document.body.appendChild(dock); }
  if (!dock) return;
  dock.innerHTML = list.map(t => `<span class="tag ${t.ring ? 'beet' : ''}" data-act="${t.ring ? 'timer-stop' : t.running ? 'timer-pause' : 'timer-resume'}" data-v="${t.key}" role="button" tabindex="0">${t.ring ? '⏰' : '⏱'} ${esc(t.label)} · <span data-clock="${t.key}">${clock(remaining(t))}</span>${t.ring ? ' · OK' : ''}</span>`).join('');
  if (!COOK && !list.length) dock.remove();
}
setInterval(() => {
  for (const t of Object.values(TIMERS)) {
    if (t.running && remaining(t) <= 0) { t.running = false; t.left = 0; t.ring = true; ring(t); refreshTimersUI(); }
    document.querySelectorAll(`[data-clock="${t.key}"]`).forEach(el => { el.textContent = clock(remaining(t)); });
  }
}, 500);
function unlockAudio() { try { audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)(); if (audioCtx.state === 'suspended') audioCtx.resume(); } catch (e) { /* kein Ton */ } }
function ring(t) {
  toast(`⏰ Timer fertig: ${t.label}`, false, 8000);
  try { navigator.vibrate && navigator.vibrate([400, 200, 400, 200, 400]); } catch (e) { /* egal */ }
  try {
    if (audioCtx) for (let k = 0; k < 6; k++) { const o = audioCtx.createOscillator(), g = audioCtx.createGain(); o.frequency.value = k % 2 ? 660 : 880; g.gain.value = 0.18; o.connect(g); g.connect(audioCtx.destination); o.start(audioCtx.currentTime + k * 0.35); o.stop(audioCtx.currentTime + k * 0.35 + 0.22); }
  } catch (e) { /* egal */ }
  try { if (document.hidden && 'Notification' in window && Notification.permission === 'granted') new Notification('Timer fertig', {body: t.label}); } catch (e) { /* egal */ }
}

/* ---------- Profil ---------- */
VIEWS.profil = {
  async load() { if (!ui.sendLog) quiet(api('GET', 'send-log').then(r => { ui.sendLog = r.log; if (route.name === 'profil') repaint(); })); },
  html() {
    const u = ST.user, ch = ST.channels, n = P().notify, cs = ui.contact;
    const verified = {email: u.email_verified, whatsapp: u.phone_verified};
    const chBoxes = kind => ['whatsapp', 'email'].filter(c => ch[c]).map(c => `<label class="check"><input type="checkbox" data-notify-ch="${kind}" value="${c}" ${n[kind].channels.includes(c) ? 'checked' : ''} ${verified[c] ? '' : 'disabled'}> ${c === 'email' ? 'E-Mail' : 'WhatsApp'}${verified[c] ? '' : ' <span class="muted small">(erst bestätigen)</span>'}</label>`).join('') || '<p class="note">Die Verwaltung hat noch keinen Versand eingerichtet.</p>';
    let h = `<h1>Profil</h1>
    <div class="card"><h2>Konto</h2><form data-form="dname" class="row"><label class="f grow" style="margin:0"><span>Anzeigename</span><input class="in" id="dname" value="${esc(u.display_name)}" maxlength="40"></label><button class="btn ghost" type="submit" style="align-self:flex-end">Speichern</button></form>
    <p class="small muted" style="margin:10px 0 0">Benutzername: <b>${esc(u.username)}</b>${u.is_admin ? ' · Verwaltung' : ''}</p>
    <div class="row" style="margin-top:12px"><button class="btn ghost small" data-act="pw-dialog">Passwort ändern</button><button class="btn ghost small" data-act="logout-others">Auf anderen Geräten abmelden</button><button class="btn ghost small" data-act="logout">Abmelden</button></div></div>`;
    h += `<div class="card"><h2>Kontakt</h2><p class="sub small">Nur bestätigte Adressen bekommen Nachrichten. Niemand sonst sieht sie.</p>`;
    h += contactBlock('email', 'E-Mail', ch.email, u.email, u.email_verified, cs.email, 'name@beispiel.at', 'email');
    h += contactBlock('phone', 'WhatsApp', ch.whatsapp, u.phone_masked, u.phone_verified, cs.phone, '+43 664 1234567', 'tel');
    h += `</div>`;
    h += `<div class="card"><h2>Automatische Nachrichten</h2>
    <label class="switch"><span><b>Einkaufsliste</b><br><span class="small muted">am Einkaufstag für die kommende Woche</span></span><input type="checkbox" id="n-shop" ${n.shopping.enabled ? 'checked' : ''}></label>
    <div class="grid2"><label class="f"><span>Einkaufstag</span><select class="in" id="n-shop-day">${DAYS.map((d, i) => `<option value="${i}" ${n.shopping.weekday === i ? 'selected' : ''}>${d}</option>`).join('')}</select></label><label class="f"><span>Uhrzeit</span><input class="in" type="time" id="n-shop-time" value="${esc(n.shopping.time)}"></label></div>
    <div class="row">${chBoxes('shopping')}</div><hr style="border:0;border-top:1px solid var(--line);margin:14px 0">
    <label class="switch"><span><b>Tagesmenü</b><br><span class="small muted">was heute gekocht wird und was noch fehlt</span></span><input type="checkbox" id="n-daily" ${n.daily.enabled ? 'checked' : ''}></label>
    <label class="f" style="max-width:200px"><span>Uhrzeit</span><input class="in" type="time" id="n-daily-time" value="${esc(n.daily.time)}"></label>
    <div class="row">${chBoxes('daily')}</div>
    <div class="row" style="margin-top:12px"><button class="btn primary" data-act="notify-save">Speichern</button></div></div>`;
    h += `<div class="card"><h2>Vorlieben</h2><p class="sub small">${plural(P().persons, 'Person', 'Personen')}, Budget ${eur(P().budget)}/Woche, ${esc(OPT.diets.find(d => d[0] === P().diet)[2])}${P().styles.length ? ', ' + plural(P().styles.length, 'Vorliebe', 'Vorlieben') : ''}.</p><a class="btn ghost" href="#/einstellungen">Einstellungen bearbeiten</a></div>`;
    if (ui.sendLog && ui.sendLog.length) h += `<div class="card"><h2>Zuletzt gesendet</h2>${ui.sendLog.slice(0, 8).map(l => `<div class="row small" style="padding:4px 0;border-bottom:1px solid var(--line)"><span>${l.status === 'sent' ? '✅' : '⚠️'}</span><span class="grow">${{shopping: 'Einkaufsliste', today: 'Tagesmenü', daily: 'Tagesmenü', week: 'Wochenplan', code: 'Bestätigungscode'}[l.kind] || esc(l.kind)} per ${l.channel === 'email' ? 'E-Mail' : 'WhatsApp'}${l.error ? ` – <span class="muted">${esc(l.error)}</span>` : ''}</span><span class="muted">${new Date(l.created * 1000).toLocaleString('de-AT', {day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit'})}</span></div>`).join('')}</div>`;
    if (u.is_admin) h += `<div class="card"><h2>Verwaltung</h2><p class="sub small">Konten, E-Mail-Server (SMTP) und WhatsApp-Gateway.</p><a class="btn ghost" href="#/verwaltung">Verwaltung öffnen</a></div>`;
    h += `<div class="card"><h2>Konto löschen</h2><p class="sub small">Löscht dein Konto mit Plan, Einkaufslisten und Vorrat unwiderruflich.</p><button class="btn danger small" data-act="delete-account">Konto löschen …</button></div>`;
    return h;
  },
};
function contactBlock(kind, label, enabled, value, verified, st, ph, type) {
  if (!enabled) return `<div style="margin-bottom:14px"><b>${label}</b><p class="note" style="margin:4px 0">${kind === 'email' ? 'Die Verwaltung hat noch keinen E-Mail-Server eingerichtet.' : 'WhatsApp-Versand über JARVIS ist auf diesem Server nicht aktiviert.'}</p></div>`;
  let h = `<div style="margin-bottom:16px"><div class="row between"><b>${label}</b>${value ? (verified ? '<span class="tag">✓ bestätigt</span>' : '<span class="tag amber">nicht bestätigt</span>') : ''}</div>`;
  if (value && verified && !(st && st.editing)) h += `<div class="row" style="margin-top:6px"><span class="grow">${esc(value)}</span><button class="link" data-act="contact-edit" data-v="${kind}">Ändern</button><button class="link danger" data-act="contact-del" data-v="${kind}">Entfernen</button></div>`;
  else if (st && st.sent) h += `<form class="row" data-form="contact-verify" data-kind="${kind}" style="margin-top:6px"><label class="f grow" style="margin:0"><span>Code aus der Nachricht an ${esc(st.sent)}</span><input class="in" id="code-${kind}" inputmode="numeric" autocomplete="one-time-code" maxlength="6" required></label><button class="btn primary" type="submit" style="align-self:flex-end">Bestätigen</button></form><button class="link small" data-act="contact-edit" data-v="${kind}">Andere ${kind === 'email' ? 'Adresse' : 'Nummer'}</button>`;
  else h += `<form class="row" data-form="contact-start" data-kind="${kind}" style="margin-top:6px"><label class="f grow" style="margin:0"><span>${kind === 'email' ? 'E-Mail-Adresse' : 'Handynummer mit WhatsApp'}</span><input class="in" id="contact-${kind}" type="${type}" placeholder="${ph}" required autocomplete="${kind === 'email' ? 'email' : 'tel'}"></label><button class="btn primary" type="submit" style="align-self:flex-end">Code senden</button></form>`;
  return h + '</div>';
}

/* ---------- Verwaltung ---------- */
VIEWS.verwaltung = {
  async load() {
    if (!ST.user.is_admin) { location.hash = '#/profil'; return; }
    const [users, cfg] = await Promise.all([api('GET', 'admin/users'), api('GET', 'admin/config')]);
    ui.admin = Object.assign(ui.admin || {}, {users: users.users, cfg});
  },
  html() {
    const A = ui.admin;
    if (!A) return '';
    const c = A.cfg, s = c.smtp, w = c.whatsapp;
    let h = `<button class="link" data-act="go" data-v="#/profil">← Profil</button><h1>Verwaltung</h1>`;
    h += `<div class="card"><h2>Konten</h2><p class="sub small">Jede Person sieht nur ihre eigenen Daten. Neue Konten bekommen ein vorläufiges Passwort, das beim ersten Anmelden geändert werden muss.</p>
    ${A.tempPw ? `<div class="info"><b>Vorläufiges Passwort für ${esc(A.tempPw.user)}:</b><div class="pw-show" style="margin-top:6px">${esc(A.tempPw.pw)}</div><p class="small" style="margin:6px 0 0">Gib es der Person persönlich weiter. Es wird nur jetzt angezeigt.</p></div>` : ''}
    <table class="users"><thead><tr><th>Name</th><th>Status</th><th></th></tr></thead><tbody>${A.users.map(x => `<tr><td><b>${esc(x.display_name)}</b><br><span class="muted small">${esc(x.username)}</span></td><td class="small">${x.is_admin ? '<span class="tag">Verwaltung</span> ' : ''}${x.disabled ? '<span class="tag beet">gesperrt</span> ' : ''}${x.locked ? '<span class="tag amber">nach Fehlversuchen gesperrt</span> ' : ''}${x.must_change_pw ? '<span class="tag amber">Passwort ändern</span> ' : ''}${x.email_verified ? '✉️ ' : ''}${x.phone_verified ? '💬' : ''}</td>
    <td style="text-align:right"><select class="in" style="width:auto;padding:6px" data-admin-user="${x.id}" aria-label="Aktion für ${esc(x.username)}"><option value="">Aktion …</option><option value="reset">Passwort zurücksetzen</option>${x.locked ? '<option value="unlock">Entsperren</option>' : ''}${x.id !== ST.user.id ? `<option value="${x.disabled ? 'enable' : 'disable'}">${x.disabled ? 'Freischalten' : 'Sperren'}</option>` : ''}<option value="${x.is_admin ? 'unadmin' : 'admin'}">${x.is_admin ? 'Verwaltungsrecht entziehen' : 'Zur Verwaltung machen'}</option>${x.id !== ST.user.id ? '<option value="delete">Löschen</option>' : ''}</select></td></tr>`).join('')}</tbody></table>
    <h3>Neues Konto</h3><form data-form="admin-new"><div class="grid2"><label class="f"><span>Name</span><input class="in" id="an-name" maxlength="40" required></label><label class="f"><span>Benutzername</span><input class="in" id="an-user" required></label></div>
    <label class="check"><input type="checkbox" id="an-admin"> Verwaltungsrechte</label><button class="btn primary" type="submit" style="margin-top:8px">Konto anlegen</button></form></div>`;
    h += `<div class="card"><h2>Registrierung</h2><div class="seg" role="group" aria-label="Registrierung">${[['closed', 'Nur Verwaltung'], ['invite', 'Mit Einladung'], ['open', 'Offen']].map(([k, l]) => `<button data-act="admin-reg" data-v="${k}" aria-pressed="${c.registration === k}">${l}</button>`).join('')}</div>
    <p class="note">${c.registration === 'open' ? 'Jede Person, die die Adresse kennt, kann ein Konto anlegen. Nur im privaten Heimnetz empfehlenswert.' : c.registration === 'invite' ? 'Neue Konten brauchen einen Einladungscode (7 Tage gültig, einmal verwendbar).' : 'Nur die Verwaltung legt Konten an. Am sichersten.'}</p>
    ${c.registration === 'invite' ? `<button class="btn ghost small" data-act="admin-invite">Einladungscode erzeugen</button>${A.invite ? `<div class="pw-show" style="margin-top:8px">${esc(A.invite)}</div>` : ''}` : ''}</div>`;
    h += `<div class="card"><h2>Adresse der App</h2><p class="sub small">Wird in E-Mails und WhatsApp-Nachrichten als Link verwendet, z. B. http://192.168.0.20:8080</p>
    <form class="row" data-form="admin-url"><input class="in grow" id="ad-url" value="${esc(c.public_url)}" placeholder="http://…"><button class="btn ghost" type="submit">Speichern</button></form></div>`;
    h += `<div class="card"><h2>E-Mail (eigener SMTP-Server)</h2><form data-form="admin-smtp">
    <div class="grid2"><label class="f"><span>Server (Host)</span><input class="in" id="sm-host" value="${esc(s.host)}" placeholder="smtp.beispiel.at"></label><label class="f"><span>Port</span><input class="in" id="sm-port" type="number" value="${esc(s.port)}"></label></div>
    <label class="f"><span>Verschlüsselung</span><select class="in" id="sm-sec">${[['starttls', 'STARTTLS (meist Port 587)'], ['ssl', 'SSL/TLS (meist Port 465)'], ['none', 'Keine (nur im lokalen Netz)']].map(([k, l]) => `<option value="${k}" ${s.security === k ? 'selected' : ''}>${l}</option>`).join('')}</select></label>
    <div class="grid2"><label class="f"><span>Benutzer</span><input class="in" id="sm-user" value="${esc(s.username)}" autocomplete="off"></label><label class="f"><span>Passwort</span><input class="in" id="sm-pw" type="password" placeholder="${s.password_set ? '•••••• (gespeichert)' : ''}" autocomplete="new-password"></label></div>
    <div class="grid2"><label class="f"><span>Absenderadresse</span><input class="in" id="sm-from" value="${esc(s.from_addr)}" placeholder="wochenteller@beispiel.at"></label><label class="f"><span>Absendername</span><input class="in" id="sm-name" value="${esc(s.from_name)}"></label></div>
    <div class="row"><button class="btn primary" type="submit">Speichern</button></div></form>
    <form class="row" data-form="admin-test-email" style="margin-top:14px"><input class="in grow" id="te-to" type="email" placeholder="Test an …" value="${esc(ST.user.email || '')}"><button class="btn ghost" type="submit">Test-E-Mail senden</button></form></div>`;
    h += `<div class="card"><h2>WhatsApp über JARVIS</h2><p class="sub small">Nutzt das JARVIS-Gateway (Whatsapp_Buissines, <code>start_gateway.bat</code>). Es nimmt nur Anfragen vom selben PC an – Wochenteller muss also auf dem JARVIS-PC laufen.</p>
    <form data-form="admin-wa"><label class="switch"><span>WhatsApp-Versand aktiv</span><input type="checkbox" id="wa-on" ${w.enabled ? 'checked' : ''}></label>
    <div class="grid2"><label class="f"><span>Gateway-Adresse</span><input class="in" id="wa-url" value="${esc(w.gateway_url)}"></label><label class="f"><span>Ländervorwahl für Nummern mit 0</span><input class="in" id="wa-cc" value="${esc(w.country_code)}" inputmode="numeric"></label></div>
    <div class="row"><button class="btn primary" type="submit">Speichern</button><button class="btn ghost" type="button" data-act="admin-health">Gateway prüfen</button><span id="wa-health" class="small"></span></div></form>
    <form class="row" data-form="admin-test-wa" style="margin-top:14px"><input class="in grow" id="tw-phone" type="tel" placeholder="Testnummer, z. B. +43 664 …"><button class="btn ghost" type="submit">Test-Nachricht</button></form></div>`;
    return h;
  },
};

/* ---------- Einstellungen / Assistent ---------- */
function startWizard(mode) {
  if (ui.wizard && ui.wizard.mode === mode) return;
  ui.wizard = {mode, step: mode === 'onboarding' ? 0 : -1, d: JSON.parse(JSON.stringify(P())), start: null, weeks: 4};
  route = {name: 'einstellungen', arg: null, q: {}};
  if (location.hash !== '#/einstellungen') history.replaceState(null, '', '#/einstellungen');
}
const STEPS = [
  {k: 'stores', t: 'Wo kaufst du ein?', sub: 'Wähle alle Geschäfte in deiner Nähe. Wir rechnen mit dem günstigsten und zeigen dir den Vergleich.', ok: d => d.stores.length > 0,
    body: () => `<div class="tiles">${OPT.stores.map(([k, n]) => tile('stores', k, '🛒', n, '', true)).join('')}</div>`},
  {k: 'persons', t: 'Für wen und wann kochst du?', sub: 'Tippe Tage weg, an denen du nicht zuhause isst.', ok: d => d.days.length > 0,
    body: d => `<div class="stepper"><button data-act="w-persons" data-dir="-1" aria-label="Eine Person weniger">−</button><output aria-live="polite">${d.persons}</output><button data-act="w-persons" data-dir="1" aria-label="Eine Person mehr">＋</button><span class="sub" style="margin:0">${d.persons === 1 ? 'Person' : 'Personen'}</span></div>
    <h3>An welchen Tagen isst du zuhause?</h3><div class="daysel">${DS.map((n, i) => `<button class="tile" aria-pressed="${d.days.includes(i)}" data-act="w-day" data-v="${i}" aria-label="${DAYS[i]}"><span class="l">${n}</span></button>`).join('')}</div>
    <h3>Welche Mahlzeiten sollen wir planen?</h3><div class="tiles">${OPT.meals.map(([k, e, l, s]) => tile('meals', k, e, l, s, false)).join('')}</div>`},
  {k: 'budget', t: 'Wie hoch ist dein Wochenbudget?', sub: 'So viel möchtest du pro Woche für diesen Einkauf ausgeben.',
    body: d => `<output class="bignum" id="bval">${d.budget} €</output><p class="muted" id="bper">${perServing(d)}</p><input type="range" min="15" max="300" step="5" value="${d.budget}" data-input="budget" aria-label="Wochenbudget in Euro"><div class="range-ends"><span>15 €</span><span>300 €</span></div>`},
  {k: 'kcal', t: 'Hast du ein Kalorienziel?', sub: 'Wir wählen Rezepte, die zu deinem Tagesziel passen, und zeigen dir die Kalorien pro Mahlzeit und Tag.',
    body: d => `<div class="chips" style="margin-bottom:16px"><button class="chip" aria-pressed="${!d.kcal}" data-act="w-kcal" data-v="0">Kein Ziel</button><button class="chip" aria-pressed="${!!d.kcal}" data-act="w-kcal" data-v="2000">Ja, ich habe ein Ziel</button></div>
    ${d.kcal ? `<output class="bignum" id="kval">${num(d.kcal)} kcal</output><p class="muted">pro Tag und Person</p><input type="range" min="1200" max="3500" step="50" value="${d.kcal}" data-input="kcal" aria-label="Kalorienziel pro Tag"><div class="range-ends"><span>1.200</span><span>3.500</span></div>` : ''}`},
  {k: 'appliances', t: 'Was hast du in der Küche?', sub: 'Wir schlagen nur Rezepte vor, die du damit kochen kannst.', ok: d => d.appliances.length > 0,
    body: () => `<div class="tiles">${OPT.appliances.map(([k, e, l]) => tile('appliances', k, e, l, '', true)).join('')}</div>`},
  {k: 'diet', t: 'Wie isst du?', sub: 'Bei Vegan, Laktose- oder Glutenfrei ersetzen wir Milch, Butter, Obers, Honig, Nudeln & Co. automatisch.',
    body: () => `<div class="tiles">${OPT.diets.map(([k, e, l]) => tile('diet', k, e, l, '', false)).join('')}</div><h3>Außerdem</h3><div class="tiles">${OPT.extras.map(([k, e, l]) => tile('extras', k, e, l, '', true)).join('')}</div><h3>Allergien und Unverträglichkeiten</h3><div class="tiles">${OPT.allergies.map(([k, e, l]) => tile('allergies', k, e, l, '', true, 'no')).join('')}</div>`},
  {k: 'proteins', t: 'Welche Proteinquellen magst du?', sub: 'Tippe weg, was du nicht essen möchtest.',
    body: () => `<div class="tiles">${OPT.proteins.map(([k, e, l]) => tile('proteins', k, e, l, '', true)).join('')}</div>`},
  {k: 'styles', t: 'Worauf hast du Lust?', sub: 'Passende Rezepte kommen öfter dran. Süße Hauptspeisen gibt es nur selten, außer du wählst sie aus.',
    body: () => `<div class="tiles">${OPT.styles.map(([k, e, l, s]) => tile('styles', k, e, l, s || '', true)).join('')}</div>`},
  {k: 'pantry', t: 'Was hast du immer zuhause?', sub: 'Grundvorrat wie Öl und Gewürze kommt nie auf die Einkaufsliste.',
    body: () => OPT.pantryOrder.slice(0, 3).map(c => `<h3>${esc(c)}</h3><div class="chips">${Object.values(INGS).filter(g => g.cat === c && !g.id.endsWith('_gf')).sort((a, b) => a.name.localeCompare(b.name, 'de')).map(g => chip('pantry', g.id, g.name)).join('')}</div>`).join('')},
  {k: 'fridge', t: 'Was ist gerade im Kühlschrank?', sub: 'Tippe an, was du da hast. Wir planen es bevorzugt ein. Mengen stellst du später im Vorrat genau ein.',
    body: d => ['Obst & Gemüse', 'Kühlregal', 'Fleisch & Fisch', 'Tiefkühl', 'Brot & Gebäck'].map(c => `<h3>${esc(c)}</h3><div class="chips">${Object.values(INGS).filter(g => g.cat === c && !g.id.endsWith('_gf')).sort((a, b) => a.name.localeCompare(b.name, 'de')).map(g => `<button class="chip" aria-pressed="${(d.fridge[g.id] || 0) > 0}" data-act="w-fridge" data-v="${g.id}">${esc(g.name)}</button>`).join('')}</div>`).join('')},
  {k: 'blocked', t: 'Gibt es etwas, das du nicht magst?', sub: 'Kleinigkeiten wie Zwiebeln, Knoblauch oder Kräuter lassen wir im Rezept weg. Bei Hauptzutaten bekommst du ein anderes Gericht.',
    body: () => `<div class="chips">${Object.values(INGS).filter(g => g.cat !== 'Gewürze & Öle' && !g.id.endsWith('_gf')).sort((a, b) => a.name.localeCompare(b.name, 'de')).map(g => chip('blocked', g.id, g.name, 'no')).join('')}</div>`},
];
function perServing(d) { const mt = OPT.mealSlots[d.meals]; const n = d.days.length * mt.length * d.persons; return n ? `rund ${eur(d.budget / n)} pro Portion bei ${n} Portionen pro Woche` : 'Wähle mindestens einen Tag'; }
VIEWS.einstellungen = {
  get nonav() { return ui.wizard && ui.wizard.mode === 'onboarding'; },
  load() { if (!ui.wizard) startWizard('edit'); },
  html() {
    const W = ui.wizard, d = W.d;
    if (W.mode === 'edit' && W.step < 0) {
      return `<button class="link" data-act="go" data-v="#/profil">← Profil</button><h1>Einstellungen</h1><p class="sub">Änderungen wirken auf neue Pläne. Danach am besten neu planen.</p>
      ${STEPS.map((s, i) => `<button class="card" style="display:block;width:100%;text-align:left;cursor:pointer" data-act="w-open" data-v="${i}"><b>${esc(s.t)}</b><br><span class="small muted">${esc(stepSummary(s.k, d))}</span></button>`).join('')}
      <button class="btn primary block" data-act="plan-dialog">Mit diesen Einstellungen neu planen</button>`;
    }
    if (W.step >= STEPS.length) return planStepHTML();
    const st = STEPS[W.step];
    const ok = !st.ok || st.ok(d);
    const total = STEPS.length + (W.mode === 'onboarding' ? 1 : 0);
    return `${W.mode === 'onboarding' ? `<div class="progress" role="progressbar" aria-label="Fortschritt" aria-valuemin="1" aria-valuemax="${total}" aria-valuenow="${W.step + 1}"><span style="width:${(W.step + 1) / total * 100}%"></span></div><p class="stepno">Schritt ${W.step + 1} von ${total}</p>` : '<button class="link" data-act="w-overview">← Übersicht</button>'}
    <h1>${esc(st.t)}</h1>${st.sub ? `<p class="sub">${esc(st.sub)}</p>` : ''}${st.body(d)}
    <div class="bar">${W.mode === 'onboarding' && W.step > 0 ? '<button class="btn ghost" data-act="w-back">Zurück</button>' : ''}<button class="btn primary" data-act="w-next" ${ok ? '' : 'disabled'}>${W.mode === 'edit' ? 'Übernehmen' : 'Weiter'}</button></div>`;
  },
};
function stepSummary(k, d) {
  const lab = (list, keys) => keys.map(x => (list.find(y => y[0] === x) || [x, '', x])[2]).join(', ');
  switch (k) {
    case 'stores': return d.stores.map(storeName).join(', ');
    case 'persons': return `${plural(d.persons, 'Person', 'Personen')}, ${d.days.map(i => DS[i]).join(' ')}, ${OPT.meals.find(m => m[0] === d.meals)[2]}`;
    case 'budget': return `${eur(d.budget)} pro Woche`;
    case 'kcal': return d.kcal ? `${num(d.kcal)} kcal pro Tag` : 'Kein Ziel';
    case 'appliances': return d.appliances.join(', ');
    case 'diet': return [OPT.diets.find(x => x[0] === d.diet)[2], lab(OPT.extras, d.extras), d.allergies.length ? 'Allergien: ' + lab(OPT.allergies, d.allergies) : ''].filter(Boolean).join(' · ');
    case 'proteins': return lab(OPT.proteins, d.proteins) || 'keine';
    case 'styles': return lab(OPT.styles, d.styles) || 'Keine besonderen Vorlieben';
    case 'pantry': return plural(d.pantry.length, 'Zutat', 'Zutaten') + ' immer zuhause';
    case 'fridge': return plural(Object.keys(d.fridge).length, 'Lebensmittel', 'Lebensmittel') + ' im Vorrat';
    case 'blocked': return d.blocked.length ? d.blocked.map(id => INGS[id].name).join(', ') : 'Nichts';
  }
  return '';
}
function planStepHTML() {
  const W = ui.wizard, t = today();
  if (!W.start) W.start = iso(wd(t) >= 4 ? addDays(mondayOf(t), 7) : t);
  const weeks = [[1, '1 Woche'], [2, '2 Wochen'], [4, '1 Monat'], [8, '2 Monate'], [13, '3 Monate'], [26, '6 Monate']];
  const total = STEPS.length + 1;
  return `<div class="progress"><span style="width:100%"></span></div><p class="stepno">Schritt ${total} von ${total}</p>
  <h1>Wie weit sollen wir planen?</h1><p class="sub">Du kannst eine Woche oder gleich mehrere Monate planen. Einzelne Gerichte tauschst du jederzeit.</p>
  <label class="f" style="max-width:260px"><span>Start</span><input class="in" type="date" id="w-start" value="${W.start}" min="${iso(addDays(t, -7))}"></label>
  <div class="chips">${weeks.map(([w, l]) => `<button class="chip" aria-pressed="${W.weeks === w}" data-act="w-weeks" data-v="${w}">${l}</button>`).join('')}</div>
  <div class="bar"><button class="btn ghost" data-act="w-back">Zurück</button><button class="btn primary" data-act="w-finish">Plan erstellen</button></div>`;
}
async function saveWizard() {
  const d = ui.wizard.d, p = P();
  const body = {};
  for (const k of ['persons', 'meals', 'days', 'budget', 'kcal', 'appliances', 'diet', 'extras', 'allergies', 'proteins', 'styles', 'pantry', 'blocked', 'stores']) body[k] = d[k];
  const fridgeOps = [];
  const keys = new Set([...Object.keys(d.fridge), ...Object.keys(p.fridge)]);
  for (const id of keys) if ((d.fridge[id] || 0) !== (p.fridge[id] || 0)) fridgeOps.push({id, qty: d.fridge[id] || 0});
  applyState(await api('PUT', 'profile', body));
  for (const op of fridgeOps) P().fridge = (await api('PUT', 'fridge', op)).fridge;
  SHOP = null;
}

/* ---------- Dialoge ---------- */
let dlgReturn = null;
function openDialog(title, body, actions) {
  closeDialog();
  dlgReturn = document.activeElement;
  const back = document.createElement('div');
  back.className = 'dlg-back'; back.id = 'dlg';
  back.innerHTML = `<div class="dlg" role="dialog" aria-modal="true" aria-labelledby="dlg-t"><div class="dlg-head"><h2 id="dlg-t">${title}</h2><button class="ib" data-act="dlg-close" aria-label="Schließen">${ICON.x}</button></div><div id="dlg-body">${body}</div>${actions ? `<div class="dlg-actions">${actions}</div>` : ''}</div>`;
  document.body.appendChild(back);
  const f = back.querySelector('input,select,button.btn.primary');
  if (f) setTimeout(() => f.focus(), 30);
}
function closeDialog() { const d = document.getElementById('dlg'); if (d) { d.remove(); if (dlgReturn && dlgReturn.focus) dlgReturn.focus(); } }
function confirmDialog(title, text, okLabel, danger = false) {
  return new Promise(res => {
    openDialog(esc(title), `<p>${esc(text)}</p>`, `<button class="btn ghost" data-act="dlg-close">Abbrechen</button><button class="btn ${danger ? 'danger' : 'primary'}" id="dlg-ok">${esc(okLabel)}</button>`);
    document.getElementById('dlg-ok').addEventListener('click', () => { closeDialog(); res(true); });
    const d = document.getElementById('dlg');
    const obs = new MutationObserver(() => { if (!document.body.contains(d)) { obs.disconnect(); res(false); } });
    obs.observe(document.body, {childList: true});
  });
}

/* ---------- Aktionen (Klicks) ---------- */
const A = {};
document.addEventListener('click', async e => {
  const b = e.target.closest('[data-act]');
  if (!b) { if (e.target.id === 'dlg') closeDialog(); return; }
  const fn = A[b.dataset.act];
  if (!fn) return;
  if (b.tagName === 'A' && b.dataset.act !== 'dlg-close') e.preventDefault();
  if (b.dataset.act === 'dlg-close' && b.tagName === 'A') { closeDialog(); return; }
  if (b.tagName === 'INPUT' && b.type === 'checkbox') { /* Checkbox-Aktionen laufen über change */ }
  else e.preventDefault();
  try { await fn(b, e); } catch (err) { if (!(err instanceof ApiErr)) { console.error(err); toast(String(err.message || err), true); } }
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { if (document.getElementById('dlg')) closeDialog(); else if (COOK) closeCook(); }
  if (COOK && !document.getElementById('dlg')) {
    if (e.key === 'ArrowRight') A['cook-next']();
    if (e.key === 'ArrowLeft') A['cook-prev']();
  }
  if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('.tag[role="button"]')) { e.preventDefault(); e.target.click(); }
});
document.addEventListener('toggle', e => {
  const d = e.target;
  if (d.matches && d.matches('details.meal[data-key]')) { if (d.open) ui.open.add(d.dataset.key); else ui.open.delete(d.dataset.key); }
}, true);

A['auth-mode'] = b => { ui.authMode = b.dataset.v; renderAuth(); };
A.logout = async () => { await quiet(api('POST', 'logout')); SES = await api('GET', 'session'); ST = null; PLAN = {from: null, to: null, rows: [], by: {}}; SHOP = null; ui.wizard = null; ui.admin = null; ui.sendLog = null; ui.contact = {}; ui.authMode = 'login'; renderAuth(); };
A['logout-others'] = () => act(() => api('POST', 'account/logout-others'), 'Alle anderen Geräte wurden abgemeldet.');
A.go = b => { location.hash = b.dataset.v; };
A.back = () => { if (history.length > 1) history.back(); else location.hash = '#/rezepte'; };
A.print = () => window.print();
A.reload = () => location.reload();
A['dlg-close'] = () => closeDialog();

A['plan-dialog'] = b => planDialog(!!b.dataset.extend);
A['pd-start'] = b => { document.querySelectorAll('#pd-starts .chip').forEach(c => c.setAttribute('aria-pressed', c === b)); document.getElementById('pd-date').value = b.dataset.v; pdNote(); };
A['pd-weeks'] = b => { document.querySelectorAll('#pd-weeks .chip').forEach(c => c.setAttribute('aria-pressed', c === b)); pdNote(); };
A['pd-go'] = async b => {
  const s = document.getElementById('pd-date').value;
  const w = +(document.querySelector('#pd-weeks [aria-pressed="true"]') || {dataset: {v: 4}}).dataset.v;
  if (!s) return;
  b.disabled = true; b.textContent = 'Plane …';
  try { await generate(s, w); closeDialog(); ui.wizard = null; ui.planMode = 'woche'; ui.planWeek = iso(mondayOf(parseD(s))); if (route.name !== 'plan') { route = {name: 'plan', arg: null, q: {day: s}}; location.hash = '#/plan?day=' + s; } else { route.q = {day: s}; render(); } }
  catch (e) { b.disabled = false; b.textContent = 'Plan erstellen'; }
};
A['plan-generate-week'] = async b => {
  const mon = parseD(ui.planWeek), next = iso(addDays(mon, 7));
  const start = ui.planWeek < todayS() ? todayS() : ui.planWeek;   // mitten in der Woche: nur die restlichen Tage
  if (start >= next) { toast('Diese Woche ist schon vorbei.', true); return; }
  if (PLAN.rows.some(r => r.date >= start && r.date < next && !r.cooked) && !(await confirmDialog('Woche neu mischen?', 'Alle noch nicht gekochten Gerichte dieser Woche werden neu ausgewählt.', 'Neu mischen'))) return;
  b.disabled = true;
  await quiet(generate(start, 1, Math.round((parseD(next) - parseD(start)) / 864e5)));
  render({top: false});
};
A['plan-mode'] = b => { ui.planMode = b.dataset.v; if (b.dataset.v === 'monat') { const w = parseD(ui.planWeek); ui.planMonth = iso(new Date(w.getFullYear(), w.getMonth(), 1)); } render({top: false}); };
A['plan-week'] = b => { ui.planWeek = iso(addDays(parseD(ui.planWeek), 7 * +b.dataset.v)); render({top: false}); };
A['plan-month'] = b => { const m = parseD(ui.planMonth); ui.planMonth = iso(new Date(m.getFullYear(), m.getMonth() + +b.dataset.v, 1)); render({top: false}); };
A['month-day'] = b => { ui.planMode = 'woche'; ui.planWeek = iso(mondayOf(parseD(b.dataset.v))); route.q = {day: b.dataset.v}; ui.open.clear(); render({top: false}); };
A.swap = async b => { await act(() => api('POST', 'plan/swap', {date: b.dataset.d, slot: b.dataset.s})); ui.open.add(b.dataset.d + '|' + b.dataset.s); await reloadPlan(); SHOP = null; repaint(); };
A.skip = async b => { await act(() => api('POST', 'plan/skip', {date: b.dataset.d, slot: b.dataset.s}), 'Ausgelassen.'); await reloadPlan(); SHOP = null; repaint(); };
A.pick = b => pickDialog(b.dataset.d, b.dataset.s);
A['pick-set'] = async b => { await act(() => api('POST', 'plan/set', {date: b.dataset.d, slot: b.dataset.s, recipe_id: b.dataset.rid}), 'Eingeplant.'); closeDialog(); await reloadPlan(); SHOP = null; repaint(); };
A['cook-toggle'] = async b => {
  const row = rowAt(b.dataset.d, b.dataset.s);
  const undo = !!(row && row.cooked);
  const res = await act(() => api('POST', 'plan/cook', {date: b.dataset.d, slot: b.dataset.s, undo}), undo ? 'Rückgängig gemacht.' : 'Gekocht! Zutaten wurden aus dem Vorrat abgebucht.');
  if (res.fridge) P().fridge = res.fridge;
  await reloadPlan(); SHOP = null; quiet(refreshState()); repaint();
};
A['plan-recipe'] = b => planRecipeDialog(b.dataset.v);
A['pr-slot'] = b => document.querySelectorAll('#pr-slot button').forEach(x => x.setAttribute('aria-pressed', x === b));
A['pr-go'] = async b => {
  const d = document.getElementById('pr-date').value;
  const s = (document.querySelector('#pr-slot [aria-pressed="true"]') || {dataset: {}}).dataset.v;
  if (!d || !s) return;
  await act(() => api('POST', 'plan/set', {date: d, slot: s, recipe_id: b.dataset.v}), `Eingeplant für ${DS[wd(parseD(d))]} ${dshort(parseD(d))}.`);
  closeDialog(); PLAN.from = null; SHOP = null;
};

A['shop-week'] = async b => { ui.shopWeek = iso(addDays(parseD(ui.shopWeek), 7 * +b.dataset.v)); await render({top: false}); };
A['shop-store'] = async b => { applyState(await act(() => api('PUT', 'profile', {store: b.dataset.v}))); setShop(await api('GET', 'shopping?week=' + ui.shopWeek)); repaint(); };
A['shop-finish'] = async () => {
  const res = await act(() => api('POST', 'shopping/finish', {week: ui.shopWeek}));
  await refreshState();
  toast(`${plural(res.moved.length, 'Artikel liegt', 'Artikel liegen')} jetzt im Vorrat.`);
  location.hash = '#/vorrat';
};
A['custom-del'] = async b => { await act(() => api('DELETE', 'shopping/custom/' + b.dataset.v)); SHOP.custom = SHOP.custom.filter(x => String(x.id) !== b.dataset.v); setShop(SHOP); repaint(); };
A['shop-share'] = async () => {
  const text = shopText();
  try { if (navigator.share) { await navigator.share({title: 'Einkaufsliste', text}); return; } } catch (e) { if (e.name === 'AbortError') return; }
  try { await navigator.clipboard.writeText(text); toast('Liste in die Zwischenablage kopiert.'); }
  catch (e) { openDialog('Einkaufsliste', `<textarea class="in" rows="14" readonly>${esc(text)}</textarea>`, '<button class="btn ghost" data-act="dlg-close">Schließen</button>'); }
};
A.send = async b => {
  if (b.dataset.unverified) { toast(`Bitte bestätige zuerst deine ${b.dataset.ch === 'email' ? 'E-Mail-Adresse' : 'WhatsApp-Nummer'} im Profil.`, true); location.hash = '#/profil'; return; }
  b.disabled = true;
  try { await act(() => api('POST', 'send', {kind: b.dataset.kind, channel: b.dataset.ch, week: b.dataset.week || todayS()}), b.dataset.ch === 'email' ? 'E-Mail ist unterwegs.' : 'WhatsApp-Nachricht ist unterwegs.'); ui.sendLog = null; }
  finally { b.disabled = false; }
};

A['f-step'] = b => { const g = INGS[b.dataset.v]; const cur = P().fridge[b.dataset.v] || 0; return setFridge(b.dataset.v, Math.max(0, cur + fstep(g) * +b.dataset.dir)); };
A['f-del'] = b => setFridge(b.dataset.v, 0);
A.pantry = async b => { const p = P().pantry.slice(); const i = p.indexOf(b.dataset.v); i < 0 ? p.push(b.dataset.v) : p.splice(i, 1); applyState(await act(() => api('PUT', 'profile', {pantry: p}))); SHOP = null; repaint(); };

A.rfilter = b => { ui.rFilter = b.dataset.v; repaint(); };
A.rcat = b => { ui.rCat = b.dataset.v; repaint(); };
A.fav = async b => { const on = !P().favorites.includes(b.dataset.v); const r = await act(() => api('POST', 'recipes/rate', {id: b.dataset.v, favorites: on}), on ? 'Als Favorit gemerkt – kommt öfter in den Plan.' : 'Aus den Favoriten entfernt.'); P().favorites = r.favorites; P().hidden = r.hidden; repaint(); };
A.hide = async b => { const on = !P().hidden.includes(b.dataset.v); const r = await act(() => api('POST', 'recipes/rate', {id: b.dataset.v, hidden: on}), on ? 'Wird nicht mehr vorgeschlagen.' : 'Wird wieder vorgeschlagen.'); P().favorites = r.favorites; P().hidden = r.hidden; await refreshState(); repaint(); };
A.portions = b => { const id = b.dataset.v; const r = RBY[id]; const row = route.q.d ? rowAt(route.q.d, route.q.s) : null; const cur = ui.portions[id] || (row ? (row.cook_portions || row.portions) : P().persons); ui.portions[id] = Math.max(1, Math.min(20, cur + +b.dataset.dir)); repaint(); return r; };

A['cook-open'] = b => openCook(b.dataset.rid, b.dataset.f, b.dataset.d ? {d: b.dataset.d, s: b.dataset.s} : null);
A['cook-close'] = () => closeCook();
A['cook-next'] = () => { if (!COOK) return; COOK.step = Math.min(COOK.r.st.length + 1, COOK.step + 1); drawCook(); };
A['cook-prev'] = () => { if (!COOK) return; COOK.step = Math.max(0, COOK.step - 1); drawCook(); };
A['cook-f'] = b => { COOK.f = Math.max(1, Math.min(20, COOK.f + +b.dataset.dir)); drawCook(); };
A['cook-ing'] = b => { if (b.checked) COOK.checked.add(b.dataset.v); else COOK.checked.delete(b.dataset.v); };
A['cook-finish'] = async () => {
  const {d, s} = COOK.slot;
  const res = await act(() => api('POST', 'plan/cook', {date: d, slot: s, undo: false}), 'Gekocht! Zutaten wurden aus dem Vorrat abgebucht.');
  if (res.fridge) P().fridge = res.fridge;
  closeCook(); await reloadPlan(); SHOP = null; quiet(refreshState()); render({top: false});
};
A['timer-start'] = b => { startTimer(b.dataset.rid, b.dataset.i, +b.dataset.sec); };
A['timer-pause'] = b => { const t = TIMERS[b.dataset.v]; if (!t) return; t.left = remaining(t); t.running = false; refreshTimersUI(); };
A['timer-resume'] = b => { const t = TIMERS[b.dataset.v]; if (!t) return; t.running = true; t.endAt = Date.now() + t.left * 1000; refreshTimersUI(); };
A['timer-add'] = b => { const t = TIMERS[b.dataset.v]; if (!t) return; t.endAt += 60000; refreshTimersUI(); };
A['timer-stop'] = b => { delete TIMERS[b.dataset.v]; refreshTimersUI(); };

// Profil
A['pw-dialog'] = () => openDialog('Passwort ändern', `<form data-form="pwchange" id="pwf"><label class="f"><span>Aktuelles Passwort</span><input class="in" id="p-old" type="password" autocomplete="current-password" required></label><label class="f"><span>Neues Passwort</span><input class="in" id="p-new" type="password" autocomplete="new-password" minlength="8" required></label><label class="f"><span>Neues Passwort wiederholen</span><input class="in" id="p-new2" type="password" autocomplete="new-password" minlength="8" required></label><p class="small muted" id="a-err" role="alert"></p></form>`, `<button class="btn ghost" data-act="dlg-close">Abbrechen</button><button class="btn primary" type="submit" form="pwf">Speichern</button>`);
A['contact-edit'] = b => { ui.contact[b.dataset.v] = {editing: true}; repaint(); };
A['contact-del'] = async b => { if (!(await confirmDialog('Entfernen?', 'Danach bekommst du dorthin keine Nachrichten mehr.', 'Entfernen', true))) return; await act(() => api('DELETE', 'contact/' + b.dataset.v), 'Entfernt.'); ui.contact[b.dataset.v] = {}; await refreshState(); repaint(); };
A['notify-save'] = async () => {
  const get = id => document.getElementById(id);
  const chs = kind => [...document.querySelectorAll(`[data-notify-ch="${kind}"]:checked`)].map(x => x.value);
  const notify = {shopping: {enabled: get('n-shop').checked, weekday: +get('n-shop-day').value, time: get('n-shop-time').value || '09:00', channels: chs('shopping')},
    daily: {enabled: get('n-daily').checked, time: get('n-daily-time').value || '16:00', channels: chs('daily')}};
  if ((notify.shopping.enabled && !notify.shopping.channels.length) || (notify.daily.enabled && !notify.daily.channels.length)) { toast('Bitte wähle mindestens einen Kanal (bestätigte E-Mail oder WhatsApp).', true); return; }
  applyState(await act(() => api('PUT', 'profile', {notify}), 'Gespeichert.'));
  repaint();
};
A['delete-account'] = () => openDialog('Konto löschen', `<p>Das löscht dein Konto mit allen Plänen, Einkaufslisten und deinem Vorrat. Das lässt sich nicht rückgängig machen.</p><form data-form="delacc" id="delf"><label class="f"><span>Zur Bestätigung dein Passwort</span><input class="in" id="del-pw" type="password" autocomplete="current-password" required></label></form>`, `<button class="btn ghost" data-act="dlg-close">Abbrechen</button><button class="btn danger" type="submit" form="delf">Endgültig löschen</button>`);

// Verwaltung
A['admin-reg'] = async b => { ui.admin.cfg = await act(() => api('PUT', 'admin/config', {registration: b.dataset.v}), 'Gespeichert.'); repaint(); };
A['admin-invite'] = async () => { const r = await act(() => api('POST', 'admin/invites', {days: 7})); ui.admin.invite = r.code; repaint(); };
A['admin-health'] = async () => {
  const el = document.getElementById('wa-health'); el.textContent = 'prüfe …';
  try { const r = await api('GET', 'admin/gateway-health'); el.textContent = r.ready ? '✅ Gateway verbunden' : r.success ? '⚠️ Gateway läuft, WhatsApp aber nicht verbunden (QR-Code scannen?)' : '❌ nicht erreichbar: ' + (r.error || ''); }
  catch (e) { el.textContent = '❌ ' + e.message; }
};

// Assistent
A['w-toggle'] = b => { const a = ui.wizard.d[b.dataset.key]; const i = a.indexOf(b.dataset.v); i < 0 ? a.push(b.dataset.v) : a.splice(i, 1); repaint(); };
A['w-set'] = b => { ui.wizard.d[b.dataset.key] = b.dataset.v; repaint(); };
A['w-persons'] = b => { const d = ui.wizard.d; d.persons = Math.max(1, Math.min(12, d.persons + +b.dataset.dir)); repaint(); };
A['w-day'] = b => { const d = ui.wizard.d, v = +b.dataset.v, i = d.days.indexOf(v); i < 0 ? d.days.push(v) : d.days.splice(i, 1); d.days.sort(); repaint(); };
A['w-kcal'] = b => { ui.wizard.d.kcal = +b.dataset.v; repaint(); };
A['w-fridge'] = b => { const d = ui.wizard.d, g = INGS[b.dataset.v]; if ((d.fridge[g.id] || 0) > 0) delete d.fridge[g.id]; else d.fridge[g.id] = g.pack; repaint(); };
A['w-open'] = b => { ui.wizard.d = JSON.parse(JSON.stringify(P())); ui.wizard.step = +b.dataset.v; paint(); };
A['w-overview'] = () => { ui.wizard.step = -1; ui.wizard.d = JSON.parse(JSON.stringify(P())); paint(); };
A['w-back'] = () => { ui.wizard.step = Math.max(0, ui.wizard.step - 1); paint(); };
A['w-next'] = async b => {
  const W = ui.wizard;
  b.disabled = true;
  try { await act(() => saveWizard()); } catch (e) { b.disabled = false; return; }
  if (W.mode === 'edit') { W.step = -1; W.d = JSON.parse(JSON.stringify(P())); toast('Gespeichert. Neu planen, damit es im Plan wirkt.'); paint(); return; }
  W.step++; W.d = JSON.parse(JSON.stringify(P())); paint();
};
A['w-weeks'] = b => { ui.wizard.weeks = +b.dataset.v; ui.wizard.start = document.getElementById('w-start').value || ui.wizard.start; repaint(); };
A['w-finish'] = async b => {
  const s = document.getElementById('w-start').value;
  if (!s) return;
  b.disabled = true; b.textContent = 'Plane …';
  try { await generate(s, ui.wizard.weeks); } catch (e) { b.disabled = false; b.textContent = 'Plan erstellen'; return; }
  ui.wizard = null; ui.planWeek = iso(mondayOf(parseD(s)));
  route = {name: 'heute', arg: null, q: {}};
  if (location.hash === '#/heute') render(); else location.hash = '#/heute';
};

/* ---------- Eingaben & Formulare ---------- */
document.addEventListener('input', e => {
  const t = e.target;
  if (t.id === 'rsearch') { ui.rQuery = t.value; const l = document.getElementById('rlist'); if (l) l.innerHTML = recipeListHTML(); return; }
  if (t.dataset.input === 'budget') { ui.wizard.d.budget = +t.value; document.getElementById('bval').textContent = t.value + ' €'; document.getElementById('bper').textContent = perServing(ui.wizard.d); }
  if (t.dataset.input === 'kcal') { ui.wizard.d.kcal = +t.value; document.getElementById('kval').textContent = num(+t.value) + ' kcal'; }
  if (t.id === 'pd-date') { document.querySelectorAll('#pd-starts .chip').forEach(c => c.setAttribute('aria-pressed', c.dataset.v === t.value)); pdNote(); }
});
document.addEventListener('change', async e => {
  const t = e.target;
  if (t.id === 'fsel') { const g = INGS[t.value]; document.getElementById('funit').textContent = g.unit; document.getElementById('famt').value = g.pack; return; }
  if (t.dataset.check) {
    const id = t.dataset.check;
    SHOP.checked[id] = t.checked; setShop(SHOP);
    t.closest('.item').classList.toggle('done', t.checked);
    const n = SHOP.items.filter(it => SHOP.checked[it.id]).length;
    const rs = document.getElementById('rsub'); if (rs) rs.textContent = `${n} von ${SHOP.items.length} im Wagen`;
    const fb = document.getElementById('shop-finish'); if (fb) fb.disabled = !n;
    quiet(act(() => api('POST', 'shopping/check', {week: SHOP.week, item: id, checked: t.checked})));
    return;
  }
  if (t.dataset.custom) {
    const x = SHOP.custom.find(c => String(c.id) === t.dataset.custom); if (x) x.checked = t.checked ? 1 : 0;
    t.closest('.item').classList.toggle('done', t.checked);
    quiet(act(() => api('POST', 'shopping/custom/' + t.dataset.custom, {checked: t.checked})));
    return;
  }
  if (t.dataset.adminUser) {
    const id = t.dataset.adminUser, v = t.value; t.value = '';
    const x = ui.admin.users.find(u => String(u.id) === id);
    const body = {reset: {reset_password: true}, unlock: {unlock: true}, disable: {disabled: true}, enable: {disabled: false}, admin: {is_admin: true}, unadmin: {is_admin: false}}[v];
    if (v === 'delete') {
      if (!(await confirmDialog('Konto löschen?', `${x.display_name} (${x.username}) und alle Daten dieses Kontos werden gelöscht.`, 'Löschen', true))) return;
      await act(() => api('DELETE', 'admin/users/' + id), 'Konto gelöscht.');
    } else if (body) {
      if (v === 'reset' && !(await confirmDialog('Passwort zurücksetzen?', `${x.display_name} bekommt ein vorläufiges Passwort und wird überall abgemeldet.`, 'Zurücksetzen'))) return;
      const r = await act(() => api('PUT', 'admin/users/' + id, body), 'Gespeichert.');
      if (r.temp_password) ui.admin.tempPw = {user: x.username, pw: r.temp_password};
    } else return;
    await render({top: false});
  }
});
document.addEventListener('submit', async e => {
  const f = e.target, k = f.dataset.form;
  if (!k) return;
  e.preventDefault();
  const v = id => (document.getElementById(id) || {}).value || '';
  try {
    if (k === 'login' || k === 'register' || k === 'setup') return await submitAuth(k);
    if (k === 'pwforce' || k === 'pwchange') {
      const err = document.getElementById('a-err');
      if (v('p-new') !== v('p-new2')) { err.textContent = 'Die neuen Passwörter stimmen nicht überein.'; return; }
      try { await api('POST', 'account/password', {current: v('p-old'), new: v('p-new')}); }
      catch (x) { err.textContent = x.message; return; }
      toast('Passwort geändert. Andere Geräte wurden abgemeldet.');
      if (k === 'pwforce') { SES = await api('GET', 'session'); await afterLogin(); } else closeDialog();
      return;
    }
    if (k === 'custom') {
      const inp = document.getElementById('custom-in'), text = inp.value.trim();
      if (!text) return;
      const r = await act(() => api('POST', 'shopping/custom', {week: SHOP.week, text}));
      SHOP.custom.push({id: r.id, text, checked: 0}); setShop(SHOP); repaint();
      const ni = document.getElementById('custom-in'); if (ni) ni.focus();
      return;
    }
    if (k === 'fadd') { const id = v('fsel'), amt = parseFloat(String(v('famt')).replace(',', '.')); if (!(amt > 0)) return; await setFridge(id, (P().fridge[id] || 0) + amt); toast(`${INGS[id].name} im Vorrat.`); return; }
    if (k === 'dname') { await act(() => api('PUT', 'account', {display_name: v('dname').trim()}), 'Gespeichert.'); await refreshState(); repaint(); return; }
    if (k === 'contact-start') {
      const kind = f.dataset.kind;
      const r = await act(() => api('POST', 'contact/' + kind, kind === 'email' ? {email: v('contact-email').trim()} : {phone: v('contact-phone').trim()}));
      ui.contact[kind] = {sent: r.sent_to}; repaint();
      const ci = document.getElementById('code-' + kind); if (ci) ci.focus();
      toast('Code ist unterwegs.');
      return;
    }
    if (k === 'contact-verify') {
      const kind = f.dataset.kind;
      await act(() => api('POST', `contact/${kind}/verify`, {code: v('code-' + kind).trim()}), 'Bestätigt!');
      ui.contact[kind] = {}; await refreshState(); repaint(); return;
    }
    if (k === 'delacc') { await act(() => api('DELETE', 'account', {password: v('del-pw')})); closeDialog(); toast('Dein Konto wurde gelöscht.'); SES = await api('GET', 'session'); renderAuth(); return; }
    if (k === 'admin-new') {
      const r = await act(() => api('POST', 'admin/users', {username: v('an-user').trim(), display_name: v('an-name').trim(), is_admin: document.getElementById('an-admin').checked}), 'Konto angelegt.');
      ui.admin.tempPw = {user: v('an-user').trim(), pw: r.temp_password}; await render({top: false}); return;
    }
    if (k === 'admin-url') { ui.admin.cfg = await act(() => api('PUT', 'admin/config', {public_url: v('ad-url').trim()}), 'Gespeichert.'); repaint(); return; }
    if (k === 'admin-smtp') {
      const smtp = {host: v('sm-host').trim(), port: +v('sm-port') || 587, security: v('sm-sec'), username: v('sm-user').trim(), from_addr: v('sm-from').trim(), from_name: v('sm-name').trim()};
      if (v('sm-pw')) smtp.password = v('sm-pw');
      ui.admin.cfg = await act(() => api('PUT', 'admin/config', {smtp}), 'E-Mail-Einstellungen gespeichert.'); await refreshState(); repaint(); return;
    }
    if (k === 'admin-test-email') { await act(() => api('POST', 'admin/test-email', {to: v('te-to').trim()}), 'Test-E-Mail gesendet.'); return; }
    if (k === 'admin-wa') {
      ui.admin.cfg = await act(() => api('PUT', 'admin/config', {whatsapp: {enabled: document.getElementById('wa-on').checked, gateway_url: v('wa-url').trim(), country_code: v('wa-cc').trim()}}), 'WhatsApp-Einstellungen gespeichert.');
      await refreshState(); repaint(); return;
    }
    if (k === 'admin-test-wa') { await act(() => api('POST', 'admin/test-whatsapp', {phone: v('tw-phone').trim()}), 'Test-Nachricht gesendet.'); return; }
  } catch (err) { if (!(err instanceof ApiErr)) { console.error(err); toast(String(err.message || err), true); } }
});

/* ---------- Start ---------- */
(async function boot() {
  try { SES = await api('GET', 'session'); }
  catch (e) { app.innerHTML = `<div class="auth"><div class="card"><h1>Keine Verbindung</h1><p>${esc(e.message)}</p><button class="btn primary" data-act="reload">Neu laden</button></div></div>`; return; }
  if (!SES.authenticated) { renderAuth(); return; }
  await afterLogin();
})();
