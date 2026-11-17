# 「本を作る」欄のヘルプ：Wikipedia2Book が受け付けるすべて

このページは Wikipedia2Book が受け付けるものをすべて挙げ、それぞれについて**ブラウザー**で試せる例と、同じ内容を **API** で行う例を示します。目的は二つあります。できることを示すことと、リリース前に手作業で確認することです。[フランス語の基準ページ](helpSearch.fr.md)の翻訳です。

基準となる動作は[機能仕様](FunctionalSpec.en.md)（ソースは 3.1 節）と[技術仕様](TechnicalSpec.en.md)（API は 13.3 節）に記載されています。

## 使い方

- **ブラウザー**：https://wikipedia2book.toolforge.org/ を開き、「本を作る」ステップの入力欄に例を貼り付けて「追加」をクリックします。`https://wikipedia2book.toolforge.org/?` で始まるアドレスはそのまま開けます。
- **API**：アドレスをブラウザーで開く（PDF がダウンロードされます）か、`curl -OJ` に渡します。`POST` の呼び出しは `curl` コマンドで示しています。
- **バージョン**：その例が動作するようになったアプリのバージョン。公開中のバージョンは https://wikipedia2book.toolforge.org/api/version で確認できます。
- 「バージョン」列はブラウザーについてのものです。API では、`GET /api/pdf/from-source`（1〜4 節）とページの `?source=` パラメーターは 1.12.0 から使えます（この番号が付く前の 2026 年 11 月 16 日夜から本番稼働）。それより古いバージョンでは、各入力を `POST /api/sources/resolve`（9.1）で判定してから、本を JSON で `POST /api/pdf`（9.3）に送ってください。
- 例は 2026 年 11 月 17 日に、ソース判定のコードで実際のウィキに対して確認しました。その後に改名・削除されたページでは結果が変わることがあります。

略記：**T** = https://wikipedia2book.toolforge.org 。API のアドレスで、`language` は PDF に生成される見出し（表紙、目次、ライセンス）の言語、`wiki` は接頭辞のないタイトルの言語です。

## 1. 1 ページ

| 番号 | ケース | ブラウザー：入力するもの | API | 期待される結果 | バージョン |
|---|---|---|---|---|---|
| 1.1 | ウィキペディア記事の URL | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | 記事が追加され、最初の記事で序文と著者が提案される | ≤ 1.9.7 |
| 1.2 | 正確なタイトル | `Montagne Pelée`（入力欄の横で言語 FR） | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | 記事「Montagne Pelée」が追加される | ≤ 1.9.7 |
| 1.3 | リダイレクトされるタイトル | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | リダイレクトをたどり「Napoléon Ier」が追加される | ≤ 1.9.7 |
| 1.4 | 一致するページがないタイトル | `volcan martinique` | `T/api/sources/resolve` を `POST`（9.1 参照）：`kind` = `search` | 検索結果が入力欄の下に表示され、クリックで追加できる。生成 API は該当テキストとともに 404 を返す | ≤ 1.9.7 |
| 1.5 | 入力中の検索 | 確定せずに `Saint-Pie` と入力 | `T/api/search?query=Saint-Pie&language=fr` | 入力欄の下に候補が表示される | ≤ 1.9.7 |
| 1.6 | 別の言語のタイトル | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | オランダ語の記事が「NL」の印付きで追加される | 1.7.0 |
| 1.7 | すべての言語 | 入力欄の横で「すべて」を選んで `Paris` | `T/api/search?query=Paris&language=all&limit=3` | 一覧の各言語の結果が、それぞれの言語の印付きで表示される。選んだ記事はその言語のまま | 1.12.4 |

## 2. ほかのウィキメディア・プロジェクト

| 番号 | ケース | ブラウザー：入力するもの | API | 期待される結果 | バージョン |
|---|---|---|---|---|---|
| 2.1 | ウィキボヤージュのページ | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | ページが追加され、カードに「ウィキボヤージュ」の印 | 1.8.0 |
| 2.2 | プロジェクトと言語の接頭辞 | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | 英語版ウィキボヤージュのページが追加される | 1.8.0 |
| 2.3 | ウィキバーシティ | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | ページが追加され、「ウィキバーシティ」の印 | 1.8.0 |
| 2.4 | ウィキクォート | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | ページが追加され、「ウィキクォート」の印 | 1.8.0 |
| 2.5 | ウィクショナリー、接頭辞が逆順 | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | ページが追加され、「ウィクショナリー」の印 | 1.8.0 |
| 2.6 | ウィキニュース | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | ページが追加され、「ウィキニュース」の印 | 1.8.0 |
| 2.7 | ウィキソースのテキスト（1 ページ） | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | ページが追加され、PDF で中国語の見出しが読める | 1.7.8 |
| 2.8 | ウィキソースの著者ページ | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | ページがそのまま追加される（略歴と作品一覧） | 1.8.1 |

## 3. 本

| 番号 | ケース | ブラウザー：入力するもの | API | 期待される結果 | バージョン |
|---|---|---|---|---|---|
| 3.1 | URL によるウィキペディアのブックページ | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | ページの順序どおりに 113 記事、`;` が章、`===` が副題。タイトルは「Martinique」 | 1.3.0 |
| 3.2 | 名前によるブックページ | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | 3.1 と同じ結果 | 1.3.0 |
| 3.3 | ウィキブックスの本の目次ページ | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | 「本全体 / 本全体とその目次 / このページのみ / キャンセル」のウィンドウ。「本全体」で章に分かれた 27 ページ | 1.10.0 |
| 3.4 | 目次付きの本全体 | 3.3 と同じく、「本全体とその目次」を選ぶ | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | 目次ページが最初の章より前に来る | 1.10.0 |
| 3.5 | 目次ページのみ | 3.3 と同じく、「このページのみ」を選ぶ | 目次ページだけで `POST /api/pdf`（9.3 参照） | 目次ページだけ | 1.10.0 |
| 3.6 | ウィキソースの作品 | `s:Les Misérables`（言語 FR） | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | 選択ウィンドウ。「本全体」で 5 部 365 章、「Texte entier」は含まれない | 1.11.0 |
| 3.7 | 手書きの印刷用版（アドレス） | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 ページ、`= … =` 見出しごとに 1 章、表紙は省略、タイトルは「Hélices de navires à déplacement」 | 1.12.0 |
| 3.8 | `{{imprimable}}` による印刷用版（アドレス） | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | 目次ページ「Programmation C」の選択ウィンドウ（21 ページ） | 1.12.0 |

## 4. ページの一覧（複数行）

すべての行を一度に入力欄へ貼り付けます（または Shift+Enter で区切ります）。API では `source=` を繰り返します（最大 50）。

| 番号 | ケース | 入力する行 | 期待される結果 | バージョン |
|---|---|---|---|---|
| 4.1 | ウィキリンク | `[[Brest]]` | 「Brest」が追加される | 1.7.0 |
| 4.2 | 言語付きウィキリンク | `[[nl:Amsterdam]]` | オランダ語の記事が追加される | 1.7.0 |
| 4.3 | 表示文字付きウィキリンク | `[[Frégate (bateau)\|Frégate]]` | 「Frégate (bateau)」が追加される | 1.7.0 |
| 4.4 | Markdown リンク、URL に括弧 | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | 「Suchet (navire)」が追加される | 1.7.0 |
| 4.5 | 行頭の番号 | `1. Lorient` | 「Lorient」が追加される | 1.7.0 |
| 4.6 | 行頭の箇条書き記号 | `* Concarneau`（`-`、`•`、`#` も可） | 「Concarneau」が追加される | 1.7.0 |
| 4.7 | 見つからない行 | `Xyzzy inexistant` | 行は入力欄に残り、最後のメッセージで「見つからない」と数えられる | 1.7.0 |
| 4.8 | 一覧の中の目次ページ | `b:Programmation Python` | その目次ページの選択ウィンドウが開く。章は引き継がれない | 1.10.0 |

ブラウザーに貼り付ける完全な一覧：

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

期待される結果：「7 ページを追加、0 ページは追加済み、0 ページは見つかりませんでした。」

API、同じ一覧：`T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. 貼り付けた本のテキスト

| 番号 | ケース | 貼り付けるテキスト | API | 期待される結果 | バージョン |
|---|---|---|---|---|---|
| 5.1 | ウィキペディア「ブック:」の書式 | 下の 5.1 ブロック | 下の 5.1 `curl` | タイトル「Ports bretons」、副題「Guide des ports」、章「Finistère」と「Morbihan」、先頭に章なしの「Brest」 | 1.12.0 |
| 5.2 | ウィキブックスの印刷用版 | 下の 5.2 ブロック | 下の 5.2 `curl` | ウィキブックスの 3 ページが 3 章に、ライセンスは省略 | 1.12.0 |

5.1 ブロック：

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

5.2 ブロック：

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

PDF を作らずに構造だけを読む：同じ内容を `POST /api/books/from-wikitext` に送ります。

## 6. 保存した本を開く（JSON）

| 番号 | ケース | ブラウザー | API | 期待される結果 | バージョン |
|---|---|---|---|---|---|
| 6.1 | アドレスによる JSON の本 | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | 背景画像と文書付きで本が開く（「本をインポートしました。」） | 1.9.6 |
| 6.2 | JSON のウィキブックスの本 | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 8 章 27 ページ | 1.9.6 |
| 6.3 | ローカルの JSON ファイル | 「開く」ボタンで、「保存」で書き出したファイルを選ぶ | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @book.json` | 本が開く / PDF が生成される | ≤ 1.9.7（ブラウザー）、1.12.0（API） |
| 6.4 | JSON のあとにほかのソース | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | JSON の本が開き、続いて追加した目次ページの選択ウィンドウ | 1.12.0 |
| 6.5 | ページのアドレスにソース | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | 3.3 と 1.2 参照 | 各ソースが入力されたのと同じように追加される（確認も含む） | 1.12.0 |
| 6.6 | 拒否されるアドレス | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | エラーメッセージ、何もインポートされない。API は 422「doit commencer par https://」を返す | 1.9.6 |

## 7. 文書と背景画像

| 番号 | ケース | ブラウザー | API（JSON の本のフィールド） | 期待される結果 | バージョン |
|---|---|---|---|---|---|
| 7.1 | パソコンの画像や PDF | 「構成」ステップ、「ファイルを選択 +」 | `data_base64` 付きの `uploaded_documents[]` | 文書が記事と同じように本に配置される。最大 15 MB | ≤ 1.9.7 |
| 7.2 | アドレスによる文書 | 「構成」ステップのアドレス欄：`https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `"url": "https://upload.wikimedia.org/…"` 付きの `uploaded_documents[]` | アドレスだけが保存され、サーバーが生成のたびに画像をダウンロードする | 1.10.0 |
| 7.3 | コモンズのファイルページによる文書 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | 画像（2 000 px のサムネイル）が使われる。PDF なら元のファイル | 1.10.0（ブラウザー）、1.12.0（API） |
| 7.4 | ファイルページによる PDF | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | `uploaded_documents[].url` に同じアドレス | 元の PDF が挿入され、ページは本の判型に合わせられる | 1.10.0（ブラウザー）、1.12.0（API） |
| 7.5 | 表紙の背景画像 | 「編集」ステップ、「表紙の背景画像」、ファイルまたはアドレス（7.2 か 7.3） | `cover_image`：`{"title": "…", "url": "…"}` または `data_base64` | 表紙の背景、ゆがみなし | 1.9.6 |
| 7.6 | 最終ページの画像 | 「編集」ステップ、「最終ページの背景画像」 | `back_image` | ライセンスのあとに独立したページ | 1.9.6 |
| 7.7 | 到達できないアドレス | 文書 `https://example.org/inexistant.png` | 同じアドレス | 生成が止まり、該当するアドレスが示される。API では 502 | 1.10.0 |

## 8. 構成とレイアウト

| 番号 | ケース | ブラウザー | API（`POST /api/pdf` に送る JSON の本） | 期待される結果 | バージョン |
|---|---|---|---|---|---|
| 8.1 | 関連記事 | 記事の「関連記事」ボタン | `POST /api/explore` | 記事のリンクがページ内の順序で提案される | ≤ 1.9.7 |
| 8.2 | 章と順序 | 「構成」ステップ、「章を作成」、ドラッグ＆ドロップ | `chapters`、`article_order`、`unassigned_first` | PDF は表示された順序に従う | ≤ 1.9.7 |
| 8.3 | 目次 | 「編集」ステップ：なし、先頭、末尾 | `table_of_contents`、`toc_position`（`start`、`end`、`before:<キー>`） | 目次が正しい位置に入り、リンクがクリックできる | 1.9.6 |
| 8.4 | 判型、向き、余白 | 「編集」ステップ | `page_format`、`orientation`、`margin_*_mm`、`custom_width_mm` | すべてのページが選んだ判型になる | ≤ 1.9.7 |
| 8.5 | ページ番号 | 「ページ番号を付ける」 | `page_numbers` | 表紙以外のページ下部に番号 | ≤ 1.9.7 |
| 8.6 | PDF の見出しの言語 | 上部の言語選択 | `language` パラメーター（12 言語） | 表紙、目次、ライセンスが選んだ言語になる | ≤ 1.9.7 |
| 8.7 | 手動での分冊 | 「構成」ステップ、「新しい巻」 | `volume_breaks`：`["before:<キー>"]`、続いて `?volume=N` | 巻ごとに 1 つの PDF、ページ番号は 1 から振り直し | 1.9.2（ブラウザー）、1.12.0（API） |
| 8.8 | 300 記事を超える場合 | 本 3.1 にほかのページを加えて 300 を超える | 分冊案は `POST /api/books/volumes`、続いて `POST /api/pdf?volume=1`、`?volume=2`… | 章の間で自動的に分冊、「第 1 巻／全 2 巻」…。`volume` なしでは巻数付きで 413 拒否 | 1.9.0（ブラウザー）、1.12.0（API） |

## 9. PDF を作らない API 呼び出し

| 番号 | ケース | 呼び出し | 期待される結果 |
|---|---|---|---|
| 9.1 | 入力を判定する | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`：`article`、`book`、`subpages`、`search` のいずれか |
| 9.2 | ブックページの構造 | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | 記事、副題、章 |
| 9.3 | JSON で記述した本の PDF | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | 目次ページ 1 枚だけの PDF |
| 9.4 | 生成の進行を追う | 同じ内容を `POST /api/pdf/stream` に送る | NDJSON の行 `progress`、`wait`、続いて `done` と PDF |
| 9.5 | 提案される序文と著者 | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | 最初の段落とページの作成者 |
| 9.6 | 公開中のバージョン | `T/api/version` | バージョン、コミット、記事数の上限 |

## 10. 拒否される入力

エラーメッセージはサーバーから返され、インターフェースの言語にかかわらずフランス語のままです。

| 番号 | 入力 | 期待される結果 |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | 「L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…」、422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | 「Seules les pages de contenu de fr.wikibooks.org…」、422 |
| 10.3 | ソース欄に `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | ソースとしては拒否（コモンズには `<言語>.<プロジェクト>.org` のアドレスがない）。文書や背景画像としては受け付けられる（7.3） |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | 「La page … est introuvable」、404 |
| 10.5 | 空の入力欄 | 「Saisissez …」、422 |
| 10.6 | 記事を選んでいない本で「PDF を生成」 | メッセージ「PDF を生成する前に、記事を少なくとも 1 つ選択してください。」、400 |
