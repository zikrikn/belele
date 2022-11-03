from deta import Deta  # Import Deta

# Initialize with a Project Key
deta = Deta()

#DB - this is like a table
db_admin = deta.Base("admin")
db_beritadanpedoman = deta.Base("beritadanpedoman")
db_kolam = deta.Base("kolam")
db_monitoring = deta.Base("monitoring")
db_pangan = deta.Base("pangan")
db_pemberipakan = deta.Base("pemberipakan")