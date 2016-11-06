Gmail notifier
---------------------------------
( https://github.com/himanshub16/gmail-notifier )

FEATURES: 
* It notifies you about any incoming email to your Google account.
* You don't need to save passwords. It works on OAuth2, using Gmail API.
* Secure.


SETTINGS file structure:
---------------------------------
{
    "client_secret_file": "client_secret.json",
    "update_interval": 600.00,
    "credentials_file": "credentials.json"
}

This is a defualt structure of settings file.

"client_secret_file" : This is the name of the file containing your client secret obtained from Google API Console.
"update_interval" : Interval at which to refresh your email (in seconds)
"credentials_file" : Filename where your email credentials are stored. 

A "client_secret_file" is already included. However, there are limits to number of requests.
API Key should not be included for security reasons. Follow "Step-1" at link below to obtain one for yourself.
https://developers.google.com/gmail/api/quickstart/python#step_1_turn_on_the_api_name


CREDENTIALS file structure:
----------------------------------
[
    {
        "emailId": "person1@gmail.com", 
        "identifier": "gmail", 
        "historyId": "######"
    }, 
    {
        "emailId": "person2@gmail.com", 
        "identifier": "gmail1", 
        "historyId": "######"
    }
]

The details are obvious, has to be in the required format. You need not worry about historyId.