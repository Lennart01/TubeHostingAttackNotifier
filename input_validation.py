import requests
from time import sleep
import json


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


# validates user input
def validate(email, password, webhook_url):
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
