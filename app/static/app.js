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
    let message = t('common.httpError', { status: response.status });
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

function lang() { return state_i18n.lang; }

function activeArticles() {
  if (!state.project) return [];
  return [...state.project.main_articles, ...state.project.discovered_articles];
}

function selectedArticles() {
  return [...activeArticles(), ...(state.project?.uploaded_documents || [])].filter((a) => a.selected);
}

function articleKey(article) {
  if (article.kind) return `doc:${article.id}`;
  return article.page_id != null
    ? `${article.language}:${article.page_id}`
    : `${article.language}:title:${article.title.toLowerCase()}`;
}

function sameArticle(a, b) {
  if (a.language !== b.language) return false;
  if (a.page_id != null && b.page_id != null) return a.page_id === b.page_id;
  return a.title.toLocaleLowerCase() === b.title.toLocaleLowerCase();
}

function normalizeProject(input) {
  const project = {
    main_articles: [], discovered_articles: [], uploaded_documents: [],
    book_title: '', book_subtitle: '', book_author: '', introduction: '', conclusion: '',
    page_format: 'A4', custom_width_mm: 148, custom_height_mm: 210, orientation: 'portrait',
    margin_top_mm: 18, margin_bottom_mm: 18, margin_inside_mm: 18, margin_outside_mm: 16,
    margin_binding_mm: 0, article_order: [], chapters: [], toc_position: 'start', table_of_contents: true, page_numbers: true, ...input,
  };
  project.main_articles = [...project.main_articles, ...project.discovered_articles.filter((a) => a.selected)];
  project.discovered_articles = project.discovered_articles.filter((a) => !a.selected);
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
  renderUploadedDocuments();
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
  $('#suggestionSource').textContent = source ? t('discovered.source', { title: source }) : '';
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
  return state.project.discovered_articles.filter((a) => !titleFilter || a.title.toLocaleLowerCase(lang()).includes(titleFilter));
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
  const meta = isMain ? [article.language.toUpperCase(), article.origin_title ? t('meta.from', { origin: article.origin_title }) : t('meta.main')] : [article.language.toUpperCase()];
  const summary = article.summary ? `<p class="article-summary">${escapeHtml(article.summary.slice(0, 290))}${article.summary.length > 290 ? '\u2026' : ''}</p>` : '';
  return `<article class="article-card${article.selected ? ' selected' : ''}" data-article-key="${escapeHtml(key)}">
    <div class="article-card-top">
      ${isMain ? `<input class="article-check" type="checkbox" aria-label="${article.selected ? escapeHtml(t('meta.deselect')) : escapeHtml(t('meta.select'))} ${escapeHtml(article.title)}" ${article.selected ? 'checked' : ''}>` : ''}
      <div class="article-title-wrap"><a class="article-title" href="${escapeHtml(article.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(article.title)}</a><div class="article-meta">${meta.map((m) => `<span>${escapeHtml(m)}</span>`).join('')}</div></div>
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
  const slots = [];
  chapters.forEach((chapter) => {
    slots.push({ type: 'chapter', chapter });
    chapter.articles.forEach((a) => slots.push({ type: 'article', article: a, chapterId: chapter.id }));
  });
  if (chapters.length && unassigned.length) slots.push({ type: 'unassigned' });
  unassigned.forEach((a) => slots.push({ type: 'article', article: a, chapterId: '' }));
  if (project.table_of_contents !== false) slots.splice(tocSlotIndex(slots), 0, { type: 'toc' });
  return slots;
}

function slotAnchor(slot) {
  if (slot.type === 'unassigned') return 'chapter:';
  return slot.type === 'chapter' ? `chapter:${slot.chapter.id}` : articleKey(slot.article);
}

function tocSlotIndex(slots) {
  const position = state.project.toc_position || 'start';
  if (position === 'end') return slots.length;
  const index = slots.findIndex((slot) => slotAnchor(slot) === position.replace(/^before:/, ''));
  return index < 0 ? 0 : index;
}

function renderOrganization() {
  const project = state.project;
  const articles = orderedSelectedArticles();
  $('#organizationCount').textContent = articles.length;
  $('#addTocButton').hidden = project.table_of_contents !== false;

  if (!articles.length) {
    $('#organizationList').innerHTML = `<div class="org-empty">${escapeHtml(t('org.emptyListLine1'))}<br>${escapeHtml(t('org.emptyListLine2'))}</div>`;
    return;
  }

  const slots = buildOrgSlots();
  const html = slots.map((slot, idx) => {
    if (slot.type === 'toc') {
      return `<div class="org-row org-toc" draggable="true" data-slot-type="toc" data-slot-index="${idx}">
        <span class="drag-handle" aria-hidden="true">\u2630</span>
        <span class="toc-icon" aria-hidden="true">\u2261</span>
        <div><div class="org-article-title">${escapeHtml(t('org.toc'))}</div><div class="org-article-origin">${escapeHtml(t('org.tocHint'))}</div></div>
        <button class="chapter-remove toc-remove" type="button" title="${escapeHtml(t('org.removeTocTitle'))}">${escapeHtml(t('org.removeToc'))}</button>
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
        <button class="chapter-remove" type="button" title="${escapeHtml(t('org.removeChapterTitle'))}">${escapeHtml(t('org.removeChapter'))}</button>
      </div>`;
    }
    // article (or document import\u00e9, int\u00e9gr\u00e9 comme un article)
    const a = slot.article;
    const k = articleKey(a);
    const chapters = project.chapters || [];
    const chapter = chapters.find((c) => c.article_keys.includes(k));
    const isDoc = Boolean(a.kind);
    const origin = isDoc
      ? (a.kind === 'pdf' ? t('org.docPdf') : t('org.docImage'))
      : (a.origin_title ? t('org.discoveredFrom', { origin: a.origin_title }) : t('org.mainArticleOrigin', { lang: a.language.toUpperCase() }));
    const openHref = isDoc ? `data:${a.mime_type};base64,${a.data_base64}` : a.url;
    const openTitle = isDoc ? t('org.openDocument') : t('org.openWikipedia');
    return `<div class="org-row org-article" draggable="true" data-slot-type="article" data-slot-index="${idx}" data-article-key="${escapeHtml(k)}">
      <span class="drag-handle" aria-hidden="true">\u2630</span>
      <div><div class="org-article-title">${escapeHtml(a.title)}</div><div class="org-article-origin">${escapeHtml(origin)}</div></div>
      <select class="chapter-select" aria-label="${escapeHtml(t('org.chapterSelectAria', { title: a.title }))}"><option value="" ${!chapter ? 'selected' : ''}>${escapeHtml(t('org.noChapterOption'))}</option>${chapters.map((c) => `<option value="${escapeHtml(c.id)}" ${chapter?.id === c.id ? 'selected' : ''}>${escapeHtml(c.title)}</option>`).join('')}</select>
      <a class="article-title org-open" href="${escapeHtml(openHref)}" target="_blank" rel="noopener noreferrer" title="${escapeHtml(openTitle)}" aria-label="${escapeHtml(openTitle)}\u00a0: ${escapeHtml(a.title)}">\u2197</a>
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
  const to = slots[toIndex];
  if (!from || !to) return;

  if (from.type === 'toc') {
    const others = slots.filter((slot) => slot.type !== 'toc');
    const at = others.indexOf(to) + (toIndex > fromIndex ? 1 : 0);
    const position = at >= others.length ? 'end' : at === 0 ? 'start' : `before:${slotAnchor(others[at])}`;
    queueSave({ toc_position: position });
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
  $('#marginPreset').value = marginPresetOf(project);
  $('#bookTitle').placeholder = defaultBookTitle() || t('heading.namePlaceholder');
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
  } catch { /* version non critique */ }
  const now = new Date().toISOString();
  state.project = normalizeProject({ id: crypto.randomUUID(), name: t('heading.defaultName'), created_at: now, updated_at: now });
  renderWorkspace();
  setView('sources');
}

async function suggestIntroAndAuthor(article) {
  if (!state.project || (state.project.introduction && state.project.book_author)) return;
  try {
    const params = new URLSearchParams({ title: article.title, language: article.language });
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

async function addArticle(source) {
  if (!state.project) return;
  const button = $('#addArticleButton');
  button.disabled = true;
  button.textContent = t('export.addingLabel');
  try {
    const article = await getJson('/api/articles', { method: 'POST', body: JSON.stringify(source) });
    if (activeArticles().some((item) => sameArticle(item, article))) throw new Error(t('sources.alreadyInBook'));
    article.selected = true;
    const wasFirst = state.project.main_articles.length === 0;
    state.project.main_articles.push(article);
    queueSave({ main_articles: state.project.main_articles });
    renderWorkspace();
    if (wasFirst) await suggestIntroAndAuthor(article);
    $('#articleQuery').value = '';
    $('#searchResults').hidden = true;
    $('#entryHint').textContent = t('sources.addedToMain');
    showToast(t('sources.articleAdded'));
  } catch (error) { showToast(error.message, true); }
  finally { button.disabled = false; button.innerHTML = `<span data-i18n="sources.addButton">${escapeHtml(t('sources.addButton'))}</span> <span aria-hidden="true">+</span>`; }
}

async function importWikipediaBook(url) {
  if (!state.project) return;
  const button = $('#addArticleButton');
  button.disabled = true;
  button.textContent = t('export.importingLabel');
  try {
    const articles = await getJson('/api/books/import', { method: 'POST', body: JSON.stringify({ url }) });
    const newArticles = articles.filter((a) => !activeArticles().some((e) => sameArticle(e, a)));
    if (!newArticles.length) throw new Error(t('sources.allBookPagesAlready'));
    const wasFirst = state.project.main_articles.length === 0;
    state.project.main_articles.push(...newArticles);
    // Extraire le titre du livre depuis l'URL (partie après le dernier /)
    try {
      const bookName = decodeURIComponent(url.split('/').pop()).replace(/_/g, ' ').trim();
      if (bookName) {
        state.project.name = bookName;
        state.project.book_title = bookName;
      }
    } catch { /* titre non critique */ }
    queueSave({ main_articles: state.project.main_articles, name: state.project.name, book_title: state.project.book_title });
    renderWorkspace();
    if (wasFirst) await suggestIntroAndAuthor(newArticles[0]);
    $('#articleQuery').value = '';
    const bookLink = `<a href="https://fr.wikipedia.org/wiki/Aide:Livres" target="_blank" rel="noopener noreferrer">${escapeHtml(t('sources.bookLinkText'))}</a>`;
    $('#entryHint').innerHTML = t('sources.pagesAddedHint', { n: newArticles.length, link: bookLink });
    showToast(t('sources.pagesAddedToast', { n: newArticles.length }));
  } catch (error) { showToast(t('sources.bookImportFailed', { error: error.message }), true); }
  finally { button.disabled = false; button.innerHTML = `<span data-i18n="sources.addButton">${escapeHtml(t('sources.addButton'))}</span> <span aria-hidden="true">+</span>`; }
}

async function searchArticles(query) {
  clearTimeout(state.searchTimer);
  if (state.sourceMode !== 'search' || query.trim().length < 2) { $('#searchResults').hidden = true; return; }
  state.searchTimer = setTimeout(async () => {
    const results = $('#searchResults');
    results.hidden = false;
    results.innerHTML = `<div class="search-result"><span><strong>${escapeHtml(t('sources.searching'))}</strong></span></div>`;
    try {
      const params = new URLSearchParams({ query: query.trim(), language: $('#articleLanguage').value, limit: '8' });
      const items = await getJson(`/api/search?${params}`);
      if ($('#articleQuery').value.trim() !== query.trim()) return;
      results.innerHTML = items.length
        ? items.map((item) => `<button class="search-result" type="button" data-add-title="${escapeHtml(item.title)}" data-page-id="${item.page_id}"><span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(t('sources.wikipediaArticleLabel'))} \u00b7 ${escapeHtml($('#articleLanguage').value.toUpperCase())}</small></span><span class="search-add" aria-hidden="true">+</span></button>`).join('')
        : `<div class="search-result"><span><strong>${escapeHtml(t('sources.noResultsTitle'))}</strong><small>${escapeHtml(t('sources.noResultsDesc'))}</small></span></div>`;
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

function renderUploadedDocuments() {
  const docs = state.project.uploaded_documents || [];
  $('#uploadedDocumentsList').innerHTML = docs.length
    ? docs.map((d) => `<div class="uploaded-document-row" data-doc-id="${escapeHtml(d.id)}">
        <input class="doc-check" type="checkbox" ${d.selected ? 'checked' : ''} aria-label="${d.selected ? escapeHtml(t('meta.deselect')) : escapeHtml(t('meta.select'))} ${escapeHtml(d.title)}">
        <span class="doc-title">${escapeHtml(d.title)}</span>
        <span class="doc-kind">${d.kind === 'pdf' ? 'PDF' : escapeHtml(t('common.image'))}</span>
        <button class="icon-button doc-remove" type="button" title="${escapeHtml(t('org.docRemoveTitle'))}" aria-label="${escapeHtml(t('org.docRemoveTitle'))} : ${escapeHtml(d.title)}">×</button>
      </div>`).join('')
    : `<p class="field-hint">${escapeHtml(t('org.noDocuments'))}</p>`;
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

function toggleUploadedDocument(id, selected) {
  (state.project.uploaded_documents || []).forEach((d) => { if (d.id === id) d.selected = selected; });
  queueSave({ uploaded_documents: state.project.uploaded_documents });
  renderWorkspace();
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

function updateChapterMembership(key, chapterId) {
  const chapters = (state.project.chapters || []).map((ch) => ({ ...ch, article_keys: ch.article_keys.filter((k) => k !== key) }));
  if (chapterId) chapters.find((ch) => ch.id === chapterId)?.article_keys.push(key);
  state.project.chapters = chapters;
  queueSave({ chapters });
  renderOrganization();
}

function addChapter() {
  const chapters = [...(state.project.chapters || [])];
  chapters.push({ id: crypto.randomUUID(), title: t('org.newChapterTitle', { n: chapters.length + 1 }), article_keys: [] });
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

function showPdfProgress(event) {
  $('#pdfProgress').hidden = false;
  $('#pdfProgressStep').textContent = event ? t('progress.step', { step: event.step, total: event.total }) : '';
  $('#pdfProgressLabel').textContent = event ? t(`progress.${event.code}`, { title: event.title || '' }) : t('progress.starting');
  $('#pdfProgressFill').style.width = event ? `${Math.round((event.step / event.total) * 100)}%` : '0%';
}

function hidePdfProgress() { $('#pdfProgress').hidden = true; }

function pdfStreamEvent(line) {
  if (!line.trim()) return null;
  const event = JSON.parse(line);
  if (event.type === 'progress') { showPdfProgress(event); return null; }
  if (event.type === 'error') throw new Error(event.detail);
  if (event.type === 'done') {
    const bytes = Uint8Array.from(atob(event.pdf_base64), (c) => c.charCodeAt(0));
    return new Blob([bytes], { type: 'application/pdf' });
  }
  return null;
}

async function streamPdf(project) {
  const response = await request(`/api/pdf/stream?language=${encodeURIComponent(lang())}`, { method: 'POST', body: JSON.stringify(project) });
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  for (;;) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const lines = buffer.split('\n');
    buffer = done ? '' : lines.pop();
    for (const line of lines) {
      const blob = pdfStreamEvent(line);
      if (blob) return blob;
    }
    if (done) throw new Error(t('progress.interrupted'));
  }
}

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
    const blob = await streamPdf(state.project);
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = objectUrl;
    anchor.download = `${bookFileName(state.project)}.pdf`;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
    setSaveState(state.isDirty ? t('export.toDownload') : t('export.loadedInMemory'));
    showToast(t('export.ready'));
  } catch (error) {
    setSaveState(t('export.error'));
    showToast(t('export.failed', { error: error.message }), true);
  } finally {
    hidePdfProgress();
    buttons.forEach((b) => { b.disabled = false; });
  }
}

function bookFileName(project) {
  return (project.book_title || defaultBookTitle() || project.name).replace(/[^a-z0-9-_ ]/gi, '').trim().replace(/\s+/g, '-') || 'livre';
}

function exportWorkspace() {
  if (!state.project) return;
  const workspace = { format: 'wikipedia2book-workspace', version: 1, saved_at: new Date().toISOString(), projects: [state.project] };
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

async function importWorkspace(file) {
  if (state.isDirty && !window.confirm(t('export.confirmReplace'))) return;
  try {
    const payload = JSON.parse(await file.text());
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

function sourceModeDefaults(mode) {
  return {
    book:   { placeholder: 'https://fr.wikipedia.org/wiki/Utilisateur:…/Livres/…', hint: t('sources.hintBook'), value: 'https://fr.wikipedia.org/wiki/Utilisateur:474D6F756C617264/Livres/Les_%C3%A9paves_de_la_rade_de_Saint-Pierre_suite_a_l%27%C3%A9ruption_de_la_montagne_Pel%C3%A9e_en_1902' },
    url:    { placeholder: 'https://fr.wikipedia.org/wiki/…', hint: t('sources.hintUrl'), value: 'https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre' },
    search: { placeholder: t('sources.placeholderSearch'), hint: t('sources.hintSearch'), value: 'Épaves de la rade de Saint-Pierre' },
  }[mode];
}

document.addEventListener('click', async (event) => {
  const viewButton = event.target.closest('[data-view]');
  if (viewButton) {
    setView(viewButton.dataset.view);
    if (viewButton.closest('.step-footer')) window.scrollTo({ top: 0, behavior: 'smooth' });
    return;
  }
  const modeButton = event.target.closest('[data-source-mode]');
  if (modeButton) {
    state.sourceMode = modeButton.dataset.sourceMode;
    $$('.entry-tab').forEach((tab) => tab.classList.toggle('active', tab === modeButton));
    const d = sourceModeDefaults(state.sourceMode);
    $('#articleQuery').placeholder = d.placeholder;
    $('#articleQuery').value = d.value;
    $('#entryHint').textContent = d.hint;
    $('#searchResults').hidden = true;
    return;
  }
  const result = event.target.closest('[data-add-title]');
  if (result) { await addArticle({ title: result.dataset.addTitle, language: $('#articleLanguage').value, page_id: Number(result.dataset.pageId) }); return; }
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
  if (event.target.closest('.toc-remove')) {
    queueSave({ table_of_contents: false });
    renderOrganization();
    showToast(t('org.tocRemovedToast'));
    return;
  }
  if (event.target.closest('#addTocButton')) {
    queueSave({ table_of_contents: true, toc_position: 'start' });
    renderOrganization();
    return;
  }
  if (event.target.closest('#uploadDocumentButton')) { $('#documentFileInput').click(); return; }
  if (event.target.closest('#importWorkspaceButton')) { $('#workspaceFileInput').click(); return; }
  if (event.target.closest('#saveWorkspaceButton')) { exportWorkspace(); return; }
  if (event.target.closest('#topExportButton, #exportButton')) { await exportPdf(); return; }
  const articleCardEl = event.target.closest('.article-card');
  if (articleCardEl && event.target.closest('.remove-article')) { await removeArticle(articleCardEl); return; }
  const chapterRow = event.target.closest('.org-chapter-row');
  if (chapterRow && event.target.closest('.chapter-remove')) { removeChapter(chapterRow); return; }
  const docRow = event.target.closest('.uploaded-document-row');
  if (docRow && event.target.closest('.doc-remove')) { removeUploadedDocument(docRow.dataset.docId); return; }
  if (!event.target.closest('#articleQuery, #searchResults')) $('#searchResults').hidden = true;
});

document.addEventListener('change', async (event) => {
  if (event.target.matches('.article-check')) { const card = event.target.closest('.article-card'); await toggleArticle(card, event.target.checked); return; }
  if (event.target.matches('.doc-check')) { const row = event.target.closest('.uploaded-document-row'); toggleUploadedDocument(row.dataset.docId, event.target.checked); return; }
  if (event.target.matches('.chapter-select')) { const row = event.target.closest('.org-article'); updateChapterMembership(row.dataset.articleKey, event.target.value); return; }
  if (event.target.matches('#articleLanguage')) { if ($('#articleQuery').value.trim().length >= 2) searchArticles($('#articleQuery').value); return; }
  if (event.target.matches('input[name="orientation"]')) { const layout = collectLayoutSettings(); Object.assign(state.project, layout); queueSave(layout); return; }
  if (event.target.matches('#pageNumbers')) { queueSave({ page_numbers: event.target.checked }); return; }
  const textSettings = { bookTitle: 'book_title', bookDescription: 'description', bookSubtitle: 'book_subtitle', bookAuthor: 'book_author', bookIntroduction: 'introduction', bookConclusion: 'conclusion' };
  if (textSettings[event.target.id]) patchSetting(event.target.id, textSettings[event.target.id]);
  const numericSettings = { customWidth: 'custom_width_mm', customHeight: 'custom_height_mm', marginTop: 'margin_top_mm', marginBottom: 'margin_bottom_mm', marginInside: 'margin_inside_mm', marginOutside: 'margin_outside_mm', marginBinding: 'margin_binding_mm' };
  if (numericSettings[event.target.id]) patchSetting(event.target.id, numericSettings[event.target.id], Number);
  if (event.target.matches('#pageFormat')) patchSetting('pageFormat', 'page_format');
  if (event.target.matches('#marginPreset')) applyMarginPreset(event.target.value);
  if (numericSettings[event.target.id]?.startsWith('margin_')) $('#marginPreset').value = marginPresetOf(state.project);
});

document.addEventListener('input', (event) => {
  if (event.target.matches('#articleQuery') && state.sourceMode === 'search') searchArticles(event.target.value);
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
  if (state.sourceMode === 'book') await importWikipediaBook(value);
  else if (state.sourceMode === 'url') await addArticle({ url: value, language: $('#articleLanguage').value });
  else await addArticle({ title: value, language: $('#articleLanguage').value });
});
$('#documentFileInput').addEventListener('change', async (event) => {
  const files = [...(event.target.files || [])];
  event.target.value = '';
  if (files.length) await handleDocumentUpload(files);
});
$('#workspaceFileInput').addEventListener('change', async (event) => {
  const file = event.target.files?.[0];
  if (file) await importWorkspace(file);
});
window.addEventListener('beforeunload', (event) => {
  if (state.isDirty) { event.preventDefault(); event.returnValue = ''; }
});
$('#languageSelect').addEventListener('change', (event) => {
  setLanguage(event.target.value);
  const d = sourceModeDefaults(state.sourceMode);
  $('#articleQuery').placeholder = d.placeholder;
  if (!$('#articleQuery').value.trim()) $('#entryHint').textContent = d.hint;
  if (state.project) renderWorkspace();
});

loadProjects();
