---
description: >-
  The ddi-l logo, favicon and documentation stylesheets, and the rules for
  using them.
---

# Documentation assets

Branding and styling assets used by the documentation site.

## Logo and favicon

The header mark lives at `docs/overrides/.icons/ddi/logo.svg`: stacked records
wrapped by an open circular arrow, for a dataset moving through the DDI
*Lifecycle*. It is drawn entirely in `currentColor`, so it takes the header's
foreground in light, dark and high-contrast modes without a second asset.
That only works because `theme.icon.logo` makes the theme inline it; set as
`theme.logo` it would load as an `<img>`, where `currentColor` is black. Do not
add palette-specific fills to it.

`favicon.svg` is a separate file rather than the same one reused. A browser tab
renders at 16–32px against the browser's chrome, not the site's, so there is no
inherited colour to take: it carries its own ground and drops the lifecycle arc,
which turns to mud at that size.

## Colours

There is one brand colour, blue, for links, buttons and the active page.
Orange marks only the keyboard focus ring. Code blocks and inline code sit on a
neutral grey with no border.

The header toggle cycles through three settings: follow the system, light
(`default`) and dark (`slate`). There is no high-contrast palette to choose:
readers whose system asks for more contrast (`prefers-contrast: more`) get
darker text, stronger borders and plainer backgrounds in either scheme, and
Windows high contrast (`forced-colors`) gets the system's own colours. Blue with
a sparingly used orange is a pairing that readers with any common colour-vision
deficiency can tell apart, so there are no separate colour-vision palettes.
Every palette entry in `zensical.toml` declares `primary = "custom"` and
`accent = "custom"`; without them the theme's own palette overrides
`palette.css`.

## Stylesheets

| File | Purpose |
| ------ | --------- |
| `palette.css` | Colour tokens for light and dark, the more-contrast and forced-colours adjustments, and the note/info boxes. |
| `site.css` | Headings, the focus ring, reduced motion, the announcement bar, cards, and the landing page's hero and terminal. |

The landing page's hero is `docs/overrides/home.html`, filled from the `hero:`
front matter of `docs/index.en.md` and `docs/index.fr.md`.
