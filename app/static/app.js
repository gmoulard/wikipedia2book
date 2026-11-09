const API = '';
const state = {
  project: null,
  activeView: 'sources',
  sourceMode: 'book',
  searchTimer: null,
  toastTimer: null,
  isDirty: false,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function escapeHtml(value = '') {
  return String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
}

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers },
  });
  if (!response.ok) {
    let message = `Erreur ${response.status}`;
    try { const p = await response.json(); message = p.detail || message; } catch { /* not json */ }
    throw new Error(message);
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

function activeArticles() {
  if (!state.project) return [];
  return [...state.project.main_articles, ...state.project.discovered_articles];
}

function selectedArticles() { return activeArticles().filter((a) => a.selected); }

function articleKey(article) {
  return article.page_id != null
    ? `${article.language}:${article.page_id}`
    : `${article.language}:title:${article.title.toLowerCase()}`;
}

function sameArticle(a, b) {
  if (a.language !== b.language) return false;
  if (a.page_id != null && b.page_id != null) return a.page_id === b.page_id;
  return a.title.toLocaleLowerCase() === b.title.toLocaleLowerCase();
}

function normalizeProject(project) {
  return {
    main_articles: [], discovered_articles: [],
    book_title: '', book_subtitle: '', book_author: '', introduction: '', conclusion: '',
    page_format: 'A4', custom_width_mm: 148, custom_height_mm: 210, orientation: 'portrait',
    margin_top_mm: 18, margin_bottom_mm: 18, margin_inside_mm: 18, margin_outside_mm: 16,
    margin_binding_mm: 0, article_order: [], chapters: [], toc_position: 'start', page_numbers: false, ...project,
  };
}

function renderWorkspace() {
  const hasProject = Boolean(state.project);
  $('#projectWorkspace').hidden = !hasProject;
  $('#topExportButton').disabled = !hasProject || selectedArticles().length === 0;
  $('#saveWorkspaceButton').disabled = !hasProject;
  $('#breadcrumbProject').textContent = hasProject ? state.project.name.toLocaleUpperCase('fr') : 'NOUVEAU PROJET';
  if (!hasProject) return;
  const nameInput = $('#projectName');
  const descInput = $('#projectDescription');
  if (document.activeElement !== nameInput) nameInput.value = state.project.name;
  if (document.activeElement !== descInput) descInput.value = state.project.description || '';
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
    ? project.main_articles.map((a) => articleCard(a, true)).join('')
    : emptyList('Aucun article principal', 'Recherchez un article ou ajoutez une URL Wikipédia.');

  const origins = [...new Set(project.discovered_articles.map((a) => a.origin_title).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'fr'));
  const originSelect = $('#originFilter');
  const selectedOrigin = originSelect.value;
  originSelect.innerHTML = '<option value="">Toutes les origines</option>' + origins.map((o) => `<option value="${escapeHtml(o)}">${escapeHtml(o)}</option>`).join('');
  originSelect.value = origins.includes(selectedOrigin) ? selectedOrigin : '';

  const titleFilter = $('#articleFilter').value.trim().toLocaleLowerCase('fr');
  const originFilter = originSelect.value;
  const depthFilter = $('#depthFilter').value;
  const visible = project.discovered_articles.filter((a) =>
    (!titleFilter || a.title.toLocaleLowerCase('fr').includes(titleFilter))
    && (!originFilter || a.origin_title === originFilter)
    && (!depthFilter || String(a.depth) === depthFilter)
  );
  $('#discoveredArticles').innerHTML = visible.length
    ? visible.map((a) => articleCard(a, false)).join('')
    : emptyList(project.discovered_articles.length ? 'Aucun résultat' : 'Pas encore de suggestions',
        project.discovered_articles.length ? 'Modifiez vos filtres.' : 'L\u2019exploration proposera des articles, sans les ajouter automatiquement au livre.');
  const hasDiscovered = project.discovered_articles.length > 0;
  $('#selectDiscoveredButton').disabled = !hasDiscovered;
  $('#selectVisibleButton').disabled = visible.length === 0;
  $('#deselectAllButton').disabled = !selectedArticles().length;
}

function articleCard(article, isMain) {
  const key = articleKey(article);
  const meta = [article.language.toUpperCase(), article.depth ? `Niveau ${article.depth}` : 'Principal', article.origin_title ? `Depuis ${article.origin_title}` : ''].filter(Boolean);
  const summary = article.summary ? `<p class="article-summary">${escapeHtml(article.summary.slice(0, 290))}${article.summary.length > 290 ? '\u2026' : ''}</p>` : '';
  return `<article class="article-card${article.selected ? ' selected' : ''}" data-article-key="${escapeHtml(key)}">
    <div class="article-card-top">
      <input class="article-check" type="checkbox" aria-label="${article.selected ? 'D\u00e9s\u00e9lectionner' : 'S\u00e9lectionner'} ${escapeHtml(article.title)}" ${article.selected ? 'checked' : ''}>
      <div class="article-title-wrap"><a class="article-title" href="${escapeHtml(article.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(article.title)}</a><div class="article-meta">${meta.map((m) => `<span>${escapeHtml(m)}</span>`).join('')}</div></div>
      ${isMain ? '<button class="remove-article" type="button" title="Retirer cet article" aria-label="Retirer cet article">\u00d7</button>' : ''}
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

// Build the flat ordered list of "slots": toc | chapters/articles
function buildOrgSlots() {
  const project = state.project;
  const articles = orderedSelectedArticles();
  const chapterByArticle = new Map();
  (project.chapters || []).forEach((ch) => ch.article_keys.forEach((k) => chapterByArticle.set(k, ch.id)));

  // group articles by chapter
  const groups = [{ id: '', title: 'Sans chapitre', articles: [] }, ...(project.chapters || []).map((ch) => ({ ...ch, articles: [] }))];
  articles.forEach((a) => {
    const k = articleKey(a);
    const g = groups.find((g) => g.id === (chapterByArticle.get(k) || '')) || groups[0];
    g.articles.push(a);
  });

  // slots: toc + chapters/articles interleaved
  const tocPos = project.toc_position || 'start';
  const slots = [];
  if (tocPos === 'start') slots.push({ type: 'toc' });
  groups.filter((g) => g.articles.length || g.id).forEach((g) => {
    if (g.id) slots.push({ type: 'chapter', chapter: g });
    g.articles.forEach((a) => slots.push({ type: 'article', article: a, chapterId: g.id }));
  });
  if (tocPos === 'end') slots.push({ type: 'toc' });
  return slots;
}

function renderOrganization() {
  const project = state.project;
  const articles = orderedSelectedArticles();
  $('#organizationCount').textContent = articles.length;

  if (!articles.length) {
    $('#organizationList').innerHTML = '<div class="org-empty">Aucun article retenu pour l\u2019instant.<br>Revenez \u00e0 l\u2019\u00e9tape Sources et cochez les articles \u00e0 inclure.</div>';
    return;
  }

  const slots = buildOrgSlots();
  const html = slots.map((slot, idx) => {
    if (slot.type === 'toc') {
      return `<div class="org-row org-toc" draggable="true" data-slot-type="toc" data-slot-index="${idx}">
        <span class="drag-handle" aria-hidden="true">\u2630</span>
        <span class="toc-icon" aria-hidden="true">\u2261</span>
        <div><div class="org-article-title">Table des mati\u00e8res</div><div class="org-article-origin">Position : ${slot === slots[0] ? 'D\u00e9but du livre' : 'Fin du livre'}</div></div>
      </div>`;
    }
    if (slot.type === 'chapter') {
      const ch = slot.chapter;
      const letterIdx = (project.chapters || []).findIndex((c) => c.id === ch.id);
      const letter = String.fromCharCode(65 + letterIdx % 26);
      return `<div class="org-row org-chapter-row" draggable="true" data-slot-type="chapter" data-slot-index="${idx}" data-chapter-id="${escapeHtml(ch.id)}">
        <span class="drag-handle" aria-hidden="true">\u2630</span>
        <span class="chapter-letter">${letter}</span>
        <input class="chapter-name" aria-label="Titre du chapitre" value="${escapeHtml(ch.title)}" maxlength="120">
        <button class="chapter-remove" type="button" title="Supprimer le chapitre">Supprimer</button>
      </div>`;
    }
    // article
    const a = slot.article;
    const k = articleKey(a);
    const chapters = project.chapters || [];
    const chapter = chapters.find((c) => c.article_keys.includes(k));
    return `<div class="org-row org-article" draggable="true" data-slot-type="article" data-slot-index="${idx}" data-article-key="${escapeHtml(k)}">
      <span class="drag-handle" aria-hidden="true">\u2630</span>
      <div><div class="org-article-title">${escapeHtml(a.title)}</div><div class="org-article-origin">${escapeHtml(a.origin_title ? `D\u00e9couvert depuis ${a.origin_title}` : `Article principal \u00b7 ${a.language.toUpperCase()}`)}</div></div>
      <select class="chapter-select" aria-label="Chapitre de ${escapeHtml(a.title)}"><option value="" ${!chapter ? 'selected' : ''}>Sans chapitre</option>${chapters.map((c) => `<option value="${escapeHtml(c.id)}" ${chapter?.id === c.id ? 'selected' : ''}>${escapeHtml(c.title)}</option>`).join('')}</select>
      <a class="article-title org-open" href="${escapeHtml(a.url)}" target="_blank" rel="noopener noreferrer" title="Ouvrir sur Wikip\u00e9dia" aria-label="Ouvrir ${escapeHtml(a.title)} sur Wikip\u00e9dia">\u2197</a>
    </div>`;
  }).join('');

  $('#organizationList').innerHTML = html;
  initDragDrop();
}

function initDragDrop() {
  const list = $('#organizationList');
  let dragIndex = null;

  list.querySelectorAll('.org-row[draggable]').forEach((row) => {
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
  const to = slots[toIndex];
  if (!from || !to) return;

  // Moving TOC: just toggle position
  if (from.type === 'toc') {
    const newPos = toIndex < fromIndex ? 'start' : 'end';
    project.toc_position = newPos;
    queueSave({ toc_position: newPos });
    renderOrganization();
    return;
  }

  // Moving an article: reorder article_order
  if (from.type === 'article') {
    const articles = orderedSelectedArticles();
    const fromKey = articleKey(from.article);
    const toKey = to.type === 'article' ? articleKey(to.article) : null;
    const fromIdx = articles.findIndex((a) => articleKey(a) === fromKey);
    const toIdx = toKey ? articles.findIndex((a) => articleKey(a) === toKey) : (toIndex < fromIndex ? 0 : articles.length - 1);
    if (fromIdx < 0 || toIdx < 0) return;
    const reordered = [...articles];
    const [moved] = reordered.splice(fromIdx, 1);
    reordered.splice(toIdx, 0, moved);
    project.article_order = reordered.map(articleKey);
    queueSave({ article_order: project.article_order });
    renderOrganization();
    return;
  }

  // Moving a chapter: reorder chapters array
  if (from.type === 'chapter') {
    const chapters = [...(project.chapters || [])];
    const fromIdx = chapters.findIndex((c) => c.id === from.chapter.id);
    const toChapterId = to.type === 'chapter' ? to.chapter.id : null;
    const toIdx = toChapterId ? chapters.findIndex((c) => c.id === toChapterId) : (toIndex < fromIndex ? 0 : chapters.length - 1);
    if (fromIdx < 0 || toIdx < 0) return;
    const [moved] = chapters.splice(fromIdx, 1);
    chapters.splice(toIdx, 0, moved);
    project.chapters = chapters;
    queueSave({ chapters });
    renderOrganization();
  }
}

function renderBookSettings() {
  const project = state.project;
  const controls = {
    bookTitle: 'book_title', bookSubtitle: 'book_subtitle', bookAuthor: 'book_author',
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
  setSaveState('Modifications \u00e0 enregistrer en JSON');
}

async function loadProjects() {
  try {
    await getJson('/health');
    $('#connectionDot').classList.add('online');
    $('#connectionStatus').textContent = 'API connect\u00e9e';
  } catch (error) {
    $('#connectionDot').classList.add('offline');
    $('#connectionStatus').textContent = 'API indisponible';
    showToast(`L\u2019API est indisponible\u00a0: ${error.message}. Vous pouvez tout de m\u00eame importer un fichier JSON.`, true);
  }
  try {
    const v = await getJson('/api/version');
    const date = v.date ? v.date.slice(0, 10) : '';
    const parts = [v.short, date, v.author].filter(Boolean);
    $('#appVersion').textContent = `v\u00a0${parts.join('\u00a0\u00b7\u00a0')}`;
    $('#appVersion').title = v.commit;
  } catch { /* version non critique */ }
  const now = new Date().toISOString();
  state.project = normalizeProject({ id: crypto.randomUUID(), name: 'Nouveau projet', created_at: now, updated_at: now });
  renderWorkspace();
  setView('sources');
}

async function addArticle(source) {
  if (!state.project) return;
  const button = $('#addArticleButton');
  button.disabled = true;
  button.textContent = 'Ajout\u2026';
  try {
    const article = await getJson('/api/articles', { method: 'POST', body: JSON.stringify(source) });
    if (activeArticles().some((item) => sameArticle(item, article))) throw new Error('Cet article est d\u00e9j\u00e0 dans le projet.');
    article.selected = true;
    state.project.main_articles.push(article);
    queueSave({ main_articles: state.project.main_articles });
    renderWorkspace();
    $('#articleQuery').value = '';
    $('#searchResults').hidden = true;
    $('#entryHint').textContent = 'Article ajout\u00e9 aux articles principaux.';
    showToast('Article principal ajout\u00e9.');
  } catch (error) { showToast(error.message, true); }
  finally { button.disabled = false; button.innerHTML = 'Ajouter <span aria-hidden="true">+</span>'; }
}

async function importWikipediaBook(url) {
  if (!state.project) return;
  const button = $('#addArticleButton');
  button.disabled = true;
  button.textContent = 'Import\u2026';
  try {
    const articles = await getJson('/api/books/import', { method: 'POST', body: JSON.stringify({ url }) });
    const newArticles = articles.filter((a) => !activeArticles().some((e) => sameArticle(e, a)));
    if (!newArticles.length) throw new Error('Toutes les pages de ce livre sont d\u00e9j\u00e0 dans le projet.');
    state.project.main_articles.push(...newArticles);
    // Extraire le titre du livre depuis l'URL (partie après le dernier /)
    try {
      const bookName = decodeURIComponent(url.split('/').pop()).replace(/_/g, ' ').trim();
      if (bookName) {
        state.project.name = bookName;
        state.project.book_title = bookName;
        $('#projectName').value = bookName;
        $('#breadcrumbProject').textContent = bookName.toLocaleUpperCase('fr');
      }
    } catch { /* titre non critique */ }
    queueSave({ main_articles: state.project.main_articles, name: state.project.name, book_title: state.project.book_title });
    renderWorkspace();
    $('#articleQuery').value = '';
    $('#entryHint').textContent = `${newArticles.length} pages ajout\u00e9es depuis le livre Wikip\u00e9dia.`;
    showToast(`${newArticles.length} pages ajout\u00e9es \u00e0 la s\u00e9lection.`);
  } catch (error) { showToast(`Import du livre impossible\u00a0: ${error.message}`, true); }
  finally { button.disabled = false; button.innerHTML = 'Ajouter <span aria-hidden="true">+</span>'; }
}

async function searchArticles(query) {
  clearTimeout(state.searchTimer);
  if (state.sourceMode !== 'search' || query.trim().length < 2) { $('#searchResults').hidden = true; return; }
  state.searchTimer = setTimeout(async () => {
    const results = $('#searchResults');
    results.hidden = false;
    results.innerHTML = '<div class="search-result"><span><strong>Recherche en cours\u2026</strong></span></div>';
    try {
      const params = new URLSearchParams({ query: query.trim(), language: $('#articleLanguage').value, limit: '8' });
      const items = await getJson(`/api/search?${params}`);
      if ($('#articleQuery').value.trim() !== query.trim()) return;
      results.innerHTML = items.length
        ? items.map((item) => `<button class="search-result" type="button" data-add-title="${escapeHtml(item.title)}" data-page-id="${item.page_id}"><span><strong>${escapeHtml(item.title)}</strong><small>Article Wikip\u00e9dia \u00b7 ${escapeHtml($('#articleLanguage').value.toUpperCase())}</small></span><span class="search-add" aria-hidden="true">+</span></button>`).join('')
        : '<div class="search-result"><span><strong>Aucun r\u00e9sultat</strong><small>Essayez un autre terme de recherche.</small></span></div>';
    } catch (error) {
      results.innerHTML = `<div class="search-result"><span><strong>Recherche indisponible</strong><small>${escapeHtml(error.message)}</small></span></div>`;
    }
  }, 250);
}

async function exploreArticles(event) {
  event.preventDefault();
  if (!state.project || !state.project.main_articles.length) {
    showToast('Ajoutez au moins un article principal avant de lancer l\u2019exploration.', true);
    return;
  }
  const button = $('#exploreForm button[type="submit"]');
  button.disabled = true;
  button.textContent = 'Exploration\u2026';
  try {
    const updated = await getJson('/api/explore', {
      method: 'POST',
      body: JSON.stringify({ project: state.project, max_depth: Number($('#exploreDepth').value), max_articles: Number($('#exploreLimit').value) }),
    });
    setProject(updated);
    state.isDirty = true;
    setSaveState('Exploration \u00e0 enregistrer en JSON');
    showToast(`${updated.discovered_articles.length} article${updated.discovered_articles.length === 1 ? '' : 's'} compl\u00e9mentaire${updated.discovered_articles.length === 1 ? '' : 's'} propos\u00e9${updated.discovered_articles.length === 1 ? '' : 's'}.`);
  } catch (error) { showToast(error.message, true); }
  finally { button.disabled = false; button.textContent = 'Explorer'; }
}

function toggleArticle(card, selected) {
  const key = card.dataset.articleKey;
  activeArticles().forEach((a) => { if (articleKey(a) === key) a.selected = selected; });
  queueSave({ main_articles: state.project.main_articles, discovered_articles: state.project.discovered_articles });
  renderWorkspace();
}

function setMultipleSelection(articles, selected) {
  const keys = new Set(articles.map(articleKey));
  activeArticles().forEach((a) => { if (keys.has(articleKey(a))) a.selected = selected; });
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
  showToast('Article retir\u00e9 de la session.');
}

function updateChapterMembership(key, chapterId) {
  const chapters = (state.project.chapters || []).map((ch) => ({ ...ch, article_keys: ch.article_keys.filter((k) => k !== key) }));
  if (chapterId) chapters.find((ch) => ch.id === chapterId)?.article_keys.push(key);
  state.project.chapters = chapters;
  queueSave({ chapters });
  renderOrganization();
}

function addChapter() {
  const chapters = [...(state.project.chapters || [])];
  chapters.push({ id: crypto.randomUUID(), title: `Chapitre ${chapters.length + 1}`, article_keys: [] });
  state.project.chapters = chapters;
  queueSave({ chapters });
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

async function exportPdf() {
  if (!state.project || !selectedArticles().length) {
    showToast('S\u00e9lectionnez au moins un article avant de g\u00e9n\u00e9rer le PDF.', true);
    return;
  }
  const buttons = [$('#exportButton'), $('#topExportButton')].filter(Boolean);
  buttons.forEach((b) => { b.disabled = true; });
  setSaveState('G\u00e9n\u00e9ration du PDF\u2026');
  try {
    const response = await request('/api/pdf', { method: 'POST', body: JSON.stringify(state.project) });
    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = objectUrl;
    anchor.download = `${(state.project.book_title || state.project.name).replace(/[^a-z0-9-_ ]/gi, '').trim().replace(/\s+/g, '-') || 'livre'}.pdf`;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
    setSaveState(state.isDirty ? 'JSON \u00e0 t\u00e9l\u00e9charger' : 'JSON charg\u00e9 en m\u00e9moire');
    showToast('Votre PDF est pr\u00eat.');
  } catch (error) {
    setSaveState('Erreur de g\u00e9n\u00e9ration');
    showToast(`La g\u00e9n\u00e9ration du PDF a \u00e9chou\u00e9\u00a0: ${error.message}`, true);
  } finally {
    buttons.forEach((b) => { b.disabled = selectedArticles().length === 0; });
  }
}

function exportWorkspace() {
  if (!state.project) return;
  const workspace = { format: 'wikipedia2book-workspace', version: 1, saved_at: new Date().toISOString(), projects: [state.project] };
  const blob = new Blob([JSON.stringify(workspace, null, 2)], { type: 'application/json' });
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = objectUrl;
  anchor.download = 'wikipedia2book-workspace.json';
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(objectUrl);
  state.isDirty = false;
  setSaveState('JSON t\u00e9l\u00e9charg\u00e9');
  showToast('Fichier JSON t\u00e9l\u00e9charg\u00e9 sur votre appareil.');
}

function readWorkspace(payload) {
  if (Array.isArray(payload)) return payload;
  if (payload?.format === 'wikipedia2book-workspace') {
    if (payload.version !== 1 || !Array.isArray(payload.projects)) throw new Error('Version ou structure du fichier JSON non prise en charge.');
    return payload.projects;
  }
  if (payload && typeof payload === 'object' && payload.id && payload.name) return [payload];
  throw new Error('Ce fichier ne contient pas de projet Wikipedia2Book valide.');
}

async function importWorkspace(file) {
  if (state.isDirty && !window.confirm('Les modifications non t\u00e9l\u00e9charg\u00e9es seront remplac\u00e9es. Continuer\u00a0?')) return;
  try {
    const payload = JSON.parse(await file.text());
    const projects = readWorkspace(payload);
    if (projects.some((p) => !p || typeof p.id !== 'string' || typeof p.name !== 'string' || !p.name.trim())) throw new Error('Un projet du fichier est invalide ou sans nom.');
    state.project = normalizeProject(projects[0]);
    state.isDirty = false;
    renderWorkspace();
    setView('sources');
    setSaveState('JSON import\u00e9 en m\u00e9moire');
    showToast(`Projet import\u00e9.`);
  } catch (error) { showToast(`Import JSON impossible\u00a0: ${error.message}`, true); }
  finally { $('#workspaceFileInput').value = ''; }
}

// ── Event listeners ──────────────────────────────────────────────────────────

document.addEventListener('click', async (event) => {
  const viewButton = event.target.closest('[data-view]');
  if (viewButton) { setView(viewButton.dataset.view); return; }
  const modeButton = event.target.closest('[data-source-mode]');
  if (modeButton) {
    state.sourceMode = modeButton.dataset.sourceMode;
    $$('.entry-tab').forEach((tab) => tab.classList.toggle('active', tab === modeButton));
    const defaults = {
      book:   { placeholder: 'https://fr.wikipedia.org/wiki/Utilisateur:…/Livres/…', hint: 'Collez l’URL d’une page de livre Wikipédia pour importer ses liens d’articles.', value: 'https://fr.wikipedia.org/wiki/Utilisateur:474D6F756C617264/Livres/Les_%C3%A9paves_de_la_rade_de_Saint-Pierre_suite_a_l%27%C3%A9ruption_de_la_montagne_Pel%C3%A9e_en_1902' },
      url:    { placeholder: 'https://fr.wikipedia.org/wiki/…', hint: 'Collez une URL HTTPS pointant vers un article Wikipédia.', value: 'https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre' },
      search: { placeholder: 'Rechercher un article…', hint: 'Saisissez quelques mots pour rechercher dans Wikipédia.', value: 'Épaves de la rade de Saint-Pierre' },
    };
    const d = defaults[state.sourceMode];
    $('#articleQuery').placeholder = d.placeholder;
    $('#articleQuery').value = d.value;
    $('#entryHint').textContent = d.hint;
    $('#searchResults').hidden = true;
    return;
  }
  const result = event.target.closest('[data-add-title]');
  if (result) { await addArticle({ title: result.dataset.addTitle, language: $('#articleLanguage').value, page_id: Number(result.dataset.pageId) }); return; }
  if (event.target.closest('#selectDiscoveredButton')) { await setMultipleSelection(state.project.discovered_articles, true); return; }
  if (event.target.closest('#selectVisibleButton')) {
    const visible = new Set($$('#discoveredArticles .article-card').map((c) => c.dataset.articleKey));
    setMultipleSelection(state.project.discovered_articles.filter((a) => visible.has(articleKey(a))), true); return;
  }
  if (event.target.closest('#deselectAllButton')) { await setMultipleSelection(activeArticles(), false); return; }
  if (event.target.closest('#addChapterButton')) { addChapter(); return; }
  if (event.target.closest('#importWorkspaceButton')) { $('#workspaceFileInput').click(); return; }
  if (event.target.closest('#saveWorkspaceButton')) { exportWorkspace(); return; }
  if (event.target.closest('#topExportButton, #exportButton')) { await exportPdf(); return; }
  const articleCardEl = event.target.closest('.article-card');
  if (articleCardEl && event.target.closest('.remove-article')) { await removeArticle(articleCardEl); return; }
  const chapterRow = event.target.closest('.org-chapter-row');
  if (chapterRow && event.target.closest('.chapter-remove')) { removeChapter(chapterRow); return; }
  if (!event.target.closest('#articleQuery, #searchResults')) $('#searchResults').hidden = true;
});

document.addEventListener('change', async (event) => {
  if (event.target.matches('.article-check')) { const card = event.target.closest('.article-card'); await toggleArticle(card, event.target.checked); return; }
  if (event.target.matches('.chapter-select')) { const row = event.target.closest('.org-article'); updateChapterMembership(row.dataset.articleKey, event.target.value); return; }
  if (event.target.matches('#articleLanguage')) { if ($('#articleQuery').value.trim().length >= 2) searchArticles($('#articleQuery').value); return; }
  if (event.target.matches('#originFilter, #depthFilter')) { renderArticles(); return; }
  if (event.target.matches('input[name="orientation"]')) { const layout = collectLayoutSettings(); Object.assign(state.project, layout); queueSave(layout); return; }
  if (event.target.matches('#pageNumbers')) { queueSave({ page_numbers: event.target.checked }); return; }
  const textSettings = { bookTitle: 'book_title', bookSubtitle: 'book_subtitle', bookAuthor: 'book_author', bookIntroduction: 'introduction', bookConclusion: 'conclusion' };
  if (textSettings[event.target.id]) patchSetting(event.target.id, textSettings[event.target.id]);
  const numericSettings = { customWidth: 'custom_width_mm', customHeight: 'custom_height_mm', marginTop: 'margin_top_mm', marginBottom: 'margin_bottom_mm', marginInside: 'margin_inside_mm', marginOutside: 'margin_outside_mm', marginBinding: 'margin_binding_mm' };
  if (numericSettings[event.target.id]) patchSetting(event.target.id, numericSettings[event.target.id], Number);
  if (event.target.matches('#pageFormat')) patchSetting('pageFormat', 'page_format');
});

document.addEventListener('input', (event) => {
  if (event.target.matches('#articleQuery') && state.sourceMode === 'search') searchArticles(event.target.value);
  if (event.target.matches('#articleFilter')) renderArticles();
  if (event.target.matches('#projectName')) {
    const value = event.target.value.trim();
    if (value) { state.project.name = value; queueSave({ name: value }); $('#breadcrumbProject').textContent = value.toLocaleUpperCase('fr'); }
  }
  if (event.target.matches('#projectDescription')) { state.project.description = event.target.value; queueSave({ description: event.target.value }); }
  const chapterNameEl = event.target.closest('.chapter-name');
  if (chapterNameEl && state.project) {
    const row = chapterNameEl.closest('.org-chapter-row');
    const chapter = state.project.chapters.find((c) => c.id === row?.dataset.chapterId);
    if (chapter && chapterNameEl.value.trim()) { chapter.title = chapterNameEl.value; queueSave({ chapters: state.project.chapters }); }
  }
  const textSettings = { bookTitle: 'book_title', bookSubtitle: 'book_subtitle', bookAuthor: 'book_author', bookIntroduction: 'introduction', bookConclusion: 'conclusion' };
  if (textSettings[event.target.id]) { state.project[textSettings[event.target.id]] = event.target.value; queueSave({ [textSettings[event.target.id]]: event.target.value }); }
});

$('#articleForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  const value = $('#articleQuery').value.trim();
  if (!value) { showToast('Saisissez une URL, un titre ou un terme de recherche avant d’ajouter.', true); return; }
  if (state.sourceMode === 'book') await importWikipediaBook(value);
  else if (state.sourceMode === 'url') await addArticle({ url: value, language: $('#articleLanguage').value });
  else await addArticle({ title: value, language: $('#articleLanguage').value });
});
$('#exploreForm').addEventListener('submit', exploreArticles);
$('#workspaceFileInput').addEventListener('change', async (event) => {
  const file = event.target.files?.[0];
  if (file) await importWorkspace(file);
});
window.addEventListener('beforeunload', (event) => {
  if (state.isDirty) { event.preventDefault(); event.returnValue = ''; }
});

loadProjects();
