#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3

import sys
import requests
import bs4 as BeautifulSoup

def url_post(url, post):
	r = session.post(url, post)
	return r

def url_get(url, get):
	r = session.get(url, params=get)
	return r

def retrieve_activities(start_date, end_date):
	print("Retrieve activities, status: ")
	url = "https://www.polarpersonaltrainer.com/user/calendar/inc/listview.ftl"
	post = {"startDate": start_date, "endDate": end_date}
	reply = url_get(url, post)
	print(reply.status_code)
	return reply.text

def login(email, password):
	print("Login, status: ")
	url = "https://www.polarpersonaltrainer.com/index.ftl"
	post = {"email": email, "password": password, ".action": "login", "tz": "0"}
	reply = url_post(url, post)
	print(reply.status_code)

def parse_activities(html):
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	print(soup.find_all('input', attrs={"name": "calendarItemName"}))

def main(argv):
	global session

	if (len(argv) < 5):
		print("usage: " + argv[0] + " email password start_date end_date")
		sys.exit(1)

	session = requests.Session()

	login(argv[1], argv[2])
	html = retrieve_activities(argv[3], argv[4])
	parse_activities(html)

if __name__ == "__main__":
	main(sys.argv)
