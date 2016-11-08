#!/usr/bin/python3

import sys
import requests

def url_post(url, post):
	r = requests.post(url, post)
	return r.text

def retrieve_sessions(start_date, end_date):
	url = "https://www.polarpersonaltrainer.com/user/calendar/inc/listview.ftl"
	post = {"startDate": start_date, "endDate": end_date}
	reply = url_post(url, post)

def login(email, password):
	url = "https://www.polarpersonaltrainer.com/index.ftl"
	post = {"email": email, "password": password, ".action": "login", "tz": "0"}
	reply = url_post(url, post)
	print (reply)

def main(argv):
	if (len(argv) < 5):
		print("usage: " + argv[0] + " email password start_date end_date")
		sys.exit(1)

	login(argv[1], argv[2])
	retrieve_sessions(argv[3], argv[4])

if __name__ == "__main__":
	main(sys.argv)
