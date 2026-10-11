---
description: >-
  Le logo, le favicon et les feuilles de style de la documentation ddi-l, et
  leurs règles d'usage.
---

# Ressources de documentation

Éléments de marque et de style utilisés par MkDocs.

## Logo et favicon

La marque de l'en-tête se trouve dans `docs/overrides/.icons/ddi/logo.svg` :
des enregistrements empilés entourés d'une flèche circulaire ouverte, pour un
jeu de données parcourant le *cycle de vie* DDI. Elle est dessinée entièrement
en `currentColor` : elle prend donc la couleur de premier plan de l'en-tête dans
chaque palette, y compris en contraste élevé, sans second fichier. Cela ne
fonctionne que parce que `theme.icon.logo` amène Material à l'insérer dans la
page ; déclarée par `theme.logo`, elle serait chargée comme `<img>`, où
`currentColor` vaut le noir. N'y ajoutez pas de remplissages propres à une
palette.

`favicon.svg` est un fichier distinct plutôt que le même réutilisé. Un onglet de
navigateur l'affiche à 16–32 px sur le fond du navigateur et non sur celui du
site : il n'y a aucune couleur à hériter. Il porte donc son propre fond et
abandonne l'arc du cycle de vie, illisible à cette taille.

## Couleurs

Il y a une seule couleur de marque, le bleu : un bleu profond pour l'en-tête,
la même famille pour les liens et les boutons. L'orange ne marque que l'anneau
de focus du clavier. Les blocs de code et le code en ligne reposent sur un gris
neutre, sans bordure.

Il y a trois palettes : claire (`default`), sombre (`slate`) et
`high-contrast`. Le bleu, avec un orange employé avec parcimonie, est une paire
que distinguent les lecteurs atteints des déficiences courantes de la vision
des couleurs ; il n'y a donc pas de palettes distinctes pour ces déficiences.
Chaque palette de `mkdocs.yml` déclare `primary: custom` et `accent: custom` ;
sans eux, les règles indigo par défaut de Material remplacent `palette.css` en
mode sombre.

## Feuilles de style

| Fichier | Rôle |
| --------- | ------ |
| `palette.css` | Jetons de couleur des trois palettes, titres, boutons, code et encadrés note/info. |
| `accessibility.css` | Lien d'évitement, anneau de focus, utilitaire réservé aux lecteurs d'écran, réglages « mouvement réduit », bandeau de version et menu des palettes. |
| `landing.css` | Boutons d'appel à l'action et grille de cartes, utilisés uniquement par `index.*.md`. |

Les modes clair et sombre sont sur le bouton de thème de l'en-tête. Le
contraste élevé se choisit depuis le menu des palettes, juste à côté, qui
propose les trois : Material fait défiler ce bouton à travers toutes les
palettes qui en déclarent un, et en contraste élevé le bouton n'a rien à
afficher, si bien que le menu sert aussi à en sortir. Voir les commentaires
dans `mkdocs.yml` et `docs/overrides/partials/palette.html`.
