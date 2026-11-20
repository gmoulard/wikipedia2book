# Yardım: «Kitabı oluşturun» alanına neler girilebilir?

<!-- {% raw %} -->

İlk adımdaki alan bir madde başlığından çok daha fazlasını kabul eder: bir adres, bütün bir kitap, bir sayfa listesi ya da bir kitap sayfasının metni. Eklemek istediğinizi yazın ya da yapıştırın, sonra «Ekle» düğmesine tıklayın. Eklenen sayfalar alanın altında görünür; onları bir sonraki adımda düzenlersiniz.

## Kısaca

| Eklemek istediğiniz… | Girmeniz gereken… | Örnek |
|---|---|---|
| başlığını bildiğiniz bir madde | başlığı | `Montagne Pelée` |
| belirli bir sayfa | adresi | `https://fr.wikipedia.org/wiki/Épaves_de_la_rade_de_Saint-Pierre` |
| başka bir dildeki madde | dil kodu, iki nokta, başlık | `nl:Rotterdam` |
| başka bir Wikimedia projesinin sayfası | proje öneki, ardından başlık | `voy:en:Lyon` |
| başka bir sitedeki bir görsel, PDF ya da web sayfası veya bir Wikimedia Commons dosyası | adresi: kitabın bir belgesi olur ve «İnternet URL'si» olarak gösterilir | `https://commons.wikimedia.org/wiki/File:Montagne_Pelée_1902.jpg` |
| bütün bir kitap | içindekiler sayfasının ya da kitap sayfasının adresi | `https://fr.wikibooks.org/wiki/Cosmologie` |
| aynı anda birkaç sayfa | her satıra bir sayfa | bkz. «Aynı anda birkaç sayfa» |
| bir «Kitap:» sayfasında hazırlanmış kitap | o sayfanın metni | bkz. «Bir kitap sayfasının metnini yapıştırma» |

## Madde arama

- Birkaç harf yazın: alanın altında öneriler görünür.
- Alanın yanındaki liste, aramanın hangi dildeki Vikipedi'de yapılacağını seçer. «Tümü» seçiliyken başlık listedeki tüm dillerde aranır ve her sonuç kendi dilini gösterir.
- Başlık bir maddeyle tam olarak eşleşirse doğrudan eklenir. Başka bir maddeye yönlendiren başlık hedef maddeyi ekler: `Napoléon Bonaparte`, «Napoléon Ier» maddesini ekler.
- Aksi halde arama sonuçları alanın altında görünür: istediğinize tıklayın.
- Eklediğiniz ilk maddenin girişi ve sayfayı oluşturan kişi, Yayın adımında kitabın girişi ve yazarı olarak önerilir. Bunları değiştirebilirsiniz.

## Başka bir dildeki ya da başka bir projedeki sayfalar

Tam adres her zaman çalışır, örneğin `https://fr.wikivoyage.org/wiki/Lyon`. Bir başlığın önüne dil öneki, proje öneki ya da ikisini birden ekleyin:

| Proje | Önek | Örnek |
|---|---|---|
| Başka dildeki Vikipedi | dil kodu | `nl:Rotterdam` |
| Vikikaynak | `s:` | `s:Les Misérables` |
| Vikikitap | `b:` | `b:Cosmologie` |
| Vikigezgin | `voy:` | `voy:en:Lyon` |
| Vikiversite | `v:` | `v:Python` |
| Vikisöz | `q:` | `q:Victor Hugo` |
| Vikisözlük | `wikt:` | `fr:wikt:chat` |
| Vikihaber | `n:` | `n:Accueil` |

Dil kodu yoksa alanın yanında seçilen dil kullanılır. Öneklerin sırası önemli değildir. Her sayfa kartında projesinin adını ve dilini korur.

## Bütün kitaplar

- **Vikipedi kitap sayfası**: adresini ya da adını girin, örneğin `Utilisateur:Alexbzh972/Livres/Martinique`. Tüm maddeleri sayfadaki sırayla, bölümleri, başlığı ve alt başlığıyla eklenir.
- **Vikikitap derlemesi**: derlemenin adresini girin, örneğin `https://fr.wikibooks.org/wiki/Wikilivres:Compilations/Programmation_C`. Sayfaları, bir Vikipedi kitap sayfasında olduğu gibi listedeki sırayla eklenir.
- **Vikikitap kitabı ya da Vikikaynak eseri**: içindekiler sayfasının adresini ya da başlığını girin, örneğin `https://fr.wikibooks.org/wiki/Cosmologie` ya da `s:Les Misérables`. Bir pencere ne istediğinizi sorar:
  - «Kitabın tamamı»: bölümlere ayrılmış tüm sayfaları;
  - «Kitabın tamamı ve içindekiler sayfası»: aynısı, içindekiler sayfası başta;
  - «Yalnızca bu sayfa»: yalnızca içindekiler sayfası;
  - «İptal»: hiçbir şey eklenmez.
- **Vikikitap yazdırılabilir sürümü**: kitabın «yazdırılabilir sürüm» sayfasının adresini girin, örneğin `https://fr.wikibooks.org/wiki/Programmation_C/Version_imprimable`. Bu sayfa elle yazılmışsa sayfaları her başlık için bir bölümle eklenir; içindekiler sayfasından üretiliyorsa kitabın seçim penceresi açılır.

## Aynı anda birkaç sayfa

Her satıra bir sayfa olacak biçimde bir liste yapıştırın (yazarken yeni satır için Shift+Enter kullanın). Her satır bir başlık, bir adres ya da önekli bir sayfa olabilir; ayrıca viki bağlantısı, Markdown bağlantısı ya da numaralı veya madde imli liste öğesi biçiminde de yazılabilir:

```
[[Brest]]
[[nl:Amsterdam]]
[Suchet](https://fr.wikipedia.org/wiki/Suchet_(navire))
1. Lorient
* Concarneau
[[voy:en:Lyon]]
fr:wikt:chat
```

Sonunda bir ileti kaç sayfanın eklendiğini, kaçının zaten kitapta olduğunu ve kaçının bulunamadığını bildirir. Bulunamayan satırlar düzeltebilmeniz için alanda kalır. Listedeki bir kitap içindekiler sayfası yukarıda anlatılan seçim penceresini açar.

## Bir kitap sayfasının metnini yapıştırma

Bir Vikipedi «Kitap:» sayfasının içeriğini yapıştırabilirsiniz: `== … ==` başlığı, `=== … ===` alt başlığı verir, her `;` satırı bir bölüm başlatır ve her `[[…]]` bağlantısı bir madde ekler.

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

`{{:…}}` eklemelerinden oluşan bir Vikikitap yazdırılabilir sürümünün metni de aynı şekilde kabul edilir: her `= … =` başlığı bir bölüm olur.

## Kaydedilmiş ya da paylaşılmış bir kitabı açma

- «Kaydet» düğmesi kitabınızı bir dosyaya indirir; «Aç» düğmesi onu daha sonra yeniden yükler. Sunucuda hiçbir şey saklanmaz: bu dosya tek yedeğinizdir.
- `https://wikipedia2book.toolforge.org/?json=https://…` biçimindeki bir bağlantı çevrimiçi kaydedilmiş bir kitabı açar (yalnızca `https://` adresleri).
- `https://wikipedia2book.toolforge.org/?source=…` biçimindeki bir bağlantı kaynaklarını siz yazmışsınız gibi ekler: bir sayfa seçimini paylaşmak için kullanışlıdır.

## Alanın reddettikleri

- içerik sayfası olmayan sayfalar (tartışma, yardım ya da topluluk sayfaları);
- var olmayan sayfalar.

Hata iletisi sorunun ne olduğunu açıklar. Sunucudan gelir ve arayüzün dili ne olursa olsun Fransızca kalır.

## Sonra?

- **Düzenleme**: sayfaları sıralayın, bölümler oluşturun, kendi görsellerinizi ya da PDF'lerinizi ekleyin, kitabı ciltlere bölün. 300 maddeyi aşan kitap otomatik olarak ciltlere bölünür.
- **Yayın**: başlık, kapak, arka plan görselleri, içindekiler, sayfa biçimi ve kenar boşlukları.
- **PDF oluştur**: her madde Vikipedi'nin yazdırdığı haliyle alınır ve hepsi baskıya hazır tek bir kitap oluşturur.

<!-- {% endraw %} -->
