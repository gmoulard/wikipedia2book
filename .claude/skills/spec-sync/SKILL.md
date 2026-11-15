---
name: spec-sync
description: Garder la spécification fonctionnelle, ses traductions, ses schémas d'architecture et le README alignés sur le code. À utiliser avant toute modification fonctionnelle (lire la spec) et dans le même changement dès qu'un comportement, un module, un endpoint, un fichier ou une procédure change.
---

# Synchroniser la documentation

Les fichiers concernés (spécification de référence et sa langue, traductions, section des évolutions futures, section des schémas, arborescence du dépôt, historique des versions, source des libellés d'interface traduits, fichiers générés à ne pas committer) sont dans la section « Paramètres des skills » du `CLAUDE.md` du dépôt.

## Avant de modifier

Lire la partie de la spécification de référence qui décrit le comportement touché : c'est elle qui fait foi sur ce que le code doit faire.

## Dans le même changement que le code

1. **La spécification reflète le comportement réel**, jamais un objectif. Une évolution pas encore implémentée va dans la section des évolutions futures, pas dans le corps du document. Ne jamais laisser la spec décrire une fonctionnalité qui n'existe pas, ni le code faire quelque chose que la spec ne décrit pas.
2. **Traductions** : reporter chaque modification dans toutes les traductions, même structure (sections, sous-sections, lignes de tableau, lignes d'historique). En cas d'écart, la langue de référence prévaut. Les libellés d'interface sont cités tels qu'ils apparaissent dans l'interface de la langue de la traduction.
3. **Schémas d'architecture** (Mermaid ou autres) : à mettre à jour quand un module, un endpoint ou une étape d'un traitement change.
4. **Arborescence du dépôt** décrite dans la spec et le README : à mettre à jour quand un fichier ou un dossier apparaît, disparaît ou bouge.
5. **README** : cohérent avec la spécification, même terminologie, pas de doublon contradictoire.
6. **Exemples** (appels d'API, commandes) : ajouter ou corriger ceux du comportement modifié.

## Vérifier

- Chercher dans la doc les anciens noms (fichiers, chemins, endpoints, options) qui auraient dû disparaître : `grep -rn "<ancien nom>" <dossiers de doc> README.md`.
- Ne pas modifier les lignes d'historique déjà publiées : elles décrivent le passé.
- Contrôler que chaque traduction a le même nombre de sections que la référence (`grep -c "^#" <fichier>`).
