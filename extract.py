#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3

import sys
import re
import requests
import bs4 as BeautifulSoup

sports_flow = {"Swimming": 23, "Running": 1, "Motocross": 54, "Renf Muscu": 34, "Cycling": 2}
sports_ppt = {"Swimming": 10650934, "Running": 10650925, "Motocross": 10658605, "Renf Muscu": 10731409, "Cycling": 10650928}

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

def export_activity(sport, id):
	url = "https://www.polarpersonaltrainer.com/user/calendar/item/multisportExercise_ajaxTransferExerciseToFlow.xml"
	headers = {
		'X-Requested-With': 'XMLHttpRequest',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
		'Content-Type': 'text/xml',
		'Referer': 'https://www.polarpersonaltrainer.com/user/calendar/item/analyze.ftl?id=' + str(id)
	}
	request = '<request><object name="root"><prop name="exerciseId" type="string"><![CDATA[' + str(id) + ']]></prop><object name="sportMapping"><prop name="sportIdInPPT" type="string"><![CDATA[' + str(sports_ppt[sport]) + ']]></prop><prop name="sportIdInFlow" type="string"><![CDATA[' + str(sports_flow[sport]) + ']]></prop></object></object></request>'

	reply = session.post(url, request, headers=headers)

	print(reply.status_code)


def parse_activities(html):
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	inputs = soup.find_all('input', attrs={"name": "calendarItemName"})
	links = soup.find_all('a', href=re.compile("id="))

	n = 0

	for i in inputs:
		sport = i['value']
		n += 1

	print("Found " + str(n) + " activities")

	n = 0

	for l in links:
		link = l['href'].partition("id=")[2];
		n += 1

	print("Found " + str(n) + " activities links")

	for i in range(n):
		export_activity(inputs[i]['value'], links[i]['href'].partition("id=")[2])

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
