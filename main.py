import datetime, sys
import getopt
from time import sleep
import requests
import json
from datetime import datetime


# send found attack to the webhook
def send_to_webhook(webhook_url, message):
    # prevent empy values because discord doesnt accept them
    for i in message:
        if message.get(i) == "":
            message[i] = "Null"

    # JSON to send via webhook
    data = {
        "content": "",
        "embeds": [
            {
                "title": "New attack detected",
                "description": "Mitigation was initiated",
                "url": "https://cp.tube-hosting.com",
                "color": 10751,
                "fields": [
                    {
                        "name": "time (UTC)",
                        "value": (message['time'].replace("T", " "))
                    },
                    {
                        "name": "ip under attack",
                        "value": str(message['ip'])
                    },
                    {
                        "name": "packet count",
                        "value": str(message['packets'])
                    },
                    {
                        "name": "traffic",
                        "value": str(message['traffic'])
                    },
                    {
                        "name": "average packet size",
                        "value": str(message['avg_pktsize'])
                    },
                    {
                        "name": "type",
                        "value": str(message['type'])
                    },
                    {
                        "name": "analyzer",
                        "value": str(message['analyzer'])
                    },
                    {
                        "name": "attack id",
                        "value": str(message['id'])
                    }
                ],
                "footer": {
                    "text": "tubehosting ddos alert\nmade with <3 by Lennart01"
                }
            }
        ],
        "username": "DDoS-Alert",
        "avatar_url": "https://resources.tube-hosting.com/logo/app_icon.png"
    }

    # sending JSON to webhook
    requests.post(webhook_url, json=data)


# getting the tubehosting auth_token via /login
def get_auth_token(email, password):
    post_data = {
        "mail": email,
        "password": password
    }
    response = requests.post("https://api.tube-hosting.com/login", json=post_data)
    # converting JSON
    response_list = json.loads(response.text)
    # returning token
    return response_list['token']


# getting the service_id via current service groups
def get_service_id(auth_token):
    # creating header for authentication
    header = {"Authorization": "Bearer " + auth_token}
    response = requests.get("https://api.tube-hosting.com/servicegroups/currents", headers=header)
    # converting JSON
    response_list = json.loads(response.text)
    # returning service_id
    return response_list[0]['groupData']['services'][1]['id']


# grab latest attacks from api
def check_for_new_attacks(auth_token, webhook_url, service_id):
    # creating header for authentication
    header = {"Authorization": "Bearer " + auth_token}
    # creating url with correct service_id
    url = "https://api.tube-hosting.com/ipbundles/" + str(service_id) + "/ddos/incidents"
    response = requests.get(url, headers=header)
    # convert JSON
    attack_list = json.loads(response.text)
    i = 0
    # defining interval and subtracting exec time and wait time from it
    interval_to_check = int(datetime.utcnow().strftime("%Y%m%d%H%M%S")) - 23
    # iterating over list of all attacks
    for i in range(len(attack_list)):
        # removing unwanted chars and casting to int. Comparing it to specified interval
        if int((attack_list[i]['time'].translate({ord(i): None for i in '-:T'}))) > interval_to_check:
            print(attack_list[i])
            # sending found attack using webhook method
            send_to_webhook(webhook_url, attack_list[i])


# recursive controller function.
def controller(email, password, webhook_url):
    # getting auth_token and service_id from api
    auth_token = get_auth_token(email, password)
    service_id = get_service_id(auth_token)
    # check for attacks
    check_for_new_attacks(auth_token, webhook_url, service_id)
    # sleeping the process for 20 seconds
    sleep(20)
    # recursive call
    controller(email, password, webhook_url)

# getting required user input
email = None
password = None
webhook_url = None

argv = sys.argv[1:]
  
opts, args = getopt.getopt(argv, "m:p:u:")
  
for opt, arg in opts:
    if opt in ['-m']:
        email = arg
    elif opt in ['-p']:
        password = arg
    elif opt in ['-u']:
        webhook_url = arg

#if there is no passed cli arg, get interactive user input
if email == None:
    email = input("Enter your email:")
if password == None:
    password = input("Enter your password:")
if webhook_url == None:    
    webhook_url = input("Enter your Webhook:")
# executing recursive controller
controller(email, password, webhook_url)
