# Brouillon : signalement Phabricator (service PDF, caractères CJK rares)

À déposer à la main sur https://phabricator.wikimedia.org/ (projet : *Proton* / *Wikimedia-PDF-Rendering*, à vérifier au moment du dépôt).

**Titre** : Rare CJK characters (Extension B and later) render as blanks in REST API PDFs

**Description**

The official PDF export (`/api/rest_v1/page/pdf/{title}/a4`) leaves blank spaces for some characters from CJK Unified Ideographs Extension B and later planes. The font used in the PDF (LiberationSerif, as reported in the PDF's font list) has no glyph for them, and no fallback font covers them.

Steps to reproduce:

1. Open https://zh.wikisource.org/api/rest_v1/page/pdf/大南寔錄%2F大南寔錄前編%2F卷10/a4
2. Look for 𡼢 (U+21F22), which is shown correctly on the HTML page.

Expected: the character is rendered (e.g. with a font such as HanaMinB, Noto Serif CJK or BabelStone Han as a fallback).

Actual: a blank space. Only characters that Wikisource provides as images are visible.

This affects users printing classical Chinese texts from Wikisource (report from a user on the Chinese Wikipedia technical village pump, November 2026). Tools built on top of this API, such as Wikipedia2Book (https://wikipedia2book.toolforge.org/), embed the official PDF unchanged and cannot fix it on their side.

Suggested fix: install a font covering CJK Extension B–H (for instance `fonts-hanazono` on Debian) in the PDF rendering service and add it to the fallback chain.
