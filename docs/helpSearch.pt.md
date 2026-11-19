# Ajuda: o que se pode escrever no campo «Construir o livro»?

<!-- {% raw %} -->

O campo da primeira etapa aceita muito mais do que o título de um artigo: um endereço, um livro inteiro, uma lista de páginas ou o texto de uma página de livro. Escreva ou cole o que quer adicionar e clique em «Adicionar». As páginas adicionadas aparecem por baixo do campo; vai organizá-las na etapa seguinte.

## Em resumo

| Quer adicionar… | Escreva… | Exemplo |
|---|---|---|
| um artigo cujo título conhece | o título | `Montagne Pelée` |
| uma página precisa | o endereço | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` |
| um artigo noutra língua | o código da língua, dois pontos, o título | `nl:Rotterdam` |
| uma página de outro projeto Wikimedia | o prefixo do projeto e depois o título | `voy:en:Lyon` |
| um livro inteiro | o endereço do sumário ou da página de livro | `https://fr.wikibooks.org/wiki/Cosmologie` |
| várias páginas de uma vez | uma página por linha | ver «Várias páginas de uma vez» |
| um livro preparado numa página «Livro:» | o texto dessa página | ver «Colar o texto de uma página de livro» |

## Pesquisar um artigo

- Escreva algumas letras: aparecem sugestões por baixo do campo.
- A lista ao lado do campo escolhe a língua da Wikipédia onde pesquisar. Com «Todas», o título é pesquisado em todas as línguas da lista e cada resultado indica a sua língua.
- Se o título corresponder exatamente a um artigo, este é adicionado logo. Um título que redireciona para outro artigo adiciona o artigo de destino: `Napoléon Bonaparte` adiciona «Napoléon Ier».
- Caso contrário, os resultados da pesquisa aparecem por baixo do campo: clique no que pretende.
- Com o primeiro artigo adicionado, a sua introdução e o criador da página são propostos como introdução e autor do livro, na etapa Edição. Pode alterá-los.

## Páginas noutra língua ou de outro projeto

Um endereço completo funciona sempre, por exemplo `https://fr.wikivoyage.org/wiki/Lyon`. Com um título, junte à frente um prefixo de língua, de projeto ou ambos:

| Projeto | Prefixo | Exemplo |
|---|---|---|
| Wikipédia noutra língua | código da língua | `nl:Rotterdam` |
| Wikisource | `s:` | `s:Les Misérables` |
| Wikilivros | `b:` | `b:Cosmologie` |
| Wikiviagem | `voy:` | `voy:en:Lyon` |
| Wikiversidade | `v:` | `v:Python` |
| Wikiquote | `q:` | `q:Victor Hugo` |
| Wikcionário | `wikt:` | `fr:wikt:chat` |
| Wikinotícias | `n:` | `n:Accueil` |

Sem código de língua, conta a língua escolhida ao lado do campo. A ordem dos prefixos não importa. Cada página mantém no seu cartão o nome do projeto e a língua.

## Livros inteiros

- **Página de livro da Wikipédia**: escreva o endereço ou o nome, por exemplo `Utilisateur:Alexbzh972/Livres/Martinique`. Todos os artigos são adicionados pela ordem da página, com os capítulos, o título e o subtítulo.
- **Compilação dos Wikilivros**: escreva o endereço da compilação, por exemplo `https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C`. As suas páginas são adicionadas pela ordem da lista, como numa página de livro da Wikipédia.
- **Livro dos Wikilivros ou obra da Wikisource**: escreva o endereço ou o título do sumário, por exemplo `https://fr.wikibooks.org/wiki/Cosmologie` ou `s:Les Misérables`. Uma janela pergunta o que pretende:
  - «O livro inteiro»: todas as páginas, organizadas em capítulos;
  - «O livro inteiro e o seu sumário»: o mesmo, com a página do sumário no início;
  - «Apenas esta página»: só o sumário;
  - «Cancelar»: nada é adicionado.
- **Versão para impressão dos Wikilivros**: escreva o endereço da página «versão para impressão» do livro, por exemplo `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable`. Se essa página for escrita à mão, as suas páginas são adicionadas com um capítulo por título; se for gerada a partir do sumário, abre-se a janela de escolha do livro.

## Várias páginas de uma vez

Cole uma lista, uma página por linha (para mudar de linha ao escrever, use Shift+Enter). Cada linha pode ser um título, um endereço ou uma página com prefixo, e pode também ser escrita como ligação wiki, ligação Markdown ou item de lista numerada ou com marcadores:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

No fim, uma mensagem indica quantas páginas foram adicionadas, quantas já estavam no livro e quantas não foram encontradas. As linhas não encontradas ficam no campo para as poder corrigir. Um sumário de livro na lista abre a janela de escolha descrita acima.

## Colar o texto de uma página de livro

Pode colar o conteúdo de uma página «Livro:» da Wikipédia: `== … ==` dá o título, `=== … ===` o subtítulo, cada linha `;` começa um capítulo e cada ligação `[[…]]` adiciona um artigo.

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

O texto de uma versão para impressão dos Wikilivros, feito de inclusões `{{:…}}`, é aceite da mesma forma: cada título `= … =` torna-se um capítulo.

## Abrir um livro guardado ou partilhado

- O botão «Salvar» descarrega o seu livro para um ficheiro; o botão «Abrir» volta a carregá-lo mais tarde. Nada fica guardado no servidor: esse ficheiro é a sua única cópia.
- Uma ligação da forma `https://wikipedia2book.toolforge.org/?json=https://…` abre um livro guardado em linha (apenas endereços `https://`).
- Uma ligação da forma `https://wikipedia2book.toolforge.org/?source=…` adiciona as suas fontes como se as tivesse escrito: prático para partilhar uma seleção de páginas.

## O que o campo recusa

- os sítios que não são projetos Wikimedia;
- as páginas que não são de conteúdo (discussões, páginas de ajuda ou da comunidade);
- os ficheiros da Wikimedia Commons: adicione-os antes como documentos na etapa Organização, ou como imagens de fundo na etapa Edição;
- as páginas que não existem.

A mensagem de erro explica o que está mal. Vem do servidor e fica em francês, seja qual for a língua da interface.

## E depois?

- **Organização**: organize as páginas, crie capítulos, adicione as suas próprias imagens ou PDF, divida o livro em volumes. Acima de 300 artigos, o livro é dividido em volumes automaticamente.
- **Edição**: título, capa, imagens de fundo, sumário, formato e margens.
- **Gerar o PDF**: cada artigo é retomado tal como a Wikipédia o imprime, e o conjunto forma um único livro pronto a imprimir.

<!-- {% endraw %} -->
