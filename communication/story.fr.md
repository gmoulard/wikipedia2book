# Imprimer Wikipédia à nouveau : l'histoire de Wikipedia2Book

Version française du billet [story.md](story.md) (le billet publié sur [Diff](https://diff.wikimedia.org/?p=223381) est en anglais). Les deux versions se modifient ensemble.

---

*Conflit d'intérêts : je suis le développeur de Wikipedia2Book. Ce billet raconte pourquoi je l'ai créé, ce qu'il fait et comment il a été fait.*

## Pourquoi je l'ai créé

Pendant des années, Wikipédia a proposé une fonction que beaucoup de lecteurs aimaient : rassembler des articles dans un « livre » avec Spécial:Livre, puis le télécharger en un seul PDF, ou en commander un exemplaire imprimé. En 2017, la production des PDF de livres a été arrêtée pour des raison que je ne connais pas. Les livres enregistrés existent toujours, par milliers, et Spécial:Livre reçoit encore beaucoup de visites, mais le bouton qui les transformait en PDF ne fonctionne plus. Les versions imprimables de Wikilivres et les œuvres de Wikisource ont le même problème : le texte est prêt à être lu sur papier, mais il n'existe pas de moyen simple d'en tirer un volume propre et imprimable.

Mon point de départ, c'était une série d'articles que j'avais commencés sur Wikipédia en français : les épaves de la rade de Saint-Pierre, en Martinique, les navires coulés lors de l'éruption de la montagne Pelée en 1902. Je les avais rassemblés dans une page de livre, [Les épaves de la rade de Saint-Pierre suite à l'éruption de la montagne Pelée en 1902](https://fr.wikipedia.org/wiki/Utilisateur:474D6F756C617264/Livres/Les_%C3%A9paves_de_la_rade_de_Saint-Pierre_suite_a_l'%C3%A9ruption_de_la_montagne_Pel%C3%A9e_en_1902), et je voulais simplement les avoir ensemble, dans un seul PDF.

J'ai donc écrit un petit outil pour retrouver ce bouton : [Wikipedia2Book](https://wikipedia2book.toolforge.org/).

L'idée de départ était très modeste : prendre les fichiers PDF que Wikipédia génère déjà pour chaque article, et les mettre bout à bout dans un seul PDF de plusieurs pages. C'est tout. Mais avec les outils de développement modernes, ajouter une fonctionnalité de plus était si facile que j'en ai ajouté plein : une couverture, une table des matières, des chapitres, les autres wikis, douze langues, des volumes… Oups !

## Ce qu'il fait

On colle ce qu'on veut lire, on obtient un livre PDF.

- **Sources** : l'adresse d'un article, un livre Wikipédia enregistré (Spécial:Livre, pages « Livre: »), un livre de Wikilivres ou sa version imprimable, une œuvre de Wikisource, une liste de pages (une par ligne : liens wiki, adresses ou titres), ou une simple recherche. Les pages peuvent venir de huit projets Wikimédia : Wikipédia, Wikisource, Wikilivres, Wikivoyage, Wikiversité, Wikiquote, Wiktionnaire et Wikinews, dans toutes les langues, et on peut mélanger les langues dans un même livre.
- **Organisation** : l'ordre d'un livre enregistré est conservé, avec ses chapitres et son sous-titre. On peut déplacer articles et chapitres, ajouter des chapitres, trouver des articles liés à partir des liens d'une page, et ajouter ses propres images, fichiers PDF ou n'importe quelle page web.
- **Édition** : titre, sous-titre, auteur, introduction et conclusion ; une couverture et une dernière page avec une image ou une couleur de fond ; format de page (A4, Letter, Legal et d'autres), orientation et marges ; table des matières au début ou à la fin, avec des liens cliquables ; numéro sur chaque page.
- **Le PDF** : une couverture, une table des matières, chaque article, et une page de licence qui cite chaque article source avec un lien vers son historique, pour que le livre respecte la licence CC BY-SA. Des signets permettent de passer d'un article à l'autre.
- **Volumes** : les gros livres sont découpés automatiquement (300 articles par volume), chaque volume avec sa couverture, sa table des matières et sa numérotation.
- **Langues** : l'interface est traduite en 12 langues (anglais, français, allemand, espagnol, italien, portugais, néerlandais, turc, chinois, japonais, persan et arabe, ces deux dernières de droite à gauche), et les pages ajoutées au PDF sont écrites dans la langue choisie.
- **Liens** : tout ce que fait l'interface existe aussi sous forme d'une simple adresse web : un lien comme `https://wikipedia2book.toolforge.org/api/pdf/from-source?source=<adresse d'un livre>` télécharge directement le PDF, si bien qu'une page wiki peut proposer son propre lien « Télécharger en PDF ».

## Comment il fonctionne, et ce qu'il ne fait pas

Le contenu des articles n'est jamais reconstruit. Pour chaque page, Wikipedia2Book demande à Wikimédia son PDF officiel, celui qu'on obtient avec le lien « Télécharger en PDF » de l'article, et n'ajoute autour que ce dont un livre a besoin : couverture, table des matières, pages de chapitre, numéros de page et licence. Le texte, les images et les références sont exactement ceux du wiki. Chaque page est seulement mise à l'échelle et centrée sur le format choisi pour le livre.

Le serveur ne garde rien. Pas de compte, pas de base de données : le livre vit dans le navigateur, et on l'enregistre soi-même dans un petit fichier JSON qu'on peut rouvrir, partager ou publier pour que d'autres reconstruisent le même livre. L'outil respecte les règles de Wikimédia sur le User-Agent et l'API ; c'est un logiciel libre (AGPL-3.0), hébergé sur Toolforge.

## Comment il a été fait

Wikipedia2Book est un projet très jeune. La première ligne a été écrite le 7 novembre 2026 : je suis parti d'une spécification écrite, d'abord rédigée avec ChatGPT, puis j'ai construit l'application avec Claude Code, un assistant de programmation par IA, en décrivant ce que je voulais et en testant moi-même chaque étape. Le projet est ouvertement « vibe codé » : le code est écrit et relu par des agents IA, tandis que je décide de ce que l'outil doit faire, vérifie les résultats sur de vrais livres et tiens une spécification et un historique détaillés, en français et en anglais.

- **7 novembre** : première version, un seul livre en mémoire, des chapitres, un PDF avec signets.
- **9 au 11 novembre** : import des livres Wikipédia enregistrés dans leur ordre réel (l'API renvoie les liens par ordre alphabétique, l'outil lit donc le wikitexte), numérotation continue des pages, page de licence, les premières langues de l'interface, puis douze.
- **12 novembre** : version 1.0, en ligne sur Toolforge.
- **13 au 18 novembre** : un seul champ pour tous les types de sources, les listes de pages, les autres projets Wikimédia, les sommaires de Wikilivres et de Wikisource, les volumes, les images de fond, les pages web, et beaucoup de travail pour que les gros livres ne fassent pas manquer de mémoire au serveur.

En douze jours, l'outil a connu plus de 370 modifications et 13 versions mineures. Entre le 12 et le 17 novembre, il a reçu environ 12 000 requêtes sur Toolforge.

Cette vitesse, c'est la vraie histoire. Travailler avec des grands modèles de langage dans un environnement conçu pour le développement logiciel, une application dans laquelle l'IA lit le code, le modifie, lance les tests et vérifie le résultat dans un navigateur, m'a donné une vélocité que je n'aurais jamais atteinte seul : une fonctionnalité décrite le matin est en général écrite, testée, documentée et en ligne le jour même. Vitesse ne veut pas dire raccourcis. Tout est ouvert, dans un [dépôt public](https://github.com/gmoulard/wikipedia2book/) : chaque modification est un commit lisible, une trentaine de fichiers de tests automatiques tournent avant chaque déploiement, des contrôles de sécurité à chaque modification de la branche principale, et les spécifications fonctionnelle et technique suivent le code, si bien que chacun peut vérifier ce que fait l'outil et comment.

[[À COMPLÉTER : ce que t'a appris ce mode de développement, ce qui a été difficile (par exemple l'ordre des articles, la mémoire sur Toolforge, les écritures rares en chinois), ce qui t'a surpris.]]

## La suite, et comment aider

L'outil a ses limites : la police et la mise en page de chaque article sont celles du PDF officiel de Wikimédia, où certaines écritures ne s'affichent pas toujours parfaitement ; un livre est limité à 300 articles par volume.

Vous pouvez aider en l'essayant avec vos propres livres enregistrés, en signalant problèmes et idées sur [GitHub](https://github.com/gmoulard/wikipedia2book), en améliorant une traduction de l'interface ou de la page d'aide, ou simplement en ajoutant un lien « Télécharger en PDF » sur une page de livre de votre wiki.

[[À COMPLÉTER (facultatif) : un remerciement, par exemple aux personnes qui ont testé ou contribué au code.]]
