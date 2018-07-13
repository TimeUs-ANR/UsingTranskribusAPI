Un script pour interroger l'API de Transkribus et générer des fichiers XML-TEI et leur métadonnées.  

- [Installation de l'environnement virtuel](https://github.com/alix-tz/UsingTranskribusAPI/wiki/Cr%C3%A9er-l'environnement-virtuel-pour-utiliser-le-script)  

- `requestingTranskribus.py` permet de récupérer l'ensemble des transcriptions disponibles dans une ou plusieurs collections correspondant à un ou plusieurs statuts. Ces informations sont indiquées dans `config.py`. Les transcriptions sont disponibles au [format PAGE](http://www.primaresearch.org/tools/PAGELibraries). *Attention, le script ne télécharge pas l'image utilisée comme facsimilé par un fichier XML-PAGE.* 
	- pour chaque collection, un dossier est créé pour contenir l'ensemble des dossiers de sous-collections.
	- pour chaque sous-collection, un dossier est créé contenant un fichier `metadata.json`, qui contient les métadonnées de la sous-collection.  
	- pour chaque page de la sous-collection aux statuts recherchés, un fichier `.xml` est créé, nommé d'après le numéro de page auquel il correspond.  
	- deux attributs sont ajoutés dans le fichier `.xml` créé, pour l'élément `Page` : **@id** dont la valeur correspond au numéro de page, et **@url** dont la valeur est l'url de récupération de l'image de la page. 

A partir de cet export de fichiers XML-PAGE :  
- `fromPAGEtoText.py` permet de transformer les fichiers XML-PAGE d'une collection en des fichiers de texte brut. Chaque sous-collection est traitée à part et donne lieu à la création d'un fichier dans le dossier `__TextExports__`. Les sauts de zones de texte et de pages sont signalés par des marqueurs dans les documents.  

- `toSingleXML.py` permet de rassembler les fichiers XML-PAGE qui composent une sous-collection en un seul fichier. Chaque sous-collection est traitée à part et donne lieu à la création d'un fichier dans le dossier `__AllInOne__`. *Attention, Un élément `<tu:PageGrp>` a été ajouté pour rassembler tous les éléments `<Page>` et leur contenu ; il n'est pas conforme au schéma PAGE original.*  

## Pour transformer les fichiers XML-PAGE obtenus en fichier XML-TEI conformes
- [page2tei_TimeUS](https://github.com/alix-tz/page2tei_TimeUS)
