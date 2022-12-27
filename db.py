from deta import Deta  # Import Deta
from settings import PROJECT_KEY

# Initialize with a Project Key
'''
Key Name kax8yf
Key Description Project Key: kax8yf
Project Key c08rolsw_ACgvH25t8UoevXnPHMqVWtFBwJ7rtYPN
'''
deta = Deta(PROJECT_KEY)

#Admin
#db_admin = deta.Base("db_admin")
db_beritadanpedoman = deta.Base("db_beritadanpedoman")

#User
db_kolam = deta.Base("db_kolam")
db_notifikasiIn = deta.Base("db_notifikasiIn")
db_notifikasiOut = deta.Base("db_notifikasiOut")
db_user = deta.Base("db_user")
db_profile = deta.Base("db_profile")