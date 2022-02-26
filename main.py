import datetime, sys
import getopt
from time import sleep
import requests
import json
import sys
import attack_handler
import input_validation
import os


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


def check_for_new_version():
    version = 2.0
    response = requests.get("https://raw.githubusercontent.com/Lennart01/TubeHostingAttackNotifier/master/version.txt")
    if float(response.text) > version:
        print("There is a new Version. Please update")


# stops script
def stop():
    sys.exit()


# controller function, executed until SIGTERM
def controller(email, password, webhook_url, ip_list, last_attack_time):
    # infinite loop
    while True:
        # preventing crash in case of an api error
        try:
            # checking for a new version
            check_for_new_version()
            # getting auth_token and service_id from api
            auth_token = get_auth_token(email, password)
            # check for attacks
            last_attack_time = attack_handler.check(auth_token, webhook_url, ip_list, last_attack_time)
        except Exception as e:
            print(e)
        # sleeping the process for 20 seconds
        sleep(20)


# getting required user input
email = None
password = None
webhook_url = None
os.system('cls' if os.name == 'nt' else 'clear')

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

# get ips to monitor from user
input_ongoing = True
ip_list = []
print("please enter the ips to monitor.\nOnly enter one ip at a time.\nSimply press enter once you are done")
while input_ongoing:
    user_input = input("ip: ")
    if len(user_input) == 0:
        input_ongoing = False
    else:
        ip_list.append(user_input)

# check user input
input_validation.validate(email, password, webhook_url)

# Initially getting last attack timestamp
auth_token = get_auth_token(email, password)
last_attack_time = attack_handler.time_stamp(auth_token, ip_list)

# clearing terminal
os.system('cls' if os.name == 'nt' else 'clear')

# notify user about successful start
print("script started successfully")

# executing controller
controller(email, password, webhook_url, ip_list, last_attack_time)
