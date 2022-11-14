from deta import Deta  # Import Deta

# Initialize with a Project Key
deta = Deta()

#DB - this is like a table 
#sedangkan schames untuk isi dari database-nya
#atribut dari table db-nya

#Admin
db_admin = deta.Base("admin")
db_beritadanpedoman = deta.Base("beritadanpedoman")

#User
db_pemberipakan = deta.Base("pemberipakan")
db_kolam = deta.Base("kolam")
db_notifikasi = deta.Base("notifikasi")
db_pangan = deta.Base("pangan")