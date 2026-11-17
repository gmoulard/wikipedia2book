# Ayuda del campo «Construir el libro»: todo lo que acepta Wikipedia2Book

Esta página enumera todo lo que acepta Wikipedia2Book, con un ejemplo para probar **en el navegador** y el mismo caso **mediante la API**. Sirve para dos cosas: mostrar las posibilidades y hacer una comprobación manual antes de publicar una versión. Es una traducción de la [página de referencia en francés](helpSearch.fr.md).

El comportamiento de referencia está descrito en las [especificaciones funcionales](FunctionalSpec.en.md) (sección 3.1 para las fuentes) y las [especificaciones técnicas](TechnicalSpec.en.md) (sección 13.3 para la API).

## Cómo usarla

- **Navegador**: abrir https://wikipedia2book.toolforge.org/, pegar el ejemplo en el campo del paso «Construir el libro» y hacer clic en «Añadir». Una dirección que empieza por `https://wikipedia2book.toolforge.org/?` se abre directamente.
- **API**: abrir la dirección en el navegador (se descarga el PDF) o pasarla a `curl -OJ`. Las llamadas `POST` se dan como comandos `curl`.
- **Versión**: versión de la aplicación a partir de la cual funciona el caso. La que está en línea la indica https://wikipedia2book.toolforge.org/api/version.
- La columna «Versión» se refiere al navegador. En la API, `GET /api/pdf/from-source` (secciones 1 a 4) y el parámetro `?source=` de la página existen desde la 1.12.0 (en producción desde la noche del 16 de noviembre de 2026, antes de recibir ese número): con una versión anterior, enviar el libro en JSON a `POST /api/pdf` (9.3) tras reconocer cada entrada con `POST /api/sources/resolve` (9.1).
- Los ejemplos se comprobaron el 17 de noviembre de 2026 con el código de reconocimiento de fuentes contra los wikis reales; una página renombrada o borrada desde entonces puede cambiar el resultado.

Abreviaturas: **T** = https://wikipedia2book.toolforge.org. En las direcciones de la API, `language` es el idioma de los títulos generados en el PDF (portada, índice, licencia) y `wiki` el idioma de los títulos sin prefijo.

## 1. Una sola página

| N.º | Caso | Navegador: qué escribir | API | Resultado esperado | Versión |
|---|---|---|---|---|---|
| 1.1 | URL de un artículo de Wikipedia | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | Se añade el artículo; introducción y autor propuestos con el primer artículo | ≤ 1.9.7 |
| 1.2 | Título exacto | `Montagne Pelée` (idioma FR junto al campo) | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | Se añade el artículo «Montagne Pelée» | ≤ 1.9.7 |
| 1.3 | Título redirigido | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | Se sigue la redirección: se añade «Napoléon Ier» | ≤ 1.9.7 |
| 1.4 | Título sin página exacta | `volcan martinique` | `T/api/sources/resolve` en `POST` (ver 9.1): `kind` = `search` | Los resultados de búsqueda aparecen bajo el campo y se añaden con un clic; la API de generación responde 404 con el texto en cuestión | ≤ 1.9.7 |
| 1.5 | Búsqueda al escribir | Escribir `Saint-Pie` sin confirmar | `T/api/search?query=Saint-Pie&language=fr` | Sugerencias bajo el campo | ≤ 1.9.7 |
| 1.6 | Título en otro idioma | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | Se añade el artículo en neerlandés, marcado «NL» | 1.7.0 |
| 1.7 | Todos los idiomas | `Paris`, con «Todas» elegido junto al campo | `T/api/search?query=Paris&language=all&limit=3` | Resultados en cada idioma de la lista, cada uno marcado con su idioma; el artículo elegido conserva el suyo | 1.12.4 |

## 2. Otros proyectos Wikimedia

| N.º | Caso | Navegador: qué escribir | API | Resultado esperado | Versión |
|---|---|---|---|---|---|
| 2.1 | Página de Wikiviajes | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | Página añadida, tarjeta marcada «Wikiviajes» | 1.8.0 |
| 2.2 | Prefijo de proyecto y de idioma | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | Se añade la página de Wikiviajes en inglés | 1.8.0 |
| 2.3 | Wikiversidad | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | Página añadida, marcada «Wikiversidad» | 1.8.0 |
| 2.4 | Wikiquote | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | Página añadida, marcada «Wikiquote» | 1.8.0 |
| 2.5 | Wikcionario, prefijos en orden inverso | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | Página añadida, marcada «Wikcionario» | 1.8.0 |
| 2.6 | Wikinoticias | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | Página añadida, marcada «Wikinoticias» | 1.8.0 |
| 2.7 | Texto de Wikisource (una página) | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | Página añadida; títulos chinos legibles en el PDF | 1.7.8 |
| 2.8 | Página de autor de Wikisource | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | Página añadida tal cual (biografía y lista de obras) | 1.8.1 |

## 3. Libros

| N.º | Caso | Navegador: qué escribir | API | Resultado esperado | Versión |
|---|---|---|---|---|---|
| 3.1 | Página de libro de Wikipedia por URL | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | 113 artículos en el orden de la página, capítulos `;`, subtítulo `===`; título «Martinique» | 1.3.0 |
| 3.2 | Página de libro por su nombre | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | Mismo resultado que 3.1 | 1.3.0 |
| 3.3 | Índice de un libro de Wikilibros | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | Ventana «El libro completo / El libro completo y su índice / Solo esta página / Cancelar»; «El libro completo» da 27 páginas en capítulos | 1.10.0 |
| 3.4 | Libro completo con su índice | Igual que 3.3, elegir «El libro completo y su índice» | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | El índice primero, antes del primer capítulo | 1.10.0 |
| 3.5 | Solo la página del índice | Igual que 3.3, elegir «Solo esta página» | `POST /api/pdf` con solo la página del índice (ver 9.3) | La página del índice sola | 1.10.0 |
| 3.6 | Obra de Wikisource | `s:Les Misérables` (idioma FR) | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | Ventana de elección; «El libro completo» da 365 capítulos en 5 partes, sin «Texte entier» | 1.11.0 |
| 3.7 | Versión imprimible escrita a mano (dirección) | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 páginas, un capítulo por título `= … =`, portada omitida, título «Hélices de navires à déplacement» | 1.12.0 |
| 3.8 | Versión imprimible mediante `{{imprimable}}` (dirección) | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | La ventana de elección del índice «Programmation C» (21 páginas) | 1.12.0 |

## 4. Listas de páginas (varias líneas)

Pegar todas las líneas a la vez en el campo (o separarlas con Mayús+Intro). En la API, repetir `source=` (50 como máximo).

| N.º | Caso | Línea que escribir | Resultado esperado | Versión |
|---|---|---|---|---|
| 4.1 | Enlace wiki | `[[Brest]]` | Se añade «Brest» | 1.7.0 |
| 4.2 | Enlace wiki con idioma | `[[nl:Amsterdam]]` | Se añade el artículo en neerlandés | 1.7.0 |
| 4.3 | Enlace wiki con texto | `[[Frégate (bateau)\|Frégate]]` | Se añade «Frégate (bateau)» | 1.7.0 |
| 4.4 | Enlace Markdown, paréntesis en la URL | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | Se añade «Suchet (navire)» | 1.7.0 |
| 4.5 | Número al inicio de línea | `1. Lorient` | Se añade «Lorient» | 1.7.0 |
| 4.6 | Viñeta al inicio de línea | `* Concarneau` (también `-`, `•`, `#`) | Se añade «Concarneau» | 1.7.0 |
| 4.7 | Línea no encontrada | `Xyzzy inexistant` | La línea queda en el campo y el mensaje final la cuenta como «no encontrada» | 1.7.0 |
| 4.8 | Índice dentro de una lista | `b:Programmation Python` | Se abre la ventana de elección para ese índice; sus capítulos no se conservan | 1.10.0 |

Lista completa para pegar en el navegador:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Resultado esperado: «7 página(s) añadida(s), 0 ya en el libro, 0 no encontrada(s).»

API, misma lista: `T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. Texto de libro pegado

| N.º | Caso | Texto que pegar | API | Resultado esperado | Versión |
|---|---|---|---|---|---|
| 5.1 | Sintaxis de Wikipedia «Libro:» | Bloque 5.1 abajo | `curl` 5.1 abajo | Título «Ports bretons», subtítulo «Guide des ports», capítulos «Finistère» y «Morbihan», «Brest» al principio sin capítulo | 1.12.0 |
| 5.2 | Versión imprimible de Wikilibros | Bloque 5.2 abajo | `curl` 5.2 abajo | 3 páginas de Wikilibros en 3 capítulos, licencia omitida | 1.12.0 |

Bloque 5.1:

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

```bash
curl -OJ -X POST 'https://wikipedia2book.toolforge.org/api/pdf/from-wikitext?language=fr' \
	-H 'Content-Type: application/json' \
	--data '{"wikitext":"== Ports bretons ==\n=== Guide des ports ===\n:[[Brest]]\n;Finistère\n:[[Concarneau]]\n:[[Douarnenez]]\n;Morbihan\n:[[Lorient]]","language":"fr"}'
```

Bloque 5.2:

```
= Le paradoxe d'Olbers =
{{:Cosmologie/Le paradoxe d'Olbers}}
= L'expansion de l'univers =
{{:Cosmologie/L'expansion de l'univers}}
= Le facteur de Hubble =
{{:Cosmologie/Le facteur de Hubble}}
{{:Licence de documentation libre GNU}}
```

```bash
curl -OJ -X POST 'https://wikipedia2book.toolforge.org/api/pdf/from-wikitext?language=fr' \
	-H 'Content-Type: application/json' \
	--data "{\"wikitext\":\"= Le paradoxe d'Olbers =\n{{:Cosmologie/Le paradoxe d'Olbers}}\n= L'expansion de l'univers =\n{{:Cosmologie/L'expansion de l'univers}}\n= Le facteur de Hubble =\n{{:Cosmologie/Le facteur de Hubble}}\n{{:Licence de documentation libre GNU}}\",\"language\":\"fr\"}"
```

Leer solo la estructura, sin PDF: mismo contenido hacia `POST /api/books/from-wikitext`.

## 6. Abrir un libro guardado (JSON)

| N.º | Caso | Navegador | API | Resultado esperado | Versión |
|---|---|---|---|---|---|
| 6.1 | Libro JSON por dirección | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | El libro se abre («Libro importado.») con sus imágenes de fondo y su documento | 1.9.6 |
| 6.2 | Libro de Wikilibros en JSON | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 27 páginas en 8 capítulos | 1.9.6 |
| 6.3 | Archivo JSON local | Botón «Abrir», elegir un archivo exportado con «Guardar» | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @libro.json` | El libro se abre / se genera el PDF | ≤ 1.9.7 (navegador), 1.12.0 (API) |
| 6.4 | JSON y después otras fuentes | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | Se abre el libro JSON y luego la ventana de elección para el índice añadido | 1.12.0 |
| 6.5 | Fuentes en la dirección de la página | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | Ver 3.3 y 1.2 | Cada fuente se añade como si se hubiera escrito, pregunta incluida | 1.12.0 |
| 6.6 | Dirección rechazada | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | Mensaje de error, no se importa nada; la API responde 422 «doit commencer par https://» | 1.9.6 |

## 7. Documentos e imágenes de fondo

| N.º | Caso | Navegador | API (campo del libro JSON) | Resultado esperado | Versión |
|---|---|---|---|---|---|
| 7.1 | Imagen o PDF del ordenador | Paso Organización, «Elegir un archivo +» | `uploaded_documents[]` con `data_base64` | Documento colocado en el libro como un artículo, 15 MB como máximo | ≤ 1.9.7 |
| 7.2 | Documento por dirección | Paso Organización, campo de dirección: `https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `uploaded_documents[]` con `"url": "https://upload.wikimedia.org/…"` | Solo se guarda la dirección; el servidor descarga la imagen en cada generación | 1.10.0 |
| 7.3 | Documento por página de archivo de Commons | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | Se usa la imagen (miniatura de 2 000 px); para un PDF, el original | 1.10.0 (navegador), 1.12.0 (API) |
| 7.4 | PDF por página de archivo | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | Misma dirección en `uploaded_documents[].url` | Se inserta el PDF original, páginas ajustadas al formato del libro | 1.10.0 (navegador), 1.12.0 (API) |
| 7.5 | Imagen de fondo de la portada | Paso Edición, «Imagen de fondo de la portada», archivo o dirección (7.2 o 7.3) | `cover_image`: `{"title": "…", "url": "…"}` o `data_base64` | Fondo de la portada, sin deformación | 1.9.6 |
| 7.6 | Imagen de la última página | Paso Edición, «Imagen de fondo de la última página» | `back_image` | Página propia después de la licencia | 1.9.6 |
| 7.7 | Dirección inaccesible | Documento `https://example.org/inexistant.png` | Misma dirección | Generación detenida, se indica la dirección en cuestión; 502 mediante la API | 1.10.0 |

## 8. Organización y maquetación

| N.º | Caso | Navegador | API (libro JSON hacia `POST /api/pdf`) | Resultado esperado | Versión |
|---|---|---|---|---|---|
| 8.1 | Artículos relacionados | Botón «Artículos relacionados» de un artículo | `POST /api/explore` | Enlaces del artículo propuestos, en el orden de la página | ≤ 1.9.7 |
| 8.2 | Capítulos y orden | Paso Organización, «Crear un capítulo», arrastrar y soltar | `chapters`, `article_order`, `unassigned_first` | El PDF sigue el orden mostrado | ≤ 1.9.7 |
| 8.3 | Índice | Paso Edición: ninguno, inicio, final | `table_of_contents`, `toc_position` (`start`, `end`, `before:<clave>`) | Índice en su lugar, enlaces clicables | 1.9.6 |
| 8.4 | Formato, orientación, márgenes | Paso Edición | `page_format`, `orientation`, `margin_*_mm`, `custom_width_mm` | Todas las páginas en el formato elegido | ≤ 1.9.7 |
| 8.5 | Números de página | «Numerar las páginas» | `page_numbers` | Números al pie de página, salvo en la portada | ≤ 1.9.7 |
| 8.6 | Idioma de los títulos del PDF | Selector de idioma arriba | Parámetro `language` (12 idiomas) | Portada, índice, licencia en el idioma elegido | ≤ 1.9.7 |
| 8.7 | Corte manual en tomos | Paso Organización, «Nuevo volumen» | `volume_breaks`: `["before:<clave>"]`, después `?volume=N` | Un PDF por tomo, numeración que vuelve a empezar en 1 | 1.9.2 (navegador), 1.12.0 (API) |
| 8.8 | Más de 300 artículos | Libro 3.1 + otras páginas hasta pasar de 300 | `POST /api/books/volumes` para el plan, después `POST /api/pdf?volume=1`, `?volume=2`… | División automática entre capítulos, «Tomo 1/2»…; sin `volume`, rechazo 413 con el número de tomos | 1.9.0 (navegador), 1.12.0 (API) |

## 9. Llamadas a la API sin PDF

| N.º | Caso | Llamada | Resultado esperado |
|---|---|---|---|
| 9.1 | Reconocer una entrada | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`: `article`, `book`, `subpages` o `search` |
| 9.2 | Estructura de una página de libro | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | Artículos, subtítulo, capítulos |
| 9.3 | PDF de un libro descrito en JSON | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | PDF de una sola página de índice |
| 9.4 | Seguir la generación | Mismo contenido hacia `POST /api/pdf/stream` | Líneas NDJSON `progress`, `wait`, después `done` y el PDF |
| 9.5 | Introducción y autor propuestos | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | Primer párrafo y creador de la página |
| 9.6 | Versión en línea | `T/api/version` | Versión, commit, límite de artículos |

## 10. Entradas rechazadas

Los mensajes de error vienen del servidor y se quedan en francés, sea cual sea el idioma de la interfaz.

| N.º | Entrada | Resultado esperado |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | «L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…»; 422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | «Seules les pages de contenu de fr.wikibooks.org…»; 422 |
| 10.3 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` en el campo de fuentes | Rechazado como fuente (Commons no tiene dirección `<idioma>.<proyecto>.org`); aceptado como documento o imagen de fondo (7.3) |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | «La page … est introuvable»; 404 |
| 10.5 | Campo vacío | «Saisissez …»; 422 |
| 10.6 | Libro sin ningún artículo seleccionado, luego «Generar el PDF» | Mensaje «Seleccione al menos un artículo antes de generar el PDF.»; 400 |
