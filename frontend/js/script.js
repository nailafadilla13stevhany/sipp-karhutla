const API_BASE = 'http://127.0.0.1:5000/api';

const $ = (selector) => document.querySelector(selector);
let dashboardMap;
let riskMap;

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {'Content-Type': 'application/json', ...(options.headers || {})},
    ...options
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || data.message || 'Permintaan gagal');
  return data;
}

function initMap(elementId, zoom = 7) {
  const map = L.map(elementId).setView([-1.9, 113.9], zoom);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);
  return map;
}

function riskColor(risk) {
  return risk === 'High' ? '#e05a5a' : risk === 'Medium' ? '#e8a63a' : '#2c9b73';
}

async function loadDashboard() {
  const [dashboard, hotspots] = await Promise.all([api('/dashboard'), api('/hotspots')]);
  $('#total-hotspots').textContent = dashboard.total_hotspots;
  $('#low-risk').textContent = dashboard.low_risk;
  $('#medium-risk').textContent = dashboard.medium_risk;
  $('#high-risk').textContent = dashboard.high_risk;
  $('#total-patrols').textContent = dashboard.total_patrols;

  if (!dashboardMap) dashboardMap = initMap('dashboard-map', 6);
  else dashboardMap.eachLayer(layer => { if (layer instanceof L.Marker) dashboardMap.removeLayer(layer); });
  hotspots.forEach(item => {
    L.circleMarker([item.latitude, item.longitude], {radius: 7, color: riskColor(item.risk_level), fillColor: riskColor(item.risk_level), fillOpacity: 0.8})
      .bindPopup(`<b>${item.location_name}</b><br>Risiko: ${item.risk_level}<br>Hotspot: ${item.hotspot_count}`)
      .addTo(dashboardMap);
  });

  $('#risk-chart').innerHTML = ['Low','Medium','High'].map(risk => {
    const value = risk === 'Low' ? dashboard.low_risk : risk === 'Medium' ? dashboard.medium_risk : dashboard.high_risk;
    const height = Math.max(20, value * 18);
    return `<div class="bar-wrap"><div class="bar" style="height:${height}px;background:${riskColor(risk)}"></div><span>${risk}: ${value}</span></div>`;
  }).join('');
}

async function loadRiskMap() {
  if (!riskMap) riskMap = initMap('risk-map', 7);
  const hotspots = await api('/hotspots');
  hotspots.forEach(item => {
    L.circleMarker([item.latitude, item.longitude], {radius: 9, color: '#fff', weight: 1, fillColor: riskColor(item.risk_level), fillOpacity: 0.85})
      .bindPopup(`<b>${item.location_name}</b><br>Risiko: <b>${item.risk_level}</b><br>Kepadatan hotspot: ${item.hotspot_density_7d}<br>Hari kering: ${item.consecutive_dry_days}`)
      .addTo(riskMap);
  });
}

async function loadPatrols() {
  const patrols = await api('/patrol');
  $('#patrol-table').innerHTML = patrols.length ? patrols.map(p => `<tr><td>${p.officer_name}</td><td>${p.location}</td><td>${p.patrol_date}</td><td>${Number(p.latitude).toFixed(4)}, ${Number(p.longitude).toFixed(4)}</td><td>${p.status}</td></tr>`).join('') : '<tr><td colspan="5">Belum ada data patroli.</td></tr>';
}

async function loadRecommendations() {
  const items = await api('/recommendations');
  $('#recommendation-list').innerHTML = items.length ? items.map(item => {
    const level = item.risk_level.toLowerCase();
    return `<div class="recommendation-item ${level}"><h3>${item.location_name} — Prioritas ${item.priority}</h3><p><b>Risiko:</b> ${item.risk_level} | <b>Keyakinan:</b> ${(item.confidence * 100).toFixed(1)}%</p><p>${item.reason}</p><p><b>Status:</b> ${item.verification_status}</p></div>`;
  }).join('') : '<p>Belum ada rekomendasi.</p>';
}

async function loadReport() {
  const dashboard = await api('/dashboard');
  $('#report-summary').innerHTML = `<div><b>${dashboard.total_hotspots}</b><br>Total titik panas</div><div><b>${dashboard.high_risk}</b><br>Wilayah risiko tinggi</div><div><b>${dashboard.total_patrols}</b><br>Patroli dilakukan</div>`;
}

const viewTitles = {dashboard:'Dashboard Overview',map:'Peta Risiko Kebakaran',prediction:'Prediksi Risiko Kebakaran',patrol:'Data Patroli',recommendation:'Rekomendasi Patroli',report:'Laporan Pemantauan'};

document.querySelectorAll('.nav-item').forEach(button => button.addEventListener('click', async () => {
  document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
  document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
  button.classList.add('active');
  const name = button.dataset.view;
  $(`#${name}-view`).classList.add('active');
  $('#page-title').textContent = viewTitles[name];
  if (name === 'map') setTimeout(loadRiskMap, 50);
  if (name === 'patrol') await loadPatrols();
  if (name === 'recommendation') await loadRecommendations();
  if (name === 'report') await loadReport();
}));

$('#prediction-form').addEventListener('submit', async event => {
  event.preventEvent?.();
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = {};
  form.forEach((value, key) => payload[key] = key === 'location_name' ? value : Number(value));
  const result = $('#prediction-result');
  result.textContent = 'Memproses prediksi...';
  try {
    const data = await api('/predict', {method:'POST', body:JSON.stringify(payload)});
    const level = data.risk_level;
    result.innerHTML = `<div class="prediction-result"><div class="risk-circle ${level.toLowerCase()}">${level}</div><p>Probabilitas: ${(data.confidence * 100).toFixed(1)}%</p><p><b>Status:</b> ${data.verification_status}</p><ul class="risk-factors">${data.factors.map(factor => `<li>${factor}</li>`).join('')}</ul></div>`;
  } catch (error) { result.textContent = error.message; }
});

$('#show-patrol-form').addEventListener('click', () => $('#patrol-form').classList.toggle('hidden'));
$('#patrol-form').addEventListener('submit', async event => {
  event.preventDefault();
  const form = new FormData(event.target);
  const payload = {};
  form.forEach((value, key) => payload[key] = ['latitude','longitude'].includes(key) ? Number(value) : value);
  try {
    await api('/patrol', {method:'POST', body:JSON.stringify(payload)});
    event.target.reset();
    $('#patrol-form').classList.add('hidden');
    await loadPatrols();
    await loadDashboard();
  } catch (error) { alert(error.message); }
});

$('#export-report').addEventListener('click', async () => {
  const [dashboard, patrols] = await Promise.all([api('/dashboard'), api('/patrol')]);
  const rows = [['Metrik','Nilai'],['Total Titik Panas',dashboard.total_hotspots],['Risiko Rendah',dashboard.low_risk],['Risiko Sedang',dashboard.medium_risk],['Risiko Tinggi',dashboard.high_risk],['Total Patroli',dashboard.total_patrols],...patrols.map(p => [`Patroli ${p.location}`,p.status])];
  const csv = rows.map(row => row.map(value => `"${String(value).replaceAll('"','""')}"`).join(',')).join('\n');
  const url = URL.createObjectURL(new Blob([csv], {type:'text/csv'}));
  const link = document.createElement('a');
  link.href = url; link.download = 'laporan-sipp-karhutla.csv'; link.click();
  URL.revokeObjectURL(url);
});

loadDashboard().catch(error => console.error(error));
