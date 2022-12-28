from deta import Deta  # Import Deta
from settings import PROJECT_KEY

# Initialize with a Project Key
deta = Deta(PROJECT_KEY)
drive_photoprofile = deta.Drive("drive_photoprofile")
drive_thumbnail = deta.Drive("drive_thumbnail")
