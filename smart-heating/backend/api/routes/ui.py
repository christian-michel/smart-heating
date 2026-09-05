from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def ui():
    return """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Smart Heating</title>
<style>
  :root {
    --bg: #F6F4F0;
    --card: #FFFFFF;
    --border: #ECE8E1;
    --accent: #E1553D;
    --accent-dark: #C1442E;
    --accent-soft: #FBE4DE;
    --track: #ECE7DF;
    --text: #211E1B;
    --text-soft: #8A8478;
    --text-faint: #B3ADA1;
    --green: #2F9E5B;
    --green-soft: #E3F3E8;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }
  .app { max-width: 460px; margin: 0 auto; padding-bottom: 40px; }
  header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 18px 10px;
  }
  .brand { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 17px; }
  .brand .icon {
    width: 34px; height: 34px; border-radius: 10px; background: var(--accent-soft);
    display: flex; align-items: center; justify-content: center; font-size: 18px;
  }
  .pill {
    font-size: 12px; font-weight: 700; padding: 6px 12px; border-radius: 999px;
    display: inline-flex; align-items: center; gap: 5px;
  }
  .pill.good { background: var(--green-soft); color: #227A45; }
  .pill.warn { background: var(--accent-soft); color: var(--accent-dark); }
  .pill.neutral { background: #F1EEE8; color: var(--text-soft); }
  main { padding: 4px 16px; display: flex; flex-direction: column; gap: 14px; }
  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: 20px;
    padding: 20px;
  }
  .row { display: flex; }
  .muted { color: var(--text-soft); }
  .faint { color: var(--text-faint); }
  .small { font-size: 12px; }
  .bold { font-weight: 700; }
  input[type=password], input[type=text] {
    width: 100%; box-sizing: border-box; padding: 10px 12px; border-radius: 10px;
    border: 1px solid var(--border); font-size: 14px;
  }
  button {
    font-family: inherit; cursor: pointer; border: none;
  }
  .btn-primary {
    background: var(--accent); color: #fff; font-weight: 700; border-radius: 12px;
    padding: 12px 0; width: 100%;
  }
  .btn-secondary {
    background: #fff; color: var(--text); font-weight: 700; border-radius: 12px;
    padding: 10px 0; width: 100%; border: 1px solid var(--border);
  }
  .round-btn {
    width: 46px; height: 46px; border-radius: 999px; border: 1px solid var(--border);
    background: #fff; display: flex; align-items: center; justify-content: center;
    font-size: 20px;
  }
  .two-col { display: flex; gap: 14px; }
  .two-col .card { flex: 1; }
  .three-col { display: flex; gap: 10px; }
  .three-col .card { flex: 1; text-align: center; padding: 14px; }
  .mode-btn {
    flex: 1; padding: 8px 0; border-radius: 10px; font-size: 12px; font-weight: 700;
    text-align: center; border: 1px solid var(--border); background: #fff; color: var(--text-soft);
  }
  .mode-btn.active { border-color: var(--accent); background: var(--accent-soft); color: var(--accent-dark); }
  svg { display: block; }
  #settingsCard, #systemCard { display: none; }
  .link-btn { background: none; border: none; color: var(--accent); font-weight: 700; font-size: 13px; padding: 0; }
  nav {
    position: sticky; bottom: 0; background: #fff; border-top: 1px solid var(--border);
    display: flex; padding: 10px 8px 16px;
  }
  nav button {
    flex: 1; background: none; display: flex; flex-direction: column; align-items: center;
    gap: 2px; color: var(--text-faint); font-size: 11px; font-weight: 700; padding: 4px;
  }
  nav button.active { color: var(--accent); }
  .hidden { display: none !important; }
</style>
</head>
<body>
<div class="app">

  <header>
    <div class="brand"><span class="icon">🔥</span> Smart Heating</div>
    <span id="connBadge" class="pill neutral">Connexion…</span>
  </header>

  <main>

    <div id="tokenCard" class="card">
      <p class="bold" style="margin:0 0 4px;">Token API</p>
      <p class="small muted" style="margin:0 0 14px;">
        Nécessaire pour piloter le chauffage. Trouvable dans <code>.env</code> (<code>API_TOKEN</code>) sur le Raspberry Pi.
      </p>
      <input id="tokenInput" type="password" placeholder="Token">
      <button class="btn-primary" style="margin-top:12px" onclick="saveToken()">Enregistrer</button>
      <p class="small faint" style="margin-top:10px">
        Stocké uniquement dans ce navigateur (localStorage), jamais envoyé ailleurs qu'à cette API.
      </p>
    </div>

    <div id="dashboard" class="hidden">

      <div class="card">
        <div class="row">
          <div style="flex:1; text-align:center">
            <div class="small muted">Min session</div>
            <div class="bold" id="minTemp">--</div>
          </div>
          <div style="flex:2; text-align:center">
            <div class="small muted">Température actuelle</div>
            <div style="font-size:44px;font-weight:700;line-height:1;margin:2px 0" id="curTemp">--<span style="font-size:20px;color:var(--text-soft)">°C</span></div>
            <div class="small muted">Sonde DS18B20</div>
          </div>
          <div style="flex:1; text-align:center">
            <div class="small muted">Max session</div>
            <div class="bold" id="maxTemp">--</div>
          </div>
        </div>
      </div>

      <div class="card" style="display:flex;flex-direction:column;align-items:center;margin-top:14px">
        <svg id="gauge" viewBox="0 0 300 300" width="260" height="260"></svg>
        <div style="display:flex;gap:16px;margin-top:8px">
          <button class="round-btn" onclick="stepTarget(-0.5)">−</button>
          <button class="round-btn" onclick="stepTarget(0.5)">+</button>
        </div>
        <div style="margin-top:12px"><span class="pill neutral">Zone recommandée : 19°C – 22°C</span></div>
      </div>

      <div class="two-col" style="margin-top:14px">
        <div class="card">
          <div class="small muted bold">Chauffage</div>
          <div id="heatingState" style="margin-top:10px;font-size:20px;font-weight:700">--</div>
          <div id="heatingSub" class="small muted">--</div>
        </div>
        <div class="card">
          <div class="small muted bold">Mode</div>
          <div style="display:flex;gap:6px;margin-top:10px">
            <button id="btnAuto" class="mode-btn" onclick="setManual(false)">Auto</button>
            <button id="btnManual" class="mode-btn" onclick="setManual(true)">Manuel</button>
          </div>
        </div>
      </div>

      <div id="manualCard" class="card hidden" style="margin-top:14px">
        <div class="small muted bold">Commande manuelle</div>
        <div style="display:flex;gap:10px;margin-top:10px">
          <button class="btn-primary" onclick="forceHeating(true)">Marche</button>
          <button class="btn-secondary" onclick="forceHeating(false)">Arrêt</button>
        </div>
      </div>

      <div class="card" style="margin-top:14px">
        <canvas id="chart" width="360" height="150" style="width:100%;height:150px"></canvas>
      </div>

      <div class="three-col" style="margin-top:14px">
        <div class="card"><div class="small muted">Dernier relevé</div><div class="small bold" id="lastUpdate">--</div></div>
        <div class="card"><div class="small muted">Tolérance</div><div class="small bold">± 0.5°C</div></div>
        <div class="card"><div class="small muted">Anti-cycle</div><div class="small bold">60s</div></div>
      </div>

      <div id="actionMsg" class="card hidden" style="margin-top:14px;background:#FFF6E9;border:none">
        <p class="small" style="margin:0;color:#8A5A1E" id="actionMsgText"></p>
      </div>

      <div style="margin-top:14px;text-align:center">
        <button class="link-btn" onclick="toggleAdvanced()">Système &amp; infos ▾</button>
      </div>

      <div id="systemCard" class="card" style="margin-top:14px">
        <p class="bold" style="margin:0 0 10px">Système</p>
        <div id="sysRows"></div>
        <p class="bold" style="margin:16px 0 6px">Informations matérielles</p>
        <div class="small" style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid var(--border)"><span class="muted">Modèle</span><span class="bold">Raspberry Pi 3</span></div>
        <div class="small" style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid var(--border)"><span class="muted">Sonde</span><span class="bold">DS18B20 (GPIO 4)</span></div>
        <div class="small" style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid var(--border)"><span class="muted">Relais</span><span class="bold">GPIO 17</span></div>
        <div class="small" style="display:flex;justify-content:space-between;padding:6px 0;border-top:1px solid var(--border)"><span class="muted">Bouton manuel</span><span class="bold">GPIO 27</span></div>
        <button class="link-btn" style="margin-top:14px" onclick="forgetToken()">Changer de token</button>
      </div>

    </div>

  </main>
</div>

<script>
const MIN_T = 5, MAX_T = 30, REC_MIN = 19, REC_MAX = 22;
const START_A = 125, SWEEP_A = 310;
let status = null;
let history = [];
let connError = null;
let actionErrorTimer = null;

function token() { return localStorage.getItem('sh_token') || ''; }

function saveToken() {
  const v = document.getElementById('tokenInput').value.trim();
  if (!v) return;
  localStorage.setItem('sh_token', v);
  document.getElementById('tokenCard').classList.add('hidden');
  document.getElementById('dashboard').classList.remove('hidden');
  poll();
}

function forgetToken() {
  localStorage.removeItem('sh_token');
  location.reload();
}

async function api(path, opts) {
  opts = opts || {};
  opts.headers = Object.assign({'Authorization': 'Bearer ' + token()}, opts.headers || {});
  const res = await fetch(path, opts);
  let data = null;
  try { data = await res.json(); } catch (e) {}
  return { ok: res.ok, data: data };
}

function fmt(v) { return (v === null || v === undefined || isNaN(v)) ? '--' : v.toFixed(1); }

function polar(cx, cy, r, angleDeg) {
  const a = angleDeg * Math.PI / 180;
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
}
function arc(cx, cy, r, a0, a1) {
  const s = polar(cx, cy, r, a0), e = polar(cx, cy, r, a1);
  const large = (a1 - a0) > 180 ? 1 : 0;
  return `M ${s.x.toFixed(1)} ${s.y.toFixed(1)} A ${r} ${r} 0 ${large} 1 ${e.x.toFixed(1)} ${e.y.toFixed(1)}`;
}
function valueToAngle(v) {
  const c = Math.min(MAX_T, Math.max(MIN_T, v));
  return START_A + (c - MIN_T) / (MAX_T - MIN_T) * SWEEP_A;
}

function drawGauge(value) {
  const cx = 150, cy = 150, r = 112;
  const angle = valueToAngle(value == null ? MIN_T : value);
  const handle = polar(cx, cy, r, angle);
  const recA0 = valueToAngle(REC_MIN), recA1 = valueToAngle(REC_MAX);
  document.getElementById('gauge').innerHTML = `
    <path d="${arc(cx, cy, r, START_A, START_A + SWEEP_A)}" fill="none" stroke="var(--track)" stroke-width="14" stroke-linecap="round"/>
    <path d="${arc(cx, cy, r, recA0, recA1)}" fill="none" stroke="var(--accent-soft)" stroke-width="14"/>
    <path d="${arc(cx, cy, r, START_A, angle)}" fill="none" stroke="var(--accent)" stroke-width="14" stroke-linecap="round"/>
    <circle cx="${handle.x.toFixed(1)}" cy="${handle.y.toFixed(1)}" r="15" fill="#fff" stroke="var(--accent)" stroke-width="3"/>
    <text x="150" y="128" text-anchor="middle" font-size="15" fill="var(--text-soft)">Consigne</text>
    <text x="150" y="178" text-anchor="middle" font-size="52" font-weight="700" fill="var(--text)">${fmt(value)}</text>
    <text x="222" y="178" font-size="20" fill="var(--text-soft)">°C</text>
  `;
}

function drawChart() {
  const canvas = document.getElementById('chart');
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  if (history.length < 2) {
    ctx.fillStyle = '#8A8478'; ctx.font = '12px sans-serif';
    ctx.fillText('La courbe se construit pendant cette session…', 10, h / 2);
    return;
  }
  const temps = history.map(p => p.temp).filter(t => typeof t === 'number');
  const min = Math.min(...temps) - 1, max = Math.max(...temps) + 1;
  const x = i => (i / (history.length - 1)) * (w - 10) + 5;
  const y = t => h - 10 - ((t - min) / (max - min || 1)) * (h - 20);
  ctx.strokeStyle = '#ECE8E1';
  for (let i = 0; i < 4; i++) {
    const yy = 10 + i * (h - 20) / 3;
    ctx.beginPath(); ctx.moveTo(0, yy); ctx.lineTo(w, yy); ctx.stroke();
  }
  ctx.strokeStyle = '#E1553D'; ctx.lineWidth = 2; ctx.beginPath();
  history.forEach((p, i) => { const px = x(i), py = y(p.temp); i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py); });
  ctx.stroke();
  ctx.strokeStyle = '#B3ADA1'; ctx.lineWidth = 1.5; ctx.setLineDash([4, 3]); ctx.beginPath();
  history.forEach((p, i) => { const px = x(i), py = y(p.target); i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py); });
  ctx.stroke(); ctx.setLineDash([]);
}

function showActionMsg(msg) {
  const el = document.getElementById('actionMsg');
  document.getElementById('actionMsgText').textContent = msg;
  el.classList.remove('hidden');
  clearTimeout(actionErrorTimer);
  actionErrorTimer = setTimeout(() => el.classList.add('hidden'), 6000);
}

function render() {
  const badge = document.getElementById('connBadge');
  if (connError) { badge.className = 'pill warn'; badge.textContent = 'Hors ligne'; }
  else if (!status) { badge.className = 'pill neutral'; badge.textContent = 'Connexion…'; }
  else if (status.running === false) { badge.className = 'pill warn'; badge.textContent = 'Système arrêté'; }
  else { badge.className = 'pill good'; badge.textContent = 'Connecté'; }

  if (!status) return;

  document.getElementById('curTemp').innerHTML = fmt(status.temperature) + '<span style="font-size:20px;color:var(--text-soft)">°C</span>';
  const temps = history.map(p => p.temp).filter(t => typeof t === 'number');
  document.getElementById('minTemp').textContent = temps.length ? fmt(Math.min(...temps)) + '°C' : '--';
  document.getElementById('maxTemp').textContent = temps.length ? fmt(Math.max(...temps)) + '°C' : '--';

  drawGauge(status.target_temperature);
  drawChart();

  document.getElementById('heatingState').textContent = status.heating ? 'ON' : 'OFF';
  document.getElementById('heatingState').style.color = status.heating ? 'var(--accent)' : 'var(--text)';
  document.getElementById('heatingSub').textContent = status.heating ? 'Chauffe en cours' : 'Inactif';

  document.getElementById('btnAuto').className = 'mode-btn' + (!status.manual_mode ? ' active' : '');
  document.getElementById('btnManual').className = 'mode-btn' + (status.manual_mode ? ' active' : '');
  document.getElementById('manualCard').className = 'card' + (status.manual_mode ? '' : ' hidden');

  document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
}

async function poll() {
  const r = await api('/status');
  if (!r.ok || !r.data) { connError = 'Connexion au serveur impossible'; render(); return; }
  connError = null;
  status = r.data;
  history.push({ t: Date.now(), temp: status.temperature, target: status.target_temperature });
  if (history.length > 120) history.shift();
  render();
}

async function stepTarget(delta) {
  if (!status) return;
  const prev = status.target_temperature;
  const next = Math.min(MAX_T, Math.max(MIN_T, Math.round((prev + delta) * 2) / 2));
  status.target_temperature = next; render();
  const r = await api('/temperature/target', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ value: next }) });
  if (!r.ok || !r.data || r.data.status !== 'ok') {
    status.target_temperature = prev; render();
    showActionMsg((r.data && r.data.detail) || 'Échec de la mise à jour de la consigne.');
  }
}

async function setManual(enabled) {
  const r = await api('/manual/' + enabled, { method: 'POST' });
  if (!r.ok || !r.data || r.data.error || typeof r.data.manual_mode !== 'boolean') {
    showActionMsg((r.data && r.data.error) || 'Échec du changement de mode.'); return;
  }
  status.manual_mode = r.data.manual_mode; render();
}

async function forceHeating(enabled) {
  const r = await api('/heating/' + enabled, { method: 'POST' });
  if (!r.ok || !r.data || r.data.error || typeof r.data.heating !== 'boolean') {
    showActionMsg((r.data && r.data.error) || 'Échec de la commande chauffage.'); return;
  }
  status.heating = r.data.heating; render();
}

function toggleAdvanced() {
  document.getElementById('systemCard').classList.toggle('hidden');
}

const sysActions = [['start', 'Démarrer'], ['stop', 'Arrêter'], ['restart', 'Redémarrer']];
function buildSystemRows() {
  const el = document.getElementById('sysRows');
  el.innerHTML = sysActions.map(([action, label]) => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-top:1px solid var(--border)">
      <span class="small">${label}</span>
      <button id="sysBtn_${action}" class="btn-secondary" style="width:auto;padding:6px 14px;font-size:12px"
        onclick="runSystemAction('${action}')">Lancer</button>
    </div>`).join('');
}

async function runSystemAction(action) {
  const btn = document.getElementById('sysBtn_' + action);
  if (btn.dataset.armed !== '1') {
    btn.dataset.armed = '1'; btn.textContent = 'Confirmer';
    setTimeout(() => { btn.dataset.armed = '0'; btn.textContent = 'Lancer'; }, 4000);
    return;
  }
  btn.dataset.armed = '0'; btn.textContent = 'Lancer';
  const r = await api('/' + action, { method: 'POST' });
  showActionMsg(r.ok ? ('Action "' + action + '" exécutée.') : 'Action impossible.');
}

buildSystemRows();

if (token()) {
  document.getElementById('tokenCard').classList.add('hidden');
  document.getElementById('dashboard').classList.remove('hidden');
  poll();
}
setInterval(() => { if (token()) poll(); }, 5000);
</script>
</body>
</html>
"""
