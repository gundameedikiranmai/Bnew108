import requests
import json
user_id = "39638"
data = {
  "_id": "65fd725a74002decb9b4b61f",
  "sender_id": "0a5fe7e2-e843-11ee-81ea-9d90563c10c2",
  "data": {
    "is_resume_upload": True,
    "resume_upload": "39638",
    "job_title": "Java Full Stack Developer",
    "job_screening_questions": [
      {
        "id": 1,
        "input_type": "radio",
        "data_key": "current_employment",
        "text": "What is your current employment situation?",
        "buttons": [
          {
            "payload": "Working Full-Time",
            "title": "Working Full-Time"
          },
          {
            "payload": "Working Part-Time",
            "title": "Working Part-Time"
          },
          {
            "payload": "Working Freelance",
            "title": "Working Freelance"
          },
          {
            "payload": "Not working currently",
            "title": "Not working currently"
          }
        ]
      },
      {
        "id": 2,
        "input_type": "radio",
        "data_key": "availability_new_opportunity",
        "text": "What's your current availability for new opportunities?",
        "buttons": [
          {
            "payload": "Available Now",
            "title": "Available Now"
          },
          {
            "payload": "Available Soon",
            "title": "Available Soon"
          },
          {
            "payload": "Passively Looking",
            "title": "Passively Looking"
          },
          {
            "payload": "Not Looking",
            "title": "Not Looking"
          }
        ]
      },
      {
        "id": 3,
        "input_type": "radio",
        "data_key": "employment_type",
        "text": "What type of employment are you seeking?",
        "buttons": [
          {
            "payload": "Full-Time Contract",
            "title": "Full-Time Contract"
          },
          {
            "payload": "Part-Time Contract",
            "title": "Part-Time Contract"
          },
          {
            "payload": "Full-Time Employee",
            "title": "Full-Time Employee"
          },
          {
            "payload": "Freelancer",
            "title": "Freelancer"
          },
          {
            "payload": "All the above",
            "title": "All the above"
          }
        ]
      },
      {
        "id": 4,
        "input_type": "radio",
        "data_key": "work_flexibility",
        "text": "What are your preferences regarding work flexibility?",
        "buttons": [
          {
            "payload": "On-Site",
            "title": "On-Site"
          },
          {
            "payload": "Remote",
            "title": "Remote"
          },
          {
            "payload": "Hybrid",
            "title": "Hybrid"
          },
          {
            "payload": "All the above",
            "title": "All the above"
          }
        ]
      }
    ],
    "job_screening_questions_count": 4,
    "screening_question_history": [
      "Working Freelance",
      "Available Now",
      "Freelancer",
      "Hybrid"
    ],
    "job_screening_questions_last_update_time": "2024-03-22 17:28:18.409524"
  }
}

get_url = f"https://api.curately.ai/QADemoCurately/chatBotPref/{user_id}"
post_url = "https://api.curately.ai/QADemoCurately/saveChatBotPref"


get_response = requests.get(get_url).json()
print(get_response)

# get_response = {'json': [{'Label': 'Current Employment Status', 'Value': '', 'Name': 'empStatusLookupID', 'datakey': 'current_employment', 'Options': [{'Name': 'Working Full-Time', 'Type': 'CheckBox', 'LookupId': 10010001}, {'Name': 'Working Part-Time', 'Type': 'CheckBox', 'LookupId': 10010002}, {'Name': 'Working Freelance', 'Type': 'CheckBox', 'LookupId': 10010003}, {'Name': 'Not Working Currently', 'Type': 'CheckBox', 'LookupId': 10010004}]}, {'Label': 'Availability Status', 'Value': '', 'Name': 'empAvailLookupID', 'datakey': 'availability_new_opportunity', 'Options': [{'Name': 'Available Now', 'Type': 'CheckBox', 'LookupId': 10011001}, {'Name': 'Available Soon', 'Type': 'CheckBox', 'LookupId': 10011002}, {'Name': 'Passively Looking', 'Type': 'CheckBox', 'LookupId': 10011003}, {'Name': 'Not Looking', 'Type': 'CheckBox', 'LookupId': 10011004}]}, {'Label': 'Employment Preference', 'Value': '', 'Name': 'empPrefLookupID', 'datakey': 'employment_type', 'Options': [{'Name': 'Any', 'Type': 'Radio Button', 'LookupId': 10019005}, {'Name': 'Part - Time Contract', 'Type': 'CheckBox', 'LookupId': 10012001}, {'Name': 'Full-Time Contract', 'Type': 'CheckBox', 'LookupId': 10012002}, {'Name': 'Full-Time Employee', 'Type': 'CheckBox', 'LookupId': 10012003}, {'Name': 'Freelancer', 'Type': 'CheckBox', 'LookupId': 10012004}]}, {'Label': 'Flexibility Preference', 'Value': '', 'Name': 'empFlexLookupID', 'datakey': 'work_flexibility', 'Options': [{'Name': 'Any', 'Type': 'RadioButton', 'LookupId': 10013004}, {'Name': 'Remote', 'Type': 'CheckBox', 'LookupId': 10013001}, {'Name': 'AtOffice', 'Type': 'CheckBox', 'LookupId': 10013002}, {'Name': 'Hybrid', 'Type': 'CheckBox', 'LookupId': 10013003}]}, {'Label': 'PreferredWorkingHours', 'Value': '', 'Name': 'prefferdworkinghours', 'datakey': 'prefferdworkinghours', 'Options': [{'Name': 'OfficeHours', 'Type': 'CheckBox', 'LookupId': 10019001}, {'Name': 'Mornings', 'Type': 'CheckBox', 'LookupId': 10019002}, {'Name': 'Afternoons', 'Type': 'CheckBox', 'LookupId': 10019003}, {'Name': 'Evening/Nights', 'Type': 'CheckBox', 'LookupId': 10019004}]}, {'Label': 'AreyoulegallyauthorizedtoworkintheUnitedStates?', 'Value': '', 'Name': 'legalStatus', 'datakey': 'legalStatus', 'Options': [{'Name': 'Yes', 'Type': 'CheckBox', 'LookupId': 10015001}, {'Name': 'No', 'Type': 'CheckBox', 'LookupId': 10015002}]}, {'Label': 'DoyouRequireaVisaSponsorship?', 'Value': '', 'Name': 'visaSponsorStatus', 'datakey': 'visaSponsorStatus', 'Options': [{'Name': 'Yes', 'Type': 'CheckBox', 'LookupId': 10016001}, {'Name': 'No', 'Type': 'CheckBox', 'LookupId': 10016002}]}, {'Label': 'CompensationPreference', 'Value': '', 'Name': 'empYearCompensation', 'datakey': 'empYearCompensation', 'Options': [{'Amount': '$0', 'Frequency': 'PerYear', 'Type': 'TextBox'}]}, {'Label': 'CompensationPreference', 'Value': '', 'Name': 'empHourCompensation', 'datakey': 'empHourCompensation', 'Options': [{'Amount': '$0', 'Frequency': 'PerHour', 'Type': 'TextBox'}]}, {'Label': 'PresentjobswithCompensationbelowtheminimumthresholdIprovidedabove.', 'Type': 'CheckBox', 'Name': 'empCompThreshhold', 'datakey': 'empCompThreshhold', 'Value': ''}]}

for item in get_response["json"]:
    for i, q in enumerate(data["data"]["job_screening_questions"]):
        if item["datakey"] == q["data_key"]:
            user_response = data["data"]["screening_question_history"][i]
            for choice in item["Options"]:
                if choice["Name"] == user_response:
                    print(choice["LookupId"])
                    item["Value"] = choice["LookupId"]
                    break
            break

# print(json.dumps(get_response, indent=4))

get_response["userId"] = user_id

response = requests.post(post_url, json=get_response)
print(response.status_code, response.text)
resp = response.json()
print(json.dumps(resp, indent=4))