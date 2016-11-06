from __future__ import print_function
import httplib2
import os
from pprint import pprint
import base64

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None


SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Gmail API Python Quickstart"

def get_credentials():
	home_dir = os.path.expanduser("~")
	credentials_dir = os.path.join(home_dir, ".credentials")
	if not os.path.exists(credentials_dir):
		os.makedirs(credentials_dir)
	credential_path = os.path.join(credentials_dir, "gmail-python-quickstart.json")
	store = Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = "Gmail notifier"
		if flags:
			credentials = tools.run_flow(flow, store, flags)
		else:
			credentials = tools.run(flow, store)
		print("Storing credentials to : " + credential_path)
	return credentials

def main():
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build("gmail", "v1", http = http)

	results = service.users().labels().list(userId="me").execute()
	labels = results.get("labels", [])

	if not labels:
		print ("No labels found")
	else:
		print ("Labels : ")
		for label in labels:
			print (label["name"])


	print("Listing inbox : ")
	results = service.users().messages().list(userId="me", labelIds="INBOX", maxResults="10").execute()
	message = results["messages"][0]
	import json
	results = service.users().messages().get(userId="me", id=message["id"], format="full").execute()
	message = results["snippet"]
	print(message)



if __name__=="__main__":
	main()
