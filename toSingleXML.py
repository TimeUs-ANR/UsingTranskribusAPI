import os
import datetime
from bs4 import BeautifulSoup
from config import singlecollectionnames as collection_list


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
    path_to_file = os.path.join(path_to_logs, "log-single-%s.txt") % TIMESTAMP
    intro = """
    BUILDING SINGLE XML DOCUMENT(PAGE FORMAT) FROM MULTIPLE XML FILES
    
    Script ran at : %s
    For collection %s.
    
    ---------------------
""" % (now, collist)
    with open(path_to_file, "w") as f:
        f.write(intro)


def create_log(log):
    """Add log to current log file.

    :param log: report identifying mashed up files.
    :type log: string
    """
    path_to_file = os.path.join(path_to_logs, "log-single-%s.txt") % TIMESTAMP
    with open(path_to_file, "a") as f:
        f.write(log)


# ========================== #

now = datetime.datetime.now()
TIMESTAMP = "%s-%s-%s-%s-%s" % (now.year, now.month, now.day, now.hour, now.minute)
cwd = os.path.dirname(os.path.abspath(__file__))
path_to_data = os.path.join(cwd, "data")
path_to_logs = os.path.join(cwd, "__logs__")
initiate_log()

for collection in collection_list:
    path = os.path.join(path_to_data, collection)
    path_to_xml_mashup = os.path.join(path, "__AllInOne__")

    # PREPARING FILES
    try:
        data_content = os.listdir(path_to_data)
        try:
            collection_content = os.listdir(path)
            if "__TextExports__" in collection_content:
                collection_content.remove("__TextExports__")
            if "__AllInOne__" in collection_content:
                collection_content.remove("__AllInOne__")

            if len(collection_content) > 0:
                create_folder(path_to_xml_mashup)
                for document in collection_content:
                    need_end = False
                    counter = 0
                    path_to_doc = os.path.join(path, document)
                    try:
                        folder_content = os.listdir(path_to_doc)
                        sorted_content = []
                        # ORDERING XML FILES
                        if len(folder_content) > 0:
                            for filename in [f for f in folder_content if f.endswith(".xml")]:
                                filename, ext = os.path.splitext(filename)
                                try:
                                    sorted_content.append(int(filename))
                                except TypeError:
                                    sorted_content.append(filename)
                            sorted_content.sort()
                            # REBUILD FILE NAMES
                            folder_content = [str(filename) + ".xml" for filename in sorted_content]
                            counter = len(folder_content)

                            path_to_export = os.path.join(path_to_xml_mashup, "%s.xml") % document
                            # CREATE CONTENT FOR THE NEW FILE
                            # CREATE HEADER
                            i = 0
                            top = len(folder_content)
                            while i != top:
                                ispagefile = os.path.join(path_to_doc, folder_content[i])
                                with open(ispagefile, "r") as f:
                                    content = f.read()
                                soup = BeautifulSoup(content, "xml")
                                if soup.PcGts:
                                    meta = str(soup.Metadata)
                                    soup.Page.decompose()
                                    soup.Metadata.decompose()
                                    intro = str(soup).split("\n")
                                    # CREATING an element PageGrp not conform to PAGE standard in timeUs namespace
                                    header = "%s\n%s\n%s\n<tu:PageGrp>" % (intro[0], intro[1], meta)
                                    with open(path_to_export, "w") as f:
                                        f.write(header)
                                    need_end = True
                                    i = top
                                else:
                                    i += 1
                            # CREATE CONTENT
                            for file in folder_content:
                                path_to_file = os.path.join(path_to_doc, file)
                                with open(path_to_file, "r") as f:
                                    content = f.read()
                                soup = BeautifulSoup(content, "xml")
                                if soup.PcGts:
                                    counter += 1
                                    page = soup.Page
                                    with open(path_to_export, "a") as f:
                                        f.write("\n" + str(page))
                            # CLOSE LAST TAGNAMES
                            if need_end is True:
                                with open(path_to_export, "a") as f:
                                    f.write("\n</tu:PageGrp>\n</PcGts>")
                                log = "Created 1 mashup file for '%s', from a total of %s file(s).\n" % (
                                    document, counter)
                                create_log(log)
                    except Exception as e:
                        print(e)
            else:
                print("No file to transform in collection named '%s'." % collection)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
