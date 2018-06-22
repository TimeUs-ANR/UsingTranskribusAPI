

# demander de choisir le dossier de data/ à traiter
# vérifier que le dossier existe
# demander de choisir le sous-dossier à traiter
# 		éventuellement choisir une liste de nom de dossier à traiter à la suite
# vérifier que le dossier existe
# vérifier que le dossier contient des fichiers .xml

# charger le fichiers dans l'ordre croissant
# récupérer le texte dans "/PcGts/Page/TextRegion/TextEquiv/Unicode/text()" (plusieurs TextRegion par fichier)
# l'écrire dans un nouveau fichier .txt

# =============================================

import os

collection = input("Dans quelle collection ? > ")
document = input("Dans quelle sous-dossier ? > ")

location = os.getcwd() #get current working directory
counter = 0 
files = []

path = location + "/data/%s/%s" % (collection, document)
try:
	foldercontent = os.listdir(path)
	if len(foldercontent) > 0:
		for file in foldercontent:
			if file.endswith(".xml"):
				counter += 1
				filepath = path + "/" + file
				with open(filepath, "r") as f:
					content = f.read()
					print(content)

		if counter == 0:
			print("No .xml file in the directory")
		else:
			print("Found %s .xml file(s) in the directory" % (counter))



	else:
		print("No file in the directory")

except Exception as e:
        print(e)





