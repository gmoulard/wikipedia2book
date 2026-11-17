# Ajuda do campo «Construir o livro»: tudo o que o Wikipedia2Book aceita

Esta página lista tudo o que o Wikipedia2Book aceita, com, para cada caso, um exemplo para testar **no navegador** e o mesmo caso **pela API**. Serve para duas coisas: mostrar as possibilidades e fazer uma verificação manual antes de publicar uma versão. É uma tradução da [página de referência em francês](helpSearch.fr.md).

O comportamento de referência está descrito nas [especificações funcionais](FunctionalSpec.en.md) (secção 3.1 para as fontes) e nas [especificações técnicas](TechnicalSpec.en.md) (secção 13.3 para a API).

## Como usar

- **Navegador**: abrir https://wikipedia2book.toolforge.org/, colar o exemplo no campo da etapa «Construir o livro» e clicar em «Adicionar». Um endereço que começa por `https://wikipedia2book.toolforge.org/?` abre diretamente.
- **API**: abrir o endereço no navegador (o PDF é descarregado) ou passá-lo a `curl -OJ`. As chamadas `POST` são dadas como comandos `curl`.
- **Versão**: versão da aplicação a partir da qual o caso funciona. A versão em linha é indicada por https://wikipedia2book.toolforge.org/api/version.
- A coluna «Versão» diz respeito ao navegador. Do lado da API, `GET /api/pdf/from-source` (secções 1 a 4) e o parâmetro `?source=` da página existem desde a 1.12.0 (em produção desde a noite de 16 de novembro de 2026, antes de receberem esse número): com uma versão anterior, enviar o livro em JSON para `POST /api/pdf` (9.3) depois de reconhecer cada entrada com `POST /api/sources/resolve` (9.1).
- Os exemplos foram verificados a 17 de novembro de 2026 com o código de reconhecimento das fontes contra os wikis reais; uma página renomeada ou eliminada desde então pode mudar o resultado.

Abreviaturas: **T** = https://wikipedia2book.toolforge.org. Nos endereços da API, `language` é a língua dos títulos gerados no PDF (capa, sumário, licença) e `wiki` a língua dos títulos sem prefixo.

## 1. Uma única página

| N.º | Caso | Navegador: o que escrever | API | Resultado esperado | Versão |
|---|---|---|---|---|---|
| 1.1 | URL de um artigo da Wikipédia | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | O artigo é adicionado; introdução e autor propostos no primeiro artigo | ≤ 1.9.7 |
| 1.2 | Título exato | `Montagne Pelée` (língua FR ao lado do campo) | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | O artigo «Montagne Pelée» é adicionado | ≤ 1.9.7 |
| 1.3 | Título redirecionado | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | O redirecionamento é seguido: é adicionado «Napoléon Ier» | ≤ 1.9.7 |
| 1.4 | Título sem página exata | `volcan martinique` | `T/api/sources/resolve` em `POST` (ver 9.1): `kind` = `search` | Os resultados da pesquisa aparecem sob o campo e são adicionados com um clique; a API de geração responde 404 com o texto em causa | ≤ 1.9.7 |
| 1.5 | Pesquisa durante a escrita | Escrever `Saint-Pie` sem confirmar | `T/api/search?query=Saint-Pie&language=fr` | Sugestões sob o campo | ≤ 1.9.7 |
| 1.6 | Título noutra língua | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | É adicionado o artigo em neerlandês, marcado «NL» | 1.7.0 |
| 1.7 | Todas as línguas | `Paris`, com «Todas» escolhido ao lado do campo | `T/api/search?query=Paris&language=all&limit=3` | Resultados em cada língua da lista, cada um marcado com a sua língua; o artigo escolhido mantém a sua | 1.12.4 |

## 2. Outros projetos Wikimedia

| N.º | Caso | Navegador: o que escrever | API | Resultado esperado | Versão |
|---|---|---|---|---|---|
| 2.1 | Página da Wikiviagem | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | Página adicionada, cartão marcado «Wikiviagem» | 1.8.0 |
| 2.2 | Prefixo de projeto e de língua | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | É adicionada a página da Wikiviagem em inglês | 1.8.0 |
| 2.3 | Wikiversidade | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | Página adicionada, marcada «Wikiversidade» | 1.8.0 |
| 2.4 | Wikiquote | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | Página adicionada, marcada «Wikiquote» | 1.8.0 |
| 2.5 | Wikcionário, prefixos em ordem inversa | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | Página adicionada, marcada «Wikcionário» | 1.8.0 |
| 2.6 | Wikinotícias | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | Página adicionada, marcada «Wikinotícias» | 1.8.0 |
| 2.7 | Texto da Wikisource (uma página) | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | Página adicionada; títulos chineses legíveis no PDF | 1.7.8 |
| 2.8 | Página de autor da Wikisource | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | Página adicionada tal como está (biografia e lista de obras) | 1.8.1 |

## 3. Livros

| N.º | Caso | Navegador: o que escrever | API | Resultado esperado | Versão |
|---|---|---|---|---|---|
| 3.1 | Página de livro da Wikipédia por URL | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | 113 artigos na ordem da página, capítulos `;`, subtítulo `===`; título «Martinique» | 1.3.0 |
| 3.2 | Página de livro pelo nome | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | Mesmo resultado que 3.1 | 1.3.0 |
| 3.3 | Sumário de um livro dos Wikilivros | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | Janela «O livro inteiro / O livro inteiro e o seu sumário / Apenas esta página / Cancelar»; «O livro inteiro» dá 27 páginas em capítulos | 1.10.0 |
| 3.4 | Livro inteiro com o seu sumário | Como 3.3, escolher «O livro inteiro e o seu sumário» | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | O sumário primeiro, antes do primeiro capítulo | 1.10.0 |
| 3.5 | Apenas a página do sumário | Como 3.3, escolher «Apenas esta página» | `POST /api/pdf` só com a página do sumário (ver 9.3) | A página do sumário sozinha | 1.10.0 |
| 3.6 | Obra da Wikisource | `s:Les Misérables` (língua FR) | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | Janela de escolha; «O livro inteiro» dá 365 capítulos em 5 partes, sem «Texte entier» | 1.11.0 |
| 3.7 | Versão para impressão escrita à mão (endereço) | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 páginas, um capítulo por título `= … =`, capa omitida, título «Hélices de navires à déplacement» | 1.12.0 |
| 3.8 | Versão para impressão por `{{imprimable}}` (endereço) | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | A janela de escolha do sumário «Programmation C» (21 páginas) | 1.12.0 |

## 4. Listas de páginas (várias linhas)

Colar todas as linhas de uma vez no campo (ou separá-las com Shift+Enter). Do lado da API, repetir `source=` (50 no máximo).

| N.º | Caso | Linha a escrever | Resultado esperado | Versão |
|---|---|---|---|---|
| 4.1 | Ligação wiki | `[[Brest]]` | «Brest» adicionado | 1.7.0 |
| 4.2 | Ligação wiki com língua | `[[nl:Amsterdam]]` | Artigo em neerlandês adicionado | 1.7.0 |
| 4.3 | Ligação wiki com texto | `[[Frégate (bateau)\|Frégate]]` | «Frégate (bateau)» adicionado | 1.7.0 |
| 4.4 | Ligação Markdown, parênteses na URL | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | «Suchet (navire)» adicionado | 1.7.0 |
| 4.5 | Número no início da linha | `1. Lorient` | «Lorient» adicionado | 1.7.0 |
| 4.6 | Marcador no início da linha | `* Concarneau` (também `-`, `•`, `#`) | «Concarneau» adicionado | 1.7.0 |
| 4.7 | Linha não encontrada | `Xyzzy inexistant` | A linha fica no campo e a mensagem final conta-a como «não encontrada» | 1.7.0 |
| 4.8 | Sumário numa lista | `b:Programmation Python` | Abre-se a janela de escolha para esse sumário; os seus capítulos não são mantidos | 1.10.0 |

Lista completa para colar no navegador:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Resultado esperado: «7 página(s) adicionada(s), 0 já no livro, 0 não encontrada(s).»

API, mesma lista: `T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. Texto de livro colado

| N.º | Caso | Texto a colar | API | Resultado esperado | Versão |
|---|---|---|---|---|---|
| 5.1 | Sintaxe da Wikipédia «Livro:» | Bloco 5.1 abaixo | `curl` 5.1 abaixo | Título «Ports bretons», subtítulo «Guide des ports», capítulos «Finistère» e «Morbihan», «Brest» no início sem capítulo | 1.12.0 |
| 5.2 | Versão para impressão dos Wikilivros | Bloco 5.2 abaixo | `curl` 5.2 abaixo | 3 páginas dos Wikilivros em 3 capítulos, licença omitida | 1.12.0 |

Bloco 5.1:

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

Bloco 5.2:

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

Ler apenas a estrutura, sem PDF: mesmo conteúdo para `POST /api/books/from-wikitext`.

## 6. Abrir um livro guardado (JSON)

| N.º | Caso | Navegador | API | Resultado esperado | Versão |
|---|---|---|---|---|---|
| 6.1 | Livro JSON por endereço | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | O livro abre («Livro importado.») com as suas imagens de fundo e o seu documento | 1.9.6 |
| 6.2 | Livro dos Wikilivros em JSON | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 27 páginas em 8 capítulos | 1.9.6 |
| 6.3 | Ficheiro JSON local | Botão «Abrir», escolher um ficheiro exportado com «Salvar» | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @livro.json` | O livro abre / o PDF é gerado | ≤ 1.9.7 (navegador), 1.12.0 (API) |
| 6.4 | JSON e depois outras fontes | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | Abre o livro JSON e depois a janela de escolha para o sumário adicionado | 1.12.0 |
| 6.5 | Fontes no endereço da página | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | Ver 3.3 e 1.2 | Cada fonte é adicionada como se tivesse sido escrita, pergunta incluída | 1.12.0 |
| 6.6 | Endereço recusado | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | Mensagem de erro, nada é importado; a API responde 422 «doit commencer par https://» | 1.9.6 |

## 7. Documentos e imagens de fundo

| N.º | Caso | Navegador | API (campo do livro JSON) | Resultado esperado | Versão |
|---|---|---|---|---|---|
| 7.1 | Imagem ou PDF do computador | Etapa Organização, «Escolher um arquivo +» | `uploaded_documents[]` com `data_base64` | Documento colocado no livro como um artigo, 15 MB no máximo | ≤ 1.9.7 |
| 7.2 | Documento por endereço | Etapa Organização, campo de endereço: `https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `uploaded_documents[]` com `"url": "https://upload.wikimedia.org/…"` | Só o endereço é guardado; o servidor descarrega a imagem a cada geração | 1.10.0 |
| 7.3 | Documento por página de ficheiro do Commons | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | A imagem (miniatura de 2 000 px) é usada; para um PDF, o original | 1.10.0 (navegador), 1.12.0 (API) |
| 7.4 | PDF por página de ficheiro | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | Mesmo endereço em `uploaded_documents[].url` | O PDF original é inserido, páginas ajustadas ao formato do livro | 1.10.0 (navegador), 1.12.0 (API) |
| 7.5 | Imagem de fundo da capa | Etapa Edição, «Imagem de fundo da capa», ficheiro ou endereço (7.2 ou 7.3) | `cover_image`: `{"title": "…", "url": "…"}` ou `data_base64` | Fundo da capa, sem deformação | 1.9.6 |
| 7.6 | Imagem da última página | Etapa Edição, «Imagem de fundo da última página» | `back_image` | Página própria depois da licença | 1.9.6 |
| 7.7 | Endereço inacessível | Documento `https://example.org/inexistant.png` | Mesmo endereço | Geração interrompida, o endereço em causa é indicado; 502 pela API | 1.10.0 |

## 8. Organização e paginação

| N.º | Caso | Navegador | API (livro JSON para `POST /api/pdf`) | Resultado esperado | Versão |
|---|---|---|---|---|---|
| 8.1 | Artigos relacionados | Botão «Artigos relacionados» de um artigo | `POST /api/explore` | Ligações do artigo propostas, na ordem da página | ≤ 1.9.7 |
| 8.2 | Capítulos e ordem | Etapa Organização, «Criar um capítulo», arrastar e largar | `chapters`, `article_order`, `unassigned_first` | O PDF segue a ordem apresentada | ≤ 1.9.7 |
| 8.3 | Sumário | Etapa Edição: nenhum, início, fim | `table_of_contents`, `toc_position` (`start`, `end`, `before:<chave>`) | Sumário no lugar certo, ligações clicáveis | 1.9.6 |
| 8.4 | Formato, orientação, margens | Etapa Edição | `page_format`, `orientation`, `margin_*_mm`, `custom_width_mm` | Todas as páginas no formato escolhido | ≤ 1.9.7 |
| 8.5 | Números de página | «Numerar as páginas» | `page_numbers` | Números no fundo da página, exceto na capa | ≤ 1.9.7 |
| 8.6 | Língua dos títulos do PDF | Seletor de língua no topo | Parâmetro `language` (12 línguas) | Capa, sumário, licença na língua escolhida | ≤ 1.9.7 |
| 8.7 | Divisão manual em volumes | Etapa Organização, «Novo volume» | `volume_breaks`: `["before:<chave>"]`, depois `?volume=N` | Um PDF por volume, numeração recomeçada em 1 | 1.9.2 (navegador), 1.12.0 (API) |
| 8.8 | Mais de 300 artigos | Livro 3.1 + outras páginas até passar de 300 | `POST /api/books/volumes` para o plano, depois `POST /api/pdf?volume=1`, `?volume=2`… | Divisão automática entre capítulos, «Volume 1/2»…; sem `volume`, recusa 413 com o número de volumes | 1.9.0 (navegador), 1.12.0 (API) |

## 9. Chamadas à API sem PDF

| N.º | Caso | Chamada | Resultado esperado |
|---|---|---|---|
| 9.1 | Reconhecer uma entrada | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`: `article`, `book`, `subpages` ou `search` |
| 9.2 | Estrutura de uma página de livro | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | Artigos, subtítulo, capítulos |
| 9.3 | PDF de um livro descrito em JSON | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | PDF de uma única página de sumário |
| 9.4 | Acompanhar a geração | Mesmo conteúdo para `POST /api/pdf/stream` | Linhas NDJSON `progress`, `wait`, depois `done` e o PDF |
| 9.5 | Introdução e autor propostos | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | Primeiro parágrafo e criador da página |
| 9.6 | Versão em linha | `T/api/version` | Versão, commit, limite de artigos |

## 10. Entradas recusadas

As mensagens de erro vêm do servidor e ficam em francês, seja qual for a língua da interface.

| N.º | Entrada | Resultado esperado |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | «L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…»; 422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | «Seules les pages de contenu de fr.wikibooks.org…»; 422 |
| 10.3 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` no campo de fontes | Recusado como fonte (o Commons não tem endereço `<língua>.<projeto>.org`); aceite como documento ou imagem de fundo (7.3) |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | «La page … est introuvable»; 404 |
| 10.5 | Campo vazio | «Saisissez …»; 422 |
| 10.6 | Livro sem nenhum artigo selecionado, depois «Gerar o PDF» | Mensagem «Selecione pelo menos um artigo antes de gerar o PDF.»; 400 |
