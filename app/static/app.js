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

const API = '';
const state = {
  project: null,
  activeView: 'sources',
  suggestionSort: 'page',
  searchTimer: null,
  toastTimer: null,
  isDirty: false,
  articleLimit: null,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function escapeHtml(value = '') {
  return String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
}

// NE PAS mettre dans un lien une adresse venue d'un livre JSON sans passer par safeUrl : ?json= charge un fichier de n'importe qui, et une adresse javascript: s'exécuterait au clic sur le site.
function safeUrl(value) {
  return /^https:\/\//i.test(String(value || '')) ? String(value) : '#';
}

const SERVER_DOWN_STATUSES = new Set([502, 503, 504]);
const PDF_AUTO_RETRIES = 2;
const SERVER_WAIT_MS = 120000;
const SERVER_POLL_MS = 3000;

class ServerCrashError extends Error {}
class RateLimitedError extends Error {}

const CLIENT_TOKEN_KEY = 'w2b-client';
let clientTokenValue = null;

function clientToken() {
  if (clientTokenValue) return clientTokenValue;
  try { clientTokenValue = localStorage.getItem(CLIENT_TOKEN_KEY); } catch { /* localStorage indisponible */ }
  if (!clientTokenValue || !/^[A-Za-z0-9-]{8,64}$/.test(clientTokenValue)) {
    clientTokenValue = window.crypto?.randomUUID ? window.crypto.randomUUID() : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
    try { localStorage.setItem(CLIENT_TOKEN_KEY, clientTokenValue); } catch { /* localStorage indisponible */ }
  }
  return clientTokenValue;
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API}${path}`, {
      ...options,
      headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers },
    });
  } catch {
    throw new ServerCrashError(t('progress.interrupted'));
  }
  if (!response.ok) {
    let message = t('common.httpError', { status: response.status });
    let detail = null;
    try { const p = await response.json(); detail = p.detail; } catch { /* not json */ }
    if (typeof detail === 'string') message = detail;
    else if (detail?.code === 'too_many_articles') message = t('export.tooManyArticles', { count: detail.count, limit: detail.limit });
    else if (detail?.code === 'request_too_large') message = t('export.requestTooLarge', { limit: Math.floor(detail.limit / 1000000) });
    else if (detail?.message) message = detail.message;
    let error;
    if (response.status === 429) {
      error = new RateLimitedError(message);
      error.retryAfter = Math.max(1, Number(response.headers.get('Retry-After')) || detail?.retry_after || 30);
    } else error = SERVER_DOWN_STATUSES.has(response.status) ? new ServerCrashError(message) : new Error(message);
    if (detail?.code) error.detail = detail;
    throw error;
  }
  if (response.status === 204) return null;
  return response;
}

async function getJson(path, options) {
  const response = await request(path, options);
  return response.json();
}

function showToast(message, isError = false) {
  const toast = $('#toast');
  toast.textContent = message;
  toast.classList.toggle('error', isError);
  toast.classList.add('visible');
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => toast.classList.remove('visible'), 3600);
}

function setSaveState(value) { $('#saveState').textContent = value; }

function lang() { return state_i18n.lang; }

function activeArticles() {
  if (!state.project) return [];
  return [...state.project.main_articles, ...state.project.discovered_articles];
}

function selectedArticles() {
  return [...activeArticles(), ...(state.project?.uploaded_documents || [])].filter((a) => a.selected);
}

// NE PAS préfixer les clés Wikipédia : elles doivent rester identiques à celles des fichiers JSON déjà exportés ; garder aligné avec Article.key dans models.py.
function articleKey(article) {
  if (article.kind) return `doc:${article.id}`;
  const prefix = article.site && article.site !== 'wikipedia' ? `${article.site}:` : '';
  return article.page_id != null
    ? `${prefix}${article.language}:${article.page_id}`
    : `${prefix}${article.language}:title:${article.title.toLowerCase()}`;
}

function articleSiteLabel(article) {
  return article.site && article.site !== 'wikipedia' ? `${article.language.toUpperCase()} · ${t(`site.${article.site}`)}` : article.language.toUpperCase();
}

function sameArticle(a, b) {
  if (a.language !== b.language || (a.site || 'wikipedia') !== (b.site || 'wikipedia')) return false;
  if (a.page_id != null && b.page_id != null) return a.page_id === b.page_id;
  return a.title.toLocaleLowerCase() === b.title.toLocaleLowerCase();
}

function normalizeProject(input) {
  const project = {
    main_articles: [], discovered_articles: [], uploaded_documents: [],
    book_title: '', book_subtitle: '', book_author: '', introduction: '', conclusion: '', cover_image: null, back_image: null,
    page_format: 'A4', custom_width_mm: 148, custom_height_mm: 210, orientation: 'portrait',
    margin_top_mm: 18, margin_bottom_mm: 18, margin_inside_mm: 18, margin_outside_mm: 16,
    margin_binding_mm: 0, article_order: [], chapters: [], toc_position: 'start', volume_breaks: [], unassigned_first: false, table_of_contents: true, page_numbers: true, ...input,
  };
  project.main_articles = [...project.main_articles, ...project.discovered_articles.filter((a) => a.selected)];
  project.discovered_articles = project.discovered_articles.filter((a) => !a.selected);
  // NE PAS garder un document importé désélectionné (fichier JSON antérieur à la 1.9.6) : il n'y a plus de case à cocher pour le reprendre, il serait invisible ; il revient dans le livre et se retire par « × ».
  project.uploaded_documents = project.uploaded_documents.map((document) => ({ ...document, selected: true }));
  // NE PAS garder une table des matières placée au milieu du livre (ancien fichier JSON) : l'étape Édition ne propose que le début ou la fin, elle revient au début.
  if (String(project.toc_position).startsWith('before:')) project.toc_position = 'start';
  return project;
}

function renderWorkspace() {
  const hasProject = Boolean(state.project);
  $('#projectWorkspace').hidden = !hasProject;
  $('#saveWorkspaceButton').disabled = !hasProject;
  $$('[data-next-step]').forEach((button) => {
    button.querySelector('.step-footer-label').textContent = t('nav.next', { step: t(`tabs.${button.dataset.nextStep}`) });
  });
  if (!hasProject) return;
  $('#sourceCount').textContent = activeArticles().length;
  $('#selectedCount').textContent = selectedArticles().length;
  $('#organizationCount').textContent = selectedArticles().length;
  renderArticles();
  renderOrganization();
  renderBookSettings();
}

function setView(view) {
  state.activeView = view;
  $$('.workflow-tab').forEach((tab) => tab.classList.toggle('active', tab.dataset.view === view));
  $$('[data-panel]').forEach((panel) => { panel.hidden = panel.dataset.panel !== view; });
}

function renderArticles() {
  const project = state.project;
  $('#mainArticleCount').textContent = project.main_articles.length;
  $('#discoveredArticleCount').textContent = project.discovered_articles.length;
  $('#mainArticles').innerHTML = project.main_articles.length
    ? project.main_articles.map((a) => articleCard(a, true, a.title === suggestionSource())).join('')
    : emptyList(t('main.emptyTitle'), t('main.emptyDesc'));

  const source = suggestionSource();
  $('#suggestionSource').hidden = !source;
  $('#suggestionSource').textContent = source ? t(state.suggestionSort === 'alpha' ? 'discovered.sourceAlpha' : 'discovered.source', { title: source }) : '';
  $('#suggestionFilters').hidden = !project.discovered_articles.length;
  const visible = visibleSuggestions();
  $('#discoveredArticles').innerHTML = visible.length
    ? visible.map((a) => articleCard(a, false)).join('')
    : emptyList(project.discovered_articles.length ? t('sources.noResultsTitle') : t('discovered.noSuggestionsTitle'),
        project.discovered_articles.length ? t('discovered.noResultsDesc') : t('discovered.noSuggestionsDesc'));
  $('#selectDiscoveredButton').hidden = visible.length === 0;
}

function suggestionSource() {
  const origins = new Set(state.project.discovered_articles.map((a) => a.origin_title));
  return origins.size === 1 ? [...origins][0] : null;
}

function visibleSuggestions() {
  const titleFilter = $('#articleFilter').value.trim().toLocaleLowerCase(lang());
  const visible = state.project.discovered_articles.filter((a) => !titleFilter || a.title.toLocaleLowerCase(lang()).includes(titleFilter));
  return state.suggestionSort === 'alpha'
    ? visible.sort((a, b) => a.title.localeCompare(b.title, lang(), { sensitivity: 'base', numeric: true }))
    : visible;
}

function addSuggestions(suggestions) {
  if (!suggestions.length) return;
  const keys = new Set(suggestions.map(articleKey));
  const added = state.project.discovered_articles.filter((a) => keys.has(articleKey(a))).map((a) => ({ ...a, selected: true }));
  queueSave({
    main_articles: [...state.project.main_articles, ...added],
    discovered_articles: state.project.discovered_articles.filter((a) => !keys.has(articleKey(a))),
  });
  renderWorkspace();
  showToast(added.length === 1 ? t('suggestion.addedToast', { title: added[0].title }) : t('suggestion.addedManyToast', { n: added.length }));
}

function dismissSuggestion(key) {
  queueSave({ discovered_articles: state.project.discovered_articles.filter((a) => articleKey(a) !== key) });
  renderWorkspace();
}

function articleCard(article, isMain, isSource = false) {
  const key = articleKey(article);
  const meta = isMain ? [articleSiteLabel(article), article.origin_title ? t('meta.from', { origin: article.origin_title }) : t('meta.main')] : [articleSiteLabel(article)];
  const summary = article.summary ? `<p class="article-summary">${escapeHtml(article.summary.slice(0, 290))}${article.summary.length > 290 ? '\u2026' : ''}</p>` : '';
  return `<article class="article-card${article.selected ? ' selected' : ''}" data-article-key="${escapeHtml(key)}">
    <div class="article-card-top">
      ${isMain ? `<input class="article-check" type="checkbox" aria-label="${article.selected ? escapeHtml(t('meta.deselect')) : escapeHtml(t('meta.select'))} ${escapeHtml(article.title)}" ${article.selected ? 'checked' : ''}>` : ''}
      <div class="article-title-wrap"><a class="article-title" href="${escapeHtml(safeUrl(article.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(article.title)}</a><div class="article-meta">${meta.map((m) => `<span>${escapeHtml(m)}</span>`).join('')}</div></div>
      ${isMain ? `<button class="text-button explore-from${isSource ? ' active' : ''}" type="button" title="${escapeHtml(t('explore.fromArticleTitle', { title: article.title }))}"><span aria-hidden="true">↗</span> ${escapeHtml(t('explore.fromArticle'))}</button><button class="remove-article" type="button" title="${escapeHtml(t('meta.removeArticle'))}" aria-label="${escapeHtml(t('meta.removeArticle'))}">\u00d7</button>` : `<button class="button button-outline add-suggestion" type="button"><span aria-hidden="true">+</span> ${escapeHtml(t('suggestion.add'))}</button><button class="remove-article dismiss-suggestion" type="button" title="${escapeHtml(t('suggestion.dismiss'))}" aria-label="${escapeHtml(t('suggestion.dismiss'))} : ${escapeHtml(article.title)}">\u00d7</button>`}
    </div>${summary}</article>`;
}

function emptyList(title, description) {
  return `<div class="empty-list"><strong>${escapeHtml(title)}</strong>${escapeHtml(description)}</div>`;
}

function orderedSelectedArticles() {
  const selected = selectedArticles();
  const byKey = new Map(selected.map((a) => [articleKey(a), a]));
  const order = state.project.article_order || [];
  const ordered = order.map((k) => byKey.get(k)).filter(Boolean);
  const seen = new Set(ordered.map(articleKey));
  selected.forEach((a) => { const k = articleKey(a); if (!seen.has(k)) ordered.push(a); });
  return ordered;
}

// NE PAS modifier sans aligner ordered_article_groups/book_slots dans book_builder.py.
function buildOrgSlots() {
  const project = state.project;
  const chapterByArticle = new Map();
  (project.chapters || []).forEach((ch) => ch.article_keys.forEach((k) => chapterByArticle.set(k, ch.id)));
  const chapters = (project.chapters || []).map((ch) => ({ ...ch, articles: [] }));
  const unassigned = [];
  orderedSelectedArticles().forEach((a) => {
    const chapter = chapters.find((c) => c.id === chapterByArticle.get(articleKey(a)));
    (chapter ? chapter.articles : unassigned).push(a);
  });
  const chapterSlots = [];
  chapters.forEach((chapter) => {
    chapterSlots.push({ type: 'chapter', chapter });
    chapter.articles.forEach((a) => chapterSlots.push({ type: 'article', article: a, chapterId: chapter.id }));
  });
  const unassignedSlots = unassigned.map((a) => ({ type: 'article', article: a, chapterId: '' }));
  if (chapters.length && unassigned.length && !project.unassigned_first) unassignedSlots.unshift({ type: 'unassigned' });
  const slots = project.unassigned_first ? [...unassignedSlots, ...chapterSlots] : [...chapterSlots, ...unassignedSlots];
  const contentSlots = [...slots];
  volumeStarts(contentSlots).forEach((start) => {
    slots.splice(slots.indexOf(contentSlots[start]), 0, { type: 'volume', anchor: slotAnchor(contentSlots[start]) });
  });
  return slots;
}

function contentOrgSlots() {
  return buildOrgSlots().filter((slot) => slot.type !== 'volume');
}

// NE PAS compter une coupure sur le premier élément ou sur un chapitre sans article : elle ne séparerait aucun article.
function volumeStarts(contentSlots) {
  const starts = new Set();
  (state.project.volume_breaks || []).forEach((position) => {
    const index = contentSlots.findIndex((slot) => slotAnchor(slot) === position.replace(/^before:/, ''));
    const slot = contentSlots[index];
    if (index > 0 && !(slot.type === 'chapter' && !slot.chapter.articles.length)) starts.add(index);
  });
  return [...starts].sort((a, b) => a - b);
}

function articleSegments() {
  const content = contentOrgSlots();
  const bounds = [0, ...volumeStarts(content), content.length];
  const segments = [];
  for (let i = 0; i < bounds.length - 1; i += 1) {
    const slots = content.slice(bounds[i], bounds[i + 1]).filter((slot) => slot.type === 'article');
    if (slots.length) segments.push(slots);
  }
  return segments;
}

function addVolumeBreak() {
  const content = contentOrgSlots();
  const starts = volumeStarts(content);
  const last = starts.length ? starts[starts.length - 1] : 0;
  const candidate = last + Math.ceil((content.length - last) / 2);
  if (candidate <= last || candidate >= content.length) { showToast(t('org.volumeTooSmall'), true); return; }
  queueSave({ volume_breaks: [...(state.project.volume_breaks || []), `before:${slotAnchor(content[candidate])}`] });
  renderOrganization();
}

function removeVolumeBreak(anchor) {
  queueSave({ volume_breaks: (state.project.volume_breaks || []).filter((position) => position !== `before:${anchor}`) });
  renderOrganization();
}

function slotAnchor(slot) {
  if (slot.type === 'unassigned') return 'chapter:';
  return slot.type === 'chapter' ? `chapter:${slot.chapter.id}` : articleKey(slot.article);
}

function renderOrganization() {
  const project = state.project;
  const articles = orderedSelectedArticles();
  $('#organizationCount').textContent = articles.length;
  const volumes = bookVolumes();
  const split = Boolean(volumes) && volumes.length > articleSegments().length;
  $('#organizationVolumes').hidden = !split;
  if (split) $('#organizationVolumes').textContent = t('org.volumesHint', { limit: state.articleLimit, count: volumes.length });

  if (!articles.length) {
    $('#organizationList').innerHTML = `<div class="org-empty">${escapeHtml(t('org.emptyListLine1'))}<br>${escapeHtml(t('org.emptyListLine2'))}</div>`;
    return;
  }

  const slots = buildOrgSlots();
  const html = slots.map((slot, idx) => {
    if (slot.type === 'volume') {
      return `<div class="org-row org-volume" draggable="true" data-slot-type="volume" data-slot-index="${idx}" data-volume-anchor="${escapeHtml(slot.anchor)}">
        <span class="drag-handle" aria-hidden="true">\u2630</span>
        <span class="volume-icon" aria-hidden="true">\u2702</span>
        <div class="org-article-text"><div class="org-article-title">${escapeHtml(t('org.volume'))}</div><div class="org-article-origin">${escapeHtml(t('org.volumeHint'))}</div></div>
        <button class="remove-article volume-remove" type="button" title="${escapeHtml(t('org.removeVolumeTitle'))}" aria-label="${escapeHtml(t('org.removeVolumeTitle'))}">×</button>
      </div>`;
    }
    if (slot.type === 'unassigned') {
      return `<div class="org-row org-chapter-row org-unassigned" data-slot-type="unassigned" data-slot-index="${idx}"><span></span><span class="chapter-letter">\u2013</span><span class="org-article-title">${escapeHtml(t('org.noChapterOption'))}</span></div>`;
    }
    if (slot.type === 'chapter') {
      const ch = slot.chapter;
      const letterIdx = (project.chapters || []).findIndex((c) => c.id === ch.id);
      const letter = String.fromCharCode(65 + letterIdx % 26);
      return `<div class="org-row org-chapter-row" draggable="true" data-slot-type="chapter" data-slot-index="${idx}" data-chapter-id="${escapeHtml(ch.id)}">
        <span class="drag-handle" aria-hidden="true">\u2630</span>
        <span class="chapter-letter">${letter}</span>
        <input class="chapter-name" aria-label="${escapeHtml(t('org.chapterNameAria'))}" value="${escapeHtml(ch.title)}" maxlength="120">
        <button class="remove-article chapter-delete" type="button" title="${escapeHtml(t('org.removeChapterTitle'))}" aria-label="${escapeHtml(t('org.removeChapterTitle'))} : ${escapeHtml(ch.title)}">×</button>
      </div>`;
    }
    // article (or document import\u00e9, int\u00e9gr\u00e9 comme un article)
    const a = slot.article;
    const k = articleKey(a);
    const isDoc = Boolean(a.kind);
    const origin = isDoc
      ? (a.kind === 'pdf' ? t('org.docPdf') : t('org.docImage'))
      : (a.origin_title ? t('org.discoveredFrom', { origin: a.origin_title }) : t('org.mainArticleOrigin', { lang: articleSiteLabel(a) }));
    const openHref = isDoc ? '#' : safeUrl(a.url);
    const openTitle = isDoc ? t('org.openDocument') : t('org.openWikipedia');
    const removeTitle = isDoc ? t('org.docRemoveTitle') : t('meta.removeArticle');
    return `<div class="org-row org-article" draggable="true" data-slot-type="article" data-slot-index="${idx}" data-article-key="${escapeHtml(k)}">
      <span class="drag-handle" aria-hidden="true">\u2630</span>
      <div class="org-article-text"><div class="org-article-title">${escapeHtml(a.title)}</div><div class="org-article-origin">${escapeHtml(origin)}</div></div>
      <button class="remove-article org-remove" type="button" title="${escapeHtml(removeTitle)}" aria-label="${escapeHtml(removeTitle)} : ${escapeHtml(a.title)}">×</button>
      <a class="article-title org-open${isDoc ? ' doc-open' : ''}" href="${escapeHtml(openHref)}" target="_blank" rel="noopener noreferrer" title="${escapeHtml(openTitle)}" aria-label="${escapeHtml(openTitle)}\u00a0: ${escapeHtml(a.title)}">\u2197</a>
    </div>`;
  }).join('');

  $('#organizationList').innerHTML = html;
  initDragDrop();
}

function initDragDrop() {
  const list = $('#organizationList');
  let dragIndex = null;

  list.querySelectorAll('.org-row').forEach((row) => {
    row.addEventListener('dragstart', (e) => {
      dragIndex = Number(row.dataset.slotIndex);
      row.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
    });
    row.addEventListener('dragend', () => row.classList.remove('dragging'));
    row.addEventListener('dragover', (e) => { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; row.classList.add('drag-over'); });
    row.addEventListener('dragleave', () => row.classList.remove('drag-over'));
    row.addEventListener('drop', (e) => {
      e.preventDefault();
      row.classList.remove('drag-over');
      const dropIndex = Number(row.dataset.slotIndex);
      if (dragIndex === null || dragIndex === dropIndex) return;
      applyDragDrop(dragIndex, dropIndex);
      dragIndex = null;
    });
  });
}

function applyDragDrop(fromIndex, toIndex) {
  const project = state.project;
  const slots = buildOrgSlots();
  const from = slots[fromIndex];
  let to = slots[toIndex];
  if (!from || !to) return;
  if (to.type === 'volume' && from.type !== 'volume') to = slots[toIndex + 1] || slots[toIndex - 1];

  if (from.type === 'volume') {
    const others = slots.filter((slot) => slot.type !== 'volume');
    const following = slots.slice(toIndex).find((slot) => others.includes(slot));
    const at = others.includes(to) ? others.indexOf(to) + (toIndex > fromIndex ? 1 : 0) : (following ? others.indexOf(following) : others.length);
    if (at <= 0 || at >= others.length) return;
    const breaks = (project.volume_breaks || []).filter((position) => position !== `before:${from.anchor}`);
    queueSave({ volume_breaks: [...new Set([...breaks, `before:${slotAnchor(others[at])}`])] });
    renderOrganization();
    return;
  }

  if (from.type === 'article' || from.type === 'chapter') {
    const sequence = slots.filter((slot) => slot.type !== 'volume');
    const target = to.type === 'volume' ? slots.slice(toIndex).find((slot) => sequence.includes(slot)) : to;
    if (target === from) return;
    const rest = sequence.filter((slot) => slot !== from);
    const into = from.type === 'article' && (target?.type === 'chapter' || target?.type === 'unassigned');
    // NE PAS insérer avant un chapitre l'article lâché sur sa ligne : il entre dans ce chapitre, en tête, qu'il vienne d'en dessous ou d'au-dessus.
    let at = target ? rest.indexOf(target) + (toIndex > fromIndex || into ? 1 : 0) : rest.length;
    // NE PAS laisser un chapitre passer sous « Sans chapitre » : ce groupe reste en fin de livre, le chapitre s'arrête juste au-dessus.
    const marker = rest.findIndex((slot) => slot.type === 'unassigned');
    if (from.type === 'chapter' && marker >= 0) at = Math.min(at, marker);
    rest.splice(at, 0, from);
    applyOrgSequence(rest);
    renderOrganization();
  }
}

// NE PAS modifier sans aligner ordered_article_groups dans book_builder.py : l'appartenance à un chapitre vient de la place de l'article sous ce chapitre, l'ordre de article_order.
function applyOrgSequence(sequence) {
  const project = state.project;
  const selected = new Set(orderedSelectedArticles().map(articleKey));
  const members = new Map();
  let current = null;
  let leading = false;
  sequence.forEach((slot) => {
    if (slot.type === 'chapter') { current = slot.chapter.id; members.set(current, []); }
    else if (slot.type === 'unassigned') current = '';
    else if (current) members.get(current).push(articleKey(slot.article));
    else if (current === null) leading = true;
  });
  const byId = new Map((project.chapters || []).map((chapter) => [chapter.id, chapter]));
  const listed = sequence.filter((slot) => slot.type === 'chapter').map((slot) => slot.chapter.id);
  const order = [...listed, ...(project.chapters || []).map((chapter) => chapter.id).filter((id) => !listed.includes(id))];
  project.chapters = order.map((id) => ({
    ...byId.get(id),
    article_keys: [...byId.get(id).article_keys.filter((key) => !selected.has(key)), ...(members.get(id) || [])],
  }));
  project.article_order = sequence.filter((slot) => slot.type === 'article').map((slot) => articleKey(slot.article));
  project.unassigned_first = leading && project.chapters.length > 0;
  queueSave({ chapters: project.chapters, article_order: project.article_order, unassigned_first: project.unassigned_first });
}

function renderBookSettings() {
  const project = state.project;
  const controls = {
    bookTitle: 'book_title', bookDescription: 'description', bookSubtitle: 'book_subtitle', bookAuthor: 'book_author',
    bookIntroduction: 'introduction', bookConclusion: 'conclusion', pageFormat: 'page_format',
    customWidth: 'custom_width_mm', customHeight: 'custom_height_mm', marginTop: 'margin_top_mm',
    marginBottom: 'margin_bottom_mm', marginInside: 'margin_inside_mm', marginOutside: 'margin_outside_mm', marginBinding: 'margin_binding_mm',
  };
  Object.entries(controls).forEach(([id, field]) => {
    const el = $(`#${id}`);
    if (document.activeElement !== el) el.value = project[field] ?? '';
  });
  const orientation = $(`input[name="orientation"][value="${project.orientation || 'portrait'}"]`);
  if (orientation) orientation.checked = true;
  $('#customDimensions').hidden = project.page_format !== 'custom';
  $('#pageNumbers').checked = project.page_numbers || false;
  const toc = project.table_of_contents === false ? 'none' : project.toc_position === 'end' ? 'end' : 'start';
  $(`input[name="tocChoice"][value="${toc}"]`).checked = true;
  $('#marginPreset').value = marginPresetOf(project);
  $('#bookTitle').placeholder = defaultBookTitle() || t('heading.namePlaceholder');
  renderBackgrounds();
}

const BACKGROUND_TYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/svg+xml'];

// NE PAS modifier ces formats sans _PAGE_SIZES de book_builder.py : la taille recommandée ne correspondrait plus à la page du PDF.
const PAGE_SIZES_MM = {
  A0: [841, 1189], A1: [594, 841], A2: [420, 594], A3: [297, 420], A4: [210, 297], A5: [148, 210],
  A6: [105, 148], Letter: [216, 279], Legal: [216, 356],
};
const BACKGROUND_DPI = 300;

function recommendedBackgroundSize(project) {
  let [width, height] = PAGE_SIZES_MM[project.page_format] || [project.custom_width_mm, project.custom_height_mm];
  if (project.orientation === 'landscape') [width, height] = [height, width];
  return { width: Math.round(width / 25.4 * BACKGROUND_DPI), height: Math.round(height / 25.4 * BACKGROUND_DPI) };
}

function backgroundWarning(image, preview, size) {
  if (!image || image.mime_type === 'image/svg+xml' || /\.svg($|\?)/i.test(image.url || '') || !preview.naturalWidth || !preview.naturalHeight) return '';
  const width = preview.naturalWidth;
  const height = preview.naturalHeight;
  const warnings = [];
  if (Math.max(size.width / width, size.height / height) > 2) warnings.push(t('edition.backgroundTooSmall', { width, height }));
  if (width !== height && size.width !== size.height && (width > height) !== (size.width > size.height)) warnings.push(t('edition.backgroundOrientation'));
  return warnings.join(' ');
}

function renderBackgrounds() {
  const size = state.project ? recommendedBackgroundSize(state.project) : null;
  document.querySelectorAll('.background-field').forEach((field) => {
    const image = state.project?.[field.dataset.background];
    const preview = field.querySelector('.background-preview');
    const warning = field.querySelector('.background-warning');
    const sizeHint = field.querySelector('.background-size');
    // NE PAS afficher la taille recommandée pour une image qui convient : elle ne s'affiche qu'avec l'alerte qui la justifie.
    const showWarning = () => {
      warning.textContent = size ? backgroundWarning(state.project?.[field.dataset.background], preview, size) : '';
      warning.hidden = !warning.textContent;
      sizeHint.textContent = warning.textContent ? t('edition.backgroundRecommended', size) : '';
    };
    preview.hidden = !image;
    preview.onload = showWarning;
    const source = image ? image.url || `data:${image.mime_type};base64,${image.data_base64}` : '';
    if (image && preview.getAttribute('src') !== source) { preview.src = source; preview.alt = image.title || ''; }
    else if (!image) preview.removeAttribute('src');
    showWarning();
    field.querySelector('.background-remove').hidden = !image;
  });
}

function readAsBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(',')[1] || '');
    reader.onerror = () => reject(new Error(t('org.docReadError')));
    reader.readAsDataURL(blob);
  });
}

async function setBackground(field, blob, title) {
  const type = (blob.type || '').split(';')[0].trim();
  if (!BACKGROUND_TYPES.includes(type)) { showToast(t('edition.backgroundTypeError', { name: title }), true); return; }
  if (blob.size > 15 * 1024 * 1024) { showToast(t('org.docTooLargeError', { name: title }), true); return; }
  const image = { title: title.slice(0, 300), mime_type: type, data_base64: await readAsBase64(blob) };
  state.project[field] = image;
  queueSave({ [field]: image });
  renderBackgrounds();
  showToast(t('edition.backgroundAddedToast'));
}

async function wikimediaFileUrl(address) {
  const match = address.hostname.match(/(^|\.)(wikimedia|wikipedia|wikisource|wikibooks|wikivoyage|wikiversity|wikiquote|wiktionary|wikinews)\.org$/);
  const page = decodeURIComponent(address.pathname).match(/^\/wiki\/[^:/]+:(.+)$/);
  if (!match || !page) return null;
  const api = new URL(`https://${address.hostname}/w/api.php`);
  Object.entries({ action: 'query', format: 'json', formatversion: '2', prop: 'imageinfo', iiprop: 'url|mime', iiurlwidth: '2000', titles: `File:${page[1]}`, origin: '*' })
    .forEach(([name, value]) => api.searchParams.set(name, value));
  const response = await fetch(api);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const info = (await response.json())?.query?.pages?.[0]?.imageinfo?.[0];
  if (!info) throw new Error(page[1]);
  return { thumb: withoutTracking(info.thumburl || info.url), original: withoutTracking(info.url), mime: info.mime, title: page[1] };
}

function withoutTracking(url) {
  const address = new URL(url);
  [...address.searchParams.keys()].filter((name) => name.startsWith('utm_')).forEach((name) => address.searchParams.delete(name));
  return address.href;
}

function addressTitle(address) {
  return (decodeURIComponent(address.pathname.split('/').pop() || '') || address.hostname).slice(0, 300);
}

function loadImage(url) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(url));
    image.src = url;
  });
}

// NE PAS remettre l'image en base64 dans le livre : seule l'adresse est enregistrée dans le JSON, le serveur la retélécharge à chaque génération.
async function setBackgroundFromUrl(field, value) {
  const text = value.trim();
  if (!text) { showToast(t('edition.backgroundUrlEmpty'), true); return; }
  if (!/^https:\/\//i.test(text)) { showToast(t('common.httpsOnly'), true); return; }
  try {
    const address = new URL(text);
    const file = await wikimediaFileUrl(address);
    const url = file ? file.thumb : address.href;
    await loadImage(url);
    state.project[field] = { title: file ? file.title.slice(0, 300) : addressTitle(address), url };
    queueSave({ [field]: state.project[field] });
    renderBackgrounds();
    showToast(t('edition.backgroundAddedToast'));
  } catch (error) {
    showToast(t('edition.backgroundUrlError', { error: error.message }), true);
  }
}

async function addDocumentFromUrl(value) {
  const text = value.trim();
  if (!text) { showToast(t('edition.backgroundUrlEmpty'), true); return; }
  if (!/^https:\/\//i.test(text)) { showToast(t('common.httpsOnly'), true); return; }
  try {
    const address = new URL(text);
    const file = await wikimediaFileUrl(address);
    const kind = (file ? file.mime === 'application/pdf' : /\.pdf$/i.test(address.pathname)) ? 'pdf' : 'image';
    const url = file ? (kind === 'pdf' ? file.original : file.thumb) : address.href;
    if (kind === 'image') await loadImage(url);
    state.project.uploaded_documents = [
      ...(state.project.uploaded_documents || []),
      { id: crypto.randomUUID(), title: file ? file.title.slice(0, 300) : addressTitle(address), kind, mime_type: '', url, selected: true },
    ];
    queueSave({ uploaded_documents: state.project.uploaded_documents });
    $('#documentUrl').value = '';
    renderWorkspace();
    showToast(t('org.docAddedToast', { n: 1 }));
  } catch (error) {
    showToast(t('org.docUrlError', { error: error.message }), true);
  }
}

function removeBackground(field) {
  state.project[field] = null;
  queueSave({ [field]: null });
  renderBackgrounds();
}

function defaultBookTitle() {
  const items = orderedSelectedArticles();
  return (items.find((item) => !item.kind) || items[0])?.title || '';
}

const MARGIN_PRESETS = {
  standard: { margin_top_mm: 18, margin_bottom_mm: 18, margin_inside_mm: 18, margin_outside_mm: 16, margin_binding_mm: 0 },
  narrow: { margin_top_mm: 10, margin_bottom_mm: 10, margin_inside_mm: 12, margin_outside_mm: 10, margin_binding_mm: 0 },
  wide: { margin_top_mm: 25, margin_bottom_mm: 25, margin_inside_mm: 25, margin_outside_mm: 22, margin_binding_mm: 0 },
  binding: { margin_top_mm: 18, margin_bottom_mm: 18, margin_inside_mm: 20, margin_outside_mm: 16, margin_binding_mm: 10 },
};

function marginPresetOf(project) {
  const match = Object.entries(MARGIN_PRESETS).find(([, margins]) => Object.entries(margins).every(([field, value]) => Number(project[field]) === value));
  return match ? match[0] : 'custom';
}

function applyMarginPreset(name) {
  const margins = MARGIN_PRESETS[name];
  if (!margins) { $('.margin-details').open = true; return; }
  queueSave({ ...margins });
  renderBookSettings();
}

function setProject(project) {
  state.project = normalizeProject(project);
  renderWorkspace();
  setView(state.activeView);
}

function queueSave(patch) {
  if (!state.project) return;
  Object.assign(state.project, patch);
  state.project.updated_at = new Date().toISOString();
  state.isDirty = true;
  setSaveState(t('save.pendingChanges'));
}

async function loadProjects() {
  $('#languageSelect').value = lang();
  applyTranslations();
  try {
    await getJson('/health');
    $('#connectionDot').classList.add('online');
    $('#connectionStatus').textContent = t('footer.apiConnected');
  } catch (error) {
    $('#connectionDot').classList.add('offline');
    $('#connectionStatus').textContent = t('footer.apiUnavailable');
    showToast(t('footer.apiUnavailableToast', { error: error.message }), true);
  }
  try {
    const v = await getJson('/api/version');
    const date = v.date ? v.date.slice(0, 10) : '';
    const parts = [v.version, v.short, date, v.author].filter(Boolean);
    $('#appVersion').textContent = `v\u00a0${parts.join('\u00a0\u00b7\u00a0')}`;
    $('#appVersion').title = v.commit;
    state.articleLimit = v.article_limit ?? null;
  } catch { /* version non critique */ }
  const now = new Date().toISOString();
  state.project = normalizeProject({ id: crypto.randomUUID(), name: t('heading.defaultName'), created_at: now, updated_at: now });
  renderWorkspace();
  setView('sources');
  const params = new URLSearchParams(window.location.search);
  const jsonUrl = params.get('json');
  if (jsonUrl) await importWorkspace(() => fetchWorkspaceText(jsonUrl));
  await addSourcesFromAddress(params);
}

// NE PAS ouvrir la fenêtre d'un sommaire sans laisser l'utilisateur choisir : ?source= ajoute comme le champ Sources, question comprise ; c'est /api/pdf/from-source qui prend le livre entier d'office.
async function addSourcesFromAddress(params) {
  const sources = params.getAll('source').map((source) => source.trim()).filter(Boolean);
  const wiki = (params.get('wiki') || '').toLowerCase();
  if (/^[a-z]{2,3}(?:-[a-z]{2,8})?$/.test(wiki)) {
    const select = $('#articleLanguage');
    if (![...select.options].some((option) => option.value === wiki)) select.add(new Option(wiki.toUpperCase(), wiki), select.querySelector(`option[value="${ALL_LANGUAGES}"]`));
    select.value = wiki;
  }
  if (sources.length === 1) {
    setQuery(sources[0]);
    await addSource(sources[0]);
  } else if (sources.length > 1) await addSourceList(sources);
}

async function fetchWorkspaceText(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.text();
}

// NE PAS écraser introduction/book_author déjà renseignés ni appeler ailleurs qu'au passage de 0 à 1 article (wasFirst capturé avant le push).
async function suggestIntroAndAuthor(article) {
  if (!state.project || (state.project.introduction && state.project.book_author)) return;
  try {
    const params = new URLSearchParams({ title: article.title, language: article.language, site: article.site || 'wikipedia' });
    const info = await getJson(`/api/articles/intro?${params}`);
    const patch = {};
    if (!state.project.introduction && info.introduction) patch.introduction = info.introduction;
    if (!state.project.book_author && info.author) patch.book_author = info.author;
    if (Object.keys(patch).length) {
      Object.assign(state.project, patch);
      queueSave(patch);
      renderBookSettings();
    }
  } catch { /* suggestion non critique */ }
}

async function withAddButton(label, task) {
  if (!state.project) return;
  const button = $('#addArticleButton');
  button.disabled = true;
  button.textContent = label;
  try { await task(); }
  catch (error) { showToast(error.message, true); }
  finally { button.disabled = false; button.innerHTML = `<span data-i18n="sources.addButton">${escapeHtml(t('sources.addButton'))}</span> <span aria-hidden="true">+</span>`; }
}

function addArticle(source) {
  return withAddButton(t('export.addingLabel'), async () => {
    await addArticleToBook(await getJson('/api/articles', { method: 'POST', body: JSON.stringify(source) }));
  });
}

function addSource(value) {
  return withAddButton(t('export.addingLabel'), async () => {
    const source = parseSourceLine(value, $('#articleLanguage').value);
    const resolved = await getJson('/api/sources/resolve', { method: 'POST', body: resolveBody(source) });
    if (resolved.kind === 'article') await addArticleToBook(resolved.article);
    else if (resolved.kind === 'book') await importBook(resolved.book, resolved.book_title, resolved.article);
    else if (resolved.kind === 'subpages') await addSubpageBook(resolved);
    else showSearchResults(resolved.results, source, t('sources.noExactPage', { query: value }));
  });
}

function isBookWikitext(lines) {
  return lines.some((line) => /^\s*(?:;|:\s*\[\[|===?[^=].*===?\s*$)|\{\{\s*:/.test(line));
}

function addBookWikitext(wikitext) {
  return withAddButton(t('export.addingLabel'), async () => {
    const resolved = await getJson('/api/books/from-wikitext', { method: 'POST', body: JSON.stringify({ wikitext, language: concreteWikiLanguage() }) });
    await importBook(resolved.book, resolved.book_title);
  });
}

function chooseSubpageBook(resolved) {
  const dialog = $('#subpageBookDialog');
  $('#subpageBookQuestion').textContent = t('sources.subpageBookQuestion', { title: resolved.article.title, site: t(`site.${resolved.article.site}`), n: resolved.book.articles.length });
  dialog.returnValue = '';
  dialog.showModal();
  return new Promise((resolve) => dialog.addEventListener('close', () => resolve(dialog.returnValue || 'cancel'), { once: true }));
}

function withSummary(book, summary) {
  return { ...book, articles: [summary, ...book.articles], unassigned_first: book.unassigned_first || book.chapters.length > 0 };
}

async function addSubpageBook(resolved) {
  const choice = await chooseSubpageBook(resolved);
  if (choice === 'page') await addArticleToBook(resolved.article);
  else if (choice === 'book') await importBook(resolved.book, resolved.book_title, resolved.article);
  else if (choice === 'book-summary') await importBook(withSummary(resolved.book, resolved.article), resolved.book_title, resolved.article);
}

async function pushArticle(article) {
  if (activeArticles().some((item) => sameArticle(item, article))) return false;
  article.selected = true;
  // NE PAS calculer wasFirst après le push : la proposition d'introduction ne doit partir qu'au premier article.
  const wasFirst = state.project.main_articles.length === 0;
  state.project.main_articles.push(article);
  queueSave({ main_articles: state.project.main_articles });
  renderWorkspace();
  if (wasFirst) await suggestIntroAndAuthor(article);
  return true;
}

async function addArticleToBook(article) {
  if (!(await pushArticle(article))) throw new Error(t('sources.alreadyInBook'));
  setQuery('');
  $('#searchResults').hidden = true;
  $('#entryHint').textContent = t('sources.addedToMain');
  showToast(t('sources.articleAdded'));
}

async function importBook(book, bookName, contents = null) {
  try {
    const newArticles = book.articles.filter((a) => !activeArticles().some((e) => sameArticle(e, a)));
    if (!newArticles.length) throw new Error(t('sources.allBookPagesAlready'));
    const wasFirst = state.project.main_articles.length === 0;
    state.project.main_articles.push(...newArticles);
    if (book.unassigned_first && !state.project.chapters.length) state.project.unassigned_first = true;
    const newKeys = new Set(newArticles.map(articleKey));
    for (const chapter of book.chapters) {
      const keys = chapter.article_keys.filter((key) => newKeys.has(key));
      if (keys.length) state.project.chapters.push({ ...chapter, article_keys: keys });
    }
    if (book.subtitle && !state.project.book_subtitle) state.project.book_subtitle = book.subtitle;
    if (bookName) {
      state.project.name = bookName;
      state.project.book_title = bookName;
    }
    queueSave({ main_articles: state.project.main_articles, chapters: state.project.chapters, unassigned_first: state.project.unassigned_first, book_subtitle: state.project.book_subtitle, name: state.project.name, book_title: state.project.book_title });
    renderWorkspace();
    if (wasFirst) await suggestIntroAndAuthor(newArticles[0]);
    setQuery('');
    const bookLink = contents
      ? `<a href="${escapeHtml(safeUrl(contents.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(contents.title)}</a>`
      : `<a href="https://fr.wikipedia.org/wiki/Aide:Livres" target="_blank" rel="noopener noreferrer">${escapeHtml(t('sources.bookLinkText'))}</a>`;
    $('#entryHint').innerHTML = contents
      ? t('sources.subpagesAddedHint', { n: newArticles.length, link: bookLink, site: escapeHtml(t(`site.${contents.site}`)) })
      : t('sources.pagesAddedHint', { n: newArticles.length, link: bookLink });
    showToast(t('sources.pagesAddedToast', { n: newArticles.length }));
  } catch (error) { throw new Error(t('sources.bookImportFailed', { error: error.message })); }
}

function setQuery(value) {
  const field = $('#articleQuery');
  field.value = value;
  field.style.height = '';
  if (value.includes('\n')) field.style.height = `${Math.min(field.scrollHeight + 2, 200)}px`;
}

function markdownLinkUrl(text) {
  const start = text.match(/^\[[^\]]*\]\(/);
  if (!start) return null;
  let depth = 1;
  for (let index = start[0].length; index < text.length; index += 1) {
    if (text[index] === '(') depth += 1;
    if (text[index] === ')') depth -= 1;
    if (depth === 0) return text.slice(start[0].length, index).trim() || null;
  }
  return null;
}

const ALL_LANGUAGES = 'all';

function searchLanguages() {
  return [...$('#articleLanguage').options].map((option) => option.value).filter((value) => value !== ALL_LANGUAGES);
}

// NE PAS envoyer « all » aux endpoints qui ne cherchent pas : pour lire une page de livre collée, il faut une seule langue, celle de l'interface si elle est dans la liste, sinon l'anglais.
function concreteWikiLanguage() {
  const value = $('#articleLanguage').value;
  if (value !== ALL_LANGUAGES) return value;
  return searchLanguages().includes(lang()) ? lang() : 'en';
}

function resolveBody(source) {
  return JSON.stringify({ input: source.input, language: source.language, site: source.site, ...(source.language === ALL_LANGUAGES ? { languages: searchLanguages() } : {}) });
}

const INTERWIKI_SITES = { w: 'wikipedia', s: 'wikisource', b: 'wikibooks', voy: 'wikivoyage', v: 'wikiversity', q: 'wikiquote', wikt: 'wiktionary', n: 'wikinews' };

function parseSourceLine(line, defaultLanguage) {
  let text = line.trim().replace(/^(?:\d+[.)]|[#*•\-–]+)\s*/, '').trim();
  if (!text) return null;
  const site = 'wikipedia';
  const markdownUrl = markdownLinkUrl(text);
  if (markdownUrl) return { label: text, input: markdownUrl, language: defaultLanguage, site };
  const wikilink = text.match(/^\[\[\s*:?([^\]|]+?)\s*(?:\|[^\]]*)?\]\]/);
  if (wikilink) text = wikilink[1];
  if (/^[a-z]+:\/\//i.test(text)) return { label: text, input: text, language: defaultLanguage, site };
  const label = text;
  let language = null;
  let project = null;
  for (let prefixed = text.match(/^([a-z][a-z-]*):(.+)$/); prefixed; prefixed = text.match(/^([a-z][a-z-]*):(.+)$/)) {
    if (!project && INTERWIKI_SITES[prefixed[1]]) project = INTERWIKI_SITES[prefixed[1]];
    else if (!language && /^[a-z]{2,3}(?:-[a-z]{2,8})?$/.test(prefixed[1])) language = prefixed[1];
    else break;
    text = prefixed[2].trim();
  }
  return { label, input: text, language: language || defaultLanguage, site: project || site };
}

async function addSourceList(lines) {
  const sources = lines.map((line) => ({ line, source: parseSourceLine(line, $('#articleLanguage').value) })).filter((item) => item.source);
  let added = 0;
  let already = 0;
  const missing = [];
  await withAddButton(t('export.addingLabel'), async () => {
    for (const [index, { line, source }] of sources.entries()) {
      $('#entryHint').textContent = t('sources.listProgress', { n: index + 1, total: sources.length, title: source.label });
      try {
        const resolved = await getJson('/api/sources/resolve', { method: 'POST', body: resolveBody(source) });
        if (resolved.kind === 'article') {
          if (await pushArticle(resolved.article)) added += 1; else already += 1;
        } else if (resolved.kind === 'book' || resolved.kind === 'subpages') {
          const choice = resolved.kind === 'subpages' ? await chooseSubpageBook(resolved) : 'book';
          const articles = { book: resolved.book.articles, 'book-summary': [resolved.article, ...resolved.book.articles], page: [resolved.article] }[choice] || [];
          for (const article of articles) {
            if (await pushArticle(article)) added += 1; else already += 1;
          }
        } else missing.push(line.trim());
      } catch { missing.push(line.trim()); }
    }
  });
  setQuery(missing.join('\n'));
  $('#entryHint').textContent = missing.length ? t('sources.listMissing', { titles: missing.join(' · ') }) : '';
  showToast(t('sources.listSummary', { added, already, missing: missing.length }), missing.length > 0);
}

function showSearchResults(items, source, hint) {
  const results = $('#searchResults');
  results.hidden = false;
  const kind = source.site === 'wikipedia' ? t('sources.wikipediaArticleLabel') : t(`site.${source.site}`);
  results.innerHTML = items.length
    ? items.map((item) => { const language = item.language || source.language; return `<button class="search-result" type="button" data-add-title="${escapeHtml(item.title)}" data-page-id="${item.page_id}" data-language="${escapeHtml(language)}" data-site="${escapeHtml(source.site)}"><span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(kind)} \u00b7 ${escapeHtml(language.toUpperCase())}</small></span><span class="search-add" aria-hidden="true">+</span></button>`; }).join('')
    : `<div class="search-result"><span><strong>${escapeHtml(t('sources.noResultsTitle'))}</strong><small>${escapeHtml(t('sources.noResultsDesc'))}</small></span></div>`;
  if (hint) $('#entryHint').textContent = hint;
}

async function searchArticles(query) {
  clearTimeout(state.searchTimer);
  if (query.trim().length < 2 || /^[a-z]+:\/\//i.test(query.trim())) { $('#searchResults').hidden = true; return; }
  state.searchTimer = setTimeout(async () => {
    const results = $('#searchResults');
    results.hidden = false;
    results.innerHTML = `<div class="search-result"><span><strong>${escapeHtml(t('sources.searching'))}</strong></span></div>`;
    try {
      const source = parseSourceLine(query, $('#articleLanguage').value);
      if (source.input.length < 2) { results.hidden = true; return; }
      const all = source.language === ALL_LANGUAGES;
      const params = new URLSearchParams({ query: source.input, language: source.language, site: source.site, limit: all ? '3' : '8', ...(all ? { languages: searchLanguages().join(',') } : {}) });
      const items = await getJson(`/api/search?${params}`);
      if ($('#articleQuery').value.trim() !== query.trim()) return;
      showSearchResults(items, source);
    } catch (error) {
      results.innerHTML = `<div class="search-result"><span><strong>${escapeHtml(t('sources.searchUnavailable'))}</strong><small>${escapeHtml(error.message)}</small></span></div>`;
    }
  }, 250);
}

async function showRelatedArticles(article, button) {
  button.disabled = true;
  button.textContent = t('explore.loading');
  try {
    const updated = await getJson('/api/explore', {
      method: 'POST',
      body: JSON.stringify({ project: { ...state.project, main_articles: [article], discovered_articles: [] }, max_depth: 1, max_articles: 200 }),
    });
    const known = new Set(state.project.main_articles.map(articleKey));
    const related = updated.discovered_articles.filter((a) => !known.has(articleKey(a)));
    $('#articleFilter').value = '';
    queueSave({ discovered_articles: related });
    renderWorkspace();
    const n = related.length;
    if (!n) showToast(t('explore.none'));
    else {
      showToast(n === 1 ? t('explore.result', { n }) : t('explore.resultPlural', { n }));
      $('.discovered-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  } catch (error) {
    showToast(error.message, true);
    renderWorkspace();
  }
}

function toggleArticle(card, selected) {
  const key = card.dataset.articleKey;
  activeArticles().forEach((a) => { if (articleKey(a) === key) a.selected = selected; });
  queueSave({ main_articles: state.project.main_articles, discovered_articles: state.project.discovered_articles });
  renderWorkspace();
}

function removeArticle(card) {
  const key = card.dataset.articleKey;
  state.project.main_articles = state.project.main_articles.filter((a) => articleKey(a) !== key);
  state.project.discovered_articles = state.project.discovered_articles.filter((a) => articleKey(a) !== key);
  state.project.article_order = state.project.article_order.filter((k) => k !== key);
  state.project.chapters = state.project.chapters.map((ch) => ({ ...ch, article_keys: ch.article_keys.filter((k) => k !== key) }));
  queueSave({ main_articles: state.project.main_articles, discovered_articles: state.project.discovered_articles, article_order: state.project.article_order, chapters: state.project.chapters });
  renderWorkspace();
  showToast(t('discovered.removedToast'));
}

async function handleDocumentUpload(files) {
  const maxBytes = 15 * 1024 * 1024;
  let added = 0;
  for (const file of files) {
    const isPdf = file.type === 'application/pdf';
    const isImage = file.type.startsWith('image/');
    if (!isPdf && !isImage) { showToast(t('org.docAcceptedTypesError', { name: file.name }), true); continue; }
    if (file.size > maxBytes) { showToast(t('org.docTooLargeError', { name: file.name }), true); continue; }
    const dataUrl = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error(t('org.docReadError')));
      reader.readAsDataURL(file);
    });
    const base64 = dataUrl.split(',')[1] || '';
    state.project.uploaded_documents = [
      ...(state.project.uploaded_documents || []),
      { id: crypto.randomUUID(), title: file.name, kind: isPdf ? 'pdf' : 'image', mime_type: file.type, data_base64: base64, selected: true },
    ];
    added += 1;
  }
  if (added) {
    queueSave({ uploaded_documents: state.project.uploaded_documents });
    renderWorkspace();
    showToast(added === 1 ? t('org.docAddedToast', { n: added }) : t('org.docAddedToastPlural', { n: added }));
  }
}

// NE PAS ouvrir le document par une adresse data: : Chrome refuse de l'afficher dans un nouvel onglet.
function openUploadedDocument(id) {
  const doc = (state.project.uploaded_documents || []).find((d) => d.id === id);
  if (!doc) return;
  if (doc.url) { window.open(safeUrl(doc.url), '_blank', 'noopener'); return; }
  const bytes = Uint8Array.from(atob(doc.data_base64), (c) => c.charCodeAt(0));
  const url = URL.createObjectURL(new Blob([bytes], { type: doc.mime_type }));
  window.open(url, '_blank', 'noopener');
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}

function removeUploadedDocument(id) {
  const key = `doc:${id}`;
  state.project.uploaded_documents = (state.project.uploaded_documents || []).filter((d) => d.id !== id);
  state.project.article_order = state.project.article_order.filter((k) => k !== key);
  state.project.chapters = state.project.chapters.map((ch) => ({ ...ch, article_keys: ch.article_keys.filter((k) => k !== key) }));
  queueSave({ uploaded_documents: state.project.uploaded_documents, article_order: state.project.article_order, chapters: state.project.chapters });
  renderWorkspace();
  showToast(t('org.docRemovedToast'));
}

function addChapter() {
  const chapters = [...(state.project.chapters || [])];
  // NE PAS faire apparaître « Sans chapitre » à la création du premier chapitre : les articles déjà là restent en tête, sans intitulé, et le chapitre s'ajoute après eux.
  const first = !chapters.length;
  chapters.push({ id: crypto.randomUUID(), title: t('org.newChapterTitle', { n: chapters.length + 1 }), article_keys: [] });
  state.project.chapters = chapters;
  queueSave(first ? { chapters, unassigned_first: true } : { chapters });
  renderOrganization();
  const last = $$('.chapter-name', $('#organizationList')).at(-1);
  last?.focus(); last?.select();
}

function removeChapter(row) {
  const id = row.dataset.chapterId;
  state.project.chapters = state.project.chapters.filter((ch) => ch.id !== id);
  queueSave({ chapters: state.project.chapters });
  renderOrganization();
}

function patchSetting(id, field, transform = (v) => v) {
  const el = $(`#${id}`);
  const value = transform(el.value);
  queueSave({ [field]: value });
  state.project[field] = value;
  if (id === 'pageFormat') $('#customDimensions').hidden = value !== 'custom';
}

function collectLayoutSettings() {
  return {
    page_format: $('#pageFormat').value,
    custom_width_mm: Number($('#customWidth').value),
    custom_height_mm: Number($('#customHeight').value),
    orientation: $('input[name="orientation"]:checked')?.value || 'portrait',
    margin_top_mm: Number($('#marginTop').value),
    margin_bottom_mm: Number($('#marginBottom').value),
    margin_inside_mm: Number($('#marginInside').value),
    margin_outside_mm: Number($('#marginOutside').value),
    margin_binding_mm: Number($('#marginBinding').value),
  };
}

let pdfProgressTotal = 0;

function showPdfProgress(event) {
  if (event) pdfProgressTotal = event.total;
  $('#pdfProgress').hidden = false;
  $('#pdfProgressStep').textContent = event ? t('progress.step', { step: event.step, total: event.total }) : '';
  $('#pdfProgressLabel').textContent = event ? t(`progress.${event.code}`, { title: event.title || '' }) : t('progress.starting');
  $('#pdfProgressFill').style.width = event ? `${Math.round((event.step / event.total) * 100)}%` : '0%';
}

function showPdfDownload(received, size) {
  const total = Math.max(pdfProgressTotal, 1);
  const share = size ? Math.min(received / size, 1) : 1;
  $('#pdfProgressStep').textContent = t('progress.step', { step: total, total });
  $('#pdfProgressLabel').textContent = t('progress.download', { percent: Math.floor(share * 100) });
  $('#pdfProgressFill').style.width = `${Math.round(((total - 1 + share) / total) * 100)}%`;
}

let pdfWaitTimer = null;

function showPdfWait(seconds) {
  clearInterval(pdfWaitTimer);
  const end = Date.now() + seconds * 1000;
  const tick = () => {
    const left = Math.ceil((end - Date.now()) / 1000);
    if (left <= 0) { hidePdfWait(); return; }
    $('#pdfProgressWait').hidden = false;
    $('#pdfProgressWait').textContent = t('progress.wait', { seconds: left });
  };
  tick();
  pdfWaitTimer = setInterval(tick, 1000);
}

function showPdfLimited(seconds) {
  clearInterval(pdfWaitTimer);
  const end = Date.now() + seconds * 1000;
  const tick = () => {
    $('#pdfProgressWait').hidden = false;
    $('#pdfProgressWait').textContent = t('progress.limited', { seconds: Math.max(0, Math.ceil((end - Date.now()) / 1000)) });
  };
  tick();
  pdfWaitTimer = setInterval(tick, 1000);
  return new Promise((resolve) => setTimeout(() => { hidePdfWait(); resolve(); }, seconds * 1000));
}

function showPdfBusy(seconds) {
  clearInterval(pdfWaitTimer);
  const start = Date.now() - seconds * 1000;
  const tick = () => {
    $('#pdfProgressWait').hidden = false;
    $('#pdfProgressWait').textContent = t('progress.busy', { seconds: Math.floor((Date.now() - start) / 1000) });
  };
  tick();
  pdfWaitTimer = setInterval(tick, 1000);
}

function hidePdfWait() {
  clearInterval(pdfWaitTimer);
  pdfWaitTimer = null;
  $('#pdfProgressWait').hidden = true;
}

function hidePdfProgress() {
  hidePdfWait();
  $('#pdfProgressVolume').hidden = true;
  $('#pdfProgressRetry').hidden = true;
  $('#pdfProgress').hidden = true;
}

function showPdfRetry(attempt) {
  $('#pdfProgressRetry').hidden = false;
  $('#pdfProgressRetry').textContent = t('progress.retry', { attempt });
}

async function waitForServer() {
  const end = Date.now() + SERVER_WAIT_MS;
  while (Date.now() < end) {
    await new Promise((resolve) => setTimeout(resolve, SERVER_POLL_MS));
    try {
      if ((await fetch(`${API}/health`, { cache: 'no-store' })).ok) return;
    } catch {
      continue;
    }
  }
}

function pdfStreamEvent(line) {
  if (!line.trim()) return null;
  const event = JSON.parse(line);
  if (event.type === 'progress') { showPdfProgress(event); return null; }
  if (event.type === 'wait') { showPdfWait(event.seconds); return null; }
  if (event.type === 'busy') { showPdfBusy(event.seconds); return null; }
  if (event.type === 'error') throw new Error(event.detail);
  if (event.type === 'done') return event;
  return null;
}

// NE PAS décoder le flux entier en texte : après le message « done », la suite est le PDF en binaire (event.size octets).
async function streamPdf(project) {
  const response = await request(`/api/pdf/stream?language=${encodeURIComponent(lang())}`, { method: 'POST', body: JSON.stringify(project), headers: { 'X-Wikipedia2Book-Client': clientToken() } });
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let pending = new Uint8Array(0);
  let done = null;
  const parts = [];
  let received = 0;
  for (;;) {
    let chunk;
    try {
      chunk = await reader.read();
    } catch {
      throw new ServerCrashError(t('progress.interrupted'));
    }
    const { value, done: finished } = chunk;
    if (value) {
      if (done) { parts.push(value); received += value.length; }
      else {
        const merged = new Uint8Array(pending.length + value.length);
        merged.set(pending);
        merged.set(value, pending.length);
        pending = merged;
        let newline = pending.indexOf(10);
        while (!done && newline !== -1) {
          done = pdfStreamEvent(decoder.decode(pending.subarray(0, newline)));
          pending = pending.subarray(newline + 1);
          newline = pending.indexOf(10);
        }
        if (done && pending.length) { parts.push(pending); received += pending.length; pending = new Uint8Array(0); }
      }
      if (done) showPdfDownload(received, done.size);
    }
    if (done && received >= done.size) return new Blob(parts, { type: 'application/pdf' });
    if (finished) throw new ServerCrashError(t('progress.interrupted'));
  }
}

function countsTowardLimit(item) {
  return !item.kind;
}

function limitedArticleCount() {
  return selectedArticles().filter(countsTowardLimit).length;
}

// NE PAS couper un chapitre tant qu'il tient dans un volume : la coupure se fait entre deux chapitres, et à l'intérieur d'un chapitre seulement s'il dépasse la limite à lui seul.
function planVolumes(limit, slots) {
  const units = [];
  slots.forEach((slot) => {
    const last = units[units.length - 1];
    if (last && last.chapterId === slot.chapterId) last.items.push(slot.article);
    else units.push({ chapterId: slot.chapterId, items: [slot.article] });
  });
  const volumes = [];
  let current = [];
  let count = 0;
  const close = () => {
    if (current.length) volumes.push(current);
    current = [];
    count = 0;
  };
  units.forEach((unit) => {
    if (count + unit.items.filter(countsTowardLimit).length > limit) close();
    unit.items.forEach((item) => {
      if (countsTowardLimit(item) && count >= limit) close();
      current.push(item);
      if (countsTowardLimit(item)) count += 1;
    });
  });
  close();
  return volumes;
}

// NE PAS faire passer le découpage automatique avant les coupures de l'utilisateur : elles délimitent d'abord les volumes, puis chaque volume encore trop gros est découpé.
// NE PAS modifier buildOrgSlots, volumeStarts, articleSegments, planVolumes ou volumeProject sans aligner app/volumes.py : le paramètre volume de l'API doit donner les mêmes volumes.
function bookVolumes() {
  if (!state.project) return null;
  const limit = state.articleLimit;
  const volumes = articleSegments().flatMap((segment) => (limit ? planVolumes(limit, segment) : [segment.map((slot) => slot.article)]));
  return volumes.length > 1 ? volumes : null;
}

function volumeProject(project, items, index, total) {
  const keys = new Set(items.map(articleKey));
  const copy = JSON.parse(JSON.stringify({ ...project, uploaded_documents: [] }));
  copy.uploaded_documents = (project.uploaded_documents || []).filter((item) => keys.has(articleKey(item)));
  [...copy.main_articles, ...copy.discovered_articles].forEach((item) => { item.selected = keys.has(articleKey(item)); });
  const title = (project.book_title || defaultBookTitle() || project.name).slice(0, 170);
  copy.book_title = t('export.volumeTitle', { title, index: index + 1, count: total });
  if (index > 0) copy.introduction = '';
  if (index < total - 1) copy.conclusion = '';
  return copy;
}

async function generatePdf(project) {
  let crashes = 0;
  for (;;) {
    try {
      return await streamPdf(project);
    } catch (error) {
      // NE PAS compter un refus HTTP 429 comme un plantage : le serveur demande seulement d'attendre (limite par client, file pleine), on réessaie sans fin et sans rien demander.
      if (error instanceof RateLimitedError) {
        await showPdfLimited(error.retryAfter);
        continue;
      }
      // NE PAS relancer sur une erreur renvoyée par le serveur (article introuvable, requête invalide…) : seul un plantage (connexion coupée, serveur en redémarrage) justifie de repartir de zéro.
      if (!(error instanceof ServerCrashError)) throw error;
      crashes += 1;
      if (crashes > PDF_AUTO_RETRIES && !window.confirm(t('export.retryConfirm', { count: crashes }))) throw error;
      showPdfProgress(null);
      showPdfRetry(crashes);
      await waitForServer();
    }
  }
}

function downloadPdf(blob, name) {
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = objectUrl;
  anchor.download = `${name}.pdf`;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(objectUrl), 60000);
}

// NE PAS désactiver les boutons pour une sélection vide : seulement pendant une génération (message ci-dessous sinon).
async function exportPdf() {
  if (!state.project || !selectedArticles().length) {
    showToast(t('export.noSelection'), true);
    return;
  }
  const buttons = [$('#exportButton'), $('#topExportButton')].filter(Boolean);
  buttons.forEach((b) => { b.disabled = true; });
  setSaveState(t('export.generating'));
  showPdfProgress(null);
  try {
    let volumes = bookVolumes();
    if (!volumes) {
      try {
        downloadPdf(await generatePdf(state.project), bookFileName(state.project));
      } catch (error) {
        if (error.detail?.code !== 'too_many_articles') throw error;
        state.articleLimit = error.detail.limit;
        volumes = bookVolumes();
        if (!volumes) throw error;
      }
    }
    if (volumes) {
      const notice = volumes.length > articleSegments().length
        ? t('export.volumesNotice', { articles: limitedArticleCount(), limit: state.articleLimit, count: volumes.length })
        : t('export.volumesManualNotice', { count: volumes.length });
      showToast(notice);
      for (const [index, items] of volumes.entries()) {
        showPdfProgress(null);
        $('#pdfProgressVolume').hidden = false;
        $('#pdfProgressVolume').textContent = t('progress.volume', { index: index + 1, count: volumes.length });
        $('#pdfProgressVolume').title = notice;
        // NE PAS envoyer tout le livre en une requête : chaque volume reste sous la limite, et sa numérotation des pages repart de 1.
        downloadPdf(await generatePdf(volumeProject(state.project, items, index, volumes.length)), `${bookFileName(state.project)}-${index + 1}`);
      }
    }
    setSaveState(state.isDirty ? t('export.toDownload') : t('export.loadedInMemory'));
    showToast(t('export.ready'));
  } catch (error) {
    setSaveState(t('export.error'));
    if (error.detail?.code === 'too_many_articles') {
      hidePdfProgress();
      window.alert(error.message);
      return;
    }
    showToast(t('export.failed', { error: error.message }), true);
  } finally {
    hidePdfProgress();
    buttons.forEach((b) => { b.disabled = false; });
  }
}

// NE PAS revenir à un nom de fichier fixe : il dérive du titre du livre.
function bookFileName(project) {
  return (project.book_title || defaultBookTitle() || project.name).replace(/[^a-z0-9-_ ]/gi, '').trim().replace(/\s+/g, '-') || 'livre';
}

function exportWorkspace() {
  if (!state.project) return;
  // NE PAS enregistrer les suggestions (articles découverts non retenus) : elles se retrouvent en relançant « Articles liés », et alourdissaient le fichier.
  const workspace = { format: 'wikipedia2book-workspace', version: 1, saved_at: new Date().toISOString(), projects: [{ ...state.project, discovered_articles: [] }] };
  const blob = new Blob([JSON.stringify(workspace, null, 2)], { type: 'application/json' });
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = objectUrl;
  anchor.download = `${bookFileName(state.project)}.json`;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(objectUrl);
  state.isDirty = false;
  setSaveState(t('export.jsonDownloaded'));
  showToast(t('export.jsonDownloadedToast'));
}

function readWorkspace(payload) {
  if (Array.isArray(payload)) return payload;
  if (payload?.format === 'wikipedia2book-workspace') {
    if (payload.version !== 1 || !Array.isArray(payload.projects)) throw new Error(t('export.unsupportedJsonVersion'));
    return payload.projects;
  }
  if (payload && typeof payload === 'object' && payload.id && payload.name) return [payload];
  throw new Error(t('export.invalidJsonFile'));
}

async function importWorkspace(readText) {
  if (state.isDirty && !window.confirm(t('export.confirmReplace'))) return;
  try {
    const payload = JSON.parse(await readText());
    const projects = readWorkspace(payload);
    if (projects.some((p) => !p || typeof p.id !== 'string' || typeof p.name !== 'string' || !p.name.trim())) throw new Error(t('export.invalidProjectInFile'));
    state.project = normalizeProject(projects[0]);
    state.isDirty = false;
    renderWorkspace();
    setView('sources');
    setSaveState(t('export.jsonImported'));
    showToast(t('export.bookImported'));
  } catch (error) { showToast(t('export.jsonImportFailed', { error: error.message }), true); }
  finally { $('#workspaceFileInput').value = ''; }
}

// ── Event listeners ──────────────────────────────────────────────────────────

document.addEventListener('click', async (event) => {
  const viewButton = event.target.closest('[data-view]');
  if (viewButton) {
    setView(viewButton.dataset.view);
    if (viewButton.closest('.step-footer')) window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }
  const result = event.target.closest('[data-add-title]');
  if (result) { await addArticle({ title: result.dataset.addTitle, language: result.dataset.language, site: result.dataset.site, page_id: Number(result.dataset.pageId) }); return; }
  if (event.target.closest('#selectDiscoveredButton')) { addSuggestions(visibleSuggestions()); return; }
  const suggestionCard = event.target.closest('#discoveredArticles .article-card');
  if (suggestionCard && event.target.closest('.add-suggestion')) { addSuggestions(state.project.discovered_articles.filter((a) => articleKey(a) === suggestionCard.dataset.articleKey)); return; }
  if (suggestionCard && event.target.closest('.dismiss-suggestion')) { dismissSuggestion(suggestionCard.dataset.articleKey); return; }
  const exploreFrom = event.target.closest('.explore-from');
  if (exploreFrom) {
    const key = exploreFrom.closest('.article-card').dataset.articleKey;
    await showRelatedArticles(state.project.main_articles.find((a) => articleKey(a) === key), exploreFrom);
    return;
  }
  if (event.target.closest('#addChapterButton')) { addChapter(); return; }
  if (event.target.closest('#addVolumeButton')) { addVolumeBreak(); return; }
  const volumeRow = event.target.closest('.org-volume');
  if (volumeRow && event.target.closest('.volume-remove')) { removeVolumeBreak(volumeRow.dataset.volumeAnchor); return; }
  if (event.target.closest('#uploadDocumentButton')) { $('#documentFileInput').click(); return; }
  if (event.target.closest('#addDocumentUrlButton')) { await addDocumentFromUrl($('#documentUrl').value); return; }
  if (event.target.closest('#importWorkspaceButton')) { $('#workspaceFileInput').click(); return; }
  if (event.target.closest('#saveWorkspaceButton')) { exportWorkspace(); return; }
  if (event.target.closest('#topExportButton, #exportButton')) { await exportPdf(); return; }
  const articleCardEl = event.target.closest('.article-card');
  if (articleCardEl && event.target.closest('.remove-article')) { await removeArticle(articleCardEl); return; }
  const openDoc = event.target.closest('.doc-open');
  if (openDoc) {
    event.preventDefault();
    const key = openDoc.closest('.org-article').dataset.articleKey;
    openUploadedDocument(key.slice(4));
    return;
  }
  const orgRow = event.target.closest('.org-article');
  if (orgRow && event.target.closest('.org-remove')) {
    const key = orgRow.dataset.articleKey;
    if (key.startsWith('doc:')) removeUploadedDocument(key.slice(4)); else removeArticle(orgRow);
    return;
  }
  const chapterRow = event.target.closest('.org-chapter-row');
  if (chapterRow && event.target.closest('.chapter-delete')) { removeChapter(chapterRow); return; }
  if (!event.target.closest('#articleQuery, #searchResults')) $('#searchResults').hidden = true;
});

document.addEventListener('change', async (event) => {
  if (event.target.matches('.article-check')) { const card = event.target.closest('.article-card'); await toggleArticle(card, event.target.checked); return; }
  if (event.target.matches('input[name="suggestionSort"]')) { state.suggestionSort = event.target.value; renderArticles(); return; }
  if (event.target.matches('#articleLanguage')) { if ($('#articleQuery').value.trim().length >= 2) searchArticles($('#articleQuery').value); return; }
  if (event.target.matches('input[name="orientation"]')) { const layout = collectLayoutSettings(); Object.assign(state.project, layout); queueSave(layout); renderBackgrounds(); return; }
  if (event.target.matches('#pageNumbers')) { queueSave({ page_numbers: event.target.checked }); return; }
  if (event.target.matches('input[name="tocChoice"]')) { queueSave({ table_of_contents: event.target.value !== 'none', toc_position: event.target.value === 'end' ? 'end' : 'start' }); return; }
  const textSettings = { bookTitle: 'book_title', bookDescription: 'description', bookSubtitle: 'book_subtitle', bookAuthor: 'book_author', bookIntroduction: 'introduction', bookConclusion: 'conclusion' };
  if (textSettings[event.target.id]) patchSetting(event.target.id, textSettings[event.target.id]);
  const numericSettings = { customWidth: 'custom_width_mm', customHeight: 'custom_height_mm', marginTop: 'margin_top_mm', marginBottom: 'margin_bottom_mm', marginInside: 'margin_inside_mm', marginOutside: 'margin_outside_mm', marginBinding: 'margin_binding_mm' };
  if (numericSettings[event.target.id]) patchSetting(event.target.id, numericSettings[event.target.id], Number);
  if (event.target.matches('#pageFormat')) patchSetting('pageFormat', 'page_format');
  if (event.target.matches('#pageFormat, #customWidth, #customHeight')) renderBackgrounds();
  if (event.target.matches('#marginPreset')) applyMarginPreset(event.target.value);
  if (numericSettings[event.target.id]?.startsWith('margin_')) $('#marginPreset').value = marginPresetOf(state.project);
});

$('#documentUrl').addEventListener('keydown', (event) => { if (event.key === 'Enter') { event.preventDefault(); addDocumentFromUrl(event.target.value); } });

document.addEventListener('input', (event) => {
  if (event.target.matches('#articleQuery')) {
    if (event.target.value.includes('\n')) { $('#searchResults').hidden = true; setQuery(event.target.value); }
    else searchArticles(event.target.value);
  }
  if (event.target.matches('#articleFilter')) renderArticles();
  const chapterNameEl = event.target.closest('.chapter-name');
  if (chapterNameEl && state.project) {
    const row = chapterNameEl.closest('.org-chapter-row');
    const chapter = state.project.chapters.find((c) => c.id === row?.dataset.chapterId);
    if (chapter && chapterNameEl.value.trim()) { chapter.title = chapterNameEl.value; queueSave({ chapters: state.project.chapters }); }
  }
  const textSettings = { bookTitle: 'book_title', bookDescription: 'description', bookSubtitle: 'book_subtitle', bookAuthor: 'book_author', bookIntroduction: 'introduction', bookConclusion: 'conclusion' };
  if (textSettings[event.target.id]) { state.project[textSettings[event.target.id]] = event.target.value; queueSave({ [textSettings[event.target.id]]: event.target.value }); }
});

$('#articleForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  const value = $('#articleQuery').value.trim();
  if (!value) { showToast(t('sources.emptyField'), true); return; }
  clearTimeout(state.searchTimer);
  $('#searchResults').hidden = true;
  const lines = value.split(/\r?\n/).filter((line) => line.trim());
  if (lines.length > 1 && isBookWikitext(lines)) await addBookWikitext(value);
  else if (lines.length > 1) await addSourceList(lines);
  else await addSource(value);
});
$('#articleQuery').addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    $('#articleForm').requestSubmit();
  }
});
document.querySelectorAll('.background-field').forEach((field) => {
  const name = field.dataset.background;
  const input = field.querySelector('.background-file');
  field.querySelector('.background-choose').addEventListener('click', () => input.click());
  input.addEventListener('change', async () => {
    const file = input.files?.[0];
    input.value = '';
    if (file) await setBackground(name, file, file.name);
  });
  const url = field.querySelector('.background-url');
  field.querySelector('.background-use-url').addEventListener('click', () => setBackgroundFromUrl(name, url.value));
  url.addEventListener('keydown', (event) => { if (event.key === 'Enter') { event.preventDefault(); setBackgroundFromUrl(name, url.value); } });
  field.querySelector('.background-remove').addEventListener('click', () => removeBackground(name));
});
$('#documentFileInput').addEventListener('change', async (event) => {
  const files = [...(event.target.files || [])];
  event.target.value = '';
  if (files.length) await handleDocumentUpload(files);
});
$('#workspaceFileInput').addEventListener('change', async (event) => {
  const file = event.target.files?.[0];
  if (file) await importWorkspace(() => file.text());
});
window.addEventListener('beforeunload', (event) => {
  if (state.isDirty) { event.preventDefault(); event.returnValue = ''; }
});
$('#languageSelect').addEventListener('change', (event) => {
  setLanguage(event.target.value);
  if (state.project) renderWorkspace();
});

function selectBrowserWikiLanguage() {
  const select = $('#articleLanguage');
  const base = (navigator.language || '').toLowerCase().split('-')[0];
  const code = base === 'nb' ? 'no' : base;
  if (!/^[a-z]{2,3}$/.test(code)) { select.value = 'en'; return; }
  if (![...select.options].some((option) => option.value === code)) select.add(new Option(code.toUpperCase(), code), select.querySelector(`option[value="${ALL_LANGUAGES}"]`));
  select.value = code;
}

selectBrowserWikiLanguage();
loadProjects();
