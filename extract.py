#!/usr/bin/python3

import sys
import re
import json
import requests
import bs4 as BeautifulSoup

sports_flow_path = "sports_flow.json"

url_list = {
	"login":"https://www.polarpersonaltrainer.com/index.ftl",
	"sports_list": "https://www.polarpersonaltrainer.com/user/settings/sports.ftl",
	"activities_list": "https://www.polarpersonaltrainer.com/user/calendar/inc/listview.ftl",
	"export_activity":"https://www.polarpersonaltrainer.com/user/calendar/item/multisportExercise_ajaxTransferExerciseToFlow.xml",
}

sports_flow = {}
sports_ppt = {}

def sanitize_string(string):
	return string.replace('\n', '').replace('\r', '').replace('\t', '').strip()

def check_sports(text):
	if sanitize_string(text) in ["Swimming", "Running", "Motocross", "Renf Muscu", "Cycling"]:
		return True

	return False

def url_post(url, post):
	r = session.post(url, post)
	return r

def url_get(url, get):
	r = session.get(url, params=get)
	return r

def load_sports_flow():
	print("Loading sports flow list for JSON files")
	json_data = open(sports_flow_path).read()
	json_object = json.loads(json_data)
	sports_flow = json_object

def retrieve_sports_ppt():
	print("Retrieving sports list for Polar Personnel Trainer: ")
	url = url_list["sports_list"];
	reply = url_get(url, "");
	html =	reply.text;
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	links = soup.find_all('a', href=re.compile("id="))

	n = 0

	for l in links:
		link = l['href'].partition("id=")[2];
		sports_ppt[l.text] = int(link);
		n += 1

	print("Found " + str(n) + " sports")


def retrieve_activities(start_date, end_date):
	print("Retrieving activities, status: ")
	url = url_list["activities_list"];
	post = {"startDate": start_date, "endDate": end_date}
	reply = url_get(url, post)
	print(reply.status_code)
	return reply.text

def login(email, password):
	print("Logging in, status: ")
	url = url_list["login"];
	post = {"email": email, "password": password, ".action": "login", "tz": "0"}
	reply = url_post(url, post)
	print(reply.status_code)

def export_activity(sport, id):
	url = url_list["export_activity"];
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
	links = soup.find_all('a', href=re.compile("id="), text=check_sports)

	n = 0

	for l in links:
		link = l['href'].partition("id=")[2];
		n += 1

	print("Found " + str(n) + " activities")

	for i in range(n):
		export_activity(sanitize_string(links[i].text), links[i]['href'].partition("id=")[2])

def main(argv):
	global session

	if (len(argv) < 5):
		print("usage: " + argv[0] + " email password start_date end_date")
		sys.exit(1)

	session = requests.Session()

	login(argv[1], argv[2])
	load_sports_flow()

	retrieve_sports_ppt()
	html = retrieve_activities(argv[3], argv[4])
	parse_activities(html)

if __name__ == "__main__":
	main(sys.argv)
