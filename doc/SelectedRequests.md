Ce fichier document les requêtes utilisées dans ce script. 

# Obtenir une clef d'authentification

`https://transkribus.eu/TrpServer/rest/auth/login`
- Body :
	- `user` = `{username}`
	- `pw` = `{password}`

``` 
curl --request POST \
  --url https://transkribus.eu/TrpServer/rest/auth/login \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data 'user={username}&pw={password}'
```

Cette requête retourne un fichier XML dans lequel doit être récupéré le code de session selon le chemin qui suit. Ce code devra être utilisé dans toutes les requêtes suivantes pour activer l'authentification, en utilisant la clef "JSESSIONID". 
- jsessionid = `/trpUserLogin/sessionId/text()`


# Accéder à l'ID d'une collection dont on connaît le nom
`https://transkribus.eu/TrpServer/rest/collections/list.xml`
- Params : 
	- `JSESSIONID` = `{jsessionid}`

``` 
curl --request GET \
  --url 'https://transkribus.eu/TrpServer/rest/collections/list.xml?JSESSIONID={jsessionid}'
```

Cette requête retourne un fichier XML dans lequel doit être récupéré l'ID de la collection que l'on souhaite utiliser, selon le chemin suivant : 
- **si** `/trpCollections/trpCollection/colName/text()` == "timeUs"
- **alors** collid = `/trpCollections/trpCollection/colId/text()`

**ID de la collection TimeUs =** `8097`.


# Accéder aux ID des documents d'une collection
`https://transkribus.eu/TrpServer/rest/collections/8097/list`
- Params :
	- `JSESSIONID` = `{jsessionid}`

```
curl --request GET \
  --url 'https://transkribus.eu/TrpServer/rest/collections/8097/list?JSESSIONID={jsessionid}'
```

Cette requête renvoie une liste de dictionnaires contenant les métadonnées de chaque documents (ou sous-ensemble) de la collection. Elle permet de récupérer les ID de chaque document ou sous-ensemble grâce à une boucle.
- docid = `liste[i].docId`
- docname = `liste[i].title`
- docpages = `liste[i].nrOfPages`


# Récupérer la transcription de chaque page d'un sous-ensemble
`https://transkribus.eu/TrpServer/rest/collections/8097/41459/fulldoc`
- Params :
	- `JSESSIONID` = `{jsessionid}`

```
curl --request GET \
  --url 'https://transkribus.eu/TrpServer/rest/collections/8097/41459/fulldoc?JSESSIONID={jsessionid}'
```

Cette requête renvoie un fichier JSON contenant des métadonnées sur chaque page d'un document ou sous-ensemble dans une collection, à partir de son ID. Il permet d'accéder, notamment, à un fichier XML au format PAGE pour chaque zone de texte transcrite. 
La structure du fichier et les informations utiles pour le moment sont les suivantes : 
- `dico.pageList.pages[i].pageId` : identifiant de la page
- `dico.pageList.pages[i].pageNr` : numéro de la page
- `dico.pageList.pages[i].url` : url d'une requête GET pour accéder à l'image de la page au format JPEG
- `dico.pageList.pages[i].created` : date de création du fichier
- `dico.pageList.pages[i].tsList.transcripts` : liste des états de transcription pour une zone donnée
- `dico.pageList.pages[i].tsList.transcripts[j].tsId` : identifiant de la transcription
- `dico.pageList.pages[i].tsList.transcripts[j].pageNr` : numéro de la page
- `dico.pageList.pages[i].tsList.transcripts[j].url` : url d'une requête GET pour accéder au fichier XML 
- `dico.pageList.pages[i].tsList.transcripts[j].status` : statut du document (NEW, IN PROGRESS, DONE)
- `dico.pageList.pages[i].tsList.transcripts[j].userName` : identifiant (mail) de l'utilisateur auteur de l'état de la transcription
- `dico.pageList.pages[i].tsList.transcripts[j].timestamp` : token numérique faisant office de timestamp

Le fichier contient également des métadonnées utiles pour établir des statistiques ou renseigner les métadonnées des fichiers : 
- `dico.md.nrOfDone` : nombre de pages de statut "Done"
- `dico.md.nrOfInProgress` : nombre de pages de statut "In Progress"
- `dico.md.nrOfNew` : nombre de pages de statut "New"
- `dico.md.nrOfLines` : nombre de lignes dans le document ou le sous-ensemble
- `dico.md.nrOfTranscribedRegions` : nombre de régions transcrites
- `dico.md.nrOfRegions` : nombre de régions identifiées
- `dico.md.title` : titre du document
- `dico.md.nrOfPages` : nombre de pages dans le document ou sous-ensemble

