import requests
import json
import webhook


# initally saves the timestamp of the last attack
def time_stamp(auth_token, serviceID_list):
    # creating header for authentication
    header = {"Authorization": "Bearer " + auth_token}
    last_attack_time = [None] * 10
    # iterating over every serviceID and saving the last attack
    for i in range(len(serviceID_list)):
        service_id = serviceID_list[i]
        if service_id is not None:
            url = "https://api.tube-hosting.com/ipbundles/" + str(service_id) + "/ddos/incidents"
            response = requests.get(url, headers=header)
            # checking if array is empty to prevent JSON error
            if len(response.text) >= 3:
                # convert JSON
                attack_list = json.loads(response.text)
                j = len(attack_list) - 1
                last_attack_time[i] = float(attack_list[j]['time'].translate({ord(i): None for i in '-:TZ'}))
            else:
                last_attack_time[i] = None
    return last_attack_time


# grab latest attacks from api
def check(auth_token, webhook_url, serviceID_list, last_attack_time):
    # creating header for authentication
    header = {"Authorization": "Bearer " + auth_token}
    # iterating over every serviceID and checking for attacks
    for i in range(len(serviceID_list)):
        service_id = serviceID_list[i]
        if service_id is not None:
            url = "https://api.tube-hosting.com/ipbundles/" + str(service_id) + "/ddos/incidents"
            response = requests.get(url, headers=header)
            # checking if array is empty to prevent JSON error
            if len(response.text) >= 3:
                # convert JSON
                attack_list = json.loads(response.text)
                # defining last attack to check wether there has been a newer attack
                last_attack = last_attack_time[i]
                # defining latest found attack
                j = len(attack_list) - 1
                last_found_attack = attack_list[j]
                # removing unwanted chars and casting to float. Comparing it to the last timestamp.
                if (last_attack is None and last_found_attack is not None) or float(last_found_attack['time'].translate({ord(i): None for i in '-:TZ'})) > float(last_attack):
                    print(last_found_attack)
                    # sending found attack using webhook method
                    webhook.send(webhook_url, last_found_attack)
                    # setting new timestamp
                    last_attack_time[i] = float(last_found_attack['time'].translate({ord(i): None for i in '-:TZ'}))
    return last_attack_time
