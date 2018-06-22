import requests
import json
import os
import xml.etree.ElementTree as ET

from secrets import username, password

COLLECTIONNAME = 'timeUS'


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

# ----------------------------- #

def getsessionid():
	"""Uses Transkribus API login tools and returns a session code as a string
	"""
	url = "https://transkribus.eu/TrpServer/rest/auth/login"
	payload = 'user=' + username + '&' + 'pw=' + password
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}
	response = requests.request("POST", url, data=payload, headers=headers)

	xml = ET.fromstring(response.text)
	sessionid = xml.find('sessionId').text

	# Reporting
	print("Successfully connected ; session ID is : " + sessionid)
	return sessionid

def getcollectionid(sessionid):
	"""Uses Trankribus API to list collection accessible on the session and retrieve the ID of the targeted collection (indicated in "COLLECTIONNAME") and rertuns that ID
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
		print("Found " + COLLECTIONNAME + " ; ID is : " + str(collectionid))
	
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

def getmetadata(data, dirname):
	"""
	"""
	metadata = data["md"]
	documenttitle = metadata["title"]
	documenttitle = documenttitle.replace("/", "-")
	dirname = dirname + "/" + documenttitle
	# Reporting
	print("Creating new folder in data/" + COLLECTIONNAME + "/ for document " + documenttitle)
	createFolder(dirname)

	path = dirname + "/metadata.json"
	with open (path, 'w') as file:
		text = json.dumps(metadata)
		file.write(text)

	return dirname, metadata

def createtranscript(url, pagenr, dirname):
	response = requests.request("GET", url)
	xml = response.text

	filepath = dirname + "/" + str(pagenr) + ".xml"
	with open(filepath, "w") as f:
		f.write(xml)
#	Reporting
#	print(response.status_code)
	return

def gettranscripts(data, dirname):
	pagedone = []
	pagereport = ''
	pagelist = data["pageList"]["pages"]
	# Reporting
	print("Creating xml files for " + data["md"]["title"])
	for page in pagelist:
		latesttranscript = page["tsList"]["transcripts"][0] 
		if latesttranscript["status"] == "DONE":
			url = latesttranscript["url"]
			pagenr = latesttranscript["pageNr"]
			createtranscript(url, pagenr, dirname)
			pagedone.append(pagenr)
	
	# Reporting
	print("Document '" + data["md"]["title"] + "' contains " + str(data["md"]["nrOfPages"]) + " pages.")
	if len(pagedone) == 0:
		print("No page with status 'DONE' in this document")
	else:
		for pagenb in pagedone:
			pagereport = pagereport + str(pagenb) + ' '
		print("Following pages have status 'DONE' : " + pagereport)
	return 

def getdocumentpage(sessionid, collectionid, documentid, dirname):
	"""
	"""
	url = "https://transkribus.eu/TrpServer/rest/collections/" + str(collectionid) + "/" + str(documentid) + "/fulldoc"
	querystring = {"JSESSIONID":sessionid}
	response = requests.request("GET", url, params=querystring)
	json_file = json.loads(response.text)

	# Get metadata and create metadata file
	dirname, metadata = getmetadata(json_file, dirname)
	transcriptlist = gettranscripts(json_file, dirname)


	
	# ----------------------------------------------------------------------------------------------------- HERE
	# ADD CREATION OF XML FILES FOR EACH PAGE	

	return



# ============================= #

sessionid = getsessionid()
collectionid = getcollectionid(sessionid)
if collectionid:
	listofdocumentid = getdocumentid(sessionid, collectionid)

	dirname = os.path.dirname(os.path.abspath(__file__))
	dirname = dirname + "/data/" + COLLECTIONNAME
	print("Creating new folder in data/ for " + COLLECTIONNAME + " collection.")
	createFolder(dirname)

	for documentid in listofdocumentid:
		getdocumentpage(sessionid, collectionid, documentid, dirname)



