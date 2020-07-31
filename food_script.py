import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
from googleapiclient import discovery
import datetime
import requests
import ast
import json
from decouple import config, Csv

scope = ['https://www.googleapis.com/auth/spreadsheets']

foodalert = {
  "type": "service_account",
  "project_id": config('GOOGLE_PROJECT_ID'),
  "private_key_id": config('GOOGLE_PRIVATE_ID'),
  "private_key": config('GOOGLE_PRIVATE_KEY'),
  "client_email": config('GOOGLE_EMAIL'),
  "client_id": config('CLIENT_ID'),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": config('CERT_URL')
}
foodalert["private_key"] = foodalert["private_key"].replace("\\n","\n") #by default python decouple escapes \n to \\n, doesnt work for verification purposes so put back to \n
creds = ServiceAccountCredentials.from_json_keyfile_dict(foodalert)

service = discovery.build('sheets','v4',credentials=creds)

spread_id = config('SPREAD_ID')

range_ = 'A1:B1000'

request = service.spreadsheets().values().get(spreadsheetId=spread_id, range=range_)
response = request.execute()

foods = response['values']
emails = config('EMAIL_LIST', cast=Csv())
notify_time = datetime.timedelta(3)
day = datetime.timedelta(1)
current_date = datetime.datetime.now()
#week = datetime.timedelta(7)



def time(day,month,year=2020):
	return datetime.datetime(year,month,day)

def send_email(email,text):
    return requests.post( #POST following details to described url
        config('MAILGUN_EMAIL'), #url to post to
        auth=("api", config('MAIL_API_KEY')), #API key for authentication
        data={"from": config('SENDER_EMAIL'), #email details
              "to": email,
              "subject": "food update",
              "text": text})
text = ''
today = ''
oneDay = ''
Days = ''
OFD = '' #OUT OF DATE - NOT CURRENTLY IMPLEMENTED DUE TO LACK OF USER DEMAND.
count = 0

for item in foods:
	count += 1
	if len(item) > 3  or len(item) < 2:
		continue
	item_name = item[0]
	try:
		date = ast.literal_eval(item[1])
	except(SyntaxError):
	    continue
	if len(date) == 2:
		try:
			expire_date = time(date[0],date[1])
		except(ValueError):
			continue
	elif len(date) == 3:
		try:
			expire_date = time(date[0],date[1],date[2])
		except(ValueError):
			continue
	if (expire_date + day*2) < current_date:
		values = [["",""]]
		body = { 'values':values }
		rangex = 'A' + str(count) + ':B' + str(count)
		value_option = 'USER_ENTERED'
		request = service.spreadsheets().values().update(spreadsheetId=spread_id, range=rangex, valueInputOption=value_option,body=body)
		result = request.execute()
		print('removed ' + item_name + 'from the spreadsheet, with date of ' + expire_date.strftime("%A"))
		continue
	#elif expire_date > current_date and (expire_date - day) < current_date:
	#	append = 'The ' + item_name + ' may have expired yesterday. \n'
	#	OFD += append
	#	continue 
	elif expire_date < current_date and (expire_date + day) > (current_date):
		append = "The " + item_name + ' will go out of date today! \n'
		today += append
		continue
	elif (expire_date - current_date) < notify_time and expire_date > current_date:
			if (expire_date - current_date).days + 1 == 1:
				days =  str((expire_date - current_date).days + 1) + " day"
				append = "The " + item_name + " will go out of date in " + days + ", on " + expire_date.strftime("%A") +'\n'
				oneDay += append
			else:
				days =  str((expire_date - current_date).days + 1) + " days"
				append = "The " + item_name + " will go out of date in " + days + ", on " + expire_date.strftime("%A") +'\n'
				Days += append
	else:
		continue
text = today + oneDay + Days

for email in emails:
	send_email(email,text)
	print('email sent to ' + email)
