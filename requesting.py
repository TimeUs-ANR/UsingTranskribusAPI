import requests, json, os, datetime
import xml.etree.ElementTree as ET

from secrets import username, password

COLLECTIONNAME = 'timeUS'
now = datetime.datetime.now()
timestamp = "%s-%s-%s-%s-%s" % (now.year, now.month, now.day, now.hour, now.minute)

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


def initiateLog(dirname):
	"""Initiates a log file with a timestamp
	"""
	filepath = dirname + "/log-" + timestamp + ".txt"
	intro = "Script ran at : \n" + str(now) + "\n\n---------------------\n\n"
	with open(filepath, "w") as f:
		f.write(intro)
	return


def createDonelog(title, nrOfPages, pagedone, errorlog):
	"""Creates simple reports for each document in the collection with status "Done"
	"""
	pagereport = ''
	dirname = os.path.dirname(os.path.abspath(__file__))
	dirname = dirname + "/data/" + COLLECTIONNAME + "/__logs__"
	nrPageDone = len(pagedone)
	reportnrpages = "Document '" + title + "' contains " + str(nrOfPages) + " pages."

	if len(pagedone) == 0:
		report = reportnrpages + "\nNo page with status 'DONE' in document '" + title + "'.\n\n"
	else:
		for pagenb in pagedone:
			pagereport = pagereport + str(pagenb) + ' '
		report = reportnrpages + "\nDocument '" + title + "' has " + str(nrPageDone) + " with status 'DONE'.\nFollowing pages have status 'DONE' : " + pagereport + "\n" + errorlog + "\n\n"

	filepath = dirname + "/log-" + timestamp + ".txt"
	with open(filepath, "a") as f:
		f.write(report)
	return


def createtranscript(url, pagenr, dirname):
	"""Creates a new xml file containing the transcript given by Transkribus for a page, in PAGE standard. File is name after corresponding page number.
	"""
	response = requests.request("GET", url)
	if response.status_code == 503:
		error = True
	else:
		error = False
		xml = response.text
		filepath = dirname + "/" + str(pagenr) + ".xml"
		with open(filepath, "w") as f:
			f.write(xml)
#	Reporting
#	print(response.status_code)
	return error

# ----------------------------- #

def getmetadata(data, dirname):
	"""Creates a new json file containing the document's metadata in the corresponding folder
	"""
	metadata = data["md"]
	documenttitle = metadata["title"]
	documenttitle = documenttitle.replace("/", "-")
	dirname = dirname + "/" + documenttitle
	# Reporting
	print("Creating new folder in data/" + COLLECTIONNAME + "/ for document " + documenttitle)
	createFolder(dirname)

	filepath = dirname + "/metadata.json"
	with open (filepath, 'w') as file:
		text = json.dumps(metadata)
		file.write(text)

	return dirname, metadata


def getDonetranscripts(data, dirname):
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
			error = createtranscript(url, pagenr, dirname)
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


def getdocumentpage(sessionid, collectionid, documentid, dirname):
	"""
	"""
	allerrors = 0
	url = "https://transkribus.eu/TrpServer/rest/collections/" + str(collectionid) + "/" + str(documentid) + "/fulldoc"
	querystring = {"JSESSIONID":sessionid}
	response = requests.request("GET", url, params=querystring)
	json_file = json.loads(response.text)

	# Get metadata and create metadata file and log
	dirname, metadata = getmetadata(json_file, dirname)
	errors = getDonetranscripts(json_file, dirname)
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
		print("Successfully connected ; session ID : " + sessionid)
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
		print('Verify targeted collection name, no collection named ' + COLLECTIONNAME + 'in the file !')
	else:
		print("Found " + COLLECTIONNAME + " ; ID : " + str(collectionid))

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
	print("Found following document IDs in " + COLLECTIONNAME + " collection : " + idreport)
	return doclist


# ============================= #

sessionid = getsessionid()
collectionid = getcollectionid(sessionid)
totalerrors = 0
if collectionid:
	listofdocumentid = getdocumentid(sessionid, collectionid)
	dirname = os.path.dirname(os.path.abspath(__file__))
	dirname = dirname + "/data/" + COLLECTIONNAME
	print("Creating new folder in data/ for " + COLLECTIONNAME + " collection.")
	createFolder(dirname)
	logfolder = dirname + "/__logs__"
	createFolder(logfolder)
	initiateLog(logfolder)

	for documentid in listofdocumentid:
		errors = getdocumentpage(sessionid, collectionid, documentid, dirname)
		totalerrors += errors
	if totalerrors != 0:
		print("Warning! %s server error(s) while retrieving xml files!" % (totalerrors))



