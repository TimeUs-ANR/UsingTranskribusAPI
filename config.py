# -----------------------------
# for requestingTranskribus.py
# -----------------------------

# Transkribus username / nom d'utilisateur Transkribus
# ex : username = 'username@mail.fr'
username = ''

# Transkribus password / mot de passe Transkribus
# ex : password = 'mypassword'
password = ''

# Targeted collection name(s)
# ex : collectionnames = ['collectionname', 'anothercollectionname', 'yetanotherone']
collectionnames = []

# Targeted document status
# values can only be : 'NEW', 'IN PROGRESS', 'DONE' or 'FINAL'
# ex : status = ['DONE', 'IN PROGRESS'] or status = ['FINAL']
status = []


# -----------------------------
# for fromPAGEtoText.py
# -----------------------------

# Targeted collection name(s). Collection must have been downloaded with requestingTranskribus.py first.
# ex : textcollectionnames = ['collectionname'] or textcollectionnames = ['firstcollection', 'secondcollection']
textcollectionnames =  []


# -----------------------------
# for toSingleXML.py
# -----------------------------

# Targeted collection name(s). Collection must have been downloaded with requestingTranskribus.py first.
# ex : textcollectionnames = ['collectionname'] or textcollectionnames = ['firstcollection', 'secondcollection']
singlecollectionnames =  []
