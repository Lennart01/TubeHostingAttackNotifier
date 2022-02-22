import datetime, sys
import getopt
from time import sleep
import requests
import json
import sys
import attack_handler

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
    response = requests.get("https://api.tube-hosting.com/servicegroups/currents?primaryOnly=false", headers=header)
    # converting JSON
    response_list = json.loads(response.text)
    # creating list to hold all service IDs
    serviceID_list = [None] * 10
    # grabbing all service ids of the user and storing them
    k = 0
    for i in range(len(response_list)):
        j = 1
        while j < len(response_list[i]['groupData']['services']):
            serviceID_list[k] = response_list[i]['groupData']['services'][j]['dataId']
            k = k + 1
            j = j + 1
    # returning serviceID_list
    return serviceID_list


def check_for_new_version():
    version = 1.0
    response = requests.get("https://raw.githubusercontent.com/Lennart01/TubeHostingAttackNotifier/master/version.txt")
    if float(response.text) > version:
        print("There is a new Version. Please update")


# stops script
def stop():
    sys.exit()


# validates user input
def input_validation(email, password, webhook_url):
    # validates login data
    try:
        get_auth_token(email, password)
    except:
        print("Wrong login data")
        print("Shutting down")
        sleep(5)
        stop()
    # testing the webhook
    data = {
        "content": "",
        "embeds": [
            {
                "title": "This is a test Message",
                "description": "Your webhook works",
                "color": 10751,

                "footer": {
                    "text": "tubehosting ddos alert\nmade with <3 by Lennart01"
                }
            }
        ],
        "username": "DDoS-Alert",
        "avatar_url": "https://resources.tube-hosting.com/logo/app_icon.png"
    }
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:
            raise ValueError('Wrong webhook')
    except:
        print("Webhook is incorrect")
        print("Shutting down")
        sleep(5)
        stop()


# controller function, executed until SIGTERM
def controller(email, password, webhook_url, last_attack_time):
    # infinite loop
    while True:
        # preventing crash in case of an api error
        try:
            # checking for a new version
            check_for_new_version()
            # getting auth_token and service_id from api
            auth_token = get_auth_token(email, password)
            service_id = get_service_id(auth_token)
            # check for attacks
            last_attack_time = attack_handler.check(auth_token, webhook_url, service_id, last_attack_time)
        except Exception as e:
            print(e)
        # sleeping the process for 20 seconds
        sleep(20)


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

# if there is no passed cli arg, get interactive user input
if email == None:
    email = input("Enter your email:")
if password == None:
    password = input("Enter your password:")
if webhook_url == None:
    webhook_url = input("Enter your Webhook:")

# check user input
input_validation(email, password, webhook_url)

# Initially getting last attack timestamp
auth_token = get_auth_token(email, password)
last_attack_time = attack_handler.time_stamp(auth_token, get_service_id(auth_token))

# executing controller
controller(email, password, webhook_url, last_attack_time)
