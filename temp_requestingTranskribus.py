import requests, json, os, datetime
from bs4 import BeautifulSoup
from config import username, password, collectionnames, status

# ======================= #

def createFolder(directory):
	""" Create a new folder
	source : https://gist.github.com/keithweaver/562d3caa8650eefe7f84fa074e9ca949
	:param directory: string
	"""
	try: 
		if not os.path.exists(directory):
			os.makedirs(directory)
	except OSError:
		print("Creating new directory. %s" % (directory))
	return

# ------- LOGS -------
def initiateLog():
	""" Initiate a log file with a timestamp
	"""
	collections = ""
	for collection in collectionnames:
		collections += "'%s' " % (collection)

	filepath = "%s/log-%s.txt" % (pathtologs, timestamp)
	intro = """
	RETRIEVING PAGE-XML FILES AND METADATA FROM TRANSKRIBUS

	Script ran at: %s
	For collection(s): %s

	---------------------
	\n""" % (now, collections)
	with open(filepath, "w") as f:
		f.write(intro)
	return


def createSeparationInLog():
	""" Create a visual separation in the log file to distinguish collections
	"""
	filepath = "%s/log-%s.txt" % (pathtologs, timestamp)
	separation = "\n =================================================== \n\n"
	with open(filepath, "a") as f:
		f.write(separation)
	return


def createLogEntry(data, errorlog, pagesnew, pagesinprogress, pagesdone, pagesfinal):
	""" Create simple reports for each document in a collection
	:param data: dict
	:param pagesnew: list
	:param pagesinprogress: list
	:param pagesdone: list
	:param pagesfinal: list
	:param errorlog: string
	"""
	nrOfPages = data["md"]["nrOfPages"]
	title = data["md"]["title"]
	nrOfNew = data["md"]["nrOfNew"]
	nrOfInProgress = data["md"]["nrOfInProgress"]
	nrOfDone = data["md"]["nrOfDone"]
	nrOfFinal = data["md"]["nrOfFinal"]

	reportPages = "\nDocument '%s' contains %s pages.\n" % (title, nrOfPages)
	reportStatus = "New: %s\nIn Progress: %s\nDone: %s\nFinal:%s\n" % (nrOfNew, nrOfInProgress, nrOfDone, nrOfFinal)
	reportWhichPages = ""
	if len(pagesnew) != 0:
		pagesnew = str(pagesnew).strip('[]')
#		" ".join(map(str, pagesnew))
		reportWhichPages += "Following pages have status 'NEW': %s\n" % (pagesnew)
	if len(pagesinprogress) != 0:
		pagesinprogress = str(pagesinprogress).strip('[]')
#		" ".join(map(str, pagesinprogress))
		reportWhichPages += "Following pages have status 'IN PROGRESS': %s\n" % (pagesinprogress)
	if len(pagesdone) != 0:
		pagesdone = str(pagesdone).strip('[]')
#		" ".join(map(str, pagesdone))
		reportWhichPages += "Following pages have status 'DONE': %s\n" % (pagesdone)
	if len(pagesfinal) != 0:
		pagesfinal = str(pagesfinal).strip('[]')
#		" ".join(map(str, pagesfinal))
		reportWhichPages += "Following pages have status 'FINAL': %s\n" % (pagesfinal)

	report = reportPages + reportStatus + reportWhichPages + errorlog

	filepath = "%s/log-%s.txt" % (pathtologs, timestamp)
	with open(filepath, "a") as f:
		f.write(report)
	return

# ------- CREATE FILES ------

def createtranscript(url, pagenr, pathtodoc):
	"""Create a new xml file containing the transcript given by Transkribus for a page, in PAGE standard. 
	File is name after corresponding page number.
	:param url: string
	:param pagenr: integer
	:param pathtodoc: string
	:return: boolean
	"""
	response = requests.request("GET", url)
	if response.status_code == 503:
		error = True
	else:
		error = False
		xml = response.text
		filepath = "%s/%s.xml" % (pathtodoc, pagenr)
		soup = BeautifulSoup(xml, "xml")
		# Adding attributes to Page elements : @url and @id
		# Attributes are not conform to Page standard but necessary for later treatment for Time Us project
		if soup.PcGts:
			soup.Page["url"] = url
			soup.Page["id"] = pagenr
			with open(filepath, "w") as f:
				f.write(str(soup))
	return error


def gettranscripts(data, pathtodoc):
	""" Identify page transcripts matching targeted status
	:param data: dict
	:param pathtodoc: string
	:return: integer
	"""
	pagesnew = []
	pagesinprogress = []
	pagesdone = []
	pagesfinal = []
	errors = 0

	pagelist = data["pageList"]["pages"]
	# Reporting
	print("Creating xml files for %s" % (data["md"]["title"]))

	for page in pagelist:
		match = False
		latesttranscript = page["tsList"]["transcripts"][0]
		for stat in status:
			if latesttranscript["status"] == stat:
				match = True
		if match is True:
			url = latesttranscript["url"]
			pagenr = latesttranscript["pageNr"]
			pagestat = latesttranscript["status"]
			error = createtranscript(url, pagenr, pathtodoc)
			if error is True:
				errors += 1

			if pagestat == "NEW":
				pagesnew.append(pagenr)
			elif pagestat == "IN PROGRESS":
				pagesinprogress.append(pagenr)
			elif pagestat == "DONE":
				pagesdone.append(pagenr)
			elif pagestat == "FINAL":
				pagesfinal.append(pagenr)

	if errors == 0:
		errorlog = "No server error while retrieving xml files.\n"
	else:
		errorlog = "%s server error(s) while retreiving xml files.\n" % (errors)
	createLogEntry(data, errorlog, pagesnew, pagesinprogress, pagesdone, pagesfinal)
	return errors


def getmetadata(data):
	"""Create a new json file containing the document's metadata in the corresponding folder
	:param data: dict (json file)
	:return: string
	"""
	metadata = data["md"]
	docid = metadata["docId"]
	documenttitle = metadata["title"]
	documenttitle = documenttitle.replace("/", "-")
	pathtodoc = "%s/%s - %s" % (pathtocol, docid, documenttitle)

	# Reporting
	print("Creating new folder in data/%s/ for document %s, if does not already exist." % (collectionname, documenttitle))
	createFolder(pathtodoc)

	# Create metadata.json file for document
	filepath = "%s/metadata.json" % (pathtodoc)
	with open (filepath, 'w') as file:
		text = json.dumps(metadata)
		file.write(text)
	return pathtodoc


# ------- REQUESTS ------- 
def getsessionid():
	"""Use Transkribus API login tools and returns a session code
	:return: string
	"""
	url = "https://transkribus.eu/TrpServer/rest/auth/login"
	payload = 'user=' + username + '&' + 'pw=' + password
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}
	response = requests.request("POST", url, data=payload, headers=headers)

	try:
		soup = BeautifulSoup(response.text, "xml")
		sessionid = soup.sessionId.string
		# Reporting
		print("Successfully connected; session ID: %s." % (sessionid))
	except Exception as e:
		print("Connection failed.")
		print(e)
	return sessionid


def getcollectionid(sessionid):
	""" Use Trankribus API to list collections accessible on the session and retrieve the ID of the targeted collection and rertuns that ID
	:param sessionid: string
	:return: string
	"""
	url = "https://transkribus.eu/TrpServer/rest/collections/list"
	querystring = {"JSESSIONID":sessionid}
	response = requests.request("GET", url, params=querystring)
	json_file = json.loads(response.text)

	collectionid = ''

	for collection in json_file:
		name = collection['colName'] 
		if name == collectionname:
			collectionid = collection['colId']

	# Reporting 
	if not collectionid:
		print('Verify targeted collection name or user\'s rights, no collection named %s !' % (collectionname))
	else:
		print("Found %s; ID: %s." % (collectionname, collectionid))
	return collectionid


def getdocumentid(sessionid, collectionid):
	""" Use Transkribus API to get a list of document ID in the targeted collection and returns that list
	:param sessionid: string
	:param collectionid: string
	:return: list
	"""
	url = "https://transkribus.eu/TrpServer/rest/collections/%s/list" % (collectionid)
	querystring = {"JSESSIONID":sessionid}
	response = requests.request("GET", url, params=querystring)
	json_file = json.loads(response.text)

	doclist = []

	for document in json_file:
		docId = document["docId"]
		doclist.append(docId)

	# Reporting
	idreport = ", ".join(map(str, doclist))
	print("Found following document IDs in '%s' collection: %s." % (collectionname, idreport))
	return doclist

def getdocumentpages(sessionid, collectionid, documentid):
	""" Use Transkribus API to get a json file with metadata and transcriptions, alos keep track of server errors for report
	:param sessionid: string
	:param collectionid: string
	:param documentid: string
	:return: integer
	"""
	totalerrors = 0
	url = "https://transkribus.eu/TrpServer/rest/collections/%s/%s/fulldoc" %(collectionid, documentid)
	querystring = {"JSESSIONID":sessionid}
	response = requests.request("GET", url, params=querystring)
	json_file = json.loads(response.text)

	# Get metadata and create metadata file and log
	pathtodoc = getmetadata(json_file)
	errors = gettranscripts(json_file, pathtodoc)
	totalerrors += errors
	return totalerrors


# ======================= #

# Ajouter une contrôle sur les valeurs dans status

now = datetime.datetime.now()
timestamp = "%s-%s-%s-%s-%s" % (now.year, now.month, now.day, now.hour, now.minute)

currentdirectory = os.path.dirname(os.path.abspath(__file__))
pathtodata = currentdirectory + "/data"
pathtologs = currentdirectory + "/__logs__"
sessionid = getsessionid()
initiateLog()

for collectionname in collectionnames:
	pathtocol = "%s/%s" % (pathtodata, collectionname)
	
	collectionid = getcollectionid(sessionid)
	totalerrors = 0
	if collectionid:
		listofdocumentid = getdocumentid(sessionid, collectionid)
		print("Creating new folder in data/ for %s collection if does not already exist." % (collectionname))
		createFolder(pathtocol)
		
		for documentid in listofdocumentid:
			errors = getdocumentpages(sessionid, collectionid, documentid)
			totalerrors += errors
		if totalerrors != 0:
			print("Warning! %s server error(s) while retrieving xml files!" % (totalerrors))
		createSeparationInLog()


