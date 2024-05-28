import requests
import uuid
import sys
import json

# Localhost
url = "http://localhost:8000"
# Localhost docker
# url = "http://localhost:8888"
# SERVER
# https://chatbot.curately.ai
# url = "http://52.40.250.118:8888"

# https://chatbot1.curately.ai/
# url = "http://54.190.26.156:8888"
# url = "http://localhost:6005/webhooks/nlu"
UUID = str(uuid.uuid1())
# UUID = "a5f0f40e-e432-11ee-ac7b-efd575c2545b"
chatbot_type = "1"
user_id = "39638"
# user_id = None

resume_1 = ("Resume Samples/Dave Paterson.docx", 'Dave Paterson.docx')
resume_2 = ("Resume Samples/IT Specialist_Resume.docx", 'IT Specialist_Resume.docx')

def send_to_rasa(usr_msg):
    payload = {
        "sender": UUID,
        "message": usr_msg,
        "metadata": {
            "job_id": "1",
            "chatbot_type": chatbot_type,
            "job_location": 'GA',
            "ip_address": "1.1.1.2",
            "client_id": "2",
            "user_id": user_id
        },
    }

    headers = {
        "Content-Type": "application/json"
    }
    print(json.dumps(payload, indent=4))

    resp = requests.post(url + "/webhooks/rest/webhook", json=payload, headers=headers)
    # print("Bot responded:", resp.json())
    for msg in resp.json():
        if msg.get("custom", {}).get("ui_component") == "select_job":
            log_jobs = []
            for j in msg.get("custom", {}).get("jobs"):
                log_jobs.append({key: value for key, value in j.items() if key in ["jobId", "jobTitle"]})
            msg["custom"]["jobs"] = log_jobs
        print("Bot:\n", msg, "\n")

    return resp


def upload_resume(resume):
    api_url = url + "/api/upload_resume"
    resume_path = "/home/dhruv/Downloads/" + resume[0]
    files=[
        ('resume',(resume[1], open(resume_path,'rb'),'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
    ]
    payload = {
        "sender": UUID,
        "metadata": json.dumps({
            "job_id": "1",
            "chatbot_type": chatbot_type,
            "job_location": 'GA',
            "ip_address": "1.1.1.2",
            "client_id": "2",
            "user_id": user_id
        }),
    }
    response = requests.request("POST", api_url, data=payload, files=files)
    print(response.status_code, response.text)
    resp = response.json()
    print(json.dumps(resp, indent=4))
    return str(resp["userId"])


def ask_a_question():
    send_to_rasa("/ask_a_question")
    for qid in range(1, 6):
        msg = '/input_user_question{"user_question": "' + str(qid) + '"}'
        send_to_rasa(msg)

def send_resume_message(resume):
    user_id = upload_resume(resume)
    # user_id = "1234"
    send_to_rasa('/input_resume_upload_data{"user_id": "' + user_id + '"}')


def screening_questions():
    send_to_rasa("John Doe")
    send_to_rasa("me@gmail.com")
    send_to_rasa("+1 1234567890")
    send_to_rasa("01/01/1960")

def answer_job_title():
    send_to_rasa('/input_job_title{"job_title": "Python Developer"}')

def answer_job_location():
    send_to_rasa('/input_job_location{"job_location": "GA"}')

def send_job():
    send_to_rasa('/input_select_job{"select_job": "1495"}')

def custom_msgs():
    msgs = [
        '/input_select_job{"select_job": "149577777"}',
        '1234567890',
        # 'working freelance',
        # 'available soon',
        # 'freelancer',
        # 'remote',

        "10010001,10010002",
        "10011001",
        "10019005",
        "10013001,10013003",
        "10019001",
        "1",
        "2",

        # greet
        # "/explore_jobs",
        # "/deny",
        # "/affirm"
    ]
    for msg in msgs:
        send_to_rasa(msg)

def explore_jobs(is_upload_resume=False, cancel=False, refine_job_search=None, start_new="ignore", resume=resume_1):
    send_to_rasa("/explore_jobs")
    if start_new in ["ignore", "true"]:
        if start_new == "true":
            # start new search
            send_to_rasa("/deny")
        # normal explore jobs, either first time or new search
        if chatbot_type == "1":
            if is_upload_resume:
                send_to_rasa("/affirm")
                if cancel:
                    send_to_rasa("/deny")
                    # select answer questions path
                    send_to_rasa("/deny")
                    answer_job_title()
                else:
                    send_resume_message(resume)
            else:
                send_to_rasa("/deny")
                answer_job_title()
        elif chatbot_type == "2":
            pass
    else:
        # resume last search
        send_to_rasa("/affirm")
    
    # jobs have been displayed, now send_job or refine.
    if refine_job_search is not None:
        send_to_rasa("/refine_job_search")
        if refine_job_search == "location":
            send_to_rasa('/input_refine_job_search_field{"refine_job_search_field": "job_location"}')
            answer_job_location()
        elif refine_job_search == "title":
            send_to_rasa('/input_refine_job_search_field{"refine_job_search_field": "job_title"}')
            answer_job_title()
    
    if chatbot_type == "2":
        send_job()
        screening_questions()
    
    # send_job()
    # # if resume was cancelled initially, upload it again
    # if not is_upload_resume or cancel:
    #     send_resume_message()
    # screening_questions()
    
send_to_rasa("/restart")
send_to_rasa("/greet")

# explore_jobs(is_upload_resume=True, resume=resume_1)
# custom_msgs()

# explore_jobs(is_upload_resume=True, refine_job_search="location", start_new="true")

# explore_jobs(is_upload_resume=True, cancel=True)
# explore_jobs(is_upload_resume=False)
# explore_jobs(is_upload_resume=False, refine_job_search="location")
# explore_jobs(is_upload_resume=True, refine_job_search="location")


# ask_a_question()

# send_to_rasa("/screening_review")

while True:
    print("\nplease enter your message:")
    msg = input()
    # if msg.lower() == "stop":
    #     break

    print()
    if "job:" in msg:
        msg = '/input_select_job{"select_job": "' + msg.split(":")[1].strip() + '"}'
    
    if "q:" in msg:
        msg = '/input_user_question{"user_question": "' + msg.split(":")[1].strip() + '"}'
    
    if "r:" in msg:
        if msg == "r:1":
            send_resume_message(resume_1)
        if msg == "r:2":
            send_resume_message(resume_2)
        continue
    send_to_rasa(msg)
