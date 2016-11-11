#!/usr/bin/python 

import backend  
import json 
import sys
import httplib2
import threading 
import time 

import gi
gi.require_version("Gtk","3.0")
from gi.repository import Notify as notify

from apiclient import discovery
from apiclient import errors

CONFIG_FILE = "config.json"
CREDENTIALS_FILE = "credentials.json"
UPDATE_INTERVAL = 600.00
APPLICATION_ID = "Gmail Notifier"
APP_ICON = "icon.png"

notify.init(APPLICATION_ID)


class User:
    def __init__(self, email, username):
        self.username = username
        self.userId = email   
        self.credentials = None 
        self.http = None 
        self.service = None 
        self.labels = None 
        self.historyId = None 
        self.send_osd = False
        self.running_status = False 
        self.last_sync = time.time()
        self.next_sync = self.last_sync + UPDATE_INTERVAL

    def authorize(self):
        try:
            self.credentials = backend.get_credentials(self.userId, self.username)
            self.http = self.credentials.authorize(httplib2.Http())
            self.service = discovery.build("gmail", "v1", http = self.http)
        except HttpError:
            notify.Notification.new("Cannot connect to network", self.userId, APP_ICON).send()
        except Exception as e:
            print "Error occured", e



    def getProfile(self):
        profile = backend.GetProfile(service=self.service, user_id=self.userId)
        if not self.userId == profile["emailAddress"]:
            print "Email addresses don't match"
            return None 
        
        try:
            self.historyId = str(int(profile["historyId"]))
        except ValueError:
            self.historyId = "1" 
        print "Profile retrieved for : ", self.userId

    def sync(self):
        self.changes, self.historyId = backend.ListHistory( \
            service=self.service, user_id=self.userId, \
            start_history_id=self.historyId)

        for change in self.changes:
            self.send_osd = 'messagesAdded' in change 
            if self.send_osd: 
                break 

    def start_poll(self):
        th = threading.Thread(target=self.poll_osd_status)
        self.running_status = True 
        th.start()

    def stop_poll(self):
        self.running_status = False 
    
    def poll_osd_status(self):
        global UPDATE_INTERVAL, APP_ICON
        n = notify.Notification.new("You have a new email", self.userId, APP_ICON)

        while self.running_status:
            if time.time() < self.next_sync:
                time.sleep(1)
                continue 
            try:
                self.sync()
                self.last_sync = time.time()
                self.next_sync = self.last_sync + UPDATE_INTERVAL
                if self.send_osd:
                    n.show()
                    self.send_osd = False
                    self.updateCredentials()
            except Exception as e:
                self.last_sync = time.time()
                self.next_sync = time.time() + (UPDATE_INTERVAL / 2)
                print "Error occured", e

               
    def updateCredentials(self):       
        data = None
        with open(CREDENTIALS_FILE) as f:
            data = json.loads(f.read())
        
        if not data:
            return 

        index = 0
        while(index < len(data)):
            if data[index]["emailId"] == self.userId:
                break 
            index += 1
        
        if index >= len(data):
            data.append[ { \
                "emailId": self.userId, \
                "identifier": self.username, \
                "historyId": self.historyId  \
            } ]
        
        else:
            data[index]["historyId"] = self.historyId

        with open(CREDENTIALS_FILE, 'w') as f:
            f.write(json.dumps(data, indent=4))
            
                    


def getAccountList():
    account_list = None
    with open(CREDENTIALS_FILE) as f:
        account_list = json.loads(f.read())
    return account_list 

def getConfig():
    config = None 
    with open(CONFIG_FILE) as f:
        config = json.loads(f.read())
    return config 


def main():
    config = getConfig()
    if not len(config.keys()) < 4:
        print "Configuration broken"
        print "Cannot continue"
        sys.exit(-1)

    try:
        backend.CLIENT_SECRET_FILE = config["client_secret_file"]
        UPDATE_INTERVAL = config["update_interval"]
        CREDENTIALS_FILE = config["credentials_file"]
    except KeyError:
        print "Broken configuration.\n Please see README"
    
    accl = getAccountList()
    account_list = [ "me" ] if not accl else accl
    user_list = []  
    try:
        for account in account_list:
            newuser = User(account["emailId"], account['identifier'])
            newuser.historyId = account["historyId"]
            user_list.append(newuser)
    except KeyError:
        print "Improper details in credentials.json.\n Please see README."
        
    for user in user_list:
        user.authorize()
        if not user.getProfile():
            continue

    return user_list
