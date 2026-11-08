const API = '';
const state = {
  projects: [],
  project: null,
  activeView: 'sources',
  sourceMode: 'search',
  searchTimer: null,
  saveTimer: null,
  toastTimer: null,
  pendingPatch: {},
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function escapeHtml(value = '') {
  return String(value).replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[character]);
}

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers },
  });
  if (!response.ok) {
    let message = `Erreur ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail || message;
    } catch { /* The response may not be JSON. */ }
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

function setSaveState(value) {
  $('#saveState').textContent = value;
}

function projectPath(suffix = '') {
  return `/api/projects/${encodeURIComponent(state.project.id)}${suffix}`;
}

function activeArticles() {
  if (!state.project) return [];
  return [...state.project.main_articles, ...state.project.discovered_articles];
}

function selectedArticles() {
  return activeArticles().filter((article) => article.selected);
}

function normalizeProject(project) {
  return {
    book_title: '', book_subtitle: '', book_author: '', introduction: '', conclusion: '',
    page_format: 'A5', custom_width_mm: 148, custom_height_mm: 210, orientation: 'portrait',
    margin_top_mm: 18, margin_bottom_mm: 18, margin_inside_mm: 18, margin_outside_mm: 16,
    margin_binding_mm: 0, article_order: [], chapters: [], ...project,
  };
}

function renderProjects() {
  const list = $('#projectList');
  list.innerHTML = state.projects.map((project) => `
    <button class="project-link${state.project?.id === project.id ? ' active' : ''}" type="button" data-project-id="${escapeHtml(project.id)}" title="${escapeHtml(project.name)}">
      <span class="project-glyph" aria-hidden="true">${escapeHtml((project.name || 'W').trim().slice(0, 1).toUpperCase())}</span>
      <span class="project-link-name">${escapeHtml(project.name)}</span>
    </button>`).join('');
}

function renderWorkspace() {
  const hasProject = Boolean(state.project);
  $('#welcomeView').hidden = hasProject;
  $('#projectWorkspace').hidden = !hasProject;
  $('#topExportButton').disabled = !hasProject || selectedArticles().length === 0;
  $('#breadcrumbProject').textContent = hasProject ? state.project.name.toLocaleUpperCase('fr') : 'NOUVEAU PROJET';
  if (!hasProject) return;

  const nameInput = $('#projectName');
  const descriptionInput = $('#projectDescription');
  if (document.activeElement !== nameInput) nameInput.value = state.project.name;
  if (document.activeElement !== descriptionInput) descriptionInput.value = state.project.description || '';
  $('#sourceCount').textContent = activeArticles().length;
  $('#selectedCount').textContent = selectedArticles().length;
  $('#organizationCount').textContent = selectedArticles().length;
  renderArticles();
  renderOrganization();
  renderBookSettings();
  renderProjects();
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
    ? project.main_articles.map((article) => articleCard(article, true)).join('')
    : emptyList('Aucun article principal', 'Recherchez un article ou ajoutez une URL Wikipédia.');

  const origins = [...new Set(project.discovered_articles.map((article) => article.origin_title).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'fr'));
  const originSelect = $('#originFilter');
  const selectedOrigin = originSelect.value;
  originSelect.innerHTML = '<option value="">Toutes les origines</option>' + origins.map((origin) => `<option value="${escapeHtml(origin)}">${escapeHtml(origin)}</option>`).join('');
  originSelect.value = origins.includes(selectedOrigin) ? selectedOrigin : '';

  const titleFilter = $('#articleFilter').value.trim().toLocaleLowerCase('fr');
  const originFilter = originSelect.value;
  const depthFilter = $('#depthFilter').value;
  const visible = project.discovered_articles.filter((article) => {
    return (!titleFilter || article.title.toLocaleLowerCase('fr').includes(titleFilter))
      && (!originFilter || article.origin_title === originFilter)
      && (!depthFilter || String(article.depth) === depthFilter);
  });
  $('#discoveredArticles').innerHTML = visible.length
    ? visible.map((article) => articleCard(article, false)).join('')
    : emptyList(project.discovered_articles.length ? 'Aucun résultat' : 'Pas encore de suggestions', project.discovered_articles.length ? 'Modifiez vos filtres.' : 'L’exploration proposera des articles, sans les ajouter automatiquement au livre.');
  const hasDiscovered = project.discovered_articles.length > 0;
  $('#selectDiscoveredButton').disabled = !hasDiscovered;
  $('#selectVisibleButton').disabled = visible.length === 0;
  $('#deselectAllButton').disabled = !selectedArticles().length;
}

function articleCard(article, isMain) {
  const key = `${article.language}:${article.page_id}`;
  const meta = [article.language.toUpperCase(), article.depth ? `Niveau ${article.depth}` : 'Principal', article.origin_title ? `Depuis ${article.origin_title}` : ''].filter(Boolean);
  const summary = article.summary ? `<p class="article-summary">${escapeHtml(article.summary.slice(0, 290))}${article.summary.length > 290 ? '…' : ''}</p>` : '';
  return `<article class="article-card${article.selected ? ' selected' : ''}" data-article-key="${escapeHtml(key)}">
    <div class="article-card-top">
      <input class="article-check" type="checkbox" aria-label="${article.selected ? 'Désélectionner' : 'Sélectionner'} ${escapeHtml(article.title)}" ${article.selected ? 'checked' : ''}>
      <div class="article-title-wrap"><a class="article-title" href="${escapeHtml(article.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(article.title)}</a><div class="article-meta">${meta.map((item) => `<span>${escapeHtml(item)}</span>`).join('')}</div></div>
      ${isMain ? '<button class="remove-article" type="button" title="Retirer cet article" aria-label="Retirer cet article">×</button>' : ''}
    </div>${summary}</article>`;
}

function emptyList(title, description) {
  return `<div class="empty-list"><strong>${escapeHtml(title)}</strong>${escapeHtml(description)}</div>`;
}

function orderedSelectedArticles() {
  const selected = selectedArticles();
  const byKey = new Map(selected.map((article) => [`${article.language}:${article.page_id}`, article]));
  const order = state.project.article_order || [];
  const ordered = order.map((key) => byKey.get(key)).filter(Boolean);
  const seen = new Set(ordered.map((article) => `${article.language}:${article.page_id}`));
  selected.forEach((article) => {
    const key = `${article.language}:${article.page_id}`;
    if (!seen.has(key)) ordered.push(article);
  });
  return ordered;
}

function renderOrganization() {
  const project = state.project;
  const articles = orderedSelectedArticles();
  $('#organizationCount').textContent = articles.length;
  if (!articles.length) {
    $('#organizationList').innerHTML = '<div class="org-empty">Aucun article retenu pour l’instant.<br>Revenez à l’étape Sources et cochez les articles à inclure.</div>';
    return;
  }
  const groups = [{ id: '', title: 'Sans chapitre', articles: [] }, ...(project.chapters || []).map((chapter) => ({ ...chapter, articles: [] }))];
  const chapterByArticle = new Map();
  (project.chapters || []).forEach((chapter) => chapter.article_keys.forEach((key) => chapterByArticle.set(key, chapter.id)));
  articles.forEach((article) => {
    const key = `${article.language}:${article.page_id}`;
    const group = groups.find((candidate) => candidate.id === (chapterByArticle.get(key) || '')) || groups[0];
    group.articles.push(article);
  });
  $('#organizationList').innerHTML = groups.filter((group) => group.articles.length || group.id).map((group, groupIndex) => `
    <section class="org-chapter" data-chapter-id="${escapeHtml(group.id)}">
      <div class="chapter-heading"><span class="chapter-letter">${group.id ? String.fromCharCode(65 + (groupIndex - 1) % 26) : '·'}</span>
        ${group.id ? `<input class="chapter-name" aria-label="Titre du chapitre" value="${escapeHtml(group.title)}" maxlength="120"><button class="chapter-remove" type="button" title="Supprimer le chapitre">Supprimer</button>` : '<strong class="chapter-name-label">Sans chapitre</strong>'}
      </div>
      ${group.articles.map((article) => organizationArticle(article, articles, project.chapters || [])).join('')}
    </section>`).join('');
}

function organizationArticle(article, articles, chapters) {
  const key = `${article.language}:${article.page_id}`;
  const index = articles.findIndex((item) => `${item.language}:${item.page_id}` === key);
  const chapter = chapters.find((item) => item.article_keys.includes(key));
  return `<div class="org-article" data-article-key="${escapeHtml(key)}">
    <div class="order-controls"><button type="button" data-move="up" aria-label="Monter ${escapeHtml(article.title)}" ${index === 0 ? 'disabled' : ''}>↑</button><button type="button" data-move="down" aria-label="Descendre ${escapeHtml(article.title)}" ${index === articles.length - 1 ? 'disabled' : ''}>↓</button></div>
    <div><div class="org-article-title">${escapeHtml(article.title)}</div><div class="org-article-origin">${escapeHtml(article.origin_title ? `Découvert depuis ${article.origin_title}` : `Article principal · ${article.language.toUpperCase()}`)}</div></div>
    <select class="chapter-select" aria-label="Chapitre de ${escapeHtml(article.title)}"><option value="" ${!chapter ? 'selected' : ''}>Sans chapitre</option>${chapters.map((item) => `<option value="${escapeHtml(item.id)}" ${chapter?.id === item.id ? 'selected' : ''}>${escapeHtml(item.title)}</option>`).join('')}</select>
    <a class="article-title org-open" href="${escapeHtml(article.url)}" target="_blank" rel="noopener noreferrer" title="Ouvrir sur Wikipédia" aria-label="Ouvrir ${escapeHtml(article.title)} sur Wikipédia">↗</a>
  </div>`;
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
    const element = $(`#${id}`);
    if (document.activeElement !== element) element.value = project[field] ?? '';
  });
  const orientation = $(`input[name="orientation"][value="${project.orientation || 'portrait'}"]`);
  if (orientation) orientation.checked = true;
  $('#customDimensions').hidden = project.page_format !== 'custom';
}

function setProject(project) {
  state.project = normalizeProject(project);
  state.pendingPatch = {};
  renderWorkspace();
  setView(state.activeView);
}

async function openProject(projectId) {
  try {
    setSaveState('Ouverture…');
    const project = await getJson(`/api/projects/${encodeURIComponent(projectId)}`);
    setProject(project);
    setSaveState('Tout est enregistré');
  } catch (error) {
    setSaveState('Erreur de chargement');
    showToast(error.message, true);
  }
}

function queueSave(patch) {
  if (!state.project) return;
  Object.assign(state.pendingPatch, patch);
  setSaveState('Modifications en cours…');
  clearTimeout(state.saveTimer);
  state.saveTimer = setTimeout(savePending, 450);
}

async function savePending() {
  if (!state.project || !Object.keys(state.pendingPatch).length) return;
  const patch = state.pendingPatch;
  state.pendingPatch = {};
  try {
    const updated = await getJson(projectPath(), { method: 'PATCH', body: JSON.stringify(patch) });
    state.project = normalizeProject({ ...state.project, ...updated });
    const projectIndex = state.projects.findIndex((project) => project.id === updated.id);
    if (projectIndex >= 0) state.projects[projectIndex] = { ...state.projects[projectIndex], ...updated };
    renderProjects();
    $('#breadcrumbProject').textContent = state.project.name.toLocaleUpperCase('fr');
    setSaveState('Tout est enregistré');
  } catch (error) {
    Object.assign(state.pendingPatch, patch);
    setSaveState('Échec de l’enregistrement');
    showToast(`Enregistrement impossible : ${error.message}`, true);
  }
}

async function flushSave() {
  clearTimeout(state.saveTimer);
  await savePending();
}

async function refreshProject() {
  if (!state.project) return;
  const project = await getJson(projectPath());
  setProject(project);
}

async function loadProjects() {
  try {
    state.projects = await getJson('/api/projects');
    $('#connectionDot').classList.add('online');
    $('#connectionStatus').textContent = 'API connectée';
    renderProjects();
    if (state.projects.length) await openProject(state.projects[0].id);
    else renderWorkspace();
  } catch (error) {
    $('#connectionDot').classList.add('offline');
    $('#connectionStatus').textContent = 'API indisponible';
    renderWorkspace();
    showToast(`Impossible de joindre l’API : ${error.message}`, true);
  }
}

function openProjectDialog() {
  $('#newProjectName').value = '';
  $('#newProjectDescription').value = '';
  $('#projectDialog').showModal();
  $('#newProjectName').focus();
}

async function createProject(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  try {
    const project = await getJson('/api/projects', {
      method: 'POST',
      body: JSON.stringify({ name: $('#newProjectName').value.trim(), description: $('#newProjectDescription').value.trim() }),
    });
    $('#projectDialog').close();
    state.projects.unshift(project);
    renderProjects();
    setProject(project);
    setView('sources');
    showToast('Projet créé. Vous pouvez ajouter votre premier article.');
  } catch (error) { showToast(error.message, true); }
}

async function deleteProject() {
  if (!state.project || !window.confirm(`Supprimer « ${state.project.name} » et tous ses réglages ?`)) return;
  try {
    await request(projectPath(), { method: 'DELETE' });
    state.projects = state.projects.filter((project) => project.id !== state.project.id);
    state.project = null;
    renderProjects();
    renderWorkspace();
    showToast('Projet supprimé.');
    if (state.projects.length) await openProject(state.projects[0].id);
  } catch (error) { showToast(error.message, true); }
}

async function addArticle(source) {
  if (!state.project) return;
  const button = $('#addArticleButton');
  button.disabled = true;
  button.textContent = 'Ajout…';
  try {
    const updated = await getJson(projectPath('/articles'), { method: 'POST', body: JSON.stringify(source) });
    setProject(updated);
    $('#articleQuery').value = '';
    $('#searchResults').hidden = true;
    $('#entryHint').textContent = 'Article ajouté aux articles principaux.';
    showToast('Article principal ajouté.');
  } catch (error) { showToast(error.message, true); }
  finally { button.disabled = false; button.innerHTML = 'Ajouter <span aria-hidden="true">+</span>'; }
}

async function searchArticles(query) {
  clearTimeout(state.searchTimer);
  if (state.sourceMode !== 'search' || query.trim().length < 2) {
    $('#searchResults').hidden = true;
    return;
  }
  state.searchTimer = setTimeout(async () => {
    const results = $('#searchResults');
    results.hidden = false;
    results.innerHTML = '<div class="search-result"><span><strong>Recherche en cours…</strong></span></div>';
    try {
      const params = new URLSearchParams({ query: query.trim(), language: $('#articleLanguage').value, limit: '8' });
      const items = await getJson(`/api/search?${params}`);
      if ($('#articleQuery').value.trim() !== query.trim()) return;
      results.innerHTML = items.length ? items.map((item) => `
        <button class="search-result" type="button" data-add-title="${escapeHtml(item.title)}">
          <span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.snippet || 'Article Wikipédia')}${item.snippet ? ' · ' : ''}</small></span><span class="search-add" aria-hidden="true">+</span>
        </button>`).join('') : '<div class="search-result"><span><strong>Aucun résultat</strong><small>Essayez un autre terme de recherche.</small></span></div>';
    } catch (error) {
      results.innerHTML = `<div class="search-result"><span><strong>Recherche indisponible</strong><small>${escapeHtml(error.message)}</small></span></div>`;
    }
  }, 250);
}

async function exploreArticles(event) {
  event.preventDefault();
  if (!state.project || !state.project.main_articles.length) {
    showToast('Ajoutez au moins un article principal avant de lancer l’exploration.', true);
    return;
  }
  const button = $('#exploreForm button[type="submit"]');
  button.disabled = true;
  button.textContent = 'Exploration…';
  try {
    const updated = await getJson(projectPath('/explore'), {
      method: 'POST',
      body: JSON.stringify({ max_depth: Number($('#exploreDepth').value), max_articles: Number($('#exploreLimit').value) }),
    });
    setProject(updated);
    showToast(`${updated.discovered_articles.length} article${updated.discovered_articles.length === 1 ? '' : 's'} complémentaire${updated.discovered_articles.length === 1 ? '' : 's'} proposé${updated.discovered_articles.length === 1 ? '' : 's'}.`);
  } catch (error) { showToast(error.message, true); }
  finally { button.disabled = false; button.textContent = 'Explorer'; }
}

async function saveSelection() {
  const keys = selectedArticles().map((article) => `${article.language}:${article.page_id}`);
  const updated = await getJson(projectPath('/selection'), { method: 'PUT', body: JSON.stringify({ article_keys: keys }) });
  setProject(updated);
}

async function toggleArticle(card, selected) {
  const key = card.dataset.articleKey;
  activeArticles().forEach((article) => {
    if (`${article.language}:${article.page_id}` === key) article.selected = selected;
  });
  renderWorkspace();
  try { await saveSelection(); } catch (error) { showToast(error.message, true); await refreshProject(); }
}

async function setMultipleSelection(articles, selected) {
  const keys = new Set(articles.map((article) => `${article.language}:${article.page_id}`));
  activeArticles().forEach((article) => {
    if (keys.has(`${article.language}:${article.page_id}`)) article.selected = selected;
  });
  renderWorkspace();
  try { await saveSelection(); } catch (error) { showToast(error.message, true); await refreshProject(); }
}

async function removeArticle(card) {
  const [language, pageId] = card.dataset.articleKey.split(':');
  try {
    const updated = await getJson(projectPath(`/articles/${encodeURIComponent(language)}/${encodeURIComponent(pageId)}`), { method: 'DELETE' });
    setProject(updated);
    showToast('Article retiré du projet.');
  } catch (error) { showToast(error.message, true); }
}

function updateArticleOrder(key, direction) {
  const articles = orderedSelectedArticles();
  const currentIndex = articles.findIndex((article) => `${article.language}:${article.page_id}` === key);
  const nextIndex = currentIndex + (direction === 'up' ? -1 : 1);
  if (currentIndex < 0 || nextIndex < 0 || nextIndex >= articles.length) return;
  [articles[currentIndex], articles[nextIndex]] = [articles[nextIndex], articles[currentIndex]];
  queueSave({ article_order: articles.map((article) => `${article.language}:${article.page_id}`) });
  state.project.article_order = articles.map((article) => `${article.language}:${article.page_id}`);
  renderOrganization();
}

function updateChapterMembership(key, chapterId) {
  const chapters = (state.project.chapters || []).map((chapter) => ({ ...chapter, article_keys: chapter.article_keys.filter((item) => item !== key) }));
  if (chapterId) chapters.find((chapter) => chapter.id === chapterId)?.article_keys.push(key);
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
  last?.focus();
  last?.select();
}

function removeChapter(section) {
  const id = section.dataset.chapterId;
  state.project.chapters = state.project.chapters.filter((chapter) => chapter.id !== id);
  queueSave({ chapters: state.project.chapters });
  renderOrganization();
}

function patchSetting(id, field, transform = (value) => value) {
  const element = $(`#${id}`);
  const value = transform(element.value);
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
    showToast('Sélectionnez au moins un article avant de générer le PDF.', true);
    return;
  }
  await flushSave();
  const buttons = [$('#exportButton'), $('#topExportButton')].filter(Boolean);
  buttons.forEach((button) => { button.disabled = true; });
  setSaveState('Génération du PDF…');
  try {
    const response = await request(projectPath('/pdf'), { method: 'POST' });
    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = objectUrl;
    anchor.download = `Wikipedia2Book-${(state.project.book_title || state.project.name).replace(/[^a-z0-9-_ ]/gi, '').trim().replace(/\s+/g, '-') || 'livre'}.pdf`;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
    setSaveState('Tout est enregistré');
    showToast('Votre PDF est prêt.');
  } catch (error) {
    setSaveState('Erreur de génération');
    showToast(`La génération du PDF a échoué : ${error.message}`, true);
  } finally {
    buttons.forEach((button) => { button.disabled = selectedArticles().length === 0; });
  }
}

function exportProjectConfig() {
  if (!state.project) return;
  const blob = new Blob([JSON.stringify(state.project, null, 2)], { type: 'application/json' });
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = objectUrl;
  anchor.download = `${state.project.name.replace(/[^a-z0-9-_ ]/gi, '').trim().replace(/\s+/g, '-') || 'projet'}.json`;
  anchor.click();
  URL.revokeObjectURL(objectUrl);
}

document.addEventListener('click', async (event) => {
  const projectButton = event.target.closest('[data-project-id]');
  if (projectButton) { await openProject(projectButton.dataset.projectId); return; }
  const viewButton = event.target.closest('[data-view]');
  if (viewButton) { await flushSave(); setView(viewButton.dataset.view); return; }
  const modeButton = event.target.closest('[data-source-mode]');
  if (modeButton) {
    state.sourceMode = modeButton.dataset.sourceMode;
    $$('.entry-tab').forEach((tab) => tab.classList.toggle('active', tab === modeButton));
    $('#articleQuery').placeholder = state.sourceMode === 'url' ? 'https://fr.wikipedia.org/wiki/…' : 'Rechercher un article…';
    $('#entryHint').textContent = state.sourceMode === 'url' ? 'Collez une URL HTTPS pointant vers un article Wikipédia.' : 'Saisissez quelques mots pour rechercher dans Wikipédia.';
    $('#searchResults').hidden = true;
    $('#articleQuery').value = '';
    return;
  }
  const result = event.target.closest('[data-add-title]');
  if (result) { await addArticle({ title: result.dataset.addTitle, language: $('#articleLanguage').value }); return; }
  if (event.target.closest('#newProjectButton, #welcomeNewProject')) { openProjectDialog(); return; }
  if (event.target.closest('#selectDiscoveredButton')) { await setMultipleSelection(state.project.discovered_articles, true); return; }
  if (event.target.closest('#selectVisibleButton')) {
    const visible = $$('#discoveredArticles .article-card').map((card) => card.dataset.articleKey);
    await setMultipleSelection(state.project.discovered_articles.filter((article) => visible.includes(`${article.language}:${article.page_id}`)), true); return;
  }
  if (event.target.closest('#deselectAllButton')) { await setMultipleSelection(activeArticles(), false); return; }
  if (event.target.closest('#addChapterButton')) { addChapter(); return; }
  if (event.target.closest('#deleteProjectButton')) { await deleteProject(); return; }
  if (event.target.closest('#exportConfigButton')) { exportProjectConfig(); return; }
  if (event.target.closest('#topExportButton, #exportButton')) { await exportPdf(); return; }
  if (event.target.closest('#cancelProjectButton')) { $('#projectDialog').close(); return; }
  const articleCardElement = event.target.closest('.article-card');
  if (articleCardElement && event.target.closest('.remove-article')) { await removeArticle(articleCardElement); return; }
  const orgArticle = event.target.closest('.org-article');
  const moveButton = event.target.closest('[data-move]');
  if (orgArticle && moveButton) { updateArticleOrder(orgArticle.dataset.articleKey, moveButton.dataset.move); return; }
  const chapterSection = event.target.closest('.org-chapter');
  if (chapterSection && event.target.closest('.chapter-remove')) removeChapter(chapterSection);
  if (!event.target.closest('#articleQuery, #searchResults')) $('#searchResults').hidden = true;
});

document.addEventListener('change', async (event) => {
  if (event.target.matches('.article-check')) {
    const card = event.target.closest('.article-card');
    await toggleArticle(card, event.target.checked);
    return;
  }
  if (event.target.matches('.chapter-select')) {
    const row = event.target.closest('.org-article');
    updateChapterMembership(row.dataset.articleKey, event.target.value);
    return;
  }
  if (event.target.matches('#articleLanguage')) {
    if ($('#articleQuery').value.trim().length >= 2) searchArticles($('#articleQuery').value);
    return;
  }
  if (event.target.matches('#originFilter, #depthFilter')) { renderArticles(); return; }
  if (event.target.matches('input[name="orientation"]')) {
    const layout = collectLayoutSettings();
    Object.assign(state.project, layout);
    queueSave(layout);
    return;
  }
  const textSettings = {
    bookTitle: 'book_title', bookSubtitle: 'book_subtitle', bookAuthor: 'book_author',
    bookIntroduction: 'introduction', bookConclusion: 'conclusion',
  };
  if (textSettings[event.target.id]) patchSetting(event.target.id, textSettings[event.target.id]);
  const numericSettings = {
    customWidth: 'custom_width_mm', customHeight: 'custom_height_mm', marginTop: 'margin_top_mm',
    marginBottom: 'margin_bottom_mm', marginInside: 'margin_inside_mm', marginOutside: 'margin_outside_mm', marginBinding: 'margin_binding_mm',
  };
  if (numericSettings[event.target.id]) patchSetting(event.target.id, numericSettings[event.target.id], Number);
  if (event.target.matches('#pageFormat')) patchSetting('pageFormat', 'page_format');
});

document.addEventListener('input', (event) => {
  if (event.target.matches('#articleQuery')) {
    if (state.sourceMode === 'search') searchArticles(event.target.value);
  }
  if (event.target.matches('#articleFilter')) renderArticles();
  if (event.target.matches('#projectName')) {
    const value = event.target.value.trim();
    if (value) {
      state.project.name = value;
      queueSave({ name: value });
      $('#breadcrumbProject').textContent = value.toLocaleUpperCase('fr');
      const selected = state.projects.find((project) => project.id === state.project.id);
      if (selected) selected.name = value;
      renderProjects();
    }
  }
  if (event.target.matches('#projectDescription')) {
    state.project.description = event.target.value;
    queueSave({ description: event.target.value });
  }
  const chapterName = event.target.closest('.chapter-name');
  if (chapterName && state.project) {
    const section = chapterName.closest('.org-chapter');
    const chapter = state.project.chapters.find((item) => item.id === section.dataset.chapterId);
    if (chapter && chapterName.value.trim()) {
      chapter.title = chapterName.value;
      queueSave({ chapters: state.project.chapters });
    }
  }
  const textSettings = {
    bookTitle: 'book_title', bookSubtitle: 'book_subtitle', bookAuthor: 'book_author',
    bookIntroduction: 'introduction', bookConclusion: 'conclusion',
  };
  if (textSettings[event.target.id]) {
    state.project[textSettings[event.target.id]] = event.target.value;
    queueSave({ [textSettings[event.target.id]]: event.target.value });
  }
});

$('#articleForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  const value = $('#articleQuery').value.trim();
  if (!value) return;
  if (state.sourceMode === 'url') await addArticle({ url: value, language: $('#articleLanguage').value });
  else await addArticle({ title: value, language: $('#articleLanguage').value });
});
$('#exploreForm').addEventListener('submit', exploreArticles);
$('#createProjectForm').addEventListener('submit', createProject);
window.addEventListener('beforeunload', () => {
  if (state.project && Object.keys(state.pendingPatch).length) {
    fetch(projectPath(), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state.pendingPatch),
      keepalive: true,
    });
  }
});

loadProjects();
