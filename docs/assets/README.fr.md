---
description: >-
  Le logo, le favicon et les feuilles de style de la documentation ddi-l, et
  leurs règles d'usage.
---

# Ressources de documentation

Éléments de marque et de style utilisés par le site de documentation.

## Logo et favicon

La marque de l'en-tête se trouve dans `docs/overrides/.icons/ddi/logo.svg` :
des enregistrements empilés entourés d'une flèche circulaire ouverte, pour un
jeu de données parcourant le *cycle de vie* DDI. Elle est dessinée entièrement
en `currentColor` : elle prend donc la couleur de premier plan de l'en-tête en
mode clair, sombre ou à contraste élevé, sans second fichier. Cela ne
fonctionne que parce que `theme.icon.logo` amène le thème à l'insérer dans la
page ; déclarée par `theme.logo`, elle serait chargée comme `<img>`, où
`currentColor` vaut le noir. N'y ajoutez pas de remplissages propres à une
palette.

`favicon.svg` est un fichier distinct plutôt que le même réutilisé. Un onglet de
navigateur l'affiche à 16–32 px sur le fond du navigateur et non sur celui du
site : il n'y a aucune couleur à hériter. Il porte donc son propre fond et
abandonne l'arc du cycle de vie, illisible à cette taille.

## Couleurs

Il y a une seule couleur de marque, le bleu, pour les liens, les boutons et la
page active. L'orange ne marque que l'anneau de focus du clavier. Les blocs de
code et le code en ligne reposent sur un gris neutre, sans bordure.

Le bouton de l'en-tête fait défiler trois réglages : suivre le système, clair
(`default`) et sombre (`slate`). Il n'y a pas de palette à contraste élevé à
choisir : les lecteurs dont le système demande plus de contraste
(`prefers-contrast: more`) obtiennent un texte plus foncé, des bordures plus
marquées et des fonds plus sobres dans les deux modes, et le contraste élevé de
Windows (`forced-colors`) reçoit les couleurs du système. Le bleu, avec un
orange employé avec parcimonie, est une paire que distinguent les lecteurs
atteints des déficiences courantes de la vision des couleurs ; il n'y a donc
pas de palettes distinctes pour ces déficiences. Chaque palette de
`zensical.toml` déclare `primary = "custom"` et `accent = "custom"` ; sans eux,
la palette propre au thème remplace `palette.css`.

## Feuilles de style

| Fichier | Rôle |
| --------- | ------ |
| `palette.css` | Jetons de couleur des modes clair et sombre, réglages « plus de contraste » et « couleurs forcées », et encadrés note/info. |
| `site.css` | Titres, anneau de focus, mouvement réduit, barre d'annonce, cartes, et bannière et terminal de la page d'accueil. |

La bannière de la page d'accueil est `docs/overrides/home.html`, remplie à
partir de l'en-tête `hero:` de `docs/index.en.md` et `docs/index.fr.md`.
