---
name: debug-frontend
description: Reproduire et diagnostiquer un bug d'interface web (JS, HTML, CSS) avec Playwright et Chromium headless, sur le site en production ou une version locale servie en statique, sans lancer le serveur applicatif. À utiliser pour tout bug d'interface, de mise en page, de traduction ou de rendu de graphique, avant de proposer un correctif.
---

# Déboguer une interface web

Les valeurs propres au dépôt (adresse de production, dossier des fichiers statiques et chemin sous lequel le serveur les publie, page d'accueil, sélecteurs utiles comme le choix de langue, emplacement de Playwright) sont dans la section « Paramètres des skills » du `CLAUDE.md` du dépôt.

Principe : reproduire pour de vrai avant de corriger. Une reproduction dans un navigateur va plus vite qu'une boucle de suppositions.

## Choisir la cible

- **Le site en production** si le bug n'est pas encore corrigé en local, ou pour savoir si un bug signalé vient d'une version déjà corrigée mais pas encore déployée : comparer le fichier JS local avec celui servi (`curl <adresse>/<chemin du js>`).
- **Une version locale non déployée** : les pages référencent souvent les fichiers statiques sous un chemin que seul le serveur applicatif fournit (par exemple `/static/app.js`). Reproduire cette structure dans un dossier temporaire (la page d'accueil à la racine, les fichiers statiques dans le sous-dossier attendu) avant de servir avec `python -m http.server`. Sinon les scripts renvoient 404, et les erreurs observées (« X is not defined »…) sont un artefact du test, pas un vrai bug.
- Simuler les appels réseau dont la page dépend avec `page.route(...)` (`route.fulfill` pour une réponse, `route.abort` pour une panne), et tester les deux cas.

## Toujours capturer les erreurs

```python
page.on("console", lambda message: print(message.type, message.text))
page.on("pageerror", lambda error: print("pageerror", error))
```

Un vrai crash JS apparaît là, pas dans le texte visible de la page. Inversement, aucune erreur JS oriente vers une cause HTML ou CSS (par exemple un attribut `required` sur un champ resté vide qui bloque un formulaire sans rien signaler).

## Recettes

- **Mise en page** (« on ne voit que 26 caractères ») : ne pas deviner la règle CSS en cause. Lire avec `page.evaluate` les `clientWidth` / `scrollWidth` des conteneurs en cascade, du conteneur racine jusqu'à l'élément : celui qui absorbe l'espace en trop saute aux yeux (exemple vécu : un `justify-content: space-between` resté orphelin après une suppression de code).
- **Fichiers** : `page.set_input_files("<sélecteur>", [chemin, ...])` remplit un `<input type="file">` sans dialogue natif.
- **Langue** : `page.select_option("<sélecteur de langue>", "de")`, puis vérifier `page.get_attribute("html", "lang")` (et `dir` pour les langues de droite à gauche) et le texte d'éléments connus, sans recharger la page.
- **Thèmes** : ouvrir la page avec `browser.new_page(color_scheme="dark")` puis `"light"` ; vérifier le contraste des éléments à fond fixe.
- **Graphiques et rendus asynchrones** : attendre le rendu (`page.wait_for_selector` ou un délai), puis inspecter le SVG produit plutôt que le texte source ; si un rendu reste en texte sans erreur, couper le scénario en variantes (avec et sans chaque étape asynchrone) pour isoler celle qui le déclenche.
- **Captures d'écran** : `page.screenshot(path=..., full_page=True)`, puis les regarder (outil de lecture d'image) avant de conclure.

## Conclure

Décrire ce qui a été reproduit, la cause établie (pas supposée), le correctif, puis rejouer le même scénario pour montrer qu'il passe.
