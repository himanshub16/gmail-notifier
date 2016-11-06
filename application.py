# Derived from :
# http://candidtim.github.io/appindicator/2014/09/13/ubuntu-appindicator-step-by-step.html

import os
import signal
import json
import time 
import webbrowser

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

import notifier 
ICON_FILE = os.path.abspath('icon.png')

APPINDICATOR_ID = 'Gmail notifier'
userlist = [] 

def main():
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, ICON_FILE , appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    notify.init(APPINDICATOR_ID)
    global userlist 
    userlist = notifier.main()
    for user in userlist:
        user.start_poll()
    gtk.main()

def build_menu():
    menu = gtk.Menu()
    refresh_all = gtk.MenuItem('Refresh')
    refresh_all.connect('activate', refresh)
    menu.append(refresh_all)
    settings = gtk.MenuItem('Settings')
    settings.connect('activate', show_settings)
    menu.append(settings)
    accounts = gtk.MenuItem('Manage accounts')
    accounts.connect('activate', show_accounts)
    menu.append(accounts)
    help = gtk.MenuItem('Help')
    help.connect('activate', show_help)
    menu.append(help)
    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu

def show_settings(_):
    webbrowser.open(notifier.CONFIG_FILE)

def show_accounts(_):
    webbrowser.open(notifier.CREDENTIALS_FILE)

def show_help(_):
    webbrowser.open('README.txt')

def refresh(_):
    for user in userlist:
        user.next_sync = time.time()

def quit(_):
    notify.uninit()
    for user in userlist:
        user.stop_poll()
    gtk.main_quit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()