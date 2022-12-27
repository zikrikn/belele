from deta import Deta  # Import Deta

# Initialize with a Project Key
'''
Key Name kax8yf
Key Description Project Key: kax8yf
Project Key c08rolsw_ACgvH25t8UoevXnPHMqVWtFBwJ7rtYPN
'''
deta = Deta("c08rolsw_ACgvH25t8UoevXnPHMqVWtFBwJ7rtYPN")

#DB - this is like a table 
#sedangkan schames untuk isi dari database-nya
#atribut dari table db-nya

#Admin
db_admin = deta.Base("admin")
db_beritadanpedoman = deta.Base("beritadanpedoman")

#User
db_pemberipakan = deta.Base("pemberipakan")
db_kolam = deta.Base("kolam")
db_notifikasiIn = deta.Base("notifikasiIn")
db_notifikasiOut = deta.Base("notifikasiOut")
db_pangan = deta.Base("pangan")
db_user = deta.Base("user")