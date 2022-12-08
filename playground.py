from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import time as tm


h = date.today() + relativedelta(days=+2) 
print(h)

v = h + relativedelta(days=+5)

print("HELLO : ", v)

y = date.today()
print(y)

if date.today() == date.today():
    print("HEYO")
    tm.sleep(10)

t1 = time(8, 00, 00)
t2 = time(12, 00, 00)
t3 = time(17, 00, 00)

pagi = datetime.combine(date.today(), t1)
siang = datetime.combine(date.today(), t2)
sore = datetime.combine(date.today(), t3)

result = datetime.today() + timedelta(hours=4, minutes=10, seconds=10)

print(result)



# dt1 = datetime.datetime(2022,3,27,13,27,45,46000) 
# dt2 = datetime.datetime(2022,6,30,14,28) 
# tdelta = dt2 - dt1 
# print(tdelta) 
# print(type(tdelta))

# i = 123
# print(type(i))

# if (datetime.datetime.now() >= datetime.datetime(2022,3,27)):
#     print("2121") #Ini bisa dianggap masuk
#     #dan langsung hapus di sini di database notifikasi agar tidak berlanjut keluar


#we have to 2 table yakni, inputNotifikasi dan outputNotifikasi



#inputNotifikasi
'''
nomorNotifikasi

while True:
    

'''

d = [{'key1': '01', 'key2': '01', 'key3': '01'}, {'key1': '02', 'key2': '02', 'key3': '02'}]

print(d[1]['key1'])

# h = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

# print(h)