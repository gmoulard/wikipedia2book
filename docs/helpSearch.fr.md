# Aide : que saisir dans le champ « Construire le livre » ?

<!-- {% raw %} -->

Le champ de la première étape accepte bien plus qu'un titre d'article : une adresse, un livre entier, une liste de pages ou le texte d'une page de livre. Tapez ou collez ce que vous voulez ajouter, puis cliquez sur « Ajouter ». Les pages ajoutées apparaissent sous le champ ; vous les rangerez à l'étape suivante.

## En bref

| Vous voulez ajouter… | Saisissez… | Exemple |
|---|---|---|
| un article dont vous connaissez le titre | son titre | `Montagne Pelée` |
| une page précise | son adresse | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` |
| un article dans une autre langue | le code de la langue, deux-points, le titre | `nl:Rotterdam` |
| une page d'un autre projet Wikimédia | le préfixe du projet, puis le titre | `voy:en:Lyon` |
| un livre entier | l'adresse de son sommaire ou de sa page de livre | `https://fr.wikibooks.org/wiki/Cosmologie` |
| plusieurs pages d'un coup | une page par ligne | voir « Plusieurs pages à la fois » |
| un livre préparé sur une page « Livre: » | le texte de cette page | voir « Coller le texte d'une page de livre » |

## Chercher un article

- Tapez quelques lettres : des suggestions s'affichent sous le champ.
- La liste à côté du champ choisit la langue de Wikipédia où chercher. Avec « Toutes », le titre est cherché dans toutes les langues de la liste et chaque résultat indique sa langue.
- Si le titre correspond exactement à un article, il est ajouté directement. Un titre qui redirige vers un autre article ajoute l'article de destination : `Napoléon Bonaparte` ajoute « Napoléon Ier ».
- Sinon, les résultats de la recherche s'affichent sous le champ : cliquez sur celui que vous voulez.
- Pour le premier article ajouté, son introduction et le créateur de la page sont proposés comme introduction et auteur du livre, à l'étape Édition. Vous pouvez les modifier.

## Pages d'une autre langue ou d'un autre projet

Une adresse complète fonctionne toujours, par exemple `https://fr.wikivoyage.org/wiki/Lyon`. Avec un titre, ajoutez devant un préfixe de langue, de projet, ou les deux :

| Projet | Préfixe | Exemple |
|---|---|---|
| Wikipédia dans une autre langue | code de la langue | `nl:Rotterdam` |
| Wikisource | `s:` | `s:Les Misérables` |
| Wikilivres | `b:` | `b:Cosmologie` |
| Wikivoyage | `voy:` | `voy:en:Lyon` |
| Wikiversité | `v:` | `v:Python` |
| Wikiquote | `q:` | `q:Victor Hugo` |
| Wiktionnaire | `wikt:` | `fr:wikt:chat` |
| Wikinews | `n:` | `n:Accueil` |

Sans code de langue, c'est la langue choisie à côté du champ qui compte. L'ordre des préfixes n'a pas d'importance. Chaque page garde le nom de son projet et sa langue sur sa carte.

## Livres entiers

- **Page de livre de Wikipédia** : saisissez son adresse ou son nom, par exemple `Utilisateur:Alexbzh972/Livres/Martinique`. Tous ses articles sont ajoutés dans l'ordre de la page, avec ses chapitres, son titre et son sous-titre.
- **Compilation de Wikilivres** : saisissez l'adresse de la compilation, par exemple `https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C`. Ses pages sont ajoutées dans l'ordre de la liste, comme pour une page de livre de Wikipédia.
- **Livre de Wikilivres ou œuvre de Wikisource** : saisissez l'adresse ou le titre de son sommaire, par exemple `https://fr.wikibooks.org/wiki/Cosmologie` ou `s:Les Misérables`. Une fenêtre vous demande ce que vous voulez :
  - « Le livre entier » : toutes ses pages, rangées en chapitres ;
  - « Le livre entier et son sommaire » : la même chose, avec la page de sommaire en tête ;
  - « Seulement cette page » : le sommaire seul ;
  - « Annuler » : rien n'est ajouté.
- **Version imprimable de Wikilivres** : saisissez l'adresse de la page « Version imprimable » du livre, par exemple `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable`. Si cette page est écrite à la main, ses pages sont ajoutées avec un chapitre par titre ; si elle est générée à partir du sommaire, c'est la fenêtre de choix du livre qui s'ouvre.

## Plusieurs pages à la fois

Collez une liste, une page par ligne (pour aller à la ligne en tapant, utilisez Maj+Entrée). Chaque ligne peut être un titre, une adresse ou une page avec préfixe, et peut aussi s'écrire comme un lien de wiki, un lien Markdown ou un élément de liste numérotée ou à puces :

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Un message indique à la fin combien de pages ont été ajoutées, combien étaient déjà dans le livre et combien sont introuvables. Les lignes introuvables restent dans le champ pour que vous puissiez les corriger. Un sommaire de livre placé dans la liste ouvre la fenêtre de choix décrite plus haut.

## Coller le texte d'une page de livre

Vous pouvez coller le contenu d'une page « Livre: » de Wikipédia : `== … ==` donne le titre, `=== … ===` le sous-titre, chaque ligne `;` commence un chapitre et chaque lien `[[…]]` ajoute un article.

```
== Ports bretons ==
=== Guide des ports ===
:[[Brest]]
;Finistère
:[[Concarneau]]
:[[Douarnenez]]
;Morbihan
:[[Lorient]]
```

Le texte d'une version imprimable de Wikilivres, fait d'inclusions `{{:…}}`, est accepté de la même façon : chaque titre `= … =` devient un chapitre.

## Ouvrir un livre enregistré ou partagé

- Le bouton « Enregistrer » télécharge votre livre dans un fichier ; le bouton « Ouvrir » le recharge plus tard. Rien n'est gardé sur le serveur : ce fichier est votre seule sauvegarde.
- Un lien de la forme `https://wikipedia2book.toolforge.org/?json=https://…` ouvre un livre enregistré en ligne (adresse en `https://` seulement).
- Un lien de la forme `https://wikipedia2book.toolforge.org/?source=…` ajoute ses sources comme si vous les aviez saisies : pratique pour partager une sélection de pages.

## Ce que le champ refuse

- les sites qui ne sont pas des projets Wikimédia ;
- les pages qui ne sont pas des pages de contenu (discussions, pages d'aide ou de communauté) ;
- les fichiers de Wikimedia Commons : ajoutez-les plutôt comme documents à l'étape Organisation, ou comme images de fond à l'étape Édition ;
- les pages qui n'existent pas.

Le message d'erreur explique ce qui ne va pas. Il vient du serveur et reste en français, quelle que soit la langue de l'interface.

## Et ensuite ?

- **Organisation** : rangez les pages, créez des chapitres, ajoutez vos propres images ou PDF, coupez le livre en volumes. Au-delà de 300 articles, le livre est découpé en volumes automatiquement.
- **Édition** : titre, couverture, images de fond, table des matières, format et marges.
- **Générer le PDF** : chaque article est repris tel que Wikipédia l'imprime, et l'ensemble forme un seul livre prêt à imprimer.

<!-- {% endraw %} -->
