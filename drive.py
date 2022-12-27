from deta import Deta  # Import Deta
from settings import PROJECT_KEY

# Initialize with a Project Key
'''
Key Name kax8yf
Key Description Project Key: kax8yf
Project Key c08rolsw_ACgvH25t8UoevXnPHMqVWtFBwJ7rtYPN
'''
deta = Deta(PROJECT_KEY)
drive_photoprofile = deta.Drive("drive_photoprofile")
drive_thumbnail = deta.Drive("drive_thumbnail")
