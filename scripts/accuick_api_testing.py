import requests
import json
import os

# url = "https://www4.accuick.com/Accuick/jobs_formbuilder_action.jsp"

# payload = {"action":"get","jobId":"228679","recrId":"1893"}

# resp = requests.post(url, json=payload)
# print(resp.status_code)
# contents = json.loads(resp.json()["json"])
# print(contents)
# print(json.dumps(contents, indent=4))


def make_request(url, payload):
    response = requests.post(url, json=payload)
    # print(response.status_code, response.text)
    resp = response.json()
    print(json.dumps(resp, indent=4))


def get_tracker_from_rasa(sender_id):
    params = {
        "token": "secret",
    }
    headers = {"Content-Type": "application/json"}
    rasa_x_url = "http://localhost:5005" + f'/conversations/{sender_id}/tracker'
    rasa_response = requests.get(rasa_x_url, headers=headers, params=params).json()
    print(rasa_response["slots"]["resume_upload"])


def upload_resume():
    # url = "https://www4.accuick.com/ChatBot/ResumeUploadChatBot.jsp"
    url = "https://app.curately.ai/Accuick_API/Curately/Chatbot/resumeUpload.jsp"
    files = [
        (
            "resume",
            (
                "IT Specialist_Resume1.docx",
                open(
                    "/home/dhruv/Downloads/Resume Samples/IT Specialist_Resume.docx",
                    "rb",
                ),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        )
    ]
    response = requests.request("POST", url, files=files, data={"clientId": 2})
    # response = requests.request("POST", url, data=payload)
    print(response.status_code, response.text)
    resp = response.json()
    print(json.dumps(resp, indent=4))

def upload_resume2():
    url = "https://api.curately.ai/QADemoCurately/reUploadResume"
    files = [
        (
            "resume",
            (
                "IT Specialist_Resume1.docx",
                open(
                    "/home/dhruv/Downloads/Resume Samples/IT Specialist_Resume.docx",
                    "rb",
                ),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        )
    ]
    response = requests.request("POST", url, files=files, data={"clientId": 2, "userId": 38930})
    # response = requests.request("POST", url, data=payload)
    print(response.status_code, response.text)
    resp = response.json()
    print(json.dumps(resp, indent=4))


def upload_resume3():
    url = "https://api.curately.ai/QADemoCurately/resumeMe"
    files = [
        (
            "resume",
            (
                "IT Specialist_Resume1.docx",
                open(
                    "/home/dhruv/Downloads/Resume Samples/IT Specialist_Resume.docx",
                    "rb",
                ),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        )
    ]
    response = requests.request("POST", url, files=files, data={"clientId": 2})
    # response = requests.request("POST", url, data=payload)
    print(response.status_code, response.text)
    resp = response.json()
    print(json.dumps(resp, indent=4))


def job_search():
    url = "https://api.cxninja.com/DemoCurately/jobsearch"
    payload = {
        "jobquery": [
            {
                "query": "Java Developer",
                "clientId": "2",
                "jobType": "All Job Types",
                "datePosted": "0",
                "locationFilters": [
                    {"address": "", "regionCode": "", "distanceInMiles": 0}
                ],
            }
        ],
        "searchMode": "JOB_SEARCH",
        "disableKeywordMatch": False,
        "enableBroadening": True,
        "keywordMatchMode": "KEYWORD_MATCH_ALL",
        "offset": 0,
    }
    make_request(url, payload)


def job_search2():
    url = "https://api.curately.ai/QADemoCurately/jobsearch"
    payload = {
        "jobquery": [
            {
                "query": "Java Developer",
                "clientId": "2",
                "timeRange":"2024-10-02T15:01:23Z",
                "jobType": "All Job Types",
                "datePosted": "0",
                "locationFilters": [
                    {"address": "", "regionCode": "", "distanceInMiles": 0}
                ],
            }
        ],
        "searchMode": "JOB_SEARCH",
        "disableKeywordMatch": False,
        "enableBroadening": True,
        "keywordMatchMode": "KEYWORD_MATCH_ALL",
        "offset": 0,
    }
    make_request(url, payload)

def job_search3():
    url = "https://api.curately.ai/QADemoCurately/sovrenjobsearch"
    location = "Atlanta, GA".strip()
    city, state, zipcode = "", "", ""
    # 
    if len(location) == 5:
        zipcode = location
    elif not (" " in location or "," in location) or len(location) == 2:
        state = location
    elif "," in location:
        locs = location.split(",")
        city = locs[0].strip()
        state = locs[1].strip()
        if len(locs) > 2:
            zipcode = locs[2].strip()

    # 
    payload = {
        "query": "",
        "city": city,
        "state": state,
        "zipcode": zipcode,
        "radius": "50",
        "daysback": "",
        "isRemote": "",
        "jobType": "",
        "clientids": "2",
        "next": 0,
        "type": "",
    }
    payload = {'query': 'Data Engineer', 'city': '', 'state': 'ga', 'zipcode': '', 'radius': '50', 'daysback': '', 'isRemote': '', 'jobType': '', 'clientids': "3", 'next': 0, 'type': ''}
    print(payload)
    make_request(url, payload)


def job_apply():
    payload = {
        "accuickJobId": 191444,
        "userId": 1236,
        "clientId": 2,
        # "jobTitle":"SF85W1EqkbIacnvOlCk7JaoaoU/7BKmW3MKnDMuIc4Q=",
        # "clientName":"",
        # "city":"",
        # "state":"",
        # "zipcode":"",
        # "payRate":"",
        # "jobType":"",
        "source": "Accuick",
        # "description":"vAR4b/eNUEzps4cuGg+AZZQ6+CCGKwkGDJs6OEqIzfLH1vM6EsBeRTp20nzAPIa66T1RMlK8k5QvpxOoKvybE5NKM13V8kUhKPckc0KH1DxCGzb9WDoe4+zcwbxu9AX678NlH2rsD8RqnXCVsCmjDt1PUYwifVkmuczAf4knQYj0mlJdev7wTgoKIJyYzUWq7bcVYpVq0gyKHfcWsksREvAdd3OzW6PA64N3izQkqSq9coIQO8OmvCcIAyPu7qmC5HXTIJMYzbY2J4oMueUL4x8pIy2qT43Le8tVI2uUro60ge3mzTu6WgBvCzhlmBtl/YBCOvzPVdYAWem2bdWHB39xP6rmT6Gnqc6Az7oS8Auo4"
    }
    url = "https://api.cxninja.com/DemoCurately/jobsapply"
    make_request(url, payload)


def get_screening_questions_for_job_id(job_id):
    # read from sample file for now.
    sample_questions_path = os.path.join(
        "app/rasa",
        "chatbot_data",
        "screening_questions",
        "sample_questions_after_job_apply.json",
    )
    sample_questions_data = json.load(open(sample_questions_path, "r"))["components"]

    questions_data_transformed = []
    for q in sample_questions_data:
        q_transformed = {"input_type": q["inputType"]}
        if q.get("labelName") is not None:
            q_transformed["text"] = q.get("labelName")
        inputType = q.get("inputType")
        if inputType == "radio":
            q_transformed["buttons"] = [
                {"payload": val.get("value"), "title": val.get("name")}
                for val in q.get("PossibleValue", [])
            ]
        elif inputType == "text":
            pass
        questions_data_transformed.append(q_transformed)

    return questions_data_transformed


def send_screening_questions():
    payload = {
        "email": "me@gmail.com",
        "candidateId": "16582",
        "fullName": "John Doe",
        "phoneNumber": "+1 1234567890",
        "jobId": "229664",
        "candidateResponses": [
            {"id": 2, "label": "What is your date of birth?", "answer": "01/01/1960"},
            {"id": 1, "label": "Employee type", "answer": "contract"},
        ],
        "clientId": 1,
    }
    url = "https://search.accuick.com/Twilio/webhook_chatbot.jsp"
    make_request(url, payload)


def get_form_builder():
    url = "https://www4.accuick.com/Accuick_API/Curately/Chatbot/getForm.jsp"
    payload = {"action": "get", "jobId": "446", "recrId": "1893", "clientId": "3"}
    # make_request(url, payload)

    response = requests.post(url, json=payload)
    print(response.status_code, response.text)
    resp = response.json()
    print(json.dumps(resp, indent=4))
    for x in json.loads(resp["json"])["components"]:
        print(json.dumps(x, indent=4))

def get_default_form_builder():
    url = "https://app.curately.ai/Accuick_API/Curately/Chatbot/getDefaultForm.jsp"
    payload = {"clientId":"2","action":"get"}
    response = requests.post(url, json=payload)
    print(response.status_code, response.text)
    resp = response.json()
    # print(json.dumps(resp, indent=4))
    for x in json.loads(resp["json"])["components"]:
        print(json.dumps(x, indent=4))

def sync_email_data():
    payload = {
        "userId": "58507",
        # "firstName":"Manasa",
        # "lastName":"Reddy",
        "clientId": "2",
        "email": "accuicktest2@gmail.com"
    }
    url = "https://api.curately.ai/QADemoCurately/savechatbotinformation"
    make_request(url, payload)
# print(get_screening_questions_for_job_id(1))
# upload_resume()

# send_screening_questions()
# job_apply()
# job_search()
# job_search2()
# job_search3()
# get_form_builder()
# get_default_form_builder()
# upload_resume2()
# upload_resume3()
# get_tracker_from_rasa("bde2192c-d6d0-11ee-a10e-2be33777c5fe")
sync_email_data()