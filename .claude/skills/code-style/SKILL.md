---
name: code-style
description: Règles d'écriture du code pour un dépôt en « vibe coding » (code écrit et relu par des agents, pas par des humains) — pas de commentaires sauf les pièges « NE PAS » et l'en-tête de licence, pas de code mort, recherche avant suppression, marqueurs de conflit, robustesse, pièges d'édition. À appliquer avant toute création ou modification de code.
---

# Style de code — « vibe coding »

Personne ne lit ce code : il est écrit et relu par des agents. Les valeurs propres au dépôt (texte et types de fichiers de l'en-tête de licence, dossiers où chercher, fichiers sensibles aux conflits, exemples de pièges déjà rencontrés) sont dans la section « Paramètres des skills » du `CLAUDE.md` du dépôt.

## Commentaires

- Pas de commentaires, pas de docstrings, sauf les deux exceptions ci-dessous. Jamais de commentaire qui décrit ce que fait le code.
- **Exception 1 : les pièges.** Un commentaire d'une ligne commençant par `NE PAS` (`# NE PAS …`, `// NE PAS …`, `/* NE PAS … */`), juste au-dessus d'un code qui a l'air simplifiable mais dont la « simplification » réintroduit un bug connu. Il s'adresse à l'agent qui modifiera cette ligne :
  - ne jamais le supprimer au nom de la règle « pas de commentaires » ;
  - le mettre à jour si le piège change ;
  - en ajouter un dès qu'un nouveau piège est découvert (avec, si besoin, le détail dans `CLAUDE.md`).
  - Les retrouver : `grep -rn "NE PAS" <dossiers du code>`.
- **Exception 2 : l'en-tête de licence** en tête de chaque fichier de code. Ne jamais le supprimer ; l'ajouter à tout nouveau fichier de code, après le shebang ou le `<!doctype html>` s'il y en a un (copier celui d'un fichier voisin du même type).

## Pas de code mort

Pas de code « au cas où » : paramètre toujours appelé avec la même valeur, branche jamais atteinte, champ de modèle jamais lu ni écrit, fonction plus appelée. Supprimer plutôt que garder.

Avant de supprimer un symbole (fonction, champ, id HTML, classe CSS, clé de traduction), chercher dans **tout** le dépôt qu'il n'est référencé nulle part, y compris d'un langage à l'autre : du code serveur peut être appelé depuis le JS/HTML, et inversement.

## Marqueurs de conflit

Un conflit de fusion Git peut rester commité sans casser la construction et passer inaperçu longtemps. Avant toute modification notable d'un gros fichier (CSS, JS, HTML surtout) :

```bash
grep -n "^<<<<<<<\|^=======$\|^>>>>>>>" <fichier>
```

## Thèmes clair et sombre

Une variable de thème pensée comme couleur de **texte** (elle s'inverse entre clair et sombre) ne doit jamais servir de `background` à un élément dont la couleur de texte est fixée en dur : l'élément devient illisible dans l'un des deux thèmes. Pour un fond sombre indépendant du thème, utiliser une couleur fixe.

## Robustesse

« Personne ne lit le code » ne veut pas dire « la fiabilité n'importe pas » : gestion des erreurs réseau des services appelés, validation des entrées, et jamais d'échec silencieux (une erreur s'affiche, se journalise ou fait échouer la commande, avec un message explicite).

## Pièges d'édition

- Un fichier peut mélanger des caractères accentués écrits en UTF-8 brut et en échappements littéraux (`é`, `&eacute;`…). `Edit` échoue si `old_string` n'a pas exactement la même forme. Après un échec sur une chaîne qui a l'air correcte : lire la forme exacte avec Python (`repr(open(chemin, encoding="utf-8").read())`) et faire le remplacement avec un script Python plutôt qu'insister.
- Ne pas passer de texte accentué en argument de commande shell (heredoc compris) pour modifier un fichier : il peut se corrompre en route ; préférer un script Python qui lit et écrit en UTF-8.
