#!/usr/bin/python 

# from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client import tools
from oauth2client.file import Storage

# defining scopes for API 
SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Gmail Notifier"

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None

def get_credentials(email, username = "me"):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   username+".json")

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        flow.params["user_id"] = email
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    print "Message snippet: %s" % message['snippet']

    return message
  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def ListHistory(service, user_id, start_history_id='1'):
  """List History of all changes to the user's mailbox.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    start_history_id: Only return Histories at or after start_history_id.

  Returns:
    A list of mailbox changes that occurred after the start_history_id.
  """
  try:
    history = (service.users().history().list(userId=user_id,
                                              startHistoryId=start_history_id)
               .execute())
    new_history_id = history['historyId']
    changes = history['history'] if 'history' in history else []
    while 'nextPageToken' in history:
      page_token = history['nextPageToken']
      history = (service.users().history().list(userId=user_id,
                                        startHistoryId=start_history_id,
                                        pageToken=page_token).execute())
      changes.extend(history['history'])
      new_history_id = history['historyId']

    return (changes, new_history_id)
  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def GetProfile(service, user_id):
    try:
        profile = service.users().getProfile(userId=user_id).execute()
    except Exception as e:
        print "An error occured: %s" % e 
    
    return profile

