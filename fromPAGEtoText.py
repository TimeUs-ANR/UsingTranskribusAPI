import os
import datetime
from bs4 import BeautifulSoup
from config import textcollectionnames as collection_list


def create_folder(directory):
    """Create a new folder.

    :param directory: path to new directory
    :type directory: string
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def initiate_log():
    """Initiate a log file in __logs__ directory, name after a timestamp.
    """
    collist = ' '.join(["'%s'" % collection for collection in collection_list])
    path_to_file = os.path.join(path_to_logs, "log-text-%s.txt") % TIMESTAMP
    intro = """
    TRANSFORMING XML FILES (PAGE FORMAT) TO TEXT FILES

    Script ran at : %s
    For collections %s.

    ---------------------
""" % (now, collist)
    with open(path_to_file, "w") as f:
        f.write(intro)


def create_log(xml_counter, page_counter, document):
    """Create simple reports in log file.

    :param xml_counter: number of xml files in document/subcollection directory.
    :param page_counter: number of xml-page files in document/subcollection directory.
    :param document: name of document/subcollection directory.
    :type xml_counter: integer
    :type page_counter: integer
    :type document: string
    """
    if xml_counter == 0:
        log = "No .xml file in '%s' directory.\n\n" % document
    else:
        log = "Found %s .xml file(s) in '%s' directory.\n" % (xml_counter, document)
        if page_counter == 0:
            log = log + "\tNo .xml file matched PAGE format (root must be '<PcGts>'.\n\n"
        else:
            log = log + "\tFound %s .xml file(s) matching PAGE format.\n\n" % page_counter
    path_to_file = os.path.join(path_to_logs, "log-text-%s.txt") % TIMESTAMP
    with open(path_to_file, "a") as f:
        f.write(log)


# ========================== #

now = datetime.datetime.now()
TIMESTAMP = "%s-%s-%s-%s-%s" % (now.year, now.month, now.day, now.hour, now.minute)
cwd = os.path.dirname(os.path.abspath(__file__))
path_to_logs = os.path.join(cwd, "__logs__")
initiate_log()

for collection in collection_list:
    path = os.path.join(cwd, "data", collection)
    path_to_export_text = os.path.join(path, "__TextExports__")

    # PREPARING FILES
    try:
        col_content = os.listdir(path)
        if "__TextExports__" in col_content:
            col_content.remove("__TextExports__")
        if "__AllInOne__" in col_content:
            col_content.remove("__AllInOne__")

        if len(col_content) > 0:
            create_folder(path_to_export_text)
            for document in col_content:
                path_to_doc = os.path.join(path, document)
                path_to_textfile = os.path.join(path_to_export_text, "%s.txt") % document
                try:
                    folder_content = os.listdir(path_to_doc)
                    sorted_content = []
                    if len(folder_content) > 0:
                        # ORDERING XML FILES
                        for filename in [f for f in folder_content if f.endswith(".xml")]:
                            filename, ext = os.path.splitext(filename)
                            try:
                                sorted_content.append(int(filename))
                            except TypeError:
                                sorted_content.append(filename)
                        sorted_content.sort()
                        if len(sorted_content) > 0:
                            # erasing file if exists already
                            with open(path_to_textfile, "w") as f:
                                f.write("")
                        folder_content = [str(filename) + ".xml" for filename in sorted_content]
                        xml_counter = len(folder_content)

                        # GETTING TEXT FROM XML FILES
                        page_counter = 0
                        for file in folder_content:
                            page_nb, ext = os.path.splitext(file)
                            path_to_file = os.path.join(path_to_doc, file)
                            with open(path_to_file, "r") as f:
                                content = f.read()
                            soup = BeautifulSoup(content, "xml")
                            if soup.PcGts:
                                page_counter += 1
                                textregion_all = soup.find_all("TextRegion")
                                for textregion in textregion_all:
                                    region_id = textregion['id']
                                    textequiv_all = textregion("TextEquiv", recursive=False)
                                    for textequiv in textequiv_all:
                                        text = textequiv.Unicode.get_text()

                                        # CREATING TEXT FILES
                                        # With Zone and Region separators
                                        with open(path_to_textfile, "a") as f:
                                            f.write("%s\n\n[.../R fin de la zone %s]\n\n" % (text, region_id))
                                with open(path_to_textfile, "a") as f:
                                    f.write("\n[.../... fin de la page %s]\n\n" % page_nb)
                        create_log(xml_counter, page_counter, document)

                except Exception as e:
                    print(e)
        else:
            print("No file to transform in collection named '%s'." % collection)
    except Exception as e:
        print(e)
