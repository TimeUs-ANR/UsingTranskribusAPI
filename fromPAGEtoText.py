import os, datetime
from bs4 import BeautifulSoup
from config import textcollectionnames as collections

# ========================== #

def createFolder(directory):
	"""Create a new folder.

	:param directory: path to new directory
	:type directory: string
	"""
	if not os.path.exists(directory):
		os.makedirs(directory)


def initiateLog():
	"""Initiate a log file in __logs__ directory, name after a timestamp.
	"""
	collist = ' '.join(["'%s'" %collection for collection in collections])
	filepath = os.path.join(pathtologs, "log-%s.txt") % (TIMESTAMP)
	intro = """
	TRANSFORMING XML FILES (PAGE FORMAT) TO TEXT FILES

	Script ran at : %s
	For collections %s.

	---------------------
""" % (now, collist)
	with open(filepath, "w") as f:
		f.write(intro)


def createlog(counter, pagecounter, document):
	"""Create simple reports in log file.

	:param counter: number of xml files in document/subcollection directory.
	:param pagecounter: number of xml-page files in document/subcollection directory.
	:param document: name of document/subcollection directory.
	:type counter: integer
	:type pagecounter: integer
	:type document: string
	"""
	if counter == 0:
		log = "No .xml file in '%s' directory.\n\n" % (document)
	else:
		log = "Found %s .xml file(s) in '%s' directory.\n" % (counter, document)
		if pagecounter == 0:
			log = log + "\tNo .xml file matched PAGE format (root must be '<PcGts>'.\n\n"
		else:
			log = log + "\tFound %s .xml file(s) matching PAGE format.\n\n" % (pagecounter)
	filepath = os.path.join(pathtologs, "log-%s.txt") % (TIMESTAMP)
	with open(filepath, "a") as f:
		f.write(log)


# ========================== #

now = datetime.datetime.now()
TIMESTAMP = "%s-%s-%s-%s-%s" % (now.year, now.month, now.day, now.hour, now.minute)
currentdirectory = os.path.dirname(os.path.abspath(__file__))
pathtologs = os.path.join(currentdirectory, "__logs__")
initiateLog()

for collection in collections:
	path = os.path.join(currentdirectory, "data", collection)
	pathtotextexport = os.path.join(path, "__TextExports__") 
	createFolder(pathtotextexport)

	# PREPARING FILES
	try:
		collectioncontent = os.listdir(path)
		if "__TextExports__" in collectioncontent:
			collectioncontent.remove("__TextExports__")
		if "__AllInOne__" in collectioncontent:
			collectioncontent.remove("__AllInOne__")

		if len(collectioncontent) > 0:
			for document in collectioncontent:
				pathtodoc = os.path.join(path, document)
				try: 
					foldercontent = os.listdir(pathtodoc)
					sortedcontent = []
					if len(foldercontent) > 0:
						# ORDERING XML FILES
						for filename in [f for f in foldercontent if f.endswith(".xml")]:
							filename, ext = os.path.splitext(filename)
							try:
								sortedcontent.append(int(filename))
							except:
								sortedcontent.append(filename)
						sortedcontent.sort()
						if len(sortedcontent) > 0:
							textfile = os.path.join(pathtotextexport, "%s.txt") % document
							with open(textfile, "w") as f:
								f.write("")

						foldercontent = [str(filename) + ".xml" for filename in sortedcontent]
						counter = len(foldercontent)

						# GETTING TEXT FROM XML FILES
						pagecounter = 0
						for file in foldercontent:
							pagenr = file.replace(".xml", "")

							filepath = os.path.join(pathtodoc, file)
							with open(filepath, "r") as f:
								content = f.read()
							soup = BeautifulSoup(content, "xml")
							if soup.PcGts:
								pagecounter += 1
								textregions = soup.find_all("TextRegion")
								for textregion in textregions:
									regionid = textregion['id']
									textequivs = textregion("TextEquiv", recursive=False)
									for textequiv in textequivs:
										text = textequiv.Unicode.get_text()
										# CREATING TEXT FILES
										# With Zone and Region separators 
										with open(textfile, "a") as f:
											f.write("%s\n\n[.../R fin de la zone %s]\n\n" %(text, regionid))
								with open(textfile, "a") as f:
									f.write("\n[.../... fin de la page %s]\n\n" % (pagenr))
						createlog(counter, pagecounter, document)

				except Exception as e:
					print(e)
	except Exception as e:
		print(e)

