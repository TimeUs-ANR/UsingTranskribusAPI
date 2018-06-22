

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
from bs4 import BeautifulSoup


collection = input("Give collection name > ")
document = input("Give directory name > ")

location = os.getcwd() #get current working directory
counter = 0 
pagecounter = 0
sortedcontent = []

path = location + "/data/%s/%s" % (collection, document)
try:
	foldercontent = os.listdir(path)

	if len(foldercontent) > 0:
		for filename in foldercontent:
			if filename.endswith(".xml"):
				filename = filename.replace(".xml", "")
				try: 
					sortedcontent.append(int(filename))
				except:
					sortedcontent.append(filename)
		sortedcontent.sort()

		foldercontent = []
		for filename in sortedcontent:
			filename = str(filename) + ".xml"
			counter += 1
			foldercontent.append(filename)

		print(foldercontent)

		for file in foldercontent:
			filepath = path + "/" + file
			with open(filepath, "r") as f:
				content = f.read()
				soup = BeautifulSoup(content, "xml")
				if soup.PcGts:
					pagecounter += 1
					textregions = soup.find_all("TextRegion")
					for textregion in textregions:
						textequivs = textregion("TextEquiv", recursive=False)
						for textequiv in textequivs:
							text = textequiv.Unicode.get_text()
							print(text)
							print("\n")

		if counter == 0:
			print("No .xml file in the directory")
		else:
			print("Found %s .xml file(s) in the directory" % (counter))
			if pagecounter == 0:
				print("No .xml file matched PAGE format (root must be '<PcGts>'")
			else:
				print("Found %s .xml file(s) matching PAGE format" % (pagecounter))

	else:
		print("No file in the directory")

except Exception as e:
        print(e)





