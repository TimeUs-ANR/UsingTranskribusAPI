import requests
import json
import os
import datetime
from bs4 import BeautifulSoup
from config import username, password, status
from config import collectionnames as collection_list


def create_folder(directory):
    """Create a new folder.

    :param directory: path to new directory
    :type directory: string
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


# ------- LOGS -------


def initiate_log():
    """Initiate a log file in __logs__ directory, name after a timestamp.
    """
    collections = ' '.join(["'%s'" % collection for collection in collection_list])
    path_to_file = os.path.join(path_to_logs, "log-req-%s.txt") % TIMESTAMP
    intro = """
    RETRIEVING PAGE-XML FILES AND METADATA FROM TRANSKRIBUS

    Script ran at: %s
    For collection(s): %s

    ---------------------
    \n""" % (now, collections)
    with open(path_to_file, "w") as f:
        f.write(intro)


def create_separation_in_log():
    """Create a visual separation in log file.
    """
    path_to_file = os.path.join(path_to_logs, "log-req-%s.txt") % TIMESTAMP
    separation = "\n =================================================== \n\n"
    with open(path_to_file, "a") as f:
        f.write(separation)


def create_log_entry(data, error_log, pages_new, pages_inprogress, pages_done, pages_final):
    """Create simple reports in log file.

    :param data: contains all data retrieved from requesting Transkribus API on a collection's documents/subcollections.
    :param pages_new: list of page numbers matching "NEW" status.
    :param pages_inprogress: list of page numbers matching "IN PROGRESS" status.
    :param pages_done: list of page numbers matching "DONE" status.
    :param pages_final: list of page numbers matching "FINAL" status.
    :param error_log: message on server errors, can be empty string.
    :type data: dictionary
    :type pages_new: list
    :type pages_inprogress: list
    :type pages_final: list
    :type error_log: string
    """
    data = data["md"]
    nr_of_pages = data["nrOfPages"]
    title = data["title"]
    nr_of_new = data["nrOfNew"]
    nr_of_inprogress = data["nrOfInProgress"]
    nr_of_done = data["nrOfDone"]
    nr_of_final = data["nrOfFinal"]

    report_pages = "\nDocument '%s' contains %s pages.\n" % (title, nr_of_pages)
    report_status = "New: %s\nIn Progress: %s\nDone: %s\nFinal:%s\n" % (nr_of_new, nr_of_inprogress, nr_of_done, nr_of_final)
    report_which_pages = ""
    if len(pages_new) != 0:
        pages_new = str(pages_new).strip('[]')
        report_which_pages += "Following pages have status 'NEW': %s\n" % pages_new
    if len(pages_inprogress) != 0:
        pages_inprogress = str(pages_inprogress).strip('[]')
        report_which_pages += "Following pages have status 'IN PROGRESS': %s\n" % pages_inprogress
    if len(pages_done) != 0:
        pages_done = str(pages_done).strip("[]")
        report_which_pages += "Following pages have status 'DONE': %s\n" % pages_done
    if len(pages_final) != 0:
        pages_final = str(pages_final).strip("[]")
        report_which_pages += "Following pages have status 'FINAL': %s\n" % pages_final

    report = report_pages + report_status + report_which_pages + error_log

    path_to_file = os.path.join(path_to_logs, "log-req-%s.txt") % TIMESTAMP
    with open(path_to_file, "a") as f:
        f.write(report)


# ------- CREATE FILES ------

def create_transcript(url_transcript, url_image, page_nb, path_to_doc, document_title, document_desc, document_lang):
    """Create xml file containing a page transcript from Transkribus, in PAGE standard. File is name after
    corresponding page number.

    :param url_transcript: url to request transcript, provided by Transkribus.
    :param url_image: url to request image of current document/subcollection page.
    :param page_nb: current page number.
    :param path_to_doc: path to directory for the current document/subcollection.
    :param document_title: title of current document/subcollection.
    :param document_desc: description of current document/subcollection.
    :param document_lang: list of languages for current document/subcollection, separated by commas.
    :type url_transcript: string
    :type url_image: string
    :type page_nb: integer
    :type path_to_doc: string
    :type document_title: string
    :type document_desc: string
    :type document_lang: string
    :return: a status to signal possible server errors.
    :rtype: boolean
    """
    response = requests.request("GET", url_transcript)
    document_title = "<title>%s</title>" % document_title
    document_desc = "<desc>%s</desc>" % document_desc
    document_page_nb = "<pagenumber>%s</pagenumber>" % page_nb
    tag_title = BeautifulSoup(document_title, "xml")
    tag_desc = BeautifulSoup(document_desc, "xml")
    tag_page_nb = BeautifulSoup(document_page_nb, "xml")
    tag_title = tag_title.title.extract()
    tag_desc = tag_desc.desc.extract()
    tag_page_nb = tag_page_nb.pagenumber.extract()
    tag_title.name = "tu:title"
    tag_desc.name = "tu:desc"
    tag_page_nb.name = "tu:pagenumber"
    if len(document_lang) != 0:
        document_lang = ''.join(["<language>%s</language>" % l.strip() for l in document_lang.split(",")])
        document_lang = "<languages>%s</languages>" % document_lang
        tag_languages = BeautifulSoup(document_lang, "xml")
        tag_languages = tag_languages.languages.extract()
        tag_lang_list = tag_languages.findAll("language")
        for tag in tag_lang_list:
            tag.name = "tu:language"

    if response.status_code == 503:
        error = True
    else:
        error = False
        xml = response.text
        path_to_file = os.path.join(path_to_doc, "%s.xml") % page_nb
        soup = BeautifulSoup(xml, "xml")
        # Adding namespace declaration for element added by Time Us project
        # Adding attributes to Page elements : @timeUs:url and @timeUs:id
        if soup.PcGts:
            soup.PcGts["xmlns:tu"] = "timeUs"
            soup.Page["tu:url"] = url_image
            soup.Page["tu:id"] = page_nb
            soup.Metadata.append(tag_title)
            soup.Metadata.append(tag_desc)
            soup.Metadata.append(tag_page_nb)
            if len(document_lang) != 0:
                for tag in tag_lang_list:
                    soup.Metadata.append(tag)
            with open(path_to_file, "w") as f:
                f.write(str(soup))
    return error


def get_transcripts(data, path_to_doc):
    """Identify page numbers matching targeted status.

    :param data: contains all data retrieved from requesting Transkribus API on a collection's documents/subcollections.
    :param path_to_doc: path to directory for the current document/subcollection.
    :type data: dictionary
    :type path_to_doc: string
    :return: sum of all signals of server errors on pages in current document/subcollection.
    :rtype: integer
    """
    pages_new = []
    pages_inprogress = []
    pages_done = []
    pages_final = []
    errors = 0

    page_list = data["pageList"]["pages"]
    document_title = data["md"]["title"]
    if "desc" in data["md"]:
        document_desc = data["md"]["desc"]
    else:
        document_desc = "No description."
    if "language" in data["md"]:
        document_lang = data["md"]["language"]
    else:
        document_lang = ""
    # Reporting
    print("Creating xml files for %s" % document_title)

    for page in page_list:
        match = False
        latest_transcript = page["tsList"]["transcripts"][0]
        for stat in status:
            if latest_transcript["status"] == stat:
                match = True
        if match is True:
            url_transcript = latest_transcript["url"]
            url_image = page["url"]
            page_nb = latest_transcript["pageNr"]
            page_stat = latest_transcript["status"]
            error = create_transcript(url_transcript, url_image, page_nb, path_to_doc, document_title, document_desc, document_lang)
            if error is True:
                errors += 1
            if page_stat == "NEW":
                pages_new.append(page_nb)
            elif page_stat == "IN PROGRESS":
                pages_inprogress.append(page_nb)
            elif page_stat == "DONE":
                pages_done.append(page_nb)
            elif page_stat == "FINAL":
                pages_final.append(page_nb)
    if errors == 0:
        error_log = "\n"
    else:
        error_log = "%s server error(s) while retreiving xml files.\n" % errors
    create_log_entry(data, error_log, pages_new, pages_inprogress, pages_done, pages_final)
    return errors


def get_metadata(data):
    """Create JSON file containing document/subcollection's metadata in collection's directory.

    :param data: contains all data retrieved from requesting Transkribus API on a collection's documents/subcollections.
    :type data: dictionary
    :return: path to directory for the current document/subcollection.
    :rtype: string
    """
    metadata = data["md"]
    document_id = metadata["docId"]
    document_title = metadata["title"]
    document_title = document_title.replace("/", "-")
    path_to_doc = os.path.join(path_to_col, "%s - %s") % (document_id, document_title)
    create_folder(path_to_doc)
    # Create metadata.json file for document
    path_to_file = os.path.join(path_to_doc, "metadata.json")
    with open(path_to_file, 'w') as file:
        text = json.dumps(metadata)
        file.write(text)
    return path_to_doc


# ------- REQUESTS ------- 
def get_session_id():
    """Request Transkribus API to authenticate.

    :return: session id for authentication.
    :rtype: string
    """
    url = "https://transkribus.eu/TrpServer/rest/auth/login"
    payload = 'user=' + username + '&' + 'pw=' + password
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.request("POST", url, data=payload, headers=headers)

    try:
        soup = BeautifulSoup(response.text, "xml")
        session_id = soup.sessionId.string
        # Reporting
        print("Successfully connected; session ID: %s." % session_id)
    except Exception as e:
        print(e)
        print("Connection failed.")
        session_id = None
    return session_id


def get_collection_id(session_id):
    """Request Trankribus API to list collections accessible for current user and retrieve id of targeted collection.

    :param session_id: session id for authentication.
    :type session_id: string
    :return: numerical id for targeted collection.
    :rtype: integer
    """
    url = "https://transkribus.eu/TrpServer/rest/collections/list"
    querystring = {"JSESSIONID": session_id}
    response = requests.request("GET", url, params=querystring)
    json_file = json.loads(response.text)

    collection_id = ''
    for collection in json_file:
        if collection['colName'] == collection_name:
            collection_id = collection['colId']

    # Reporting
    if not collection_id:
        print('Verify targeted collection name or user\'s rights, no collection named %s!' % collection_name)
    else:
        print("Found %s; ID: %s." % (collection_name, collection_id))
    return collection_id


def get_document_id(session_id, collection_id):
    """Request Transkribus API to list documents/subcollections in targeted collection.

    :param session_id: session id for authentication.
    :param collection_id: numerical id for targeted collection.
    :type session_id: string
    :type collection_id: integer
    :return: list of numerical id for documents/subcollections in targeted collection.
    :rtype: list
    """
    url = "https://transkribus.eu/TrpServer/rest/collections/%s/list" % collection_id
    querystring = {"JSESSIONID": session_id}
    response = requests.request("GET", url, params=querystring)
    json_file = json.loads(response.text)
    document_list = [document["docId"] for document in json_file]

    # Reporting
    id_list = ", ".join(map(str, document_list))
    print("Found following document IDs in '%s' collection: %s." % (collection_name, id_list))
    return document_list


def get_document_pages(session_id, collection_id, document_id):
    """Request Transkribus API to get document/subcollection's metadata.

    :param session_id: session id for authentication.
    :param collection_id: numerical id for targeted collection.
    :param document_id: numerical id for document/subcollection in targeted collection.
    :type session_id: string
    :type collection_id: integer
    :type document_id: integer
    :return: sum of all signals of server errors for current document/subcollection.
    :rtype: integer
    """
    total_errors = 0
    url = "https://transkribus.eu/TrpServer/rest/collections/%s/%s/fulldoc" % (collection_id, document_id)
    querystring = {"JSESSIONID": session_id}
    response = requests.request("GET", url, params=querystring)
    json_file = json.loads(response.text)

    # Get metadata and create metadata file and log
    path_to_doc = get_metadata(json_file)
    errors = get_transcripts(json_file, path_to_doc)
    total_errors += errors
    return total_errors


# ======================= #

now = datetime.datetime.now()
TIMESTAMP = "%s-%s-%s-%s-%s" % (now.year, now.month, now.day, now.hour, now.minute)

invalid_status = []
for stat in status:
    if not (stat == "NEW" or stat == "IN PROGRESS" or stat == "DONE" or stat == "FINAL"):
        print("Warning! %s is not a valid satus" % stat)
        invalid_status.append(stat)
if len(invalid_status) > 0:
    [status.remove(wrong) for wrong in invalid_status]
    if len(status) > 0:
        print("Working with valid status: %s" % (str(status).strip('[]')))

if len(status) > 0:
    cwd = os.path.dirname(os.path.abspath(__file__))
    path_to_data = os.path.join(cwd, "data")
    path_to_logs = os.path.join(cwd, "__logs__")
    session_id = get_session_id()
    if session_id:
        initiate_log()

        for collection_name in collection_list:
            path_to_col = os.path.join(path_to_data, collection_name)

            collection_id = get_collection_id(session_id)
            total_errors = 0
            if collection_id:
                list_of_document_id = get_document_id(session_id, collection_id)
                print("Creating new folder in data/ for %s collection if does not already exist." % collection_name)
                create_folder(path_to_col)

                for document_id in list_of_document_id:
                    errors = get_document_pages(session_id, collection_id, document_id)
                    total_errors += errors
                if total_errors != 0:
                    print("Warning! %s server error(s) while retrieving xml files!" % total_errors)
                create_separation_in_log()
else:
    print("No valid status to work with.")
