# Ayuda: ¿qué se puede escribir en el campo «Construir el libro»?

<!-- {% raw %} -->

El campo del primer paso acepta mucho más que el título de un artículo: una dirección, un libro completo, una lista de páginas o el texto de una página de libro. Escribe o pega lo que quieras añadir y haz clic en «Añadir». Las páginas añadidas aparecen bajo el campo; las ordenarás en el paso siguiente.

## En resumen

| Quieres añadir… | Escribe… | Ejemplo |
|---|---|---|
| un artículo cuyo título conoces | su título | `Montagne Pelée` |
| una página concreta | su dirección | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` |
| un artículo en otro idioma | el código del idioma, dos puntos y el título | `nl:Rotterdam` |
| una página de otro proyecto Wikimedia | el prefijo del proyecto y luego el título | `voy:en:Lyon` |
| una imagen, un PDF o una página web de otro sitio, o un archivo de Wikimedia Commons | su dirección: se convierte en un documento del libro, marcado «URL de Internet» | `https://commons.wikimedia.org/wiki/File:Montagne_Pelée_1902.jpg` |
| un libro completo | la dirección de su índice o de su página de libro | `https://fr.wikibooks.org/wiki/Cosmologie` |
| varias páginas a la vez | una página por línea | ver «Varias páginas a la vez» |
| un libro preparado en una página «Libro:» | el texto de esa página | ver «Pegar el texto de una página de libro» |

## Buscar un artículo

- Escribe unas letras: aparecen sugerencias bajo el campo.
- La lista junto al campo elige en qué idioma de Wikipedia buscar. Con «Todas», el título se busca en todos los idiomas de la lista y cada resultado indica su idioma.
- Si el título coincide exactamente con un artículo, se añade directamente. Un título que redirige a otro artículo añade el artículo de destino: `Napoléon Bonaparte` añade «Napoléon Ier».
- Si no, los resultados de la búsqueda aparecen bajo el campo: haz clic en el que quieras.
- Con el primer artículo añadido, su introducción y el creador de la página se proponen como introducción y autor del libro en el paso Edición. Puedes cambiarlos.

## Páginas en otro idioma o de otro proyecto

Una dirección completa siempre funciona, por ejemplo `https://fr.wikivoyage.org/wiki/Lyon`. Con un título, añade delante un prefijo de idioma, de proyecto o ambos:

| Proyecto | Prefijo | Ejemplo |
|---|---|---|
| Wikipedia en otro idioma | código del idioma | `nl:Rotterdam` |
| Wikisource | `s:` | `s:Les Misérables` |
| Wikilibros | `b:` | `b:Cosmologie` |
| Wikiviajes | `voy:` | `voy:en:Lyon` |
| Wikiversidad | `v:` | `v:Python` |
| Wikiquote | `q:` | `q:Victor Hugo` |
| Wikcionario | `wikt:` | `fr:wikt:chat` |
| Wikinoticias | `n:` | `n:Accueil` |

Sin código de idioma, se usa el idioma elegido junto al campo. El orden de los prefijos no importa. Cada página conserva en su tarjeta el nombre de su proyecto y su idioma.

## Libros completos

- **Página de libro de Wikipedia**: escribe su dirección o su nombre, por ejemplo `Utilisateur:Alexbzh972/Livres/Martinique`. Todos sus artículos se añaden en el orden de la página, con sus capítulos, su título y su subtítulo.
- **Compilación de Wikilibros**: escribe la dirección de la compilación, por ejemplo `https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C`. Sus páginas se añaden en el orden de la lista, como en una página de libro de Wikipedia.
- **Libro de Wikilibros u obra de Wikisource**: escribe la dirección o el título de su índice, por ejemplo `https://fr.wikibooks.org/wiki/Cosmologie` o `s:Les Misérables`. Una ventana te pregunta qué quieres:
  - «El libro completo»: todas sus páginas, ordenadas en capítulos;
  - «El libro completo y su índice»: lo mismo, con la página del índice al principio;
  - «Solo esta página»: solo el índice;
  - «Cancelar»: no se añade nada.
- **Versión imprimible de Wikilibros**: escribe la dirección de la página «versión imprimible» del libro, por ejemplo `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable`. Si esa página está escrita a mano, sus páginas se añaden con un capítulo por título; si se genera a partir del índice, se abre la ventana de elección del libro.

## Varias páginas a la vez

Pega una lista, una página por línea (para cambiar de línea al escribir, usa Mayús+Intro). Cada línea puede ser un título, una dirección o una página con prefijo, y también puede escribirse como enlace wiki, enlace Markdown o elemento de lista numerada o con viñetas:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Al final, un mensaje indica cuántas páginas se añadieron, cuántas ya estaban en el libro y cuántas no se encontraron. Las líneas no encontradas se quedan en el campo para que puedas corregirlas. Un índice de libro dentro de la lista abre la ventana de elección descrita antes.

## Pegar el texto de una página de libro

Puedes pegar el contenido de una página «Libro:» de Wikipedia: `== … ==` da el título, `=== … ===` el subtítulo, cada línea `;` empieza un capítulo y cada enlace `[[…]]` añade un artículo.

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

El texto de una versión imprimible de Wikilibros, hecho de inclusiones `{{:…}}`, se acepta igual: cada título `= … =` se convierte en un capítulo.

## Abrir un libro guardado o compartido

- El botón «Guardar» descarga tu libro en un archivo; el botón «Abrir» lo vuelve a cargar más tarde. No se guarda nada en el servidor: ese archivo es tu única copia.
- Un enlace de la forma `https://wikipedia2book.toolforge.org/?json=https://…` abre un libro guardado en línea (solo direcciones `https://`).
- Un enlace de la forma `https://wikipedia2book.toolforge.org/?source=…` añade sus fuentes como si las hubieras escrito: práctico para compartir una selección de páginas.

## Lo que el campo rechaza

- las páginas que no son de contenido (discusiones, páginas de ayuda o de la comunidad);
- las páginas que no existen.

El mensaje de error explica qué ocurre. Viene del servidor y se queda en francés, sea cual sea el idioma de la interfaz.

## ¿Y después?

- **Organización**: ordena las páginas, crea capítulos, añade tus propias imágenes o PDF, divide el libro en tomos. Por encima de 300 artículos, el libro se divide en tomos automáticamente.
- **Edición**: título, portada, imágenes de fondo, índice, formato y márgenes.
- **Generar el PDF**: cada artículo se toma tal como Wikipedia lo imprime, y el conjunto forma un solo libro listo para imprimir.

<!-- {% endraw %} -->
