import requests


# send found attack to the webhook
def send(webhook_url, message):
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
                        "value": str(message['avgPacketSize'])
                    },
                    {
                        "name": "type",
                        "value": str(message['type'])
                    },
                    {
                        "name": "packets per second",
                        "value": str(message['pps'])
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
