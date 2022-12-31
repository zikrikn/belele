from pydantic import ValidationError
from datetime import datetime, time, tzinfo, timedelta
from dateutil.relativedelta import relativedelta
import time as tm
import random
import string
import pytz

# Menentukan timezone Indonesia Barat
tz = pytz.timezone('Asia/Jakarta')
class TZ(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=7)

tz_py2 = TZ() # untk melakukan return detatime in Python 2

inT1 = time(17, 1, 00)
inT2 = time(8, 1, 00)
inT3 = time(12, 1, 00)

outT1 = time(8, 00, 00)
outT2 = time(12, 00, 00)
outT3 = time(17, 00, 00)

inPagi = datetime.combine(datetime.now().date(), inT1).replace(tzinfo=tz_py2)
inSiang = datetime.combine(datetime.now().date(), inT2).replace(tzinfo=tz_py2)
inSore = datetime.combine(datetime.now().date(), inT3).replace(tzinfo=tz_py2)
outPagi = datetime.combine(datetime.now().date(), outT1).replace(tzinfo=tz_py2)
outSiang = datetime.combine(datetime.now().date(), outT2).replace(tzinfo=tz_py2)
outSore = datetime.combine(datetime.now().date(), outT3).replace(tzinfo=tz_py2)

if (datetime.now().replace(tzinfo=tz_py2) >= inPagi and datetime.now().replace(tzinfo=tz_py2) <= outPagi):
    print("Pagi")
elif (datetime.now().replace(tzinfo=tz_py2) >= inSiang and datetime.now().replace(tzinfo=tz_py2) <= outSiang):
    print("Siang")
elif (datetime.now().replace(tzinfo=tz_py2) >= inSore and datetime.now().replace(tzinfo=tz_py2) <= outSore):
    print("Sore")