import requests, json, os, datetime
import xml.etree.ElementTree as ET
from secrets import username, password

COLLECTIONNAME = 'timeUS'

now = datetime.datetime.now()
timestamp = "%s-%s-%s-%s-%s" % (now.year, now.month, now.day, now.hour, now.minute)

currentdirectory = os.path.dirname(os.path.abspath(__file__))
pathtodata = currentdirectory + "/data"
pathtocol = pathtodata + "/%s" % (COLLECTIONNAME)
pathtologs = currentdirectory + "/__logs__"


# ============================= #

def createFolder(directory):
	"""Creates a new folder
	source : https://gist.github.com/keithweaver/562d3caa8650eefe7f84fa074e9ca949
	"""
	try:
		if not os.path.exists(directory):
			os.makedirs(directory)
	except OSError:
		print('Creating new directory. ' + directory)
	return


def initiateLog():
	"""Initiates a log file with a timestamp
	"""
	filepath = "%s/log-%s.txt" % (pathtologs, timestamp)
	intro = """
	RETRIEVING XML FILES FROM TRANSKRIBUS

	Script ran at : %s
	For collection '%s'

	---------------------

""" % (now, COLLECTIONNAME)
	with open(filepath, "w") as f:
		f.write(intro)
	return


def createDonelog(title, nrOfPages, pagedone, errorlog):
	"""Creates simple reports for each document in the collection with status "Done"
	"""
	pagereport = ''
	nrPageDone = len(pagedone)
	reportnrpages = "Document '%s' contains %s pages." % (title, nrOfPages)

	if len(pagedone) == 0:
		report = "%s\nNo page with status 'DONE' in document '%s'.\n\n" % (reportnrpages, title)
	else:
		for pagenb in pagedone:
			pagereport = pagereport + str(pagenb) + ' '
		report = "%s\nDocument '%s' has %s with status 'DONE'.\nFollowing pages have status 'DONE' : %s\n%s\n\n" % (reportnrpages, title, nrPageDone, pagereport, errorlog)

	filepath = "%s/log-%s.txt" % (pathtologs, timestamp)
	with open(filepath, "a") as f:
		f.write(report)
	return


def createtranscript(url, pagenr, pathtodoc):
	"""Creates a new xml file containing the transcript given by Transkribus for a page, in PAGE standard. File is name after corresponding page number.
	"""
	response = requests.request("GET", url)
	if response.status_code == 503:
		error = True
	else:
		error = False
		xml = response.text
		filepath = "%s/%s.xml" % (pathtodoc, pagenr)
		with open(filepath, "w") as f:
			f.write(xml)
	return error

# ----------------------------- #

def getmetadata(data):
	"""Creates a new json file containing the document's metadata in the corresponding folder
	"""
	metadata = data["md"]
	documenttitle = metadata["title"]
	documenttitle = documenttitle.replace("/", "-")
	pathtodoc = pathtocol + documenttitle
	# Reporting
	print("Creating new folder in data/%s/ for document %s." % (COLLECTIONNAME, documenttitle))
	createFolder(pathtodoc)

	filepath = "%s/metadata.json" % (pathtodoc)
	with open (filepath, 'w') as file:
		text = json.dumps(metadata)
		file.write(text)

	return pathtodoc, metadata


def getDonetranscripts(data, pathtodoc):
	"""Identify page transcripts with status DONE for a given document, provokes creation of xml file and log
	"""
	pagedone = []
	errors = 0
	pagelist = data["pageList"]["pages"]
	# Reporting
	print("Creating xml files for " + data["md"]["title"])
	for page in pagelist:
		latesttranscript = page["tsList"]["transcripts"][0] 
		if latesttranscript["status"] == "DONE":
			url = latesttranscript["url"]
			pagenr = latesttranscript["pageNr"]
			error = createtranscript(url, pagenr, pathtodoc)
			pagedone.append(pagenr)
			if error is True:
				errors += 1

	# Reporting
	if errors == 0:
		errorlog = "No server error while retrieving xml files."
	else :
		errorlog = str(errors) + " server error(s) retrieving xml files."
	nrOfPages = data["md"]["nrOfPages"]
	title = data["md"]["title"]
	createDonelog(title, nrOfPages, pagedone, errorlog)	
	return errors


def getdocumentpage(sessionid, collectionid, documentid):
	"""
	"""
	allerrors = 0
	url = "https://transkribus.eu/TrpServer/rest/collections/%s/%s/fulldoc" %(collectionid, documentid)
	querystring = {"JSESSIONID":sessionid}
	response = requests.request("GET", url, params=querystring)
	json_file = json.loads(response.text)

	# Get metadata and create metadata file and log
	pathtodoc, metadata = getmetadata(json_file)
	errors = getDonetranscripts(json_file, pathtodoc)
	allerrors += errors
	return allerrors


def getsessionid():
	"""Uses Transkribus API login tools and returns a session code as a string
	"""
	url = "https://transkribus.eu/TrpServer/rest/auth/login"
	payload = 'user=' + username + '&' + 'pw=' + password
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}
	response = requests.request("POST", url, data=payload, headers=headers)

	try:
		xml = ET.fromstring(response.text)
		sessionid = xml.find('sessionId').text
		# Reporting
		print("Successfully connected ; session ID : %s." % (sessionid))
	except Exception as e:
		print("Connection failed.")
		print(e)
	return sessionid


def getcollectionid(sessionid):
	"""Uses Trankribus API to list collections accessible on the session and retrieve the ID of the targeted collection (given in "COLLECTIONNAME") and rertuns that ID
	"""
	url = "https://transkribus.eu/TrpServer/rest/collections/list"
	querystring = {"JSESSIONID":sessionid}
	response = requests.request("GET", url, params=querystring)
	json_file = json.loads(response.text)

	collectionid = ''

	for collection in json_file:
		name = collection['colName'] 
		if name == COLLECTIONNAME:
			collectionid = collection['colId']

	# Reporting 
	if not collectionid:
		print('Verify targeted collection name, no collection named %s in the file !' % (COLLECTIONNAME))
	else:
		print("Found %s ; ID : %s." % (COLLECTIONNAME, collectionid))

	return collectionid


def getdocumentid(sessionid, collectionid):
	"""Uses Transkribus API to get a list of document ID in the targeted collection and returns that list
	"""
	url = "https://transkribus.eu/TrpServer/rest/collections/" + str(collectionid) + "/list"
	querystring = {"JSESSIONID":sessionid}
	response = requests.request("GET", url, params=querystring)
	json_file = json.loads(response.text)

	doclist = []

	for document in json_file:
		docId = document["docId"]
		doclist.append(docId)

	# Reporting
	idreport = ''
	for docid in doclist:
		idreport = idreport + str(docid) + ' '
	print("Found following document IDs in %s collection : %s." % (COLLECTIONNAME, idreport))
	return doclist


# ============================= #

sessionid = getsessionid()
collectionid = getcollectionid(sessionid)
totalerrors = 0
if collectionid:
	listofdocumentid = getdocumentid(sessionid, collectionid)
	print("Creating new folder in data/ for %s collection if does not already exist." % (COLLECTIONNAME))
	createFolder(pathtocol)
	initiateLog()

	for documentid in listofdocumentid:
		errors = getdocumentpage(sessionid, collectionid, documentid)
		totalerrors += errors
	if totalerrors != 0:
		print("Warning! %s server error(s) while retrieving xml files!" % (totalerrors))



