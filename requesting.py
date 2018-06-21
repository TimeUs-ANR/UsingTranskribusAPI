import requests
import json
import xml.etree.ElementTree as ET

from secrets import username, password

COLLECTIONNAME = 'timeUS'


# ============================= #

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

# ============================= #

sessionid = getsessionid()
collectionid = getcollectionid(sessionid)
if collectionid:
	listofdocumentid = getdocumentid(sessionid, collectionid)



