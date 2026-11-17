# “构建图书”输入框帮助：Wikipedia2Book 接受的所有内容

本页列出 Wikipedia2Book 接受的所有内容，每种情况都给出一个可在**浏览器中**试用的示例，以及**通过 API** 的相同情况。它有两个用途：展示各种可能，以及在发布版本前进行人工检查。本页译自[法语参考页面](helpSearch.fr.md)。

参考行为见[功能规格](FunctionalSpec.en.md)（来源见第 3.1 节）和[技术规格](TechnicalSpec.en.md)（API 见第 13.3 节）。

## 使用方法

- **浏览器**：打开 https://wikipedia2book.toolforge.org/ ，将示例粘贴到“构建图书”步骤的输入框中，然后点击“添加”。以 `https://wikipedia2book.toolforge.org/?` 开头的地址可直接打开。
- **API**：在浏览器中打开该地址（会下载 PDF），或将其交给 `curl -OJ`。`POST` 调用以 `curl` 命令给出。
- **版本**：该情况开始可用的应用版本。线上版本见 https://wikipedia2book.toolforge.org/api/version 。
- “版本”一栏针对浏览器。API 方面，`GET /api/pdf/from-source`（第 1 至 4 节）和页面的 `?source=` 参数自 1.12.0 起提供（在获得这个编号之前，自 2026 年 11 月 16 日晚已上线）：对于更早的版本，先用 `POST /api/sources/resolve`（9.1）识别每一项输入，再把 JSON 格式的图书发送到 `POST /api/pdf`（9.3）。
- 这些示例于 2026 年 11 月 17 日用来源识别代码对真实的维基进行了验证；此后被重命名或删除的页面可能改变结果。

缩写：**T** = https://wikipedia2book.toolforge.org 。在 API 地址中，`language` 是 PDF 中生成标题（封面、目录、许可协议）的语言，`wiki` 是不带前缀的标题所用的语言。

## 1. 单个页面

| 编号 | 情况 | 浏览器：输入内容 | API | 预期结果 | 版本 |
|---|---|---|---|---|---|
| 1.1 | 维基百科条目的 URL | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | 添加该条目；添加第一篇条目时建议简介和作者 | ≤ 1.9.7 |
| 1.2 | 精确标题 | `Montagne Pelée`（输入框旁语言选 FR） | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | 添加条目“Montagne Pelée” | ≤ 1.9.7 |
| 1.3 | 重定向的标题 | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | 跟随重定向：添加“Napoléon Ier” | ≤ 1.9.7 |
| 1.4 | 没有精确页面的标题 | `volcan martinique` | 以 `POST` 调用 `T/api/sources/resolve`（见 9.1）：`kind` = `search` | 搜索结果显示在输入框下方，点击即可添加；生成 API 返回 404 并附上相关文本 | ≤ 1.9.7 |
| 1.5 | 输入时搜索 | 输入 `Saint-Pie` 但不确认 | `T/api/search?query=Saint-Pie&language=fr` | 输入框下方出现建议 | ≤ 1.9.7 |
| 1.6 | 其他语言的标题 | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | 添加荷兰语条目，标记为“NL” | 1.7.0 |
| 1.7 | 全部语言 | `Paris`，输入框旁选择“全部” | `T/api/search?query=Paris&language=all&limit=3` | 列表中每种语言的结果，各自标明语言；选中的条目保留其语言 | 1.12.4 |

## 2. 其他维基媒体项目

| 编号 | 情况 | 浏览器：输入内容 | API | 预期结果 | 版本 |
|---|---|---|---|---|---|
| 2.1 | 维基导游页面 | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | 页面已添加，卡片标记为“维基导游” | 1.8.0 |
| 2.2 | 项目前缀和语言前缀 | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | 添加英语维基导游页面 | 1.8.0 |
| 2.3 | 维基学院 | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | 页面已添加，标记为“维基学院” | 1.8.0 |
| 2.4 | 维基语录 | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | 页面已添加，标记为“维基语录” | 1.8.0 |
| 2.5 | 维基词典，前缀顺序相反 | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | 页面已添加，标记为“维基词典” | 1.8.0 |
| 2.6 | 维基新闻 | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | 页面已添加，标记为“维基新闻” | 1.8.0 |
| 2.7 | 维基文库文本（单页） | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | 页面已添加；PDF 中的中文标题清晰可读 | 1.7.8 |
| 2.8 | 维基文库作者页面 | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | 页面按原样添加（传记和作品列表） | 1.8.1 |

## 3. 图书

| 编号 | 情况 | 浏览器：输入内容 | API | 预期结果 | 版本 |
|---|---|---|---|---|---|
| 3.1 | 通过 URL 的维基百科图书页面 | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | 按页面顺序的 113 篇条目，`;` 为章节，`===` 为副标题；标题“Martinique” | 1.3.0 |
| 3.2 | 通过名称的图书页面 | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | 与 3.1 相同 | 1.3.0 |
| 3.3 | 维基教科书图书的目录页 | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | 弹出“整本书 / 整本书及其目录 / 仅此页面 / 取消”窗口；“整本书”得到分章节的 27 页 | 1.10.0 |
| 3.4 | 整本书及其目录 | 同 3.3，选择“整本书及其目录” | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | 目录页在最前，位于第一章之前 | 1.10.0 |
| 3.5 | 仅目录页 | 同 3.3，选择“仅此页面” | 仅含目录页的 `POST /api/pdf`（见 9.3） | 只有目录页 | 1.10.0 |
| 3.6 | 维基文库作品 | `s:Les Misérables`（语言 FR） | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | 选择窗口；“整本书”得到 5 部分共 365 章，不含“Texte entier” | 1.11.0 |
| 3.7 | 手写的可打印版本（地址） | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 页，每个 `= … =` 标题为一章，省略封面，标题“Hélices de navires à déplacement” | 1.12.0 |
| 3.8 | 通过 `{{imprimable}}` 的可打印版本（地址） | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | 目录页“Programmation C”的选择窗口（21 页） | 1.12.0 |

## 4. 页面列表（多行）

将所有行一次性粘贴到输入框中（或用 Shift+Enter 分隔）。API 方面，重复 `source=`（最多 50 个）。

| 编号 | 情况 | 输入的行 | 预期结果 | 版本 |
|---|---|---|---|---|
| 4.1 | 维基链接 | `[[Brest]]` | 添加“Brest” | 1.7.0 |
| 4.2 | 带语言的维基链接 | `[[nl:Amsterdam]]` | 添加荷兰语条目 | 1.7.0 |
| 4.3 | 带文字的维基链接 | `[[Frégate (bateau)\|Frégate]]` | 添加“Frégate (bateau)” | 1.7.0 |
| 4.4 | Markdown 链接，URL 中含括号 | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | 添加“Suchet (navire)” | 1.7.0 |
| 4.5 | 行首编号 | `1. Lorient` | 添加“Lorient” | 1.7.0 |
| 4.6 | 行首项目符号 | `* Concarneau`（也可用 `-`、`•`、`#`） | 添加“Concarneau” | 1.7.0 |
| 4.7 | 找不到的行 | `Xyzzy inexistant` | 该行留在输入框中，最后的消息将其计为“未找到” | 1.7.0 |
| 4.8 | 列表中的目录页 | `b:Programmation Python` | 为该目录页打开选择窗口；其章节不会被保留 | 1.10.0 |

可粘贴到浏览器的完整列表：

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

预期结果：“已添加 7 个页面，0 个已在书中，0 个未找到。”

API，相同列表：`T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. 粘贴的图书文本

| 编号 | 情况 | 粘贴的文本 | API | 预期结果 | 版本 |
|---|---|---|---|---|---|
| 5.1 | 维基百科“图书:”语法 | 下方 5.1 代码块 | 下方 5.1 `curl` | 标题“Ports bretons”，副标题“Guide des ports”，章节“Finistère”和“Morbihan”，“Brest”在最前且无章节 | 1.12.0 |
| 5.2 | 维基教科书可打印版本 | 下方 5.2 代码块 | 下方 5.2 `curl` | 3 章共 3 个维基教科书页面，省略许可协议 | 1.12.0 |

5.1 代码块：

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

5.2 代码块：

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

只读取结构而不生成 PDF：将相同内容发送到 `POST /api/books/from-wikitext`。

## 6. 打开已保存的图书（JSON）

| 编号 | 情况 | 浏览器 | API | 预期结果 | 版本 |
|---|---|---|---|---|---|
| 6.1 | 通过地址的 JSON 图书 | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | 图书打开（“图书已导入。”），带有背景图片和文档 | 1.9.6 |
| 6.2 | JSON 格式的维基教科书图书 | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 8 章共 27 页 | 1.9.6 |
| 6.3 | 本地 JSON 文件 | “打开”按钮，选择用“保存”导出的文件 | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @book.json` | 图书打开 / 生成 PDF | ≤ 1.9.7（浏览器），1.12.0（API） |
| 6.4 | 先 JSON，再其他来源 | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | JSON 图书打开，然后为新增的目录页弹出选择窗口 | 1.12.0 |
| 6.5 | 页面地址中的来源 | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | 见 3.3 和 1.2 | 每个来源都像手动输入一样被添加，包括提问 | 1.12.0 |
| 6.6 | 被拒绝的地址 | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | 显示错误消息，不导入任何内容；API 返回 422“doit commencer par https://” | 1.9.6 |

## 7. 文档和背景图片

| 编号 | 情况 | 浏览器 | API（JSON 图书字段） | 预期结果 | 版本 |
|---|---|---|---|---|---|
| 7.1 | 来自电脑的图片或 PDF | “组织”步骤，“选择文件 +” | 带 `data_base64` 的 `uploaded_documents[]` | 文档像条目一样放入书中，最大 15 MB | ≤ 1.9.7 |
| 7.2 | 通过地址的文档 | “组织”步骤，地址栏：`https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | 带 `"url": "https://upload.wikimedia.org/…"` 的 `uploaded_documents[]` | 只保存地址；服务器每次生成时下载图片 | 1.10.0 |
| 7.3 | 通过维基共享资源文件页面的文档 | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | 使用图片（2 000 像素缩略图）；PDF 则使用原文件 | 1.10.0（浏览器），1.12.0（API） |
| 7.4 | 通过文件页面的 PDF | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | `uploaded_documents[].url` 中使用相同地址 | 插入原始 PDF，页面调整为图书格式 | 1.10.0（浏览器），1.12.0（API） |
| 7.5 | 封面背景图片 | “编辑”步骤，“封面背景图片”，文件或地址（7.2 或 7.3） | `cover_image`：`{"title": "…", "url": "…"}` 或 `data_base64` | 封面背景，不变形 | 1.9.6 |
| 7.6 | 最后一页的图片 | “编辑”步骤，“最后一页背景图片” | `back_image` | 许可协议之后的独立一页 | 1.9.6 |
| 7.7 | 无法访问的地址 | 文档 `https://example.org/inexistant.png` | 相同地址 | 生成中止，并指出相关地址；通过 API 返回 502 | 1.10.0 |

## 8. 组织和排版

| 编号 | 情况 | 浏览器 | API（发送到 `POST /api/pdf` 的 JSON 图书） | 预期结果 | 版本 |
|---|---|---|---|---|---|
| 8.1 | 相关条目 | 条目的“相关条目”按钮 | `POST /api/explore` | 按页面顺序建议该条目的链接 | ≤ 1.9.7 |
| 8.2 | 章节和顺序 | “组织”步骤，“创建章节”，拖放 | `chapters`、`article_order`、`unassigned_first` | PDF 按显示的顺序排列 | ≤ 1.9.7 |
| 8.3 | 目录 | “编辑”步骤：无、开头、结尾 | `table_of_contents`、`toc_position`（`start`、`end`、`before:<键>`） | 目录位置正确，链接可点击 | 1.9.6 |
| 8.4 | 纸张格式、方向、页边距 | “编辑”步骤 | `page_format`、`orientation`、`margin_*_mm`、`custom_width_mm` | 所有页面均为所选格式 | ≤ 1.9.7 |
| 8.5 | 页码 | “页面编号” | `page_numbers` | 页面底部显示页码，封面除外 | ≤ 1.9.7 |
| 8.6 | PDF 标题的语言 | 顶部的语言选择 | `language` 参数（12 种语言） | 封面、目录、许可协议使用所选语言 | ≤ 1.9.7 |
| 8.7 | 手动分册 | “组织”步骤，“新分卷” | `volume_breaks`：`["before:<键>"]`，然后 `?volume=N` | 每册一个 PDF，页码从 1 重新开始 | 1.9.2（浏览器），1.12.0（API） |
| 8.8 | 超过 300 篇条目 | 图书 3.1 + 其他页面直至超过 300 | 先用 `POST /api/books/volumes` 获取分册方案，再 `POST /api/pdf?volume=1`、`?volume=2`… | 在章节之间自动分册，“（第 1/2 册）”…；不带 `volume` 时返回 413 并给出册数 | 1.9.0（浏览器），1.12.0（API） |

## 9. 不生成 PDF 的 API 调用

| 编号 | 情况 | 调用 | 预期结果 |
|---|---|---|---|
| 9.1 | 识别一项输入 | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`：`article`、`book`、`subpages` 或 `search` |
| 9.2 | 图书页面的结构 | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | 条目、副标题、章节 |
| 9.3 | 以 JSON 描述的图书的 PDF | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | 只有一页目录页的 PDF |
| 9.4 | 跟踪生成进度 | 将相同内容发送到 `POST /api/pdf/stream` | NDJSON 行 `progress`、`wait`，然后是 `done` 和 PDF |
| 9.5 | 建议的简介和作者 | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | 第一段和页面创建者 |
| 9.6 | 线上版本 | `T/api/version` | 版本、提交、条目上限 |

## 10. 被拒绝的输入

错误消息来自服务器，无论界面语言如何，都保持法语。

| 编号 | 输入 | 预期结果 |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | “L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…”；422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | “Seules les pages de contenu de fr.wikibooks.org…”；422 |
| 10.3 | 在来源输入框中输入 `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | 作为来源被拒绝（维基共享资源没有 `<语言>.<项目>.org` 地址）；可作为文档或背景图片接受（7.3） |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | “La page … est introuvable”；404 |
| 10.5 | 空输入框 | “Saisissez …”；422 |
| 10.6 | 未选择任何条目的图书，然后点击“生成 PDF” | 消息“生成 PDF 前请至少选择一篇文章。”；400 |
