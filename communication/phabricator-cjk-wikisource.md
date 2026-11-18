# Brouillon : signalement Phabricator (service PDF, caractères CJK rares)

Déposé le 18/11/2026 : https://phabricator.wikimedia.org/T445303 (formulaire Bug Report, étiquettes Proton et All-and-every-Wikisource ; PDF-Rendering est archivé).

Ticket voisin, fermé : T226633 (« PDF renderer needs better CJK font », 2019-2020, polices Noto CJK). Texte déposé : modèle du formulaire Bug Report rempli avec les mêmes éléments.

**Titre** : PDF export drops rare CJK characters (Extension B and later) on zh.wikisource

**Description**

The official PDF export of the REST API (`/api/rest_v1/page/pdf/{title}/a4`) leaves blank spaces for some characters from the CJK Unified Ideographs Extension B and later planes (U+20000 and above), although they are in the page HTML.

Steps to reproduce (checked on 2026-11-18):

1. Get the HTML of https://zh.wikisource.org/wiki/大南寔錄/大南寔錄前編/卷10 (`/api/rest_v1/page/html/…`): it contains three characters above U+20000: 𡼢 U+21F22, 𨭎 U+28B4E, 𪻳 U+2AEF3.
2. Get the PDF: https://zh.wikisource.org/api/rest_v1/page/pdf/大南寔錄%2F大南寔錄前編%2F卷10/a4
3. Extract its text (e.g. with pypdf): only U+28B4E is there; U+21F22 and U+2AEF3 are missing and show as blanks. The embedded fonts are LiberationSerif, DejaVuSans and Type 3 subsets; no font of the renderer seems to cover these code points.

Expected: every character of the page is rendered, with a fallback font covering CJK Extension B to H (for instance HanaMinB, Debian package `fonts-hanazono`).

This affects readers who print classical Chinese texts from Wikisource (reported by a user on the Chinese Wikipedia technical village pump, November 2026). Tools that embed the official PDF unchanged, such as Wikipedia2Book (https://wikipedia2book.toolforge.org/, disclosure: I maintain it), cannot fix it on their side.

Related: T226633 (CJK fonts for the PDF renderer, resolved).
