import datetime
import getopt
from time import sleep
import requests
import json
import sys
import attack_handler
import input_validation
import os
import sys


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
    version = 3.0
    response = requests.get("https://raw.githubusercontent.com/Lennart01/TubeHostingAttackNotifier/master/version.txt")
    if float(response.text) > version:
        print("There is a new Version. Please update")



# controller function, executed until SIGTERM
def controller(email, password, webhook_url, ip_list, last_attack_time):
    # infinite loop
    while True:
        # preventing crash in case of an api error
        try:
            # checking for a new version
            check_for_new_version()
            # get auth_token from api
            auth_token = get_auth_token(email, password)
            # check for attacks
            last_attack_time = attack_handler.check(auth_token, webhook_url, ip_list, last_attack_time)
        except Exception as e:
            print(e)
        # sleeping the process for 20 seconds
        sleep(20)


# set docker environment variables
email = os.getenv("mail", None)
password = os.getenv("passwd", None)
webhook_url = os.getenv("url", None)
ip_list = os.getenv("ips", None)
if ip_list is not None:
    ip_list = ip_list.split(",")
os.system('cls' if os.name == 'nt' else 'clear')

# if there is no passed cli arg, get interactive user input
if email is None:
    email = input("Enter your email:")
if password is None:
    password = input("Enter your password:")
if webhook_url is None:
    webhook_url = input("Enter your Webhook:")
if ip_list is None:
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
