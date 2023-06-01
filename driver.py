import requests
import uuid
import sys


url = "http://localhost:8888"
# url = "http://localhost:6005/webhooks/nlu"
UUID = str(uuid.uuid1())
# EMAIL = "ssms123@wl.com"

def send_to_rasa(msg):
    payload = {
        "sender": UUID,
        "message": msg,
        # "metadata": {},
    }

    headers = {
        "Content-Type": "application/json"
    }

    resp = requests.post(url + "/webhooks/rest/webhook", json=payload, headers=headers)
    # print("Bot responded:")
    for msg in resp.json():
        print("Bot:", msg, "\n")

    return resp

while True:
    print("\nplease enter your message:")
    msg = input()
    # if msg.lower() == "stop":
    #     break

    print()
    send_to_rasa(msg)
