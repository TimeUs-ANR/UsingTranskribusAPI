import requests, json, os, datetime
from bs4 import BeautifulSoup
from config import username, password, collectionnames, status

# ======================= #

def createFolder(directory):
	"""Create a new folder.

	:param directory: path to new directory
	:type directory: string
	"""
	if not os.path.exists(directory):
		os.makedirs(directory)

# ------- LOGS -------
def initiateLog():
	"""Initiate a log file in __logs__ directory, name after a timestamp.
	"""
	collections = ' '.join(["'%s'" %collection for collection in collectionnames])
	filepath = os.path.join(pathtologs, "log-%s.txt") % (TIMESTAMP)
	intro = """
	RETRIEVING PAGE-XML FILES AND METADATA FROM TRANSKRIBUS

	Script ran at: %s
	For collection(s): %s

	---------------------
	\n""" % (now, collections)
	with open(filepath, "w") as f:
		f.write(intro)


def createSeparationInLog():
	"""Create a visual separation in log file.
	"""
	filepath = os.path.join(pathtologs, "log-%s.txt") % (TIMESTAMP)
	separation = "\n =================================================== \n\n"
	with open(filepath, "a") as f:
		f.write(separation)


def createLogEntry(data, errorlog, pagesnew, pagesinprogress, pagesdone, pagesfinal):
	"""Create simple reports in log file.

	:param data: contains all data retrieved from requesting Transkribus API on a collection's documents/subcollections.
	:param pagesnew: list of page numbers matching "NEW" status.
	:param pagesinprogress: list of page numbers matching "IN PROGRESS" status.
	:param pagesdone: list of page numbers matching "DONE" status.
	:param pagesfinal: list of page numbers matching "FINAL" status.
	:param errorlog: message on server errors, can be empty string.
	:type data: dictionnary
	:type pagesnew: list
	:type pagesinprogress: list
	:type pagesfinal: list
	:type errorlog: string
	"""
	data = data["md"]
	nrOfPages = data["nrOfPages"]
	title = data["title"]
	nrOfNew = data["nrOfNew"]
	nrOfInProgress = data["nrOfInProgress"]
	nrOfDone = data["nrOfDone"]
	nrOfFinal = data["nrOfFinal"]

	reportPages = "\nDocument '%s' contains %s pages.\n" % (title, nrOfPages)
	reportStatus = "New: %s\nIn Progress: %s\nDone: %s\nFinal:%s\n" % (nrOfNew, nrOfInProgress, nrOfDone, nrOfFinal)
	reportWhichPages = ""
	if len(pagesnew) != 0:
		pagesnew = str(pagesnew).strip('[]')
		reportWhichPages += "Following pages have status 'NEW': %s\n" % (pagesnew)
	if len(pagesinprogress) != 0:
		pagesinprogress = str(pagesinprogress).strip('[]')
		reportWhichPages += "Following pages have status 'IN PROGRESS': %s\n" % (pagesinprogress)
	if len(pagesdone) != 0:
		pagesdone = str(pagesdone).strip('[]')
		reportWhichPages += "Following pages have status 'DONE': %s\n" % (pagesdone)
	if len(pagesfinal) != 0:
		pagesfinal = str(pagesfinal).strip('[]')
		reportWhichPages += "Following pages have status 'FINAL': %s\n" % (pagesfinal)

	report = reportPages + reportStatus + reportWhichPages + errorlog

	filepath = os.path.join(pathtologs, "log-%s.txt") % (TIMESTAMP)
	with open(filepath, "a") as f:
		f.write(report)


# ------- CREATE FILES ------

def createtranscript(url, pagenr, pathtodoc):
	"""Create xml file containing a page transcript from Transkribus, in PAGE standard. File is name after corresponding page number.

	:param url: url to request transcript, provided by Transkribus.
	:param pagenr: current page number.
	:param pathtodoc: path to directory for the current document/subcollection.
	:type url: string
	:type pagenr: integer
	:type pathtodoc: string
	:return: a status to signal possible server errors.
	:rtype: boolean
	"""
	response = requests.request("GET", url)
	if response.status_code == 503:
		error = True
	else:
		error = False
		xml = response.text
		filepath = os.path.join(pathtodoc, "%s.xml") % (pagenr)
		soup = BeautifulSoup(xml, "xml")
		# Adding namespace declaration for element added by Time Us project
		# Adding attributes to Page elements : @timeUs:url and @itmeUs:id
		if soup.PcGts:
			soup.PcGts["xmlns:tu"] = "timeUs"
			soup.Page["tu:url"] = url
			soup.Page["tu:id"] = pagenr
			with open(filepath, "w") as f:
				f.write(str(soup))
	return error


def gettranscripts(data, pathtodoc):
	"""Identify page numbers matching targeted status.

	:param data: contains all data retrieved from requesting Transkribus API on a collection's documents/subcollections.
	:param pathtodoc: path to directory for the current document/subcollection.
	:type data: dictionnary
	:type pathtodoc: string
	:return: sum of all signals of server errors on pages in current document/subcollection.
	:rtype: integer
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
		errorlog = "\n"
	else:
		errorlog = "%s server error(s) while retreiving xml files.\n" % (errors)
	createLogEntry(data, errorlog, pagesnew, pagesinprogress, pagesdone, pagesfinal)
	return errors


def getmetadata(data):
	"""Create JSON file containing document/subcollection's metadata in collection's directory.

	:param data: contains all data retrieved from requesting Transkribus API on a collection's documents/subcollections.
	:type data: dictionnary
	:return: path to directory for the current document/subcollection.
	:rtype: string
	"""
	metadata = data["md"]
	docid = metadata["docId"]
	documenttitle = metadata["title"]
	documenttitle = documenttitle.replace("/", "-")
	pathtodoc = os.path.join(pathtocol, "%s - %s") % (docid, documenttitle)
	createFolder(pathtodoc)
	# Create metadata.json file for document
	filepath = os.path.join(pathtodoc, "metadata.json")
	with open (filepath, 'w') as file:
		text = json.dumps(metadata)
		file.write(text)
	return pathtodoc


# ------- REQUESTS ------- 
def getsessionid():
	"""Request Transkribus API to authentificate.

	:return: session id for authentification.
	:rtype: string
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
	"""Request Trankribus API to list collections accessible for current user and retrieve id of targeted collection.
	
	:param sessionid: session id for authentification.
	:type sessionid: string
	:return: numerical id for targeted collection.
	:rtype: integer
	"""
	url = "https://transkribus.eu/TrpServer/rest/collections/list"
	querystring = {"JSESSIONID":sessionid}
	response = requests.request("GET", url, params=querystring)
	json_file = json.loads(response.text)

	collectionid = ''
	for collection in json_file: 
		if collection['colName'] == collectionname:
			collectionid = collection['colId']

	# Reporting 
	if not collectionid:
		print('Verify targeted collection name or user\'s rights, no collection named %s!' % (collectionname))
	else:
		print("Found %s; ID: %s." % (collectionname, collectionid))
	return collectionid


def getdocumentid(sessionid, collectionid):
	"""Request Transkribus API to list documents/subcollections in targeted collection.
	
	:param sessionid: session id for authentification.
	:param collectionid: numerical id for targeted collection.
	:type sessionid: string
	:type collectionid: integer
	:return: list of numerical id for documents/subcollections in targeted collection.
	:rtype: list
	"""
	url = "https://transkribus.eu/TrpServer/rest/collections/%s/list" % (collectionid)
	querystring = {"JSESSIONID":sessionid}
	response = requests.request("GET", url, params=querystring)
	json_file = json.loads(response.text)
	doclist = [document["docId"] for document in json_file]

	# Reporting
	idreport = ", ".join(map(str, doclist))
	print("Found following document IDs in '%s' collection: %s." % (collectionname, idreport))
	return doclist

def getdocumentpages(sessionid, collectionid, documentid):
	"""Request Transkribus API to get document/subcollection's metadata.
	
	:param sessionid: session id for authentification.
	:param collectionid: numerical id for targeted collection.
	:param documentid: numerical id for document/subcollection in targeted collection.
	:type sessionid: string
	:type collectioid: integer
	:type documentid: integer
	:return: sum of all signals of server errors for current document/subcollection.
	:rtype: integer
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

now = datetime.datetime.now()
TIMESTAMP = "%s-%s-%s-%s-%s" % (now.year, now.month, now.day, now.hour, now.minute)

verifystatus = []
for stat in status:
	if not (stat == "NEW" or stat == "IN PROGRESS" or stat == "DONE" or stat == "FINAL"):
		print("Warning! %s is not a valid satus" % (stat))
		verifystatus.append(stat)
if len(verifystatus) > 0:
	[status.remove(wrong) for wrong in verifystatus]
	if len(status) > 0:
		print("Working with valid status: %s" % (str(status).strip('[]')))

if len(status) > 0:
	currentdirectory = os.path.dirname(os.path.abspath(__file__))
	pathtodata = os.path.join(currentdirectory, "data")
	pathtologs = os.path.join(currentdirectory, "__logs__")
	sessionid = getsessionid()
	initiateLog()

	for collectionname in collectionnames:
		pathtocol = os.path.join(pathtodata, collectionname)
		
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
else:
	print("No valid status to work with.")


