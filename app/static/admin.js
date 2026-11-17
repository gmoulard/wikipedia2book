/*
  This file is part of Wikipedia2Book
  <https://github.com/gmoulard/wikipedia2book>.
  Copyright (c) 2026 Guillaume Moulard.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, version 3.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

const ADMIN_REFRESH_MS = 30000;
const ADMIN_ERRORS = {
  denied: 'admin.errorDenied',
  state: 'admin.errorState',
  oauth: 'admin.errorOauth',
  forbidden: 'admin.errorForbidden',
  not_configured: 'admin.notConfigured',
};
const ADMIN_STATUSES = ['done', 'error', 'aborted', 'running'];
let adminTimer = null;

function adminById(id) { return document.getElementById(id); }

function formatNumber(value, options = {}) {
  return value == null ? '—' : new Intl.NumberFormat(state_i18n.lang, options).format(value);
}

function formatSeconds(value) {
  return formatNumber(value, { style: 'unit', unit: 'second', maximumFractionDigits: 1 });
}

function formatBytes(value) {
  if (value == null) return '—';
  if (value >= 1e9) return formatNumber(value / 1e9, { style: 'unit', unit: 'gigabyte', maximumFractionDigits: 2 });
  return formatNumber(value / 1e6, { style: 'unit', unit: 'megabyte', maximumFractionDigits: 1 });
}

function formatTime(iso) {
  if (!iso) return '—';
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? iso : date.toLocaleString(state_i18n.lang, { dateStyle: 'short', timeStyle: 'medium' });
}

function statusLabel(status) {
  return ADMIN_STATUSES.includes(status) ? t(`admin.status_${status}`) : status;
}

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text != null) node.textContent = String(text);
  if (className) node.className = className;
  return node;
}

function fillTiles(id, entries) {
  adminById(id).replaceChildren(...entries.map(([key, value]) => {
    const tile = element('div');
    tile.append(element('dt', t(key)), element('dd', value));
    return tile;
  }));
}

function fillTable(id, headers, rows, numeric = []) {
  const head = element('thead');
  const headRow = element('tr');
  headers.forEach((header) => headRow.append(element('th', header)));
  head.append(headRow);
  const body = element('tbody');
  rows.forEach((cells) => {
    const row = element('tr');
    cells.forEach((cell, index) => {
      const content = typeof cell === 'object' && cell !== null ? cell : { text: cell };
      const td = element('td', null, numeric.includes(index) ? 'number' : null);
      if (content.href) {
        const link = element('a', content.text);
        link.href = content.href;
        link.target = '_blank';
        link.rel = 'noopener';
        td.append(link);
      } else {
        td.textContent = content.text ?? '';
      }
      if (content.className) td.classList.add(content.className);
      row.append(td);
    });
    body.append(row);
  });
  adminById(id).replaceChildren(head, body);
}

function renderSummary(data) {
  const server = data.server;
  const memory = server.memory || {};
  const gates = [server.memory_gate, server.disk_gate, server.generation_gate].map((gate) => gate?.waiting_stages ?? '—');
  fillTiles('adminServer', [
    ['admin.version', `${data.version.version} · ${data.version.short || '—'}`],
    ['admin.started', formatTime(server.started)],
    ['admin.inProgress', formatNumber(server.generations_in_progress)],
    ['admin.memory', `${formatBytes(memory.used_bytes)} / ${formatBytes(memory.limit_bytes)} (${memory.used_percent == null ? '—' : formatNumber(memory.used_percent / 100, { style: 'percent', maximumFractionDigits: 1 })})`],
    ['admin.processMemory', formatBytes(memory.process_rss_bytes)],
    ['admin.disk', formatBytes(server.temporary?.free_bytes)],
    ['admin.waiting', gates.join(' / ')],
  ]);

  const usage = data.usage;
  const counts = ADMIN_STATUSES.filter((status) => usage.generations[status]).map((status) => `${statusLabel(status)} ${formatNumber(usage.generations[status])}`);
  fillTiles('adminUsage', [
    ['admin.hits24', formatNumber(usage.hits_24h)],
    ['admin.hits48', formatNumber(usage.hits_48h)],
    ['admin.generations', counts.join(' · ') || '0'],
    ['admin.items', `${formatNumber(usage.articles)} / ${formatNumber(usage.documents)}`],
  ]);

  const perf = data.performance;
  fillTiles('adminPerformance', [
    ['admin.median', formatSeconds(perf.median_s)],
    ['admin.p90', formatSeconds(perf.p90_s)],
    ['admin.max', formatSeconds(perf.max_s)],
    ['admin.perArticle', formatSeconds(perf.median_s_per_article)],
    ['admin.size', formatBytes(perf.median_size_bytes)],
    ['admin.peak', formatBytes(perf.max_peak_rss_bytes)],
    ['admin.waited', formatSeconds(perf.waited_s)],
  ]);

  const limits = server.request_limits || {};
  const settings = data.settings;
  fillTable('adminLimits', [t('admin.limit'), t('admin.value')], [
    ['article_limit', formatNumber(settings.article_limit)],
    ['downloads', formatNumber(settings.downloads)],
    ['client_concurrent', formatNumber(limits.client_concurrent)],
    ['client_per_minute', formatNumber(limits.client_per_minute)],
    ['total_concurrent', formatNumber(limits.total_concurrent)],
    ['total_per_minute', formatNumber(limits.total_per_minute)],
    ['waiting_limit', formatNumber(limits.waiting_limit)],
    ['memory_ratio', formatNumber(settings.memory_ratio)],
    ['disk_ratio', formatNumber(settings.disk_ratio)],
    ['generations_ratio', formatNumber(settings.generations_ratio)],
  ], [1]);

  const alerts = Object.entries(server.alerts || {});
  fillTable('adminAlerts', [t('admin.alerts'), t('admin.alertCount'), t('admin.alertLast')],
    alerts.length ? alerts.map(([kind, entry]) => [{ text: kind, className: 'admin-status-error' }, formatNumber(entry.count), formatTime(entry.last)]) : [[t('admin.alertsNone'), '', '']],
    [1]);

  fillTable('adminRecent', [t('admin.colJournal'), t('admin.colStarted'), t('admin.colStatus'), t('admin.colDuration'), t('admin.colArticles'), t('admin.colSize'), t('admin.colWaited'), t('admin.colPeak'), t('admin.version')],
    data.recent.map((row) => [
      { text: `#${row.id}`, href: `/api/health/generations/${row.id}` },
      formatTime(row.started),
      { text: statusLabel(row.status), className: `admin-status-${row.status}` },
      formatSeconds(row.duration_s),
      row.documents ? `${formatNumber(row.articles)} + ${formatNumber(row.documents)}` : formatNumber(row.articles),
      formatBytes(row.size_bytes),
      row.waited_s ? formatSeconds(row.waited_s) : '—',
      formatBytes(row.peak_rss_bytes),
      row.version || '—',
    ]),
    [3, 4, 5, 6, 7]);

  fillTable('adminHours', [t('admin.colHour'), t('admin.colCount')],
    Object.entries(usage.hours).reverse().map(([hour, count]) => [hour.replace('T', ' ') + ':00', formatNumber(count)]),
    [1]);

  adminById('adminUpdated').textContent = t('admin.updated', { time: new Date().toLocaleTimeString(state_i18n.lang) });
}

function showMessage(text) {
  const message = adminById('adminMessage');
  message.hidden = !text;
  message.textContent = text || '';
}

function showLogin(configured) {
  clearInterval(adminTimer);
  adminById('adminBoard').hidden = true;
  adminById('adminLogout').hidden = true;
  adminById('adminUser').textContent = '';
  adminById('adminLogin').hidden = false;
  adminById('adminLoginButton').hidden = !configured;
  if (!configured) showMessage(t('admin.notConfigured'));
}

async function loadSummary() {
  let response;
  try {
    response = await fetch('/api/admin/summary', { cache: 'no-store', credentials: 'same-origin' });
  } catch (error) {
    showMessage(t('admin.loadFailed', { error: error.message }));
    return;
  }
  if (response.status === 401) {
    showLogin(true);
    return;
  }
  if (!response.ok) {
    showMessage(t('admin.loadFailed', { error: `HTTP ${response.status}` }));
    return;
  }
  showMessage('');
  renderSummary(await response.json());
}

async function startAdmin() {
  applyTranslations();
  const params = new URLSearchParams(window.location.search);
  const error = params.get('error');
  if (error) {
    showMessage(t(ADMIN_ERRORS[error] || 'admin.errorOauth'));
    window.history.replaceState(null, '', '/admin');
  }
  let session;
  try {
    session = await (await fetch('/api/admin/session', { cache: 'no-store', credentials: 'same-origin' })).json();
  } catch (failure) {
    showMessage(t('admin.loadFailed', { error: failure.message }));
    return;
  }
  if (!session.user) {
    showLogin(session.configured);
    return;
  }
  adminById('adminLogin').hidden = true;
  adminById('adminBoard').hidden = false;
  adminById('adminLogout').hidden = false;
  adminById('adminUser').textContent = t('admin.signedIn', { user: session.user });
  await loadSummary();
  adminTimer = setInterval(loadSummary, ADMIN_REFRESH_MS);
}

adminById('adminRefresh').addEventListener('click', loadSummary);
startAdmin();
