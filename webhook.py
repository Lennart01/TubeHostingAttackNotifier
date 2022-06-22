import requests
import locale

#convert protocol id to protocol name (tcp, udp, icmp, etc.), if there is no match return id
def prtIdToPrt(protocolID):

    if protocolID == 1:
        return "ICMP"
    elif protocolID == 6:
        return "TCP"
    elif protocolID == 17:
        return "UDP"
    else:
        return str(protocolID) + " (id)"

#set decimal/thousand seperator for numbers (1000 to 1.000) following the local "standard"
def decSep(rawNumber):
    return f'{int(rawNumber):,}'.replace(",",locale.localeconv()["decimal_point"])

# send found attack to the webhook
def send(webhook_url, message):
    # prevent empy values because discord doesnt accept them
    for i in message:
        if message.get(i) == "":
            message[i] = "Null"

    # build the bandwidth result
    bandwidth=message['traffic']
    if bandwidth<10000:
        bandwidth = decSep(str(message['traffic']))+" Mbit/s"
    else:
        bandwidth = "~"+decSep(str(round(message['traffic']/1000)))+" Gbit/s"

    data = {
        "content": "",
        "embeds": [
            {
                "title": "New attack detected",
                "description": str(message['id']),
                "url": "https://cp.tube-hosting.com",
                "color": 10751,
                "fields": [
                    {
                        "name": "⠀",
                        "value": "> *IP under attack*:\n"
                                 "> **"+str(message['ip'])+"**\n⠀",
                        "inline": "true"
                    },
                    {
                        "name": "⠀",
                        "value": "> *time:*\n"
                                 "> **"+(message['time'].replace("T", " "))+"**\n⠀",
                        "inline": "true"
                    },
                    {
                        "name": "⠀",
                        "value": "> *type:*\n"
                                 "> **"+str(message['type'])+"**\n⠀",
                        "inline": "true"
                    },
                    {
                        "name": "⠀",
                        "value": "> *initital bandwith*:\n"
                                 "> **"+bandwidth+"**\n⠀",
                        "inline": "true"
                    },
                    {
                        "name": "⠀",
                        "value": "> *Initial Packets per second:*\n"
                                 "> **" + decSep(str(message['pps'])) + " Packets/s**\n⠀",
                    "inline": "true"
                    },
                    {
                        "name": "⠀",
                        "value": "> *avg. packet size:*\n"
                                 "> **"+str(message['avgPacketSize'])+"**\n⠀",
                        "inline": "true"
                    }
                ],
                "footer": {
                    "text": "tubehosting ddos alert made with <3 by Lennart01"
                },
                "timestamp": (message['time'].replace("T", " ")[:-4])
            }
        ],
        "username": "DDoS-Alert",
        "avatar_url": "https://resources.tube-hosting.com/logo/app_icon.png"
    }

    # JSON to send via webhook

    # sending JSON to webhook
    requests.post(webhook_url, json=data)

    # Building sample jSON to send via webhook
    samplesFirst = ""
    samplesSecond = ""
    sampleCount = len(message['samples'])
    #get first half of samples
    for i in range(round(sampleCount/2)):
        samplesFirst += "> src. IP: **" + str(message['samples'][i]['srcIP']) + "** ⠀|⠀" \
                       "target port: **" + str(message['samples'][i]['dstPort'])+"** ⠀|⠀" \
                       "protocol: **" + prtIdToPrt((message['samples'][i]['ipProtocol'])) + "**\n"

    #get second half of samples
    for i in range(round(sampleCount / 2)):
        j = i + round(sampleCount / 2)
        samplesSecond += "> src. IP: **" + str(message['samples'][j]['srcIP']) + "** ⠀|⠀" \
                       "target port: **" + str(message['samples'][j]['dstPort'])+"** ⠀|⠀" \
                       "protocol: **" + prtIdToPrt((message['samples'][j]['ipProtocol'])) + "**\n"

    data = {
      "content": "",
      "embeds": [
          {
              "title": "DDos Samples",
              "color": 10751,
              "fields": [
                  {
                      "name": "⠀",
                      "value": samplesFirst
                  },
                  {
                      "name": "⠀",
                      "value": samplesSecond
                  }
              ],
              "footer": {
                  "text": "tubehosting ddos alert made with <3 by Lennart01"
              },
              "timestamp": (message['time'].replace("T", " ")[:-4])
          }
      ],
      "username": "DDoS-Alert",
      "avatar_url": "https://resources.tube-hosting.com/logo/app_icon.png"
    }

    # sending JSON to webhook
    requests.post(webhook_url, json=data)
