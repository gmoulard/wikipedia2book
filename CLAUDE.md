# CLAUDE.md

Instructions pour Claude Code (ou tout agent) travaillant sur ce dépôt.

## Le projet

Wikipedia2Book crée directement un livre PDF imprimable à partir d'articles Wikipédia — il n'y a pas de notion de « projet » dans l'UI ni dans la doc produit (un seul livre, en mémoire, dès l'ouverture de la page). Le comportement de référence est documenté dans [SPECIFICATIONS.md](SPECIFICATIONS.md) : le lire avant toute modification fonctionnelle, et le mettre à jour dans le même changement si le comportement bouge. Ne jamais laisser la spec décrire une fonctionnalité qui n'existe pas dans le code, ni l'inverse.

## Principes de conception à préserver

- **Pas de gestion multi-projets.** Un seul livre à la fois, créé automatiquement en mémoire navigateur. Ne jamais réintroduire un écran de création/liste/suppression de « projets ».
- **Serveur sans état.** Aucune persistance disque côté serveur (pas de DB, pas de fichier projet, pas de PDF stocké). La sauvegarde est entièrement à la charge de l'utilisateur via export/import JSON depuis le navigateur.
- **Le contenu des articles n'est jamais reconstruit, leur format physique si.** Chaque article sélectionné est intégré via le PDF officiel Wikipédia (`/api/rest_v1/page/pdf/{titre}`) : texte, images, références restent ceux de Wikipédia, jamais reparsés/reconstruits en HTML (c'était du code mort, `article_parser.py`, supprimé). En revanche, depuis que « toutes les pages doivent respecter le format d'impression » a été demandé, chaque page (article, document importé, ou générée par l'app) est recomposée — mise à l'échelle et centrée, sans déformation — sur le format/orientation choisis pour le livre (`pdf_generator.fit_page_to_format`/`fit_pdf_to_format`). Ce n'est pas une régression du principe « PDF officiel conservé » : seul le contenu compte, pas la forme physique de la page source.

## Style de code — « vibe coding »

Personne ne lit ce code. En conséquence :

- Pas de commentaires, pas de docstrings, pas de code mort ou « au cas où » (paramètre toujours appelé avec la même valeur, branche jamais atteinte, champ de modèle jamais lu/écrit). Supprimer plutôt que garder.
- Avant de supprimer un symbole (fonction, champ Pydantic, id HTML, classe CSS), `grep` tout le dépôt (`app/`, `app/static/`) pour confirmer qu'il n'est référencé nulle part — y compris côté JS/HTML pour du code backend et inversement.
- `styles.css` a déjà contenu un conflit de fusion Git (`<<<<<<< HEAD` / `=======` / `>>>>>>> ...`) resté commité tel quel pendant plusieurs changements, invisible jusqu'à ce qu'il casse le contraste d'un bouton. Avant toute modification notable de `styles.css`/`app.js`/`index.html`, `grep -n "^<<<<<<<\|^=======$\|^>>>>>>>"` sur le fichier pour s'assurer qu'il n'y a pas de marqueur de conflit oublié.
- Ne jamais utiliser `var(--ink)` (ou toute variable liée au thème clair/sombre) comme `background` d'un élément dont la couleur de texte est fixée en dur (ex. `color: #fff`) : `--ink` est pensé comme couleur de *texte*, qui s'inverse entre thème clair et sombre — en arrière-plan avec un texte fixe, ça rend l'élément illisible dans un des deux thèmes. `.button-dark` et `.toast` utilisent volontairement une couleur sombre fixe (`#1d2927`) pour cette raison, indépendante du thème système.
- La robustesse fonctionnelle reste non négociable malgré l'absence de lecture humaine : gestion des erreurs réseau Wikipédia, validation des entrées, pas d'échec silencieux. « Personne ne lit le code » ne veut pas dire « la fiabilité n'importe pas ».

## Documentation à garder synchronisée

- `SPECIFICATIONS.md` : reflète le comportement réel, pas un objectif futur. Les évolutions non implémentées vont en section 18, pas dans le corps du document.
- `README.md` : doit rester cohérent avec `SPECIFICATIONS.md` (pas de doublon contradictoire, même terminologie).

## Repères d'architecture

- `app/main.py` — endpoints FastAPI, sans état.
- `app/models.py` — modèle Pydantic `Project` = l'état complet du livre. Le nom `Project` (et le format JSON exporté `{"format": "wikipedia2book-workspace", "version": 1, "projects": [...]}`) est un détail d'implémentation conservé pour la compatibilité des fichiers déjà exportés par des utilisateurs : ne pas renommer sans gérer une migration. `UploadedDocument` (image ou PDF importé par l'utilisateur, contenu en base64 dans `data_base64`) a le même rôle qu'`Article` pour l'organisation du livre — voir `BookItem` dans `book_builder.py`.
- `app/wikipedia_api.py` — unique point de contact avec MediaWiki (recherche, liens, PDF officiel). Toute nouvelle requête Wikipédia passe par `MediaWikiClient`, avec le même `User-Agent` et les mêmes bornes de timeout. `get_book_links` lit le **wikitexte brut** de la page de livre (pas `prop=links` ni `action=parse&prop=links`, qui renvoient tous les deux les liens triés par ordre alphabétique) afin de préserver l'ordre réel des articles — vérifié en direct contre l'API live de fr.wikipedia.org pendant le développement de cette fonctionnalité; ne pas revenir à `prop=links` pour « simplifier », ça réintroduit le bug. `get_intro_and_creator` fait deux appels (`prop=extracts&exintro=1` puis `prop=revisions&rvdir=newer&rvlimit=1` pour la toute première révision = le créateur de la page) — pas un seul appel combiné, l'API MediaWiki ne le permet pas pour ces deux props à la fois dans un format directement exploitable.
- `app/book_builder.py` — génère uniquement couverture, table des matières, pages de chapitre et conclusion (WeasyPrint). Les pages d'articles ne sont jamais générées par l'app : toujours le PDF officiel Wikipédia tel quel, fusionné par `pypdf`. `BookItem = Article | UploadedDocument` : `ordered_article_groups`/`build_toc_html` travaillent sur ce type union (articles et documents importés se réordonnent/se chapitrent de façon identique, via leur `.key`). `build_cover_html` (couverture + introduction) et `build_toc_html` (table des matières seule, accepte `article_pages`/`chapter_pages` — page de départ de chaque entrée, `None`/absent quand la numérotation est désactivée) sont **deux documents séparés**, volontairement : `main.create_pdf` doit pouvoir insérer la table des matières soit juste après la couverture (`project.toc_position == "start"`), soit après le dernier chapitre/article (`"end"`) — ce découpage est ce qui permet à la position choisie dans l'étape Organisation d'être réellement respectée dans le PDF (avant, la table des matières faisait partie d'un seul bloc couverture+TOC toujours placé en premier, quelle que soit `toc_position`). `page_size_mm` expose le format de page calculé, pour `pdf_generator.image_to_pdf`.
- `app/pdf_generator.py` — `generate_pdf` (WeasyPrint, HTML → PDF); `stamp_page_numbers` (pypdf + reportlab : superpose un numéro en bas de chaque page du `PdfWriter` final — appelé en tout dernier, après `fit_pdf_to_format`, pour que chaque page ait déjà une origine (0,0) propre); `image_to_pdf` (reportlab : convertit une image importée en une page PDF unique); `fit_page_to_format`/`fit_pdf_to_format` (pypdf `Transformation`/`merge_transformed_page`, après `transfer_rotation_to_content()` sur la page source : recompose n'importe quelle page — article Wikipédia, document importé, page générée par l'app — sur un format/orientation cible donné en mm, mise à l'échelle et centrée sans déformation; appelé sur **toutes** les pages dans `main.append_pdf`, y compris celles déjà au bon format, de façon idempotente). Aucune de ces fonctions n'a besoin de WeasyPrint ni de GTK/Pango, mais l'import du *module* échoue quand même sur cette machine à cause du `from weasyprint import HTML` en tête de fichier — voir le contournement (stub `sys.modules`) dans `tests/test_pdf_generation.py`.
- `app/explorer.py` — BFS sur les liens internes, bornes `max_depth ≤ 3`, `max_articles ≤ 200`.
- `app/static/app.js` — toute la logique front, un seul fichier, pas de framework. L'état vit dans `state.project`. `articleKey()` gère aussi bien `Article` (clé `langue:id`/`langue:title:titre`) que `UploadedDocument` (clé `doc:<id>`) — `selectedArticles()` fusionne les deux pour tout ce qui touche à l'étape Organisation. `bookFileName(project)` dérive le nom de fichier (JSON et PDF) du titre du livre — ne pas revenir à un nom fixe. `suggestIntroAndAuthor(article)` est appelée uniquement quand `main_articles` passe de 0 à ≥1 (capturer `wasFirst` *avant* le `push`, pas après) ; elle ne touche jamais `introduction`/`book_author` s'ils sont déjà renseignés — ne pas la rendre plus agressive sans qu'on le demande explicitement.
- `app/static/i18n.js` — chargé *avant* `app.js` (même scope global, pas de modules ES) : dictionnaire `I18N[lang][clé]`, `t(clé, vars)` (interpolation `{nom}`), `setLanguage(lang)`, `applyTranslations()` (remplit `[data-i18n]`/`data-i18n-placeholder`/`data-i18n-title`/`data-i18n-aria-label`), `state_i18n.lang` (persisté en `localStorage`, détecté depuis `navigator.language` au premier chargement, repli sur `fr`). Toute nouvelle chaîne visible côté front passe par `t()`, jamais de texte français en dur dans `app.js`/`index.html` — sauf les URL/valeurs d'exemple (non traduites, ce sont des URL, pas du texte). **Important** : cette langue d'interface ne couvre ni les messages d'erreur renvoyés par le serveur (`error.message` reste tel que FastAPI/Pydantic l'a produit, en français) ni le contenu du PDF généré (couverture, table des matières, pages de chapitre restent en français côté `book_builder.py`) — étendre ça demanderait de faire voyager la langue jusqu'au backend, hors du périmètre actuel.

Les boutons « Générer le PDF » (`#topExportButton`, `#exportButton`) ne sont **jamais** désactivés pour cause de sélection vide — seulement pendant une génération en cours (double-soumission). Le cas « rien de sélectionné » est géré par un message dans `exportPdf()`, pas par `disabled`.

`fit_page_to_format` déclenche un `pypdf.DeprecationWarning` sur `transfer_rotation_to_content()` (appelé sur une page pas encore attachée à un writer) : attendu avec `pypdf` 5/6.x, inoffensif, et hors de portée tant que `requirements.txt` épingle `pypdf<7` — ne pas « corriger » sans qu'une migration pypdf 7 soit explicitement demandée.

## Déploiement

Pas de `docker-compose.yml` dans ce dépôt : build/run via `Dockerfile` + `docker-build.sh` (injecte commit/date/auteur git pour le pied de page). Ne pas réintroduire Compose sans raison explicite de l'utilisateur.

## Versionnement

Chaque génération/modification de code par un agent doit incrémenter le numéro de version de l'application, dans `app/main.py` (`FastAPI(version="x.y.z")`) :

- Patch (x.y.**Z**) : corrections, nettoyage, petits ajustements.
- Minor (x.**Y**.0) : nouvelle fonctionnalité ou changement de comportement visible.
- Major (**X**.0.0) : rupture de compatibilité (ex. format JSON exporté, API publique).

Ne jamais terminer une génération de code sans ce bump, même minime.

Ajouter la nouvelle version dans le tableau de la section 19 de `SPECIFICATIONS.md` (« Historique des versions »), avec la date et un résumé court des modifications — dans le même changement, pas après coup.

## Vérification avant de considérer une tâche terminée

Des tests automatisés existent sous `tests/` (stdlib `unittest`, lancés avec le `.venv`) :

```bash
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

- `test_syntax.py` : tous les fichiers `.py` sous `app/` parsent sans erreur de syntaxe.
- `test_pdf_generation.py` : comportement réel de `stamp_page_numbers`, `fit_pdf_to_format` (pages de tailles différentes forcées au même format cible) et des numéros de page dans la table des matières (`build_book_html`) — pypdf/reportlab, sans WeasyPrint. Essaie d'abord un vrai `import weasyprint` ; si ça échoue (cas de cette machine), stub `sys.modules["weasyprint"]` avant d'importer `app.pdf_generator` — réutiliser ce motif pour tout nouveau test touchant à `pdf_generator.py`/`book_builder.py` sans dépendre de WeasyPrint.
- `test_uploaded_documents.py` : `image_to_pdf` (taille de page correcte) et regroupement/TOC avec un mélange `Article`/`UploadedDocument`. Utilise Pillow (dépendance de reportlab, déjà installée) pour fabriquer une image de test en mémoire.
- `test_wikipedia_api.py` : `get_book_links` sans réseau, via `client._get = AsyncMock(return_value=...)` — vérifie l'ordre de wikitexte et le filtrage des liens namespacés (`Catégorie:`, `Utilisateur:`, etc.). `get_intro_and_creator` avec `AsyncMock(side_effect=[...])` (deux réponses différentes, une par appel à `_get`).
- `test_i18n.py` : lit `i18n.js` comme du texte (regex, pas de moteur JS) et vérifie que les 5 langues définissent exactement les mêmes clés, sans doublon, et que les paramètres `{n}`/`{error}`/etc. correspondent entre langues pour chaque clé. Ajouter toute nouvelle clé dans les 5 blocs sous peine de faire échouer ce test — c'est le but.

Reste un angle mort : l'assemblage complet du PDF dans `/api/pdf` (main.py) n'est testé par rien d'automatisé — seules ses briques (book_builder, pdf_generator) le sont (gap partiel, section 18 de la spec).

- `python`/`py` dans le PATH par défaut pointent vers l'alias cassé du Microsoft Store. Le vrai interpréteur est `C:\Users\<utilisateur>\AppData\Local\Programs\Python\Python312\python.exe`.
- Un virtualenv `.venv/` existe à la racine (ignoré par git) avec `requirements.txt` déjà installé : `.venv/Scripts/python.exe`.
- `import app.main` échoue nativement sur cette machine Windows : WeasyPrint a besoin des libs GTK/Pango/Cairo (`libgobject-2.0-0`, etc.) que seul le conteneur Docker installe (via `apt-get`, voir `Dockerfile`). Ce n'est pas un bug du code — ne pas essayer de « corriger » ça côté app. Pour vérifier le code qui ne dépend pas de `pdf_generator`/WeasyPrint (`models`, `book_builder`, `wikipedia_api`, `explorer`), importer ces modules directement, ils fonctionnent dans ce `.venv`.
- Pour tester la génération PDF de bout en bout (WeasyPrint inclus), il faut lancer l'app dans le conteneur Docker (`sh docker-build.sh && docker run --rm -p 8000:8000 wikipedia2book`) et dérouler le flux Sources → Organisation → Édition → export PDF.

### Déboguer un bug frontend (JS/HTML) sans pouvoir lancer le backend localement

Playwright + Chromium headless sont installés dans `.venv` (`pip install playwright && playwright install chromium`, déjà fait une fois sur cette machine). Pour reproduire un bug UI, piloter directement :

- **Le site en production** (`https://wikipedia2book-production.up.railway.app/`) si la correction n'est pas encore locale, ou pour vérifier si un bug reporté vient d'une version déjà corrigée en local mais pas encore déployée (comparer `app/static/app.js` local avec `curl .../static/app.js` déployé).
- **Une version locale non déployée** : `app/static/` ne peut pas être servi tel quel avec un simple `http.server` (les pages référencent `/static/app.js`, un chemin qui n'existe que parce que FastAPI monte `app/static/` sous `/static` en plus de servir `index.html` à `/`). Reproduire cette structure dans un dossier temporaire (`index.html` à la racine + copie de `app/static/*` dans un sous-dossier `static/`) avant de servir avec `python -m http.server`, sinon `app.js` renvoie 404 et toutes les erreurs observées (`state is not defined`, etc.) sont un artefact du test, pas un vrai bug.
- Capturer `page.on("console", ...)` et `page.on("pageerror", ...)` systématiquement : un vrai crash JS apparaît là, pas dans le texte visible de la page.

C'est exactement ce qui a permis de confirmer que le bouton « Ajouter » ne causait aucune erreur JS, et que le vrai problème était l'attribut HTML `required` sur un champ resté vide (mode par défaut sans valeur pré-remplie) — aucune boucle de supposition n'aurait été aussi rapide qu'une reproduction réelle.

Pour mesurer un problème de layout CSS (ex. « on ne voit que 26 caractères »), ne pas deviner la règle CSS en cause : `page.evaluate` pour lire `clientWidth`/`scrollWidth` des conteneurs en cascade (de `.app-shell` jusqu'à l'élément) repère immédiatement lequel absorbe l'espace en trop — c'est comme ça qu'un `justify-content: space-between` orphelin (sans second enfant flex, laissé par une suppression de code mort antérieure) a été trouvé.

Pour tester un `<input type="file">`, `page.set_input_files("#selector", [chemin, ...])` fonctionne directement sans dialogue natif à gérer.

Pour tester le changement de langue : `page.select_option("#languageSelect", "de")` puis vérifier `page.get_attribute("html", "lang")` et le texte d'éléments connus — pas besoin de recharger la page. Limite connue, pas corrigée : les chaînes avec un compteur (`org.docAddedToast`, etc.) n'ont qu'une forme singulier/pluriel par langue (comme en français), donc un compte de 1 peut sonner faux en allemand/italien (« 1 Seiten » au lieu de « 1 Seite ») — accepté comme limitation mineure plutôt que construire une vraie pluralisation pour un seul cas.

Piège d'encodage rencontré pendant le développement de l'i18n : une partie de `app.js` écrit ses caractères accentués en échappement JS littéral (`'Sélectionnez'`, texte ASCII, pas un vrai « é »), une autre partie en UTF-8 brut — les deux sont mélangés dans le même fichier. `Edit` échoue silencieusement si `old_string` ne correspond pas à la bonne forme. En cas d'échec répété sur une chaîne qui a l'air correcte : lire le fichier via Python (`repr(open(path, encoding='utf-8').read())`) pour voir la forme exacte, et faire le remplacement avec un script Python (pas un heredoc bash — les accents passés en argument de commande peuvent eux-mêmes se corrompre) plutôt qu'insister avec `Edit`.
