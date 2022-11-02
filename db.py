from deta import Deta  # Import Deta

# Initialize with a Project Key
deta = Deta()

# This how to connect to or create a database.
db = deta.Base("lele_db")

# You can create as many as you want without additional charges.
admin = deta.Base("admin")
beritadanpedoman = deta.Base("beritadanpedoman")
kolam = deta.Base("kolam")
monitoring = deta.Base("monitoring")
pangan = deta.Base("pangan")
pemberipakan = deta.Base("pemberipakan")