#!/usr/bin/python3

"""Polar exporter.

Usage:
  polar_export.py LOGIN PASSWORD START_DATE END_DATE [--custom=<filepath>]
  polar_export.py (-h | --help)

Arguments:
  LOGIN		Polar personal trainer login
  PASSWORD	Polar personal trainer password
  START_DATE	Start date: dd.MM.YYYY
  END_DATE	End date: dd.MM.YYYY

Options:
  -h --help     Show this screen.
  -c --custom=<filepath>   List for sports that is in Polar Personal Trainer but not in Polar Flow sports list.
"""

import sys
import re
import copy
import json
import requests
import bs4 as BeautifulSoup
from docopt import docopt

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

def get_export_status(html):
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	prop = soup.find_all('prop')
	return prop[0].text

def url_post(url, post):
	r = session.post(url, post)
	return r

def url_get(url, get):
	r = session.get(url, params=get)
	return r

def custom_sports_mapping(filepath):
	print("[+] Mapping custom sports")
	json_data = open(filepath).read()
	json_object = json.loads(json_data)
	for sport in json_object.items():
		id = sports_flow[sport[1]]
		sports_flow[sport[0]] = id

def load_sports_flow():
	print("[+] Loading sports flow list for JSON files")
	json_data = open(sports_flow_path).read()
	json_object = json.loads(json_data)
	for sport in json_object.items():
		sports_flow[sport[0]] = sport[1]

def retrieve_sports_ppt():
	print("[+] Retrieving sports list for Polar Personnel Trainer: ")
	url = url_list["sports_list"]
	reply = url_get(url, "")
	html =	reply.text
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	links = soup.find_all('a', href=re.compile("id="))

	n = 0

	for l in links:
		link = l['href'].partition("id=")[2]
		sports_ppt[l.text] = int(link)
		n += 1

	print("[+] Found " + str(n) + " sports")


def retrieve_activities(start_date, end_date):
	print("[+] Retrieving activities, status: ", end="")
	url = url_list["activities_list"]
	post = {"startDate": start_date, "endDate": end_date}
	reply = url_get(url, post)

	if (reply.status_code == 200):
		print("OK")
	else:
		print("KO")

	return reply.text

def login(email, password):
	print("[+] Logging in, status: ", end="")
	url = url_list["login"]
	post = {"email": email, "password": password, ".action": "login", "tz": "0"}
	reply = url_post(url, post)

	if (reply.status_code == 200):
		print("OK")
	else:
		print("KO")

def export_activity(sport, id):
	url = url_list["export_activity"]
	headers = {
		'X-Requested-With': 'XMLHttpRequest',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
		'Content-Type': 'text/xml',
		'Referer': 'https://www.polarpersonaltrainer.com/user/calendar/item/analyze.ftl?id=' + str(id)
	}
	request = '<request><object name="root"><prop name="exerciseId" type="string"><![CDATA[' + str(id) + ']]></prop><object name="sportMapping"><prop name="sportIdInPPT" type="string"><![CDATA[' + str(sports_ppt[sport]) + ']]></prop><prop name="sportIdInFlow" type="string"><![CDATA[' + str(sports_flow[sport]) + ']]></prop></object></object></request>'

	reply = session.post(url, request, headers=headers)

	status = get_export_status(reply.text)
	return status


def parse_activities(html):
	soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
	links = soup.find_all('a', href=re.compile("id="), text=check_sports)

	n = 0

	for l in links:
		link = l['href'].partition("id=")[2]
		n += 1

	print("[+] Found " + str(n) + " activities")

	for i in range(n):
		status = export_activity(sanitize_string(links[i].text), links[i]['href'].partition("id=")[2])
		print("[!] Exporting activity n°" + str(i + 1) + " : " + status)

def main(argv):
	global session

	session = requests.Session()

	login(argv['LOGIN'], argv['PASSWORD'])
	load_sports_flow()

	if (argv['--custom'] is not None):
		custom_sports_mapping(argv['--custom'])

	retrieve_sports_ppt()
	html = retrieve_activities(argv['START_DATE'], argv['END_DATE'])
	parse_activities(html)

if __name__ == "__main__":
	arguments = docopt(__doc__, version='Polar Exporter 1.0')
	main(arguments)
