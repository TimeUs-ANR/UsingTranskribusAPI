

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


import os, datetime
from bs4 import BeautifulSoup

# ========================== #

now = datetime.datetime.now()
timestamp = "%s-%s-%s-%s-%s" % (now.year, now.month, now.day, now.hour, now.minute)

collection = input("Give collection name : ")

currentdirectory = os.path.dirname(os.path.abspath(__file__))
path = currentdirectory + "/data/%s" % (collection)
pathtologs = currentdirectory + "/__logs__"

# ========================== #

def initiateLog():
	"""Initiates a log file with a timestamp
	"""
	filepath = "%s/log-%s.txt" % (pathtologs, timestamp)
	intro = """
	TRANSFORMING XML FILES (PAGE FORMAT) TO TEXT FILES

	Script ran at : %s
	For collection '%s'.

	---------------------
""" % (now, collection)
	with open(filepath, "w") as f:
		f.write(intro)
	return


def createlog(counter, pagecounter, document):
	if counter == 0:
		log = "No .xml file in '%s' directory.\n\n" % (document)
	else:
		log = "Found %s .xml file(s) in '%s' directory.\n" % (counter, document)
		if pagecounter == 0:
			log = log + "\tNo .xml file matched PAGE format (root must be '<PcGts>'.\n\n"
		else:
			log = log + "\tFound %s .xml file(s) matching PAGE format.\n\n" % (pagecounter)

	filepath = "%s/log-%s.txt" % (pathtologs, timestamp)
	with open(filepath, "a") as f:
		f.write(log)
	return


# ========================== #

# PREPARING XML FILES

initiateLog()

try:
	collectioncontent = os.listdir(path)

	if len(collectioncontent) > 0:
		for document in collectioncontent:
			pathtodoc = path + "/%s" % (document)
			try: 
				foldercontent = os.listdir(pathtodoc)
				sortedcontent = []
				if len(foldercontent) > 0:
					for filename in foldercontent:
						if filename.endswith(".xml"):
							filename = filename.replace(".xml", "")
							try:
								sortedcontent.append(int(filename))
							except:
								sortedcontent.append(filename)
					sortedcontent.sort()

					counter = 0
					foldercontent = []
					for filename in sortedcontent:
						filename = str(filename) + ".xml"
						counter += 1
						foldercontent.append(filename)

# CREATIONG NEW TEXT FILES 
					pagecounter = 0
					for file in foldercontent:
						filepath = pathtodoc + "/%s" % (file)
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

					createlog(counter, pagecounter, document)

			except Exception as e:
				print(e)
except Exception as e:
	print(e)

