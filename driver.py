import requests
import uuid
import sys
import json

# Localhost
url = "http://localhost:8000"
# Localhost docker
# url = "http://localhost:8888"
# SERVER
# url = "http://52.40.250.118:8888"
# url = "http://localhost:6005/webhooks/nlu"
UUID = str(uuid.uuid1())

def send_to_rasa(msg):
    payload = {
        "sender": UUID,
        "message": msg,
        "metadata": {
            "job_id": "2"
        },
    }

    headers = {
        "Content-Type": "application/json"
    }
    print(json.dumps(payload, indent=4))

    resp = requests.post(url + "/webhooks/rest/webhook", json=payload, headers=headers)
    # print("Bot responded:")
    for msg in resp.json():
        print("Bot:", msg, "\n")

    return resp

send_to_rasa("/greet")

while True:
    print("\nplease enter your message:")
    msg = input()
    # if msg.lower() == "stop":
    #     break

    print()
    send_to_rasa(msg)
