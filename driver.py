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
        # "metadata": {
        #     "job_id": "2"
        # },
    }

    headers = {
        "Content-Type": "application/json"
    }
    print(json.dumps(payload, indent=4))

    resp = requests.post(url + "/webhooks/rest/webhook", json=payload, headers=headers)
    # print("Bot responded:")
    for msg in resp.json():
        if msg.get("custom", {}).get("ui_component") == "select_job":
            log_jobs = []
            for j in msg.get("custom", {}).get("jobs"):
                log_jobs.append({key: value for key, value in j.items() if key in ["requisitionId_", "title_"]})
            msg["custom"]["jobs"] = log_jobs
        print("Bot:\n", msg, "\n")

    return resp


def upload_resume():
    api_url = url + "/api/upload_resume"
    files=[
        ('resume',('IT Specialist_Resume.docx',open('/home/dhruv/Downloads/Resume Samples/IT Specialist_Resume.docx','rb'),'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
    ]
    payload = {
        "sender": UUID,
        "metadata": json.dumps({
            "job_id": "2"
        }),
    }
    response = requests.request("POST", api_url, data=payload, files=files)
    print(response.status_code, response.text)
    resp = response.json()
    print(json.dumps(resp, indent=4))
    return resp["candidate_id"]


def send_resume_message():
    candidate_id = upload_resume()
    # candidate_id = "1234"
    send_to_rasa('/input_resume_upload_data{"candidate_id": "' + candidate_id + '"}')


def explore_jobs(is_upload_resume=False, cancel=False):
    send_to_rasa("/greet")
    send_to_rasa("/explore_jobs")
    if is_upload_resume:
        send_to_rasa("/affirm")
        if cancel:
            send_to_rasa("/deny")
            # select answer questions path
            send_to_rasa("/deny")
        else:
            send_resume_message()
    else:
        send_to_rasa("/deny")
    send_to_rasa('/input_job_title{"job_title": "Java Developer"}')
    send_to_rasa('/input_job_location{"job_location": "CA"}')
    send_to_rasa('/input_select_job{"select_job": "227842"}')
    # if resume was cancelled initially, upload it again
    if not is_upload_resume or cancel:
        send_resume_message()
    send_to_rasa("John Doe")
    send_to_rasa("me@gmail.com")
    send_to_rasa("+1 1234567890")
    send_to_rasa("01/01/1960")
    

# send_to_rasa("/job_screening")
# send_to_rasa("/greet")

# explore_jobs(is_upload_resume=True)
explore_jobs(is_upload_resume=True, cancel=True)
# explore_jobs(is_upload_resume=False)

while True:
    print("\nplease enter your message:")
    msg = input()
    # if msg.lower() == "stop":
    #     break

    print()
    send_to_rasa(msg)
