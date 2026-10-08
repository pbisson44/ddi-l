---
description: >-
  Le logo, le favicon et les feuilles de style de la documentation ddi-l, et
  leurs règles d'usage.
---

# Ressources de documentation

Éléments de marque et de style utilisés par MkDocs.

## Logo et favicon

`logo.svg` est la marque de l'en-tête : des enregistrements empilés entourés
d'une flèche circulaire ouverte, pour un jeu de données parcourant le *cycle de
vie* DDI. Il est dessiné entièrement en `currentColor` : il hérite donc de la
couleur de premier plan de l'en-tête et reste lisible dans les six palettes,
y compris en contraste élevé, sans second fichier. N'y ajoutez pas de
remplissages propres à une palette.

`favicon.svg` est un fichier distinct plutôt que le même réutilisé. Un onglet de
navigateur l'affiche à 16–32 px sur le fond du navigateur et non sur celui du
site : il n'y a aucune couleur à hériter. Il porte donc son propre fond et
abandonne l'arc du cycle de vie, illisible à cette taille.

## Feuilles de style

| Fichier | Rôle |
| --------- | ------ |
| `palette.css` | Jetons de couleur des six schémas : `default`, `slate`, `high-contrast` et les palettes `deuteranopia` / `protanopia` / `tritanopia` adaptées aux déficiences de la vision des couleurs. |
| `accessibility.css` | Lien d'évitement, utilitaire réservé aux lecteurs d'écran, réglages « mouvement réduit », bandeau de version et menu des palettes d'accessibilité. |
| `landing.css` | Boutons d'appel à l'action et grille de cartes, utilisés uniquement par `index.*.md`. |

Les palettes d'accessibilité se choisissent depuis un menu de l'en-tête plutôt
que depuis le bouton de thème : Material fait défiler ce bouton à travers
*toutes* les palettes qui en déclarent un, si bien qu'avec les six il fallait
six clics pour revenir au mode clair. Voir les commentaires dans `mkdocs.yml` et
`docs/overrides/partials/palette.html`.
