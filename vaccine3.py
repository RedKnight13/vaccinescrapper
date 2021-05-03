import requests
from datetime import date,datetime
import os
import smtplib
from time import time,ctime


minutes = 1

today = date.today()


__district = "307" 

'''
295 - Kasargod
296 - Thiruvananthapuram
298 - kollam
299 - Wayanad
300 - Pathanamthitta
302 - Malappuram
303 - thrissue
305 - Kozikode
306- idukki
307 - ernakulam
308 - palakkad
'''



d1 = today.strftime("%d/%m/%Y")

__date = str(d1).replace("/","-")	

def parse_json(result):
	output = []
	centers = result['centers']
	for center in centers:
		sessions = center['sessions']
		for session in sessions:
			if session['available_capacity'] > 0:
				res = { 'name': center['name'], 'block_name':center['block_name'],'age_limit':session['min_age_limit'], 'vaccine_type':session['vaccine'] , 'date':session['date'],'available_capacity':session['available_capacity'] }
				output.append(res)
	return output
				
	
def call_api():
    print((ctime(time())))
    api = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=" + __district+ "&date="+ __date

    response = requests.get(api)

    if response.status_code == 200:
        print("Status 200 success")
        result = response.json()
        output = parse_json(result)
        if len(output) > 0:
            print("Vaccines available")
            print('\007')
        
            for center in output:

                print(center['name']) 
                print ("block:"+center['block_name'])
                print ("vaccine count:"+str(center['available_capacity']))
                print ("vaccines type:" + center['vaccine_type'])
                print (center['date'])
                print ("age_limit:"+ str(center['age_limit']))
                print ("---------------------------------------------------------") 
              
           

        else:
            
            print("Vaccines not available yet \n")

t = datetime.now()

if __name__ == '__main__':
    call_api()
    while True:
        delta = datetime.now()-t
        if delta.seconds >= minutes * 60:
            call_api()
            t = datetime.now()
