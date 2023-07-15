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

def upload_resume():
    # url = "https://www4.accuick.com/ChatBot/ResumeUploadChatBot.jsp"
    url = "http://localhost:8000/api/upload_resume"
    files=[
        ('resume',('IT Specialist_Resume.docx',open('/home/dhruv/Downloads/Resume Samples/IT Specialist_Resume.docx','rb'),'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
    ]
    response = requests.request("POST", url, files=files)
    # response = requests.request("POST", url, data=payload)
    print(response.status_code, response.text)
    resp = response.json()
    print(json.dumps(resp, indent=4))

    
# Input: {
# filename: (binary)
# }


def get_screening_questions_for_job_id(job_id):
    # read from sample file for now.
    sample_questions_path = os.path.join("app/rasa", "chatbot_data", "screening_questions", "sample_questions_after_job_apply.json")
    sample_questions_data = json.load(open(sample_questions_path, 'r'))["components"]

    questions_data_transformed = []
    for q in sample_questions_data:
        q_transformed = {}
        if q.get("labelName") is not None:
            q_transformed["text"] = q.get("labelName")
        inputType = q.get("inputType")
        if inputType == "radio":
            q_transformed["buttons"] = [{"payload": val.get("value"), "title": val.get("name")} for val in q.get("PossibleValue", [])]
        elif inputType == "text":
            pass
        questions_data_transformed.append(q_transformed)

    return questions_data_transformed

# print(get_screening_questions_for_job_id(1))
upload_resume()