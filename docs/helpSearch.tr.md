# «Kitabı oluşturun» alanı yardımı: Wikipedia2Book'un kabul ettiği her şey

Bu sayfa Wikipedia2Book'un kabul ettiği her şeyi listeler; her durum için **tarayıcıda** denenecek bir örnek ve aynı durumun **API üzerinden** karşılığı verilir. İki amaca hizmet eder: olanakları göstermek ve bir sürümü yayımlamadan önce elle doğrulama yapmak. [Fransızca başvuru sayfasının](helpSearch.fr.md) çevirisidir.

Başvuru davranışı [işlevsel belirtimlerde](FunctionalSpec.en.md) (kaynaklar için bölüm 3.1) ve [teknik belirtimlerde](TechnicalSpec.en.md) (API için bölüm 13.3) anlatılır.

## Nasıl kullanılır

- **Tarayıcı**: https://wikipedia2book.toolforge.org/ adresini açın, örneği «Kitabı oluşturun» adımının alanına yapıştırın ve «Ekle» düğmesine tıklayın. `https://wikipedia2book.toolforge.org/?` ile başlayan bir adres doğrudan açılır.
- **API**: adresi tarayıcıda açın (PDF indirilir) ya da `curl -OJ` komutuna verin. `POST` çağrıları `curl` komutları olarak verilmiştir.
- **Sürüm**: durumun çalıştığı ilk uygulama sürümü. Yayındaki sürümü https://wikipedia2book.toolforge.org/api/version gösterir.
- «Sürüm» sütunu tarayıcı içindir. API tarafında `GET /api/pdf/from-source` (bölüm 1-4) ve sayfanın `?source=` parametresi 1.12.0'dan beri vardır (bu numarayı almadan önce, 16 Kasım 2026 akşamından beri üretimde): daha eski bir sürümde, her girdiyi `POST /api/sources/resolve` (9.1) ile tanıdıktan sonra kitabı JSON olarak `POST /api/pdf` adresine (9.3) gönderin.
- Örnekler 17 Kasım 2026'da kaynak tanıma koduyla gerçek vikilere karşı doğrulandı; o zamandan beri adı değişen ya da silinen bir sayfa sonucu değiştirebilir.

Kısaltmalar: **T** = https://wikipedia2book.toolforge.org. API adreslerinde `language`, PDF'te üretilen başlıkların (kapak, içindekiler, lisans) dilidir; `wiki` ise öneksiz başlıkların dilidir.

## 1. Tek bir sayfa

| No | Durum | Tarayıcı: girilecek | API | Beklenen sonuç | Sürüm |
|---|---|---|---|---|---|
| 1.1 | Bir Vikipedi maddesinin URL'si | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` | `T/api/pdf/from-source?source=https://fr.wikipedia.org/wiki/%C3%89paves_de_la_rade_de_Saint-Pierre` | Madde eklenir; ilk maddede giriş ve yazar önerilir | ≤ 1.9.7 |
| 1.2 | Tam başlık | `Montagne Pelée` (alanın yanında FR dili) | `T/api/pdf/from-source?source=Montagne%20Pel%C3%A9e&wiki=fr` | «Montagne Pelée» maddesi eklenir | ≤ 1.9.7 |
| 1.3 | Yönlendirilen başlık | `Napoléon Bonaparte` | `T/api/pdf/from-source?source=Napol%C3%A9on%20Bonaparte&wiki=fr` | Yönlendirme izlenir: «Napoléon Ier» eklenir | ≤ 1.9.7 |
| 1.4 | Tam sayfası olmayan başlık | `volcan martinique` | `POST` ile `T/api/sources/resolve` (bkz. 9.1): `kind` = `search` | Arama sonuçları alanın altında görünür ve tek tıkla eklenir; oluşturma API'si ilgili metinle 404 döner | ≤ 1.9.7 |
| 1.5 | Yazarken arama | Onaylamadan `Saint-Pie` yazın | `T/api/search?query=Saint-Pie&language=fr` | Alanın altında öneriler | ≤ 1.9.7 |
| 1.6 | Başka bir dilde başlık | `nl:Rotterdam` | `T/api/pdf/from-source?source=nl:Rotterdam` | Felemenkçe madde eklenir, «NL» olarak işaretlenir | 1.7.0 |
| 1.7 | Tüm diller | Alanın yanında «Tümü» seçiliyken `Paris` | `T/api/search?query=Paris&language=all&limit=3` | Listedeki her dilde sonuçlar, her biri kendi diliyle işaretli; seçilen madde kendi dilini korur | 1.12.4 |

## 2. Diğer Wikimedia projeleri

| No | Durum | Tarayıcı: girilecek | API | Beklenen sonuç | Sürüm |
|---|---|---|---|---|---|
| 2.1 | Vikigezgin sayfası | `https://fr.wikivoyage.org/wiki/Lyon` | `T/api/pdf/from-source?source=https://fr.wikivoyage.org/wiki/Lyon` | Sayfa eklenir, kart «Vikigezgin» olarak işaretlenir | 1.8.0 |
| 2.2 | Proje ve dil öneki | `[[voy:en:Lyon]]` | `T/api/pdf/from-source?source=voy:en:Lyon` | İngilizce Vikigezgin sayfası eklenir | 1.8.0 |
| 2.3 | Vikiversite | `https://fr.wikiversity.org/wiki/Python` | `T/api/pdf/from-source?source=v:Python&wiki=fr` | Sayfa eklenir, «Vikiversite» olarak işaretlenir | 1.8.0 |
| 2.4 | Vikisöz | `https://fr.wikiquote.org/wiki/Victor_Hugo` | `T/api/pdf/from-source?source=q:Victor%20Hugo&wiki=fr` | Sayfa eklenir, «Vikisöz» olarak işaretlenir | 1.8.0 |
| 2.5 | Vikisözlük, önekler ters sırada | `fr:wikt:chat` | `T/api/pdf/from-source?source=fr:wikt:chat` | Sayfa eklenir, «Vikisözlük» olarak işaretlenir | 1.8.0 |
| 2.6 | Vikihaber | `https://fr.wikinews.org/wiki/Accueil` | `T/api/pdf/from-source?source=https://fr.wikinews.org/wiki/Accueil` | Sayfa eklenir, «Vikihaber» olarak işaretlenir | 1.8.0 |
| 2.7 | Vikikaynak metni (tek sayfa) | `https://zh.wikisource.org/wiki/論語/學而第一` | `T/api/pdf/from-source?source=https://zh.wikisource.org/wiki/%E8%AB%96%E8%AA%9E/%E5%AD%B8%E8%80%8C%E7%AC%AC%E4%B8%80` | Sayfa eklenir; Çince başlıklar PDF'te okunabilir | 1.7.8 |
| 2.8 | Vikikaynak yazar sayfası | `https://fr.wikisource.org/wiki/Auteur:François_Rabelais` | `T/api/pdf/from-source?source=https://fr.wikisource.org/wiki/Auteur:Fran%C3%A7ois_Rabelais` | Sayfa olduğu gibi eklenir (biyografi ve eser listesi) | 1.8.1 |

## 3. Kitaplar

| No | Durum | Tarayıcı: girilecek | API | Beklenen sonuç | Sürüm |
|---|---|---|---|---|---|
| 3.1 | URL ile Vikipedi kitap sayfası | `https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/books/generate-from-wikipedia-book?url=https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique` | Sayfadaki sırayla 113 madde, `;` bölümleri, `===` alt başlığı; başlık «Martinique» | 1.3.0 |
| 3.2 | Adıyla kitap sayfası | `Utilisateur:Alexbzh972/Livres/Martinique` | `T/api/pdf/from-source?source=Utilisateur:Alexbzh972/Livres/Martinique` | 3.1 ile aynı sonuç | 1.3.0 |
| 3.3 | Bir Vikikitap kitabının içindekiler sayfası | `https://fr.wikibooks.org/wiki/Cosmologie` | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr` | «Kitabın tamamı / Kitabın tamamı ve içindekiler sayfası / Yalnızca bu sayfa / İptal» penceresi; «Kitabın tamamı» bölümlere ayrılmış 27 sayfa verir | 1.10.0 |
| 3.4 | İçindekiler sayfasıyla birlikte kitabın tamamı | 3.3 gibi, «Kitabın tamamı ve içindekiler sayfası» seçin | `T/api/pdf/from-source?source=b:Cosmologie&wiki=fr&summary=1` | Önce içindekiler sayfası, ilk bölümden önce | 1.10.0 |
| 3.5 | Yalnızca içindekiler sayfası | 3.3 gibi, «Yalnızca bu sayfa» seçin | Yalnızca içindekiler sayfasıyla `POST /api/pdf` (bkz. 9.3) | Tek başına içindekiler sayfası | 1.10.0 |
| 3.6 | Vikikaynak eseri | `s:Les Misérables` (FR dili) | `T/api/pdf/from-source?source=s:Les%20Mis%C3%A9rables&wiki=fr` | Seçim penceresi; «Kitabın tamamı» 5 kısımda 365 bölüm verir, «Texte entier» olmadan | 1.11.0 |
| 3.7 | Elle yazılmış yazdırılabilir sürüm (adres) | `https://fr.wikibooks.org/wiki/Hélices_de_navires_à_déplacement/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/H%C3%A9lices_de_navires_%C3%A0_d%C3%A9placement/Version_imprimable` | 13 sayfa, her `= … =` başlığı için bir bölüm, kapak atlanır, başlık «Hélices de navires à déplacement» | 1.12.0 |
| 3.8 | `{{imprimable}}` ile yazdırılabilir sürüm (adres) | `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | `T/api/pdf/from-source?source=https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable` | «Programmation C» içindekiler sayfası için seçim penceresi (21 sayfa) | 1.12.0 |

## 4. Sayfa listeleri (birden çok satır)

Tüm satırları alana bir kerede yapıştırın (ya da Shift+Enter ile ayırın). API tarafında `source=` parametresini yineleyin (en çok 50).

| No | Durum | Girilecek satır | Beklenen sonuç | Sürüm |
|---|---|---|---|---|
| 4.1 | Viki bağlantısı | `[[Brest]]` | «Brest» eklenir | 1.7.0 |
| 4.2 | Dilli viki bağlantısı | `[[nl:Amsterdam]]` | Felemenkçe madde eklenir | 1.7.0 |
| 4.3 | Metinli viki bağlantısı | `[[Frégate (bateau)\|Frégate]]` | «Frégate (bateau)» eklenir | 1.7.0 |
| 4.4 | Markdown bağlantısı, URL'de parantez | `[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))` | «Suchet (navire)» eklenir | 1.7.0 |
| 4.5 | Satır başında numara | `1. Lorient` | «Lorient» eklenir | 1.7.0 |
| 4.6 | Satır başında madde imi | `* Concarneau` (ayrıca `-`, `•`, `#`) | «Concarneau» eklenir | 1.7.0 |
| 4.7 | Bulunamayan satır | `Xyzzy inexistant` | Satır alanda kalır, son ileti onu «bulunamadı» olarak sayar | 1.7.0 |
| 4.8 | Liste içinde içindekiler sayfası | `b:Programmation Python` | Bu içindekiler sayfası için seçim penceresi açılır; bölümleri alınmaz | 1.10.0 |

Tarayıcıya yapıştırılacak tam liste:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Beklenen sonuç: «7 sayfa eklendi, 0 zaten kitapta, 0 bulunamadı.»

API, aynı liste: `T/api/pdf/from-source?source=[[Brest]]&source=[[nl:Amsterdam]]&source=1.%20Lorient&source=*%20Concarneau&source=[[voy:en:Lyon]]&source=fr:wikt:chat&wiki=fr`

## 5. Yapıştırılan kitap metni

| No | Durum | Yapıştırılacak metin | API | Beklenen sonuç | Sürüm |
|---|---|---|---|---|---|
| 5.1 | Vikipedi «Kitap:» sözdizimi | Aşağıdaki 5.1 bloğu | Aşağıdaki 5.1 `curl` komutu | Başlık «Ports bretons», alt başlık «Guide des ports», «Finistère» ve «Morbihan» bölümleri, başta bölümsüz «Brest» | 1.12.0 |
| 5.2 | Vikikitap yazdırılabilir sürümü | Aşağıdaki 5.2 bloğu | Aşağıdaki 5.2 `curl` komutu | 3 bölümde 3 Vikikitap sayfası, lisans atlanır | 1.12.0 |

5.1 bloğu:

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

5.2 bloğu:

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

PDF olmadan yalnızca yapıyı okumak için: aynı içeriği `POST /api/books/from-wikitext` adresine gönderin.

## 6. Kaydedilmiş bir kitabı açma (JSON)

| No | Durum | Tarayıcı | API | Beklenen sonuç | Sürüm |
|---|---|---|---|---|---|
| 6.1 | Adresle JSON kitap | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Wrecks-of-Saint-Pierre-harbor.json&language=en` | Kitap arka plan görselleri ve belgesiyle açılır («Kitap içe aktarıldı.») | 1.9.6 |
| 6.2 | JSON olarak Vikikitap kitabı | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | `T/api/pdf/from-json?url=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json` | 8 bölümde 27 sayfa | 1.9.6 |
| 6.3 | Yerel JSON dosyası | «Aç» düğmesi, «Kaydet» ile dışa aktarılmış bir dosya seçin | `curl -OJ -X POST 'T/api/pdf/from-json' -H 'Content-Type: application/json' --data @kitap.json` | Kitap açılır / PDF oluşturulur | ≤ 1.9.7 (tarayıcı), 1.12.0 (API) |
| 6.4 | JSON, ardından başka kaynaklar | `T/?json=https://gmoulard.github.io/wikipedia2book/static/Cosmologie.json&source=b:Programmation%20Python` | — | JSON kitap açılır, ardından eklenen içindekiler sayfası için seçim penceresi | 1.12.0 |
| 6.5 | Sayfa adresinde kaynaklar | `T/?source=https://fr.wikibooks.org/wiki/Cosmologie&source=Montagne%20Pel%C3%A9e&wiki=fr` | Bkz. 3.3 ve 1.2 | Her kaynak, soru dahil, yazılmış gibi eklenir | 1.12.0 |
| 6.6 | Reddedilen adres | `T/?json=http://example.com/livre.json` | `T/api/pdf/from-json?url=http://example.com/livre.json` | Hata iletisi, hiçbir şey içe aktarılmaz; API 422 «doit commencer par https://» döner | 1.9.6 |

## 7. Belgeler ve arka plan görselleri

| No | Durum | Tarayıcı | API (JSON kitap alanı) | Beklenen sonuç | Sürüm |
|---|---|---|---|---|---|
| 7.1 | Bilgisayardan görsel ya da PDF | Düzenleme adımı, «Dosya seç +» | `data_base64` ile `uploaded_documents[]` | Belge kitaba bir madde gibi yerleştirilir, en çok 15 MB | ≤ 1.9.7 |
| 7.2 | Adresle belge | Düzenleme adımı, adres alanı: `https://upload.wikimedia.org/wikipedia/commons/1/16/La_Pel%C3%A9e_vue_du_Carbet.jpg` | `"url": "https://upload.wikimedia.org/…"` ile `uploaded_documents[]` | Yalnızca adres saklanır; sunucu görseli her oluşturmada indirir | 1.10.0 |
| 7.3 | Commons dosya sayfasıyla belge | `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | `"url": "https://commons.wikimedia.org/wiki/File:La_Pel%C3%A9e_vue_du_Carbet.jpg"` | Görsel (2 000 px önizleme) kullanılır; PDF için özgün dosya | 1.10.0 (tarayıcı), 1.12.0 (API) |
| 7.4 | Dosya sayfasıyla PDF | `https://commons.wikimedia.org/wiki/File:Interpersonal_communication_and_coordination_in_Wikipedia_Working_Paper_30_June_2020.pdf` | `uploaded_documents[].url` içinde aynı adres | Özgün PDF eklenir, sayfalar kitap biçimine uydurulur | 1.10.0 (tarayıcı), 1.12.0 (API) |
| 7.5 | Kapak arka plan görseli | Yayın adımı, «Kapak arka plan görseli», dosya ya da adres (7.2 veya 7.3) | `cover_image`: `{"title": "…", "url": "…"}` ya da `data_base64` | Kapak arka planı, bozulma olmadan | 1.9.6 |
| 7.6 | Son sayfa görseli | Yayın adımı, «Son sayfa arka plan görseli» | `back_image` | Lisanstan sonra ayrı bir sayfa | 1.9.6 |
| 7.7 | Erişilemeyen adres | Belge `https://example.org/inexistant.png` | Aynı adres | Oluşturma durur, ilgili adres belirtilir; API üzerinden 502 | 1.10.0 |

## 8. Düzenleme ve sayfa düzeni

| No | Durum | Tarayıcı | API (`POST /api/pdf` adresine JSON kitap) | Beklenen sonuç | Sürüm |
|---|---|---|---|---|---|
| 8.1 | İlgili maddeler | Bir maddenin «İlgili maddeler» düğmesi | `POST /api/explore` | Maddenin bağlantıları sayfadaki sırayla önerilir | ≤ 1.9.7 |
| 8.2 | Bölümler ve sıra | Düzenleme adımı, «Bölüm oluştur», sürükle-bırak | `chapters`, `article_order`, `unassigned_first` | PDF görüntülenen sırayı izler | ≤ 1.9.7 |
| 8.3 | İçindekiler | Yayın adımı: yok, başta, sonda | `table_of_contents`, `toc_position` (`start`, `end`, `before:<anahtar>`) | İçindekiler doğru yerde, tıklanabilir bağlantılar | 1.9.6 |
| 8.4 | Biçim, yön, kenar boşlukları | Yayın adımı | `page_format`, `orientation`, `margin_*_mm`, `custom_width_mm` | Tüm sayfalar seçilen biçimde | ≤ 1.9.7 |
| 8.5 | Sayfa numaraları | «Sayfaları numaralandır» | `page_numbers` | Kapak dışında sayfa altında numaralar | ≤ 1.9.7 |
| 8.6 | PDF başlıklarının dili | Üstteki dil seçici | `language` parametresi (12 dil) | Kapak, içindekiler, lisans seçilen dilde | ≤ 1.9.7 |
| 8.7 | Elle ciltlere bölme | Düzenleme adımı, «Yeni cilt» | `volume_breaks`: `["before:<anahtar>"]`, ardından `?volume=N` | Her cilt için bir PDF, numaralandırma 1'den yeniden başlar | 1.9.2 (tarayıcı), 1.12.0 (API) |
| 8.8 | 300'den fazla madde | 3.1 kitabı + 300'ü aşana dek başka sayfalar | Plan için `POST /api/books/volumes`, ardından `POST /api/pdf?volume=1`, `?volume=2`… | Bölümler arasında otomatik bölme, «Cilt 1/2»…; `volume` olmadan cilt sayısıyla 413 reddi | 1.9.0 (tarayıcı), 1.12.0 (API) |

## 9. PDF'siz API çağrıları

| No | Durum | Çağrı | Beklenen sonuç |
|---|---|---|---|
| 9.1 | Bir girdiyi tanıma | `curl -X POST 'T/api/sources/resolve' -H 'Content-Type: application/json' --data '{"input":"volcan martinique","language":"fr"}'` | `kind`: `article`, `book`, `subpages` ya da `search` |
| 9.2 | Bir kitap sayfasının yapısı | `curl -X POST 'T/api/books/structure' -H 'Content-Type: application/json' --data '{"url":"https://fr.wikipedia.org/wiki/Utilisateur:Alexbzh972/Livres/Martinique"}'` | Maddeler, alt başlık, bölümler |
| 9.3 | JSON ile tanımlanan bir kitabın PDF'i | `curl -OJ -X POST 'T/api/pdf?language=fr' -H 'Content-Type: application/json' --data '{"name":"Test","main_articles":[{"title":"Cosmologie","language":"fr","site":"wikibooks","url":"https://fr.wikibooks.org/wiki/Cosmologie","selected":true}]}'` | Tek bir içindekiler sayfasının PDF'i |
| 9.4 | Oluşturmayı izleme | Aynı içerik `POST /api/pdf/stream` adresine | NDJSON satırları `progress`, `wait`, ardından `done` ve PDF |
| 9.5 | Önerilen giriş ve yazar | `T/api/articles/intro?title=Montagne%20Pel%C3%A9e&language=fr` | İlk paragraf ve sayfayı oluşturan kişi |
| 9.6 | Yayındaki sürüm | `T/api/version` | Sürüm, commit, madde sınırı |

## 10. Reddedilen girdiler

Hata iletileri sunucudan gelir ve arayüzün dili ne olursa olsun Fransızca kalır.

| No | Girdi | Beklenen sonuç |
|---|---|---|
| 10.1 | `https://example.com/wiki/Chat` | «L'URL doit pointer vers une page HTTPS d'un projet Wikimédia…»; 422 |
| 10.2 | `https://fr.wikibooks.org/wiki/Wikilivres:Le_Bistro` | «Seules les pages de contenu de fr.wikibooks.org…»; 422 |
| 10.3 | Kaynaklar alanında `https://commons.wikimedia.org/wiki/File:La_Pelée_vue_du_Carbet.jpg` | Kaynak olarak reddedilir (Commons'un `<dil>.<proje>.org` adresi yoktur); belge ya da arka plan görseli olarak kabul edilir (7.3) |
| 10.4 | `https://fr.wikipedia.org/wiki/Page_qui_n_existe_pas` | «La page … est introuvable»; 404 |
| 10.5 | Boş alan | «Saisissez …»; 422 |
| 10.6 | Seçili maddesi olmayan kitap, ardından «PDF oluştur» | «PDF oluşturmadan önce en az bir madde seçin.» iletisi; 400 |
